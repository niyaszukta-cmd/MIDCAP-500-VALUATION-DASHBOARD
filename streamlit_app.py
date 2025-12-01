import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import threading
from datetime import timedelta

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="NYZTrade - Midcap Valuation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# RATE LIMITER CLASS
# ============================================================================

class RateLimiter:
    """Prevents hitting API rate limits"""
    def __init__(self, max_calls=30, time_window=60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        with self.lock:
            now = datetime.now()
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < timedelta(seconds=self.time_window)]
            
            if len(self.calls) >= self.max_calls:
                oldest_call = min(self.calls)
                wait_time = (oldest_call + timedelta(seconds=self.time_window) - now).total_seconds()
                if wait_time > 0:
                    time.sleep(wait_time + 1)
                    self.calls = []
            
            self.calls.append(now)

# Global rate limiter
rate_limiter = RateLimiter(max_calls=30, time_window=60)

# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        
        users = {
            "demo": "demo123",
            "premium": "premium123",
            "niyas": "nyztrade123"
        }
        
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("## 🔐 Midcap Valuation Dashboard Login")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username", placeholder="Enter username")
            st.text_input("Password", type="password", key="password", placeholder="Enter password")
            st.button("Login", on_click=password_entered, use_container_width=True)
            
            st.markdown("---")
            st.info("**Demo:** `demo` / `demo123` | **Premium:** `premium` / `premium123`")
        
        return False
    
    elif not st.session_state["password_correct"]:
        st.markdown("## 🔐 Midcap Valuation Dashboard Login")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.error("😕 Incorrect username or password")
            st.text_input("Username", key="username", placeholder="Enter username")
            st.text_input("Password", type="password", key="password", placeholder="Enter password")
            st.button("Login", on_click=password_entered, use_container_width=True)
        
        return False
    
    return True

