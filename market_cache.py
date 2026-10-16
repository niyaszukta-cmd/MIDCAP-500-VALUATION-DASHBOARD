"""
Shared market-data cache for the NYZTrade screener.

WHY THIS EXISTS
---------------
The screener used to call yf.Ticker(t).info once per stock, inside the user's
request. Three things make that break as soon as real users arrive:

  1. .info is one HTTP call per ticker to Yahoo's most rate-limited endpoint.
     A 90-stock category is 90 calls for one click of one button.

  2. Streamlit Cloud gives every visitor the SAME outbound IP. Ten people
     screening at once is not ten small bursts, it is one burst of 900
     requests from a single address. Yahoo answers that with 429.

  3. st.cache_data lives in the process. Community Cloud sleeps the app after
     idle time and restarts it on deploy, and each restart throws the cache
     away, so the first visitor back pays the full cost again.

THE FIX
-------
Reading and fetching are separated. Users read from a cache; only the refresh
job talks to Yahoo.

    layer 1  process memory   microseconds, per container, dies on restart
    layer 2  Supabase table   milliseconds, shared by everyone, survives restarts
    layer 3  Yahoo            last resort, throttled, never during a screen

The cost stops scaling with users. One refresh of a 109-ticker universe is 109
calls a day no matter whether one person or a thousand use the app.

Two rules this module keeps, because they are what make it sellable:

  * It never raises at the caller. A dead database or a 429 degrades to older
    data, and every row carries how old it is so the UI can say so.
  * It never fetches live inside a screen unless explicitly told it may.

No new dependencies: Supabase is reached over its REST API with requests,
exactly as nyz_access.py already does.
"""

import json
import os
import random
import threading
import time

import requests

try:
    import streamlit as st
except Exception:          # the refresh job runs without Streamlit
    st = None


# ---------------------------------------------------------------------------
# configuration
# ---------------------------------------------------------------------------
TABLE = "quote_cache"

# How old a row may be before a screen treats it as stale. Fundamentals barely
# move intraday, so a day is generous; the refresh job keeps it far fresher.
DEFAULT_MAX_AGE = 24 * 3600

# Rows older than this are not shown at all, even as a fallback. A price from
# last month is worse than saying "we could not refresh this".
HARD_EXPIRY = 7 * 24 * 3600

# Ceiling on live calls, enforced across threads in this process. Yahoo is not
# documented, so this is deliberately conservative.
LIVE_CALLS_PER_MINUTE = 20

_mem = {}                   # ticker -> (payload, fetched_at)
_mem_lock = threading.Lock()
_bucket_lock = threading.Lock()
_bucket = []                # timestamps of recent live calls


def _secret(name, default=None):
    """Read from Streamlit secrets when present, else the environment."""
    if st is not None:
        try:
            val = st.secrets.get(name)
            if val:
                return val
        except Exception:
            pass
    return os.environ.get(name.upper(), default)


def _sb():
    url = (_secret("supabase_url") or "").rstrip("/")
    key = _secret("supabase_service_key") or ""
    return (url, key) if (url and key) else (None, None)


def _headers(key):
    """New-style sb_secret_ keys go in apikey only; legacy JWTs also need
    Authorization. Sending Bearer with an sb_secret_ key is rejected."""
    h = {"apikey": key, "Content-Type": "application/json"}
    if key.startswith("eyJ"):
        h["Authorization"] = f"Bearer {key}"
    return h


def configured():
    """True when a shared cache is available. False means memory-only."""
    return _sb()[0] is not None


# ---------------------------------------------------------------------------
# throttle
# ---------------------------------------------------------------------------
def _take_slot(timeout=30):
    """Block until a live call is allowed, or give up. Returns True if taken."""
    deadline = time.time() + timeout
    while True:
        with _bucket_lock:
            now = time.time()
            _bucket[:] = [t for t in _bucket if now - t < 60]
            if len(_bucket) < LIVE_CALLS_PER_MINUTE:
                _bucket.append(now)
                return True
        if time.time() > deadline:
            return False
        # jitter, so parallel workers do not all wake together
        time.sleep(0.4 + random.random() * 0.4)


