"""
Warm the shared cache. Run this on a schedule, never inside the app.

    python refresh_cache.py              # the whole universe
    python refresh_cache.py --limit 20   # a quick smoke test
    python refresh_cache.py --dry-run    # show the plan, call nothing

This is the piece that makes the screener safe to sell. Every Yahoo request
the product makes happens here, on a timer, from one place. However many
people use the app, the bill stays the same: one pass over the universe.

Credentials come from the environment so a scheduler can supply them:

    export SUPABASE_URL="https://xxxx.supabase.co"
    export SUPABASE_SERVICE_KEY="sb_secret_xxx"

GitHub Actions is the easiest free scheduler; the workflow is in SETUP_CACHE.md.
"""

import argparse
import os
import sys
import time

import market_cache as mc


def universe():
    """Read the ticker list out of the app rather than keeping a second copy,
    so adding a stock to the app cannot silently leave it uncached."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import midcap_app as app
    except Exception as exc:
        print(f"Could not import midcap_app.py to read the ticker list: {exc}")
        print("Put refresh_cache.py in the same folder as the app.")
        return []
    stocks = getattr(app, "INDIAN_STOCKS", {})
    out = []
    for group in stocks.values():
        out.extend(group.keys())
    return list(dict.fromkeys(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0,
                    help="only refresh this many tickers")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rate", type=int, default=mc.LIVE_CALLS_PER_MINUTE,
                    help="Yahoo calls per minute (default %(default)s)")
    args = ap.parse_args()

    tickers = universe()
    if args.limit:
        tickers = tickers[:args.limit]
    if not tickers:
        print("No tickers found. Nothing to do.")
        return 1

    print(f"Universe: {len(tickers)} tickers")
    if not mc.configured():
        print("No Supabase settings found, so there is nowhere shared to write.")
        print("Set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
        return 1

    mins = len(tickers) / max(1, args.rate)
    print(f"Rate: {args.rate}/min, so roughly {mins:.0f} minute(s)")
    if args.dry_run:
        print("Dry run. First few:", ", ".join(tickers[:8]))
        return 0

    mc.LIVE_CALLS_PER_MINUTE = args.rate
    started = time.time()

    def progress(done, total, ticker, ok):
        if done % 10 == 0 or done == total or not ok:
            mark = "" if ok else "  (no data)"
            print(f"  {done:4}/{total}  {ticker}{mark}", flush=True)

    result = mc.refresh(tickers, on_progress=progress)
    took = time.time() - started

    print(f"\nRefreshed {result['refreshed']} of {result['total']} "
          f"in {took/60:.1f} minutes")
    if result["failed"]:
        print(f"No data for {len(result['failed'])}: "
              f"{', '.join(result['failed'][:12])}"
              f"{' ...' if len(result['failed']) > 12 else ''}")

    # A handful of failures is normal: delisted symbols, renamed tickers.
    # Most of the universe failing means something systemic, worth a loud exit
    # code so a scheduled run shows up as failed rather than passing quietly.
    if result["refreshed"] < max(1, int(result["total"] * 0.6)):
        print("\nMore than 40% failed. Likely rate limiting or a bad ticker "
              "list rather than individual stocks.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