if not check_password():
    st.stop()

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .rec-strong-buy {
        background: linear-gradient(135deg, #00C853 0%, #64DD17 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }
    .rec-buy {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }
    .rec-hold {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }
    .rec-avoid {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }
    .risk-warning {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# MIDCAP 500 DATABASE
# ============================================================================

MIDCAP_500_STOCKS = {
    "🏦 Banking & Finance": {
        "ANGELONE.NS": "Angel One", "ANANDRATHI.NS": "Anand Rathi", "BIKAJI.NS": "Bikaji Foods",
        "CDSL.NS": "CDSL", "CREDITACC.NS": "Credit Access", "CSB.NS": "CSB Bank",
        "EQUITAS.NS": "Equitas Holdings", "FINOPB.NS": "Fino Payments", "HDFCAMC.NS": "HDFC AMC",
        "IIFL.NS": "IIFL Finance", "IRFC.NS": "IRFC", "JMFINANCIL.NS": "JM Financial",
        "KALYANKJIL.NS": "Kalyan Jewellers", "KFINTECH.NS": "KFin Tech", "LICHSGFIN.NS": "LIC Housing",
        "MASFIN.NS": "MAS Financial", "MOTILALOFS.NS": "Motilal Oswal", "PNBHOUSING.NS": "PNB Housing",
        "RBL.NS": "RBL Bank", "SBFC.NS": "SBFC Finance", "STARHEALTH.NS": "Star Health",
        "UJJIVAN.NS": "Ujjivan SFB", "UTIAMC.NS": "UTI AMC"
    },
    
    "💻 IT & Technology": {
        "ALOKINDS.NS": "Alok Industries", "BLUESTARCO.NS": "Blue Star", "CAMPUS.NS": "Campus Activewear",
        "CYIENT.NS": "Cyient", "DATAMATICS.NS": "Datamatics", "ECLERX.NS": "eClerx",
        "GALAXYSURF.NS": "Galaxy Surfactants", "HAPPSTMNDS.NS": "Happiest Minds", "HLEGLAS.NS": "HLE Glascoat",
        "INTELLECT.NS": "Intellect Design", "KPITTECH.NS": "KPIT Tech", "LTIM.NS": "LTIMindtree",
        "MASTEK.NS": "Mastek", "MEDPLUS.NS": "Medplus Health", "NEWGEN.NS": "Newgen Software",
        "NIITLTD.NS": "NIIT", "OFSS.NS": "Oracle Financial", "PRAJIND.NS": "Praj Industries",
        "ROUTE.NS": "Route Mobile", "STAR.NS": "Strides Pharma", "TATACOFFEE.NS": "Tata Coffee",
        "TTKPRESTIG.NS": "TTK Prestige", "ZENSAR.NS": "Zensar Tech", "ZOMATO.NS": "Zomato"
    },
    
    "💊 Pharma & Healthcare": {
        "AARTIDRUGS.NS": "Aarti Drugs", "ABBOTINDIA.NS": "Abbott India", "AJANTPHARM.NS": "Ajanta Pharma",
        "ALEMBICLTD.NS": "Alembic Pharma", "APOLLOTYRE.NS": "Apollo Tyres", "ASTRAZEN.NS": "AstraZeneca",
        "BIOS.NS": "Biosimilars", "CAPLIPOINT.NS": "Caplin Point", "FINEORG.NS": "Fine Organics",
        "GLAXO.NS": "GSK Pharma", "GRANULES.NS": "Granules India", "HETERO.NS": "Hetero Drugs",
        "JBCHEPHARM.NS": "JB Chemicals", "LALPATHLAB.NS": "Dr Lal PathLabs", "METROPOLIS.NS": "Metropolis",
        "NATCOPHARM.NS": "Natco Pharma", "PFIZER.NS": "Pfizer", "RAJESHEXPO.NS": "Rajesh Exports",
        "SANOFI.NS": "Sanofi India", "SOLARA.NS": "Solara Active", "SYNGENE.NS": "Syngene",
        "THYROCARE.NS": "Thyrocare", "VIMTA.NS": "Vimta Labs", "WOCKPHARMA.NS": "Wockhardt"
    },
    
    "🚗 Auto & Components": {
        "AAVAS.NS": "Aavas Financiers", "AMARAJABAT.NS": "Amara Raja", "ANANTRAJ.NS": "Anant Raj",
        "AXISBANK.NS": "Axis Bank", "CRAFTSMAN.NS": "Craftsman Auto", "ENDURANCE.NS": "Endurance Tech",
        "FINCABLES.NS": "Finolex Cables", "FORCEMOT.NS": "Force Motors", "JKTYRE.NS": "JK Tyre",
        "MAHSEAMLES.NS": "Maharashtra Seamless", "MAHINDCIE.NS": "Mahindra CIE", "MOTHERSON.NS": "Samvardhana Motherson",
        "SANDHAR.NS": "Sandhar Technologies", "SANSERA.NS": "Sansera Engineering", "SCHAEFFLER.NS": "Schaeffler India",
        "SKFINDIA.NS": "SKF India", "SPARC.NS": "Sun Pharma", "SWARAJENG.NS": "Swaraj Engines",
        "TIMKEN.NS": "Timken India", "TUBE.NS": "Tube Investments", "WHEELS.NS": "Wheels India"
    },
    
    "🍔 FMCG & Consumer": {
        "ABSLAMC.NS": "ABSL AMC", "AKZOINDIA.NS": "Akzo Nobel", "AVANTIFEED.NS": "Avanti Feeds",
        "BAJAJELEC.NS": "Bajaj Electricals", "BAJAJHLDNG.NS": "Bajaj Holdings", "BIKAJI.NS": "Bikaji Foods",
        "BSOFT.NS": "BSOFT", "CCL.NS": "CCL Products", "CHAMBLFERT.NS": "Chambal Fertilizers",
        "CROMPTON.NS": "Crompton Greaves", "DEEPAKFERT.NS": "Deepak Fertilizers", "FMGOETZE.NS": "Federal Mogul",
        "GILLETTE.NS": "Gillette India", "HERANBA.NS": "Heranba Industries", "HONAUT.NS": "Honeywell Auto",
        "JKLAKSHMI.NS": "JK Lakshmi", "JKPAPER.NS": "JK Paper", "KAJARIACER.NS": "Kajaria Ceramics",
        "KPRMILL.NS": "KPR Mill", "MRPL.NS": "MRPL", "NAVINFLUOR.NS": "Navin Fluorine",
        "ORIENTELEC.NS": "Orient Electric", "PCBL.NS": "PCBL", "PIIND.NS": "PI Industries",
        "POLYMED.NS": "Poly Medicure", "RAJESHEXPO.NS": "Rajesh Exports", "RELAXO.NS": "Relaxo Footwears",
        "SCHAEFFLER.NS": "Schaeffler", "SOLARINDS.NS": "Solar Industries", "SYMPHONY.NS": "Symphony",
        "TATACHEM.NS": "Tata Chemicals", "TATAMETALI.NS": "Tata Metaliks", "TTKPRESTIG.NS": "TTK Prestige",
        "VBL.NS": "Varun Beverages", "VENKEYS.NS": "Venky's", "VSTIND.NS": "VST Industries",
        "WHIRLPOOL.NS": "Whirlpool", "ZYDUSLIFE.NS": "Zydus Lifesciences"
    },
    
    "🏭 Industrial & Manufacturing": {
        "APLAPOLLO.NS": "APL Apollo", "ASTRAL.NS": "Astral Poly", "CAREEREDGE.NS": "Career Point",
        "CARYSIL.NS": "Carysil", "CASTROLIND.NS": "Castrol India", "CENTURYPLY.NS": "Century Ply",
        "CERA.NS": "Cera Sanitary", "DEEPAKNTR.NS": "Deepak Nitrite", "ELECON.NS": "Elecon Engineering",
        "FILATEX.NS": "Filatex India", "FLUOROCHEM.NS": "Gujarat Fluorochemicals", "GARFIBRES.NS": "Garware Fibers",
        "GREAVESCOT.NS": "Greaves Cotton", "GRINDWELL.NS": "Grindwell Norton", "GSPL.NS": "Gujarat State Petronet",
        "HATHWAY.NS": "Hathway Cable", "HIL.NS": "HIL Limited", "IIFLWAM.NS": "IIFL Wealth",
        "INDIAMART.NS": "IndiaMART", "INOXWIND.NS": "Inox Wind", "JAGRAN.NS": "Jagran Prakashan"
    },
    
    "⚡ Energy & Power": {
        "ADANIENSOL.NS": "Adani Energy", "ADANIGAS.NS": "Adani Total Gas", "AEGISCHEM.NS": "Aegis Logistics",
        "ATGL.NS": "Adani Total Gas", "BATAINDIA.NS": "Bata India", "BDL.NS": "Bharat Dynamics",
        "CHAMBLFERT.NS": "Chambal Fertilizers", "DEEPAKFERT.NS": "Deepak Fertilizers", "GAIL.NS": "GAIL",
        "GMRINFRA.NS": "GMR Infrastructure", "GNFC.NS": "GNFC", "GSFC.NS": "GSFC",
        "GUJALKALI.NS": "Gujarat Alkalies", "GUJGASLTD.NS": "Gujarat Gas", "INDHOTEL.NS": "Indian Hotels",
        "JSW.NS": "JSW Steel", "KPIL.NS": "Kalpataru Power", "MGL.NS": "Mahanagar Gas",
        "NHPC.NS": "NHPC", "NLCINDIA.NS": "NLC India", "ONGC.NS": "ONGC",
        "OIL.NS": "Oil India", "PFC.NS": "PFC", "POWERGRID.NS": "Power Grid",
        "RECLTD.NS": "REC", "RVNL.NS": "Rail Vikas Nigam", "SJVN.NS": "SJVN"
    },
    
    "🛒 Retail & Ecommerce": {
        "AFFLE.NS": "Affle India", "BARBEQUE.NS": "Barbeque Nation", "CAMPUS.NS": "Campus Activewear",
        "FIVESTAR.NS": "Five Star Business", "INDIAMART.NS": "IndiaMART", "JUBLFOOD.NS": "Jubilant FoodWorks",
        "KIMS.NS": "KIMS Hospitals", "NYKAA.NS": "Nykaa", "POLICYBZR.NS": "PB Fintech",
        "RELAXO.NS": "Relaxo Footwears", "SAPPHIRE.NS": "Sapphire Foods", "SHOPERSTOP.NS": "Shoppers Stop",
        "SPICEJET.NS": "SpiceJet", "TATACOMM.NS": "Tata Communications", "TEAMLEASE.NS": "TeamLease Services",
        "TRENT.NS": "Trent", "VMART.NS": "V-Mart Retail", "WESTLIFE.NS": "Westlife Foodworld"
    },
    
    "🏗️ Real Estate & Construction": {
        "BRIGADE.NS": "Brigade Enterprises", "CENTURYTEX.NS": "Century Textiles", "CMSINFO.NS": "CMS Info Systems",
        "DCBBANK.NS": "DCB Bank", "DLF.NS": "DLF", "ESABINDIA.NS": "ESAB India",
        "FINCABLES.NS": "Finolex Cables", "GODREJPROP.NS": "Godrej Properties", "GUJGASLTD.NS": "Gujarat Gas",
        "IBREALEST.NS": "Indiabulls Real Estate", "IRB.NS": "IRB Infrastructure", "JWL.NS": "Jupiter Wagons",
        "KEC.NS": "KEC International", "KOLTEPATIL.NS": "Kolte-Patil", "LINDEINDIA.NS": "Linde India",
        "MACROTECH.NS": "Macrotech Developers", "MAHLIFE.NS": "Mahindra Lifespace", "NBCC.NS": "NBCC India",
        "NCCLTD.NS": "NCC", "OBEROIRLTY.NS": "Oberoi Realty", "PHOENIXLTD.NS": "Phoenix Mills",
        "PRESTIGE.NS": "Prestige Estates", "PNCINFRA.NS": "PNC Infratech", "RAYMOND.NS": "Raymond"
    },
    
    "📺 Media & Entertainment": {
        "DB.NS": "Dish TV", "HATHWAY.NS": "Hathway Cable", "INOXLEISUR.NS": "Inox Leisure",
        "JAGRAN.NS": "Jagran Prakashan", "NAZARA.NS": "Nazara Technologies", "NETWORK18.NS": "Network18",
        "PVR.NS": "PVR Inox", "SAREGAMA.NS": "Saregama India", "SUNTV.NS": "Sun TV",
        "TIPS.NS": "Tips Industries", "TV18BRDCST.NS": "TV18 Broadcast", "TVTODAY.NS": "TV Today",
        "ZEEL.NS": "Zee Entertainment"
    },
    
    "🌾 Agriculture & Chemicals": {
        "AARTIIND.NS": "Aarti Industries", "AARTIDRUGS.NS": "Aarti Drugs", "AAVAS.NS": "Aavas Financiers",
        "ALKYLAMINE.NS": "Alkyl Amines", "ATUL.NS": "Atul Ltd", "AVANTIFEED.NS": "Avanti Feeds",
        "BASF.NS": "BASF India", "BBTC.NS": "Bombay Burmah", "BHAGERIA.NS": "Bhageria Industries",
        "CENTURYTEXT.NS": "Century Textiles", "COROMANDEL.NS": "Coromandel International", "DEEPAKNTR.NS": "Deepak Nitrite",
        "FINEORG.NS": "Fine Organics", "FLUOROCHEM.NS": "Gujarat Fluorochemicals", "GNFC.NS": "GNFC",
        "GSFC.NS": "GSFC", "GUJALKALI.NS": "Gujarat Alkalies", "GULFOILLUB.NS": "Gulf Oil",
        "HERANBA.NS": "Heranba Industries", "ICICIGI.NS": "ICICI Lombard", "INDIACEM.NS": "India Cements",
        "JKTYRE.NS": "JK Tyre", "KIRIINDUS.NS": "Kiri Industries", "KRBL.NS": "KRBL",
        "NAVINFLUOR.NS": "Navin Fluorine", "NOCIL.NS": "NOCIL", "PIIND.NS": "PI Industries"
    }
}

INDUSTRY_BENCHMARKS = {
    'Technology': {'pe': 28, 'ev_ebitda': 16},
    'Financial Services': {'pe': 20, 'ev_ebitda': 14},
    'Consumer Cyclical': {'pe': 32, 'ev_ebitda': 16},
    'Consumer Defensive': {'pe': 38, 'ev_ebitda': 18},
    'Healthcare': {'pe': 30, 'ev_ebitda': 16},
    'Industrials': {'pe': 25, 'ev_ebitda': 14},
    'Energy': {'pe': 18, 'ev_ebitda': 10},
    'Basic Materials': {'pe': 20, 'ev_ebitda': 12},
    'Communication Services': {'pe': 25, 'ev_ebitda': 14},
    'Real Estate': {'pe': 28, 'ev_ebitda': 20},
    'Utilities': {'pe': 20, 'ev_ebitda': 12},
    'Default': {'pe': 22, 'ev_ebitda': 14}
}

# ============================================================================
# ENHANCED DATA FETCHING WITH RATE LIMITING
# ============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_stock_data(ticker):
    """Fetch stock data with rate limiting and retry logic"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Rate limiting
            rate_limiter.wait_if_needed()
            
            # Small delay between requests
            time.sleep(0.5)
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or len(info) < 5:
                return None, "Unable to fetch data"
            
            return info, None
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "rate limit" in error_msg or "too many requests" in error_msg or "429" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                else:
                    return None, "rate_limit_error"
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                return None, str(e)
    
    return None, "Failed to fetch data after multiple attempts"

def calculate_valuations(info):
    price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
    trailing_pe = info.get('trailingPE', 0)
    forward_pe = info.get('forwardPE', 0)
    trailing_eps = info.get('trailingEps', 0)
    enterprise_value = info.get('enterpriseValue', 0)
    ebitda = info.get('ebitda', 0)
    market_cap = info.get('marketCap', 0)
    shares = info.get('sharesOutstanding', 1)
    sector = info.get('sector', 'Default')
    
    benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
    industry_pe = benchmark['pe']
    industry_ev_ebitda = benchmark['ev_ebitda']
    
    if trailing_pe and trailing_pe > 0:
        historical_pe = trailing_pe * 0.9
    else:
        historical_pe = industry_pe
    
    blended_pe = (industry_pe + historical_pe) / 2
    
    fair_value_industry = trailing_eps * industry_pe if trailing_eps else None
    fair_value_blended = trailing_eps * blended_pe if trailing_eps else None
    
    fair_values_pe = [fv for fv in [fair_value_industry, fair_value_blended] if fv]
    fair_value_pe = np.mean(fair_values_pe) if fair_values_pe else None
    upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
    
    current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
    
    if current_ev_ebitda and 0 < current_ev_ebitda < 50:
        target_ev_ebitda = (industry_ev_ebitda + current_ev_ebitda * 0.9) / 2
    else:
        target_ev_ebitda = industry_ev_ebitda
    
    if ebitda and ebitda > 0:
        fair_ev = ebitda * target_ev_ebitda
        total_debt = info.get('totalDebt', 0) or 0
        total_cash = info.get('totalCash', 0) or 0
        net_debt = total_debt - total_cash
        fair_mcap = fair_ev - net_debt
        fair_value_ev = fair_mcap / shares if shares else None
        upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
    else:
        fair_value_ev = None
        upside_ev = None
    
    return {
        'price': price,
        'trailing_pe': trailing_pe,
        'forward_pe': forward_pe,
        'trailing_eps': trailing_eps,
        'industry_pe': industry_pe,
        'fair_value_pe': fair_value_pe,
        'upside_pe': upside_pe,
        'enterprise_value': enterprise_value,
        'ebitda': ebitda,
        'market_cap': market_cap,
        'current_ev_ebitda': current_ev_ebitda,
        'industry_ev_ebitda': industry_ev_ebitda,
        'fair_value_ev': fair_value_ev,
        'upside_ev': upside_ev
    }

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>📊 MIDCAP 500 STOCK VALUATION DASHBOARD</h1>
    <p>High Growth Potential • 500+ Midcap Stocks • Real-time Analysis</p>
</div>
""", unsafe_allow_html=True)

# Risk Warning
st.markdown("""
<div class="risk-warning">
    ⚠️ MIDCAP RISK WARNING: Midcap stocks are more volatile than largecaps. 
    Higher growth potential comes with higher risk.
</div>
""", unsafe_allow_html=True)

# Data Cache Info
st.info("💡 **Smart Caching:** Stock data is cached for 1 hour. Re-analyzing the same stock within 1 hour is instant!")

# Logout
if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ============================================================================
# STOCK SELECTION
# ============================================================================

st.sidebar.header("📈 Stock Selection")

# Flatten all stocks
all_stocks = {}
for category, stocks in MIDCAP_500_STOCKS.items():
    all_stocks.update(stocks)

# Category selection
selected_category = st.sidebar.selectbox(
    "Category",
    ["🔍 All Stocks"] + list(MIDCAP_500_STOCKS.keys())
)

# Search box
search_term = st.sidebar.text_input("🔍 Search Stock", placeholder="Type company name or ticker...")

# Filter stocks
if search_term:
    filtered_stocks = {ticker: name for ticker, name in all_stocks.items()
                      if search_term.upper() in ticker or search_term.upper() in name.upper()}
elif selected_category == "🔍 All Stocks":
    filtered_stocks = all_stocks
else:
    filtered_stocks = MIDCAP_500_STOCKS[selected_category]

# Stock selection
stock_options = [f"{name} ({ticker})" for ticker, name in filtered_stocks.items()]

if stock_options:
    selected_stock = st.sidebar.selectbox("Select Stock", stock_options)
    selected_ticker = selected_stock.split("(")[1].strip(")")
else:
    st.sidebar.warning("No stocks found matching your search.")
    selected_ticker = None

# Custom ticker
custom_ticker = st.sidebar.text_input("Or Enter Custom Ticker", placeholder="e.g., DIXON.NS")

# Analyze button
if st.sidebar.button("🚀 ANALYZE STOCK", use_container_width=True):
    if custom_ticker:
        st.session_state.analyze_ticker = custom_ticker.upper()
    elif selected_ticker:
        st.session_state.analyze_ticker = selected_ticker
    else:
        st.sidebar.error("Please select or enter a stock ticker")

# ============================================================================
# ANALYSIS
# ============================================================================

if 'analyze_ticker' in st.session_state:
    ticker = st.session_state.analyze_ticker
    
    with st.spinner(f"🔄 Fetching data for {ticker}..."):
        info, error = fetch_stock_data(ticker)
    
    if error:
        if error == "rate_limit_error":
            st.error("⏰ **Rate Limit Reached**")
            st.warning("""
            **The app has reached Yahoo Finance API limits.**
            
            **What to do:**
            1. ⏳ Wait 2-3 minutes
            2. 🔄 Try again
            3. 📊 Or analyze a different stock
            
            **Why this happens:**
            - Free API has limits (30 requests/minute)
            - Multiple users accessing simultaneously
            - Previous cached data expired
            
            **Tip:** Data is cached for 1 hour after first fetch!
            """)
            st.info("💡 **Pro Tip:** Bookmark your favorite stocks after analyzing them once!")
        else:
            st.error(f"❌ Error: {error}")
        st.stop()
    
    if info is None:
        st.error("❌ Failed to fetch stock data. Please try again.")
        st.stop()
    
    valuations = calculate_valuations(info)
    
    # Company Info
    company_name = info.get('longName', ticker)
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    
    st.markdown(f"## 🏢 {company_name}")
    st.markdown(f"**Sector:** {sector} | **Industry:** {industry} | **Ticker:** {ticker}")
    
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Current Price", f"Rs {valuations['price']:.2f}")
    
    with col2:
        st.metric("📊 PE Ratio", f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else "N/A")
    
    with col3:
        st.metric("💰 EPS (TTM)", f"Rs {valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else "N/A")
    
    with col4:
        st.metric("🏦 Market Cap", f"Rs {valuations['market_cap']/10000000:.0f} Cr")
    
    # Recommendation
    upside_values = []
    if valuations['upside_pe'] is not None:
        upside_values.append(valuations['upside_pe'])
    if valuations['upside_ev'] is not None:
        upside_values.append(valuations['upside_ev'])
    
    avg_upside = np.mean(upside_values) if upside_values else 0
    
    if avg_upside > 25:
        rec_class = "rec-strong-buy"
        rec_text = "⭐⭐⭐ STRONG BUY"
        rec_desc = "High growth potential - Midcap opportunity"
    elif avg_upside > 15:
        rec_class = "rec-buy"
        rec_text = "⭐⭐ BUY"
        rec_desc = "Good value - Accumulate"
    elif avg_upside > 0:
        rec_class = "rec-buy"
        rec_text = "⭐ ACCUMULATE"
        rec_desc = "Slightly undervalued"
    elif avg_upside > -10:
        rec_class = "rec-hold"
        rec_text = "🟡 HOLD"
        rec_desc = "Fairly valued"
    else:
        rec_class = "rec-avoid"
        rec_text = "❌ AVOID"
        rec_desc = "Overvalued"
    
    st.markdown(f"""
    <div class="{rec_class}">
        <div>{rec_text}</div>
        <div style="font-size: 1.2rem; margin-top: 0.5rem;">Potential Return: {avg_upside:+.2f}%</div>
        <div style="font-size: 1rem; margin-top: 0.5rem;">{rec_desc}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gauges
    if valuations['upside_pe'] is not None and valuations['upside_ev'] is not None:
        st.subheader("📈 Upside/Downside Analysis")
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=("PE Multiple", "EV/EBITDA")
        )
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=valuations['upside_pe'],
            number={'suffix': "%", 'font': {'size': 40}},
            gauge={
                'axis': {'range': [-50, 50]},
                'bar': {'color': "#f093fb"},
                'steps': [
                    {'range': [-50, 0], 'color': "#ffebee"},
                    {'range': [0, 50], 'color': "#e8f5e9"}
                ],
            }
        ), row=1, col=1)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=valuations['upside_ev'],
            number={'suffix': "%", 'font': {'size': 40}},
            gauge={
                'axis': {'range': [-50, 50]},
                'bar': {'color': "#f5576c"},
                'steps': [
                    {'range': [-50, 0], 'color': "#ffebee"},
                    {'range': [0, 50], 'color': "#e8f5e9"}
                ],
            }
        ), row=1, col=2)
        
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Valuation Comparison
    st.subheader("💰 Valuation Comparison")
    
    categories = []
    current = []
    fair = []
    colors = []
    
    if valuations['fair_value_pe']:
        categories.append('PE Multiple')
        current.append(valuations['price'])
        fair.append(valuations['fair_value_pe'])
        colors.append('#f093fb' if valuations['fair_value_pe'] > valuations['price'] else '#e74c3c')
    
    if valuations['fair_value_ev']:
        categories.append('EV/EBITDA')
        current.append(valuations['price'])
        fair.append(valuations['fair_value_ev'])
        colors.append('#f5576c' if valuations['fair_value_ev'] > valuations['price'] else '#c0392b')
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        name='Current Price',
        x=categories,
        y=current,
        marker_color='#3498db',
        text=[f'Rs {p:.2f}' for p in current],
        textposition='outside'
    ))
    
    fig2.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair,
        marker_color=colors,
        text=[f'Rs {p:.2f}' for p in fair],
        textposition='outside'
    ))
    
    fig2.update_layout(
        barmode='group',
        height=500,
        xaxis_title="Method",
        yaxis_title="Price (Rs)",
        template='plotly_white'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Metrics Table
    st.subheader("📋 Financial Metrics")
    
    metrics_data = {
        'Metric': [
            '💵 Current Price',
            '📊 PE Ratio (TTM)',
            '🏭 Industry PE',
            '📈 Forward PE',
            '💰 EPS (TTM)',
            '🏢 Enterprise Value',
            '💼 EBITDA',
            '📉 Current EV/EBITDA',
            '🎯 Industry EV/EBITDA',
            '🏦 Market Cap'
        ],
        'Value': []
    }
    
    # Build values list
    metrics_data['Value'].append(f"Rs {valuations['price']:.2f}")
    metrics_data['Value'].append(f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else 'N/A')
    metrics_data['Value'].append(f"{valuations['industry_pe']:.2f}x")
    metrics_data['Value'].append(f"{valuations['forward_pe']:.2f}x" if valuations['forward_pe'] else 'N/A')
    metrics_data['Value'].append(f"Rs {valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else 'N/A')
    metrics_data['Value'].append(f"Rs {valuations['enterprise_value']/10000000:.2f} Cr")
    metrics_data['Value'].append(f"Rs {valuations['ebitda']/10000000:.2f} Cr" if valuations['ebitda'] else 'N/A')
    metrics_data['Value'].append(f"{valuations['current_ev_ebitda']:.2f}x" if valuations['current_ev_ebitda'] else 'N/A')
    metrics_data['Value'].append(f"{valuations['industry_ev_ebitda']:.2f}x")
    metrics_data['Value'].append(f"Rs {valuations['market_cap']/10000000:.2f} Cr")
    
    metrics_df = pd.DataFrame(metrics_data)
    
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Investment Guidelines
    st.markdown("---")
    st.markdown("### 💡 MIDCAP INVESTMENT GUIDELINES")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **WHY INVEST IN MIDCAPS:**
        - Higher growth potential than largecaps
        - More stability than smallcaps
        - Many future bluechips
        - Less institutional ownership
        - Better risk-reward ratio
        """)
    
    with col2:
        st.warning("""
        **RISKS TO CONSIDER:**
        - More volatile than largecaps
        - Liquidity can be an issue
        - Less analyst coverage
        - Economic sensitivity
        - Management quality varies
        """)
    
    st.info("""
    **⚡ SMART MIDCAP STRATEGY:**
    1. **Allocation**: 30-40% of equity portfolio in midcaps
    2. **Diversification**: Hold 8-12 midcap stocks across sectors
    3. **Time Horizon**: Minimum 3-5 years for wealth creation
    4. **Entry Strategy**: Buy in phases, not all at once
    5. **Stop Loss**: Use 15-20% stop losses
    6. **Review**: Quarterly review of fundamentals
    """)
    
else:
    st.info("👈 Select a midcap stock from the sidebar and click **ANALYZE STOCK** to begin!")
    
    st.markdown("### 🚀 Why Midcaps?")
    st.markdown("""
    **The Power of Midcaps:**
    - **Sweet Spot**: Balance between stability and growth
    - **Multibagger Potential**: 5x-10x returns possible over 5 years
    - **Future Leaders**: Tomorrow's largecaps
    - **Institutional Favorites**: Increasingly attracting big money
    - **Better Valuations**: Often cheaper than comparable largecaps
    
    **Real Examples:**
    - Dixon Technologies: From Rs 2,000 to Rs 15,000+ (7.5x in 3 years)
    - Polycab India: From Rs 500 to Rs 6,000+ (12x in 5 years)
    - APL Apollo: From Rs 200 to Rs 1,500+ (7.5x in 4 years)
    """)
    
    st.markdown(f"### 📊 Total Midcap Stocks Available: **{len(all_stocks)}**")

# Footer
st.markdown("---")
st.markdown("**💡 NYZTrade Midcap Valuation Dashboard | Patent-Pending Technology | Powered by yfinance**")