# ---------------------------------------------------------------------------
# layer 2: Supabase
# ---------------------------------------------------------------------------
def _db_read(tickers):
    """{ticker: (payload, age_seconds)} for whatever the table holds."""
    url, key = _sb()
    if not url or not tickers:
        return {}
    out = {}
    # URL length is finite, so ask in chunks rather than one huge in() list
    for i in range(0, len(tickers), 100):
        chunk = tickers[i:i + 100]
        quoted = ",".join('"%s"' % t.replace('"', "") for t in chunk)
        try:
            r = requests.get(
                f"{url}/rest/v1/{TABLE}",
                headers=_headers(key), timeout=8,
                params={"ticker": f"in.({quoted})",
                        "select": "ticker,data,updated_at"})
            if r.status_code >= 300:
                continue
            now = time.time()
            for row in r.json() or []:
                payload = row.get("data")
                if isinstance(payload, str):
                    try:
                        payload = json.loads(payload)
                    except Exception:
                        continue
                if not isinstance(payload, dict):
                    continue
                stamp = payload.get("_fetched_at")
                age = max(0.0, now - float(stamp)) if stamp else HARD_EXPIRY
                out[row["ticker"]] = (payload, age)
        except Exception:
            # A database wobble must not take the screener down with it.
            continue
    return out


def _db_write(rows):
    """Upsert. Failure is silent: a cache that cannot be written is still a
    working app, just a slower one."""
    url, key = _sb()
    if not url or not rows:
        return False
    body = [{"ticker": t, "data": p} for t, p in rows.items()]
    try:
        h = _headers(key)
        h["Prefer"] = "resolution=merge-duplicates,return=minimal"
        r = requests.post(f"{url}/rest/v1/{TABLE}?on_conflict=ticker",
                          headers=h, json=body, timeout=12)
        return r.status_code < 300
    except Exception:
        return False


# ---------------------------------------------------------------------------
# layer 3: Yahoo
# ---------------------------------------------------------------------------
def _fetch_one(ticker):
    """One ticker's fundamentals. Returns a payload dict, or None."""
    import yfinance as yf
    if not _take_slot():
        return None
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception:
        return None
    if len(info) < 5:
        return None
    info = {k: v for k, v in info.items() if _jsonable(v)}
    info["_fetched_at"] = time.time()
    return info


def _jsonable(v):
    return v is None or isinstance(v, (str, int, float, bool, list, dict))


def fetch_prices(tickers, period="1y"):
    """Batched history for many tickers in ONE request rather than one each.

    This is the only part of the data Yahoo will serve in bulk, so it is worth
    using: 90 tickers becomes 1 call instead of 90.
    """
    import yfinance as yf
    if not tickers:
        return {}
    if not _take_slot():
        return {}
    try:
        df = yf.download(list(tickers), period=period, interval="1d",
                         group_by="ticker", auto_adjust=False,
                         progress=False, threads=True)
    except Exception:
        return {}
    out = {}
    for t in tickers:
        try:
            sub = df[t] if len(tickers) > 1 else df
            closes = sub["Close"].dropna()
            if closes.empty:
                continue
            out[t] = {
                "price": float(closes.iloc[-1]),
                "52w_high": float(sub["High"].dropna().max()),
                "52w_low": float(sub["Low"].dropna().min()),
                "volume": float(sub["Volume"].dropna().iloc[-1])
                if not sub["Volume"].dropna().empty else None,
                "avg_volume": float(sub["Volume"].dropna().tail(20).mean())
                if not sub["Volume"].dropna().empty else None,
            }
        except Exception:
            continue
    return out


# ---------------------------------------------------------------------------
# the entry point the app uses
# ---------------------------------------------------------------------------
def get_quotes(tickers, max_age=DEFAULT_MAX_AGE, allow_live=False,
               live_budget=8):
    """Return {ticker: payload} plus a small report on where it came from.

    allow_live=False is the right setting for a screener: it reads cache only,
    so a hundred people screening at once make zero Yahoo calls. Live fetching
    is for the single-stock view, where one user looking at one stock is a
    request Yahoo will not mind.

    live_budget caps how many misses a single call will chase, so one unlucky
    user cannot trigger a hundred live requests.
    """
    tickers = [t for t in dict.fromkeys(tickers) if t]
    found, report = {}, {"memory": 0, "database": 0, "live": 0,
                         "stale": 0, "missing": 0, "oldest_age": 0.0}
    if not tickers:
        return found, report

    now = time.time()
    pending = []

    # layer 1
    with _mem_lock:
        for t in tickers:
            hit = _mem.get(t)
            if hit and now - hit[1] <= max_age:
                found[t] = hit[0]
                report["memory"] += 1
            else:
                pending.append(t)

    # layer 2
    if pending:
        rows = _db_read(pending)
        still = []
        for t in pending:
            row = rows.get(t)
            if not row or row[1] > HARD_EXPIRY:
                still.append(t)
                continue
            payload, age = row
            found[t] = payload
            report["oldest_age"] = max(report["oldest_age"], age)
            with _mem_lock:
                _mem[t] = (payload, now - age)
            if age > max_age:
                # Usable, just old. Counted so the UI can say "as of ...".
                report["stale"] += 1
                still.append(t) if allow_live else None
            else:
                report["database"] += 1
        pending = still

    # layer 3, only when the caller allows it
    if pending and allow_live:
        fresh = {}
        for t in pending[:live_budget]:
            payload = _fetch_one(t)
            if payload:
                fresh[t] = payload
                found[t] = payload
                report["live"] += 1
                with _mem_lock:
                    _mem[t] = (payload, time.time())
        if fresh:
            _db_write(fresh)

    report["missing"] = len([t for t in tickers if t not in found])
    return found, report


def age_text(seconds):
    """'4 minutes ago' style, for telling the user how fresh a screen is."""
    if not seconds or seconds < 0:
        return "just now"
    m = int(seconds // 60)
    if m < 1:
        return "just now"
    if m < 60:
        return f"{m} minute{'s' if m != 1 else ''} ago"
    h = m // 60
    if h < 24:
        return f"{h} hour{'s' if h != 1 else ''} ago"
    d = h // 24
    return f"{d} day{'s' if d != 1 else ''} ago"


# ---------------------------------------------------------------------------
# used by the refresh job
# ---------------------------------------------------------------------------
def refresh(tickers, period="1y", on_progress=None):
    """Warm the cache for a list of tickers. Meant to run on a schedule, not
    in a user's request. Returns a summary dict."""
    tickers = [t for t in dict.fromkeys(tickers) if t]
    done, failed = 0, []

    prices = fetch_prices(tickers, period=period)   # one batched call

    payloads = {}
    for i, t in enumerate(tickers):
        payload = _fetch_one(t)
        if payload is None:
            # Keep the batched price data even when .info is refused, so the
            # row is still useful rather than absent.
            if t in prices:
                payload = dict(prices[t])
                payload["_fetched_at"] = time.time()
                payload["_partial"] = True
            else:
                failed.append(t)
                if on_progress:
                    on_progress(i + 1, len(tickers), t, False)
                continue
        else:
            for k, v in prices.get(t, {}).items():
                payload.setdefault(k, v)
        payloads[t] = payload
        done += 1
        if on_progress:
            on_progress(i + 1, len(tickers), t, True)
        if len(payloads) >= 25:
            _db_write(payloads)
            payloads = {}

    if payloads:
        _db_write(payloads)
    return {"refreshed": done, "failed": failed, "total": len(tickers)}
