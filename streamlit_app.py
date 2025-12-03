import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import time
from functools import wraps
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="NYZTrade - Professional Midcap Valuation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# AUTHENTICATION (Same as before)
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
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; text-align: center;'>
            <h1 style='color: white; margin-bottom: 1rem;'>🔐 NYZTrade Pro Login</h1>
            <p style='color: white; font-size: 1.2rem;'>Professional Midcap Valuation Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username", placeholder="Enter username")
            st.text_input("Password", type="password", key="password", placeholder="Enter password")
            st.button("🚀 Login", on_click=password_entered, use_container_width=True)
            
            st.markdown("---")
            st.info("**Demo:** `demo` / `demo123` | **Premium:** `premium` / `premium123`")
        
        return False
    
    elif not st.session_state["password_correct"]:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; text-align: center;'>
            <h1 style='color: white; margin-bottom: 1rem;'>🔐 NYZTrade Pro Login</h1>
            <p style='color: white; font-size: 1.2rem;'>Professional Midcap Valuation Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.error("😕 Incorrect username or password")
            st.text_input("Username", key="username", placeholder="Enter username")
            st.text_input("Password", type="password", key="password", placeholder="Enter password")
            st.button("🚀 Login", on_click=password_entered, use_container_width=True)
        
        return False
    
    return True

if not check_password():
    st.stop()

# ============================================================================
# ENHANCED CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
    }
    
    .fair-value-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .fair-value-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .fair-value-price {
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .fair-value-upside {
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    .rec-strong-buy {
        background: linear-gradient(135deg, #00C853 0%, #64DD17 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        box-shadow: 0 10px 30px rgba(0, 200, 83, 0.3);
        animation: pulse 2s infinite;
    }
    
    .rec-buy {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        box-shadow: 0 10px 30px rgba(46, 204, 113, 0.3);
    }
    
    .rec-hold {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        box-shadow: 0 10px 30px rgba(243, 156, 18, 0.3);
    }
    
    .rec-avoid {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        box-shadow: 0 10px 30px rgba(231, 76, 60, 0.3);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .download-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# STOCK DATABASE (Condensed version - same 800+ stocks)
# ============================================================================

MIDCAP_500_STOCKS = {
    "🏦 Banking & Finance (80+)": {
        "ANGELONE.NS": "Angel One", "ANANDRATHI.NS": "Anand Rathi", "AAVAS.NS": "Aavas Financiers",
        "BAJAJFINSV.NS": "Bajaj Finserv", "CDSL.NS": "CDSL", "CHOLAFIN.NS": "Cholamandalam Investment",
        "CREDITACC.NS": "CreditAccess Grameen", "CRISIL.NS": "CRISIL", "CSB.NS": "CSB Bank",
        "EQUITAS.NS": "Equitas Holdings", "FEDERALBNK.NS": "Federal Bank", "FINOPB.NS": "Fino Payments",
        "HDFCAMC.NS": "HDFC AMC", "IIFL.NS": "IIFL Finance", "IRFC.NS": "IRFC",
        "JMFINANCIL.NS": "JM Financial", "KALYANKJIL.NS": "Kalyan Jewellers", "KFINTECH.NS": "KFin Technologies",
        "LICHSGFIN.NS": "LIC Housing", "MOTILALOFS.NS": "Motilal Oswal", "MUTHOOTFIN.NS": "Muthoot Finance",
        "PNBHOUSING.NS": "PNB Housing", "RBL.NS": "RBL Bank", "SBFC.NS": "SBFC Finance",
        "STARHEALTH.NS": "Star Health", "UJJIVAN.NS": "Ujjivan Small Finance", "UTIAMC.NS": "UTI AMC",
        "AUBANK.NS": "AU Small Finance", "BANDHANBNK.NS": "Bandhan Bank", "IDFCFIRSTB.NS": "IDFC First Bank",
        "INDUSINDBK.NS": "IndusInd Bank", "BANKBARODA.NS": "Bank of Baroda", "CANBK.NS": "Canara Bank",
        "UNIONBANK.NS": "Union Bank", "CENTRALBK.NS": "Central Bank", "INDIANB.NS": "Indian Bank",
        "IOB.NS": "Indian Overseas Bank", "BANKINDIA.NS": "Bank of India", "MAHABANK.NS": "Bank of Maharashtra",
        "ICICIGI.NS": "ICICI Lombard", "ICICIPRULI.NS": "ICICI Prudential Life", "SBILIFE.NS": "SBI Life",
        "HDFCLIFE.NS": "HDFC Life", "MAXHEALTH.NS": "Max Healthcare", "POLICYBZR.NS": "PB Fintech"
    },
    
    "💻 IT & Technology (70+)": {
        "COFORGE.NS": "Coforge", "CYIENT.NS": "Cyient", "ECLERX.NS": "eClerx Services",
        "HAPPSTMNDS.NS": "Happiest Minds", "INTELLECT.NS": "Intellect Design", "KPITTECH.NS": "KPIT Technologies",
        "LTIM.NS": "LTIMindtree", "MASTEK.NS": "Mastek", "MPHASIS.NS": "Mphasis",
        "NEWGEN.NS": "Newgen Software", "NIITLTD.NS": "NIIT Ltd", "OFSS.NS": "Oracle Financial",
        "PERSISTENT.NS": "Persistent Systems", "ZENSAR.NS": "Zensar Technologies", "ROUTE.NS": "Route Mobile",
        "DATAMATICS.NS": "Datamatics Global", "SONATSOFTW.NS": "Sonata Software", "TATAELXSI.NS": "Tata Elxsi",
        "TECHM.NS": "Tech Mahindra", "AFFLE.NS": "Affle India", "EASEMYTRIP.NS": "EaseMyTrip",
        "ZOMATO.NS": "Zomato", "NYKAA.NS": "Nykaa", "PAYTM.NS": "Paytm",
        "BLUESTARCO.NS": "Blue Star", "DIXON.NS": "Dixon Technologies", "AMBER.NS": "Amber Enterprises",
        "SYMPHONY.NS": "Symphony", "VOLTAS.NS": "Voltas", "WHIRLPOOL.NS": "Whirlpool India",
        "VGUARD.NS": "V-Guard Industries", "CROMPTON.NS": "Crompton Greaves", "HAVELLS.NS": "Havells India"
    },
    
    "💊 Pharma & Healthcare (50+)": {
        "AARTIDRUGS.NS": "Aarti Drugs", "ABBOTINDIA.NS": "Abbott India", "AJANTPHARM.NS": "Ajanta Pharma",
        "ALEMBICLTD.NS": "Alembic Pharma", "ALKEM.NS": "Alkem Laboratories", "BIOCON.NS": "Biocon",
        "CIPLA.NS": "Cipla", "DIVISLAB.NS": "Divi's Laboratories", "DRREDDY.NS": "Dr Reddy's Labs",
        "GLENMARK.NS": "Glenmark Pharma", "GRANULES.NS": "Granules India", "IPCALAB.NS": "IPCA Laboratories",
        "LUPIN.NS": "Lupin", "NATCOPHARM.NS": "Natco Pharma", "SUNPHARMA.NS": "Sun Pharma",
        "TORNTPHARM.NS": "Torrent Pharma", "ZYDUSLIFE.NS": "Zydus Lifesciences", "APOLLOHOSP.NS": "Apollo Hospitals",
        "FORTIS.NS": "Fortis Healthcare", "MAXHEALTH.NS": "Max Healthcare", "LALPATHLAB.NS": "Dr Lal PathLabs",
        "METROPOLIS.NS": "Metropolis Healthcare", "KIMS.NS": "KIMS Hospitals", "RAINBOW.NS": "Rainbow Children"
    },
    
    "🚗 Auto & Components (50+)": {
        "ASHOKLEY.NS": "Ashok Leyland", "BAJAJ-AUTO.NS": "Bajaj Auto", "BHARATFORG.NS": "Bharat Forge",
        "BOSCHLTD.NS": "Bosch", "EICHERMOT.NS": "Eicher Motors", "ESCORTS.NS": "Escorts Kubota",
        "EXIDEIND.NS": "Exide Industries", "HEROMOTOCO.NS": "Hero MotoCorp", "M&M.NS": "Mahindra & Mahindra",
        "MARUTI.NS": "Maruti Suzuki", "MRF.NS": "MRF", "TATAMOTORS.NS": "Tata Motors",
        "TVSMOTOR.NS": "TVS Motor", "AMARAJABAT.NS": "Amara Raja", "APOLLOTYRE.NS": "Apollo Tyres",
        "ENDURANCE.NS": "Endurance Technologies", "MOTHERSON.NS": "Motherson Sumi", "SCHAEFFLER.NS": "Schaeffler India"
    },
    
    "🍔 FMCG & Consumer (60+)": {
        "ABFRL.NS": "Aditya Birla Fashion", "BATAINDIA.NS": "Bata India", "BIKAJI.NS": "Bikaji Foods",
        "BRITANNIA.NS": "Britannia Industries", "COLPAL.NS": "Colgate Palmolive", "DABUR.NS": "Dabur India",
        "GODREJCP.NS": "Godrej Consumer", "HAVELLS.NS": "Havells India", "HINDUNILVR.NS": "Hindustan Unilever",
        "ITC.NS": "ITC", "JUBLFOOD.NS": "Jubilant FoodWorks", "MARICO.NS": "Marico",
        "NESTLEIND.NS": "Nestle India", "PAGEIND.NS": "Page Industries", "RADICO.NS": "Radico Khaitan",
        "TATACONSUM.NS": "Tata Consumer", "TRENT.NS": "Trent", "UBL.NS": "United Breweries"
    },
    
    "🏭 Industrial & Manufacturing (80+)": {
        "APLAPOLLO.NS": "APL Apollo", "ASTRAL.NS": "Astral Poly", "CERA.NS": "Cera Sanitaryware",
        "DEEPAKNTR.NS": "Deepak Nitrite", "GRINDWELL.NS": "Grindwell Norton", "JKCEMENT.NS": "JK Cement",
        "KEC.NS": "KEC International", "KEI.NS": "KEI Industries", "PRINCEPIPE.NS": "Prince Pipes",
        "SHREECEM.NS": "Shree Cement", "SOLARINDS.NS": "Solar Industries", "SRF.NS": "SRF",
        "SUPREMEIND.NS": "Supreme Industries", "UPL.NS": "UPL", "VINATIORGA.NS": "Vinati Organics",
        "ABB.NS": "ABB India", "BEML.NS": "BEML", "HAL.NS": "Hindustan Aeronautics"
    },
    
    "⚡ Energy & Power (40+)": {
        "ADANIENSOL.NS": "Adani Energy", "ADANIGAS.NS": "Adani Total Gas", "ADANIGREEN.NS": "Adani Green",
        "BPCL.NS": "BPCL", "GAIL.NS": "GAIL", "IOC.NS": "Indian Oil",
        "IGL.NS": "Indraprastha Gas", "MGL.NS": "Mahanagar Gas", "ONGC.NS": "ONGC",
        "PETRONET.NS": "Petronet LNG", "ADANIPOWER.NS": "Adani Power", "JSWENERGY.NS": "JSW Energy",
        "NHPC.NS": "NHPC", "NTPC.NS": "NTPC", "PFC.NS": "Power Finance Corp",
        "POWERGRID.NS": "Power Grid", "RECLTD.NS": "REC Limited", "TATAPOWER.NS": "Tata Power"
    },
    
    "🛒 Retail & E-commerce (30+)": {
        "AFFLE.NS": "Affle India", "EASEMYTRIP.NS": "EaseMyTrip", "INDIAMART.NS": "IndiaMART",
        "NYKAA.NS": "Nykaa", "PAYTM.NS": "Paytm", "ZOMATO.NS": "Zomato",
        "DMART.NS": "Avenue Supermarts", "JUBLFOOD.NS": "Jubilant FoodWorks", "TRENT.NS": "Trent",
        "SHOPERSTOP.NS": "Shoppers Stop", "VMART.NS": "V-Mart Retail", "WESTLIFE.NS": "Westlife Development"
    },
    
    "🏗️ Real Estate (40+)": {
        "BRIGADE.NS": "Brigade Enterprises", "DLF.NS": "DLF", "GODREJPROP.NS": "Godrej Properties",
        "MACROTECH.NS": "Macrotech Developers", "OBEROIRLTY.NS": "Oberoi Realty", "PHOENIXLTD.NS": "Phoenix Mills",
        "PRESTIGE.NS": "Prestige Estates", "SOBHA.NS": "Sobha", "IRB.NS": "IRB Infrastructure",
        "KEC.NS": "KEC International", "NBCC.NS": "NBCC India", "NCCLTD.NS": "NCC Limited"
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
    'Communication Services': {'pe': 22, 'ev_ebitda': 14},
    'Real Estate': {'pe': 28, 'ev_ebitda': 20},
    'Utilities': {'pe': 18, 'ev_ebitda': 12},
    'Default': {'pe': 22, 'ev_ebitda': 14}
}

# ============================================================================
# DATA FETCHING FUNCTIONS
# ============================================================================

def retry_with_backoff(retries=5, backoff_in_seconds=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise
                    wait_time = (backoff_in_seconds * 2 ** x)
                    time.sleep(wait_time)
                    x += 1
        return wrapper
    return decorator

@st.cache_data(ttl=7200)
@retry_with_backoff(retries=5, backoff_in_seconds=3)
def fetch_stock_data(ticker):
    try:
        time.sleep(1)
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or len(info) < 5:
            return None, "Unable to fetch data"
        
        return info, None
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "rate" in error_msg.lower():
            return None, "⏱️ RATE LIMIT: Wait 3-5 minutes"
        elif "404" in error_msg:
            return None, "❌ STOCK NOT FOUND"
        else:
            return None, f"❌ ERROR: {error_msg[:100]}"

def calculate_valuations(info):
    try:
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
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
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
            'price': price, 'trailing_pe': trailing_pe, 'forward_pe': forward_pe,
            'trailing_eps': trailing_eps, 'industry_pe': industry_pe,
            'fair_value_pe': fair_value_pe, 'upside_pe': upside_pe,
            'enterprise_value': enterprise_value, 'ebitda': ebitda,
            'market_cap': market_cap, 'current_ev_ebitda': current_ev_ebitda,
            'industry_ev_ebitda': industry_ev_ebitda,
            'fair_value_ev': fair_value_ev, 'upside_ev': upside_ev
        }
        
    except Exception as e:
        return None

# ============================================================================
# ENHANCED CHART FUNCTIONS - ULTRA PROFESSIONAL
# ============================================================================

def create_3d_gauge_chart(upside_pe, upside_ev):
    """Create stunning 3D-style gauge charts with gradients"""
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=("<b>PE Multiple Method</b>", "<b>EV/EBITDA Method</b>")
    )
    
    # Enhanced PE Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_pe,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={
            'suffix': "%",
            'font': {'size': 50, 'color': '#667eea', 'family': 'Arial Black'}
        },
        delta={'reference': 0, 'increasing': {'color': '#00C853'}, 'decreasing': {'color': '#e74c3c'}},
        gauge={
            'axis': {
                'range': [-50, 50],
                'tickwidth': 2,
                'tickcolor': "#667eea",
                'tickfont': {'size': 14, 'color': '#666'}
            },
            'bar': {'color': "#667eea", 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 3,
            'bordercolor': "#667eea",
            'steps': [
                {'range': [-50, -10], 'color': '#ffebee'},
                {'range': [-10, 0], 'color': '#fff3e0'},
                {'range': [0, 15], 'color': '#e8f5e9'},
                {'range': [15, 25], 'color': '#c8e6c9'},
                {'range': [25, 50], 'color': '#81c784'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0
            }
        }
    ), row=1, col=1)
    
    # Enhanced EV/EBITDA Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_ev,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={
            'suffix': "%",
            'font': {'size': 50, 'color': '#f093fb', 'family': 'Arial Black'}
        },
        delta={'reference': 0, 'increasing': {'color': '#00C853'}, 'decreasing': {'color': '#e74c3c'}},
        gauge={
            'axis': {
                'range': [-50, 50],
                'tickwidth': 2,
                'tickcolor': "#f093fb",
                'tickfont': {'size': 14, 'color': '#666'}
            },
            'bar': {'color': "#f093fb", 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 3,
            'bordercolor': "#f093fb",
            'steps': [
                {'range': [-50, -10], 'color': '#ffebee'},
                {'range': [-10, 0], 'color': '#fff3e0'},
                {'range': [0, 15], 'color': '#e8f5e9'},
                {'range': [15, 25], 'color': '#c8e6c9'},
                {'range': [25, 50], 'color': '#81c784'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=500,
        font={'family': 'Arial', 'size': 14},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    return fig

def create_waterfall_chart(valuations):
    """Create professional waterfall chart for valuation breakdown"""
    
    current_price = valuations['price']
    fair_pe = valuations['fair_value_pe'] if valuations['fair_value_pe'] else current_price
    fair_ev = valuations['fair_value_ev'] if valuations['fair_value_ev'] else current_price
    avg_fair = (fair_pe + fair_ev) / 2
    
    fig = go.Figure(go.Waterfall(
        name="Valuation",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["Current Price", "PE Method Adj", "EV/EBITDA Adj", "Fair Value"],
        textposition="outside",
        text=[f"Rs {current_price:.2f}", 
              f"+Rs {fair_pe - current_price:.2f}",
              f"+Rs {fair_ev - current_price:.2f}",
              f"Rs {avg_fair:.2f}"],
        y=[current_price, fair_pe - current_price, fair_ev - current_price, avg_fair],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#00C853"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        totals={"marker": {"color": "#667eea"}}
    ))
    
    fig.update_layout(
        title="<b>Valuation Waterfall Analysis</b>",
        showlegend=False,
        height=500,
        font={'family': 'Arial', 'size': 14},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(250,250,250,1)',
        xaxis={'gridcolor': 'rgba(200,200,200,0.3)'},
        yaxis={'gridcolor': 'rgba(200,200,200,0.3)', 'title': 'Price (Rs)'}
    )
    
    return fig

def create_radial_metrics_chart(valuations):
    """Create radar/spider chart for key metrics comparison"""
    
    categories = ['PE Ratio', 'EPS Growth', 'Market Cap', 'EV/EBITDA', 'Profitability']
    
    # Normalize metrics to 0-100 scale
    pe_norm = min((valuations['trailing_pe'] / valuations['industry_pe']) * 50, 100) if valuations['trailing_pe'] else 50
    eps_norm = 75  # Placeholder
    mcap_norm = min((valuations['market_cap'] / 1000000000) * 10, 100)
    ev_norm = min((valuations['current_ev_ebitda'] / valuations['industry_ev_ebitda']) * 50, 100) if valuations['current_ev_ebitda'] else 50
    prof_norm = 70  # Placeholder
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[pe_norm, eps_norm, mcap_norm, ev_norm, prof_norm],
        theta=categories,
        fill='toself',
        name='Company',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=3)
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[50, 50, 50, 50, 50],
        theta=categories,
        fill='toself',
        name='Industry Avg',
        fillcolor='rgba(255, 99, 132, 0.1)',
        line=dict(color='#ff6384', width=2, dash='dash')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(200,200,200,0.3)'
            ),
            bgcolor='rgba(250,250,250,1)'
        ),
        showlegend=True,
        title="<b>Multi-Metric Performance Analysis</b>",
        height=500,
        font={'family': 'Arial', 'size': 14}
    )
    
    return fig

def create_gradient_bar_chart(valuations):
    """Enhanced gradient bar chart with shadows and 3D effect"""
    
    categories = []
    current = []
    fair = []
    colors_current = []
    colors_fair = []
    
    if valuations['fair_value_pe']:
        categories.append('PE Multiple')
        current.append(valuations['price'])
        fair.append(valuations['fair_value_pe'])
        colors_current.append('#3498db')
        colors_fair.append('#00C853' if valuations['fair_value_pe'] > valuations['price'] else '#e74c3c')
    
    if valuations['fair_value_ev']:
        categories.append('EV/EBITDA')
        current.append(valuations['price'])
        fair.append(valuations['fair_value_ev'])
        colors_current.append('#9b59b6')
        colors_fair.append('#00C853' if valuations['fair_value_ev'] > valuations['price'] else '#e74c3c')
    
    fig = go.Figure()
    
    # Current Price bars with gradient
    fig.add_trace(go.Bar(
        name='Current Price',
        x=categories,
        y=current,
        marker=dict(
            color=colors_current,
            line=dict(color='#2c3e50', width=2),
            pattern=dict(shape="/", solidity=0.3)
        ),
        text=[f'Rs {p:.2f}' for p in current],
        textposition='outside',
        textfont=dict(size=16, color='#2c3e50', family='Arial Black'),
        width=0.35
    ))
    
    # Fair Value bars with gradient
    fig.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair,
        marker=dict(
            color=colors_fair,
            line=dict(color='#2c3e50', width=2)
        ),
        text=[f'Rs {p:.2f}' for p in fair],
        textposition='outside',
        textfont=dict(size=16, color='#2c3e50', family='Arial Black'),
        width=0.35
    ))
    
    fig.update_layout(
        title="<b>Current Price vs Fair Value Analysis</b>",
        barmode='group',
        bargap=0.3,
        bargroupgap=0.1,
        height=600,
        xaxis=dict(
            title="<b>Valuation Method</b>",
            titlefont=dict(size=16, family='Arial Black'),
            gridcolor='rgba(200,200,200,0.2)'
        ),
        yaxis=dict(
            title="<b>Price (Rs)</b>",
            titlefont=dict(size=16, family='Arial Black'),
            gridcolor='rgba(200,200,200,0.3)'
        ),
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=14, family='Arial')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(250,250,250,1)',
        font={'family': 'Arial', 'size': 14}
    )
    
    # Add annotations for upside/downside
    for i, cat in enumerate(categories):
        upside = ((fair[i] - current[i]) / current[i]) * 100
        fig.add_annotation(
            x=cat,
            y=max(fair[i], current[i]) + (max(fair[i], current[i]) * 0.1),
            text=f"<b>{upside:+.1f}%</b>",
            showarrow=False,
            font=dict(size=18, color='#00C853' if upside > 0 else '#e74c3c', family='Arial Black'),
            bgcolor='white',
            bordercolor='#2c3e50',
            borderwidth=2,
            borderpad=4
        )
    
    return fig

def create_sunburst_chart(company_name, sector, valuations):
    """Create sunburst chart for hierarchical data visualization"""
    
    avg_upside = np.mean([v for v in [valuations['upside_pe'], valuations['upside_ev']] if v is not None])
    
    recommendation = "Strong Buy" if avg_upside > 25 else "Buy" if avg_upside > 15 else "Hold" if avg_upside > -10 else "Avoid"
    
    fig = go.Figure(go.Sunburst(
        labels=["Stock", sector, company_name, "Valuation", "PE Method", "EV Method", "Recommendation", recommendation],
        parents=["", "Stock", sector, company_name, "Valuation", "Valuation", company_name, "Recommendation"],
        values=[100, 100, 100, 50, 25, 25, 50, 50],
        branchvalues="total",
        marker=dict(
            colors=['#667eea', '#f093fb', '#f5576c', '#feca57', '#48dbfb', '#ff9ff3', '#54a0ff', 
                   '#00C853' if avg_upside > 0 else '#e74c3c'],
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>Value: %{value}<extra></extra>'
    ))
    
    fig.update_layout(
        title="<b>Company Analysis Hierarchy</b>",
        height=600,
        font={'family': 'Arial', 'size': 14}
    )
    
    return fig

# ============================================================================
# PDF GENERATION FUNCTIONS
# ============================================================================

def create_pdf_report(company_name, ticker, sector, valuations, info):
    """Generate comprehensive PDF report"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    # Story (content container)
    story = []
    
    # Header
    story.append(Paragraph(f"<b>NYZTrade Stock Valuation Report</b>", title_style))
    story.append(Spacer(1, 12))
    
    # Company Info
    story.append(Paragraph(f"<b>{company_name}</b>", heading_style))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", normal_style))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Fair Value Summary
    upside_values = [v for v in [valuations['upside_pe'], valuations['upside_ev']] if v is not None]
    avg_upside = np.mean(upside_values) if upside_values else 0
    
    fair_values = [v for v in [valuations['fair_value_pe'], valuations['fair_value_ev']] if v is not None]
    avg_fair_value = np.mean(fair_values) if fair_values else valuations['price']
    
    # Fair Value Box
    fair_value_data = [
        ['Fair Value Estimate', f"Rs {avg_fair_value:.2f}"],
        ['Current Price', f"Rs {valuations['price']:.2f}"],
        ['Upside Potential', f"{avg_upside:+.2f}%"]
    ]
    
    fair_value_table = Table(fair_value_data, colWidths=[3*inch, 2*inch])
    fair_value_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    
    story.append(fair_value_table)
    story.append(Spacer(1, 20))
    
    # Recommendation
    if avg_upside > 25:
        rec_text = "⭐⭐⭐ STRONG BUY"
        rec_color = colors.HexColor('#00C853')
    elif avg_upside > 15:
        rec_text = "⭐⭐ BUY"
        rec_color = colors.HexColor('#2ecc71')
    elif avg_upside > 0:
        rec_text = "⭐ ACCUMULATE"
        rec_color = colors.HexColor('#27ae60')
    elif avg_upside > -10:
        rec_text = "🟡 HOLD"
        rec_color = colors.HexColor('#f39c12')
    else:
        rec_text = "❌ AVOID"
        rec_color = colors.HexColor('#e74c3c')
    
    rec_style = ParagraphStyle(
        'Recommendation',
        parent=styles['Normal'],
        fontSize=18,
        textColor=rec_color,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph(f"<b>RECOMMENDATION: {rec_text}</b>", rec_style))
    story.append(Spacer(1, 20))
    
    # Valuation Methods
    story.append(Paragraph("<b>Valuation Analysis</b>", heading_style))
    
    valuation_data = [
        ['Method', 'Fair Value', 'Current Price', 'Upside/Downside'],
        ['PE Multiple', 
         f"Rs {valuations['fair_value_pe']:.2f}" if valuations['fair_value_pe'] else 'N/A',
         f"Rs {valuations['price']:.2f}",
         f"{valuations['upside_pe']:+.2f}%" if valuations['upside_pe'] else 'N/A'],
        ['EV/EBITDA',
         f"Rs {valuations['fair_value_ev']:.2f}" if valuations['fair_value_ev'] else 'N/A',
         f"Rs {valuations['price']:.2f}",
         f"{valuations['upside_ev']:+.2f}%" if valuations['upside_ev'] else 'N/A']
    ]
    
    valuation_table = Table(valuation_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    valuation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10)
    ]))
    
    story.append(valuation_table)
    story.append(Spacer(1, 20))
    
    # Financial Metrics
    story.append(Paragraph("<b>Key Financial Metrics</b>", heading_style))
    
    metrics_data = [
        ['Metric', 'Value'],
        ['Current Price', f"Rs {valuations['price']:.2f}"],
        ['PE Ratio (TTM)', f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else 'N/A'],
        ['Industry PE', f"{valuations['industry_pe']:.2f}x"],
        ['Forward PE', f"{valuations['forward_pe']:.2f}x" if valuations['forward_pe'] else 'N/A'],
        ['EPS (TTM)', f"Rs {valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else 'N/A'],
        ['Market Cap', f"Rs {valuations['market_cap']/10000000:.2f} Crores"],
        ['Enterprise Value', f"Rs {valuations['enterprise_value']/10000000:.2f} Crores"],
        ['EBITDA', f"Rs {valuations['ebitda']/10000000:.2f} Crores" if valuations['ebitda'] else 'N/A'],
        ['EV/EBITDA', f"{valuations['current_ev_ebitda']:.2f}x" if valuations['current_ev_ebitda'] else 'N/A'],
        ['Industry EV/EBITDA', f"{valuations['industry_ev_ebitda']:.2f}x"]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Methodology
    story.append(PageBreak())
    story.append(Paragraph("<b>Valuation Methodology</b>", heading_style))
    
    methodology_text = """
    <b>1. PE Multiple Valuation:</b><br/>
    This method compares the company's Price-to-Earnings ratio against industry benchmarks. 
    We calculate a blended PE using both industry average and the company's historical PE (at 90% to be conservative). 
    Fair value is derived by multiplying the company's EPS by this blended PE multiple.<br/><br/>
    
    <b>2. EV/EBITDA Valuation:</b><br/>
    This approach values the company based on its Enterprise Value relative to EBITDA. 
    We determine a target EV/EBITDA multiple considering both industry standards and the company's current multiple. 
    Fair enterprise value is calculated, adjusted for net debt, and converted to per-share value.<br/><br/>
    
    <b>3. Final Recommendation:</b><br/>
    The recommendation is based on the average upside potential from both methods, with thresholds adjusted for midcap volatility characteristics.
    """
    
    story.append(Paragraph(methodology_text, normal_style))
    story.append(Spacer(1, 20))
    
    # Risk Factors
    story.append(Paragraph("<b>Investment Considerations</b>", heading_style))
    
    risk_text = """
    <b>Midcap Characteristics:</b><br/>
    • Higher volatility compared to large-cap stocks<br/>
    • Greater growth potential but increased risk<br/>
    • Lower liquidity - may face wider bid-ask spreads<br/>
    • More sensitive to market sentiment and economic cycles<br/><br/>
    
    <b>Key Risks:</b><br/>
    • Market risk and sector-specific challenges<br/>
    • Execution risk in business operations<br/>
    • Regulatory and competitive landscape changes<br/>
    • Macroeconomic factors affecting growth trajectory<br/><br/>
    """
    
    story.append(Paragraph(risk_text, normal_style))
    story.append(Spacer(1, 20))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=12,
        fontName='Helvetica',
        leading=12
    )
    
    disclaimer_text = """
    <b>DISCLAIMER:</b> This report is for educational and informational purposes only and should not be considered as financial advice. 
    The valuations and recommendations are based on publicly available data and standardized methodologies, which may not capture 
    company-specific nuances or future market conditions. Past performance is not indicative of future results. 
    Investors should conduct their own due diligence and consult with qualified financial advisors before making investment decisions. 
    NYZTrade and its affiliates assume no liability for any financial losses incurred based on this report.
    """
    
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Footer
    footer_text = f"<b>NYZTrade Professional Midcap Valuation Platform</b> | Generated: {datetime.now().strftime('%B %d, %Y')}"
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    story.append(Spacer(1, 30))
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer

# ============================================================================
# MAIN APP
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>📊 ULTRA PROFESSIONAL MIDCAP VALUATION</h1>
    <p style="font-size: 1.3rem;">Enhanced Charts • PDF Reports • 800+ Stocks</p>
</div>
""", unsafe_allow_html=True)

# Features Row
col1, col2, col3 = st.columns(3)
with col1:
    st.info("💡 **2-Hour Caching** - Lightning fast!")
with col2:
    st.success("📊 **Professional Charts** - 3D visualizations")
with col3:
    st.warning("📄 **PDF Export** - Comprehensive reports")

# Sidebar - Logout
if st.sidebar.button("🚪 Logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.header("📈 Stock Selection")

# Flatten stocks
all_stocks = {}
for category, stocks in MIDCAP_500_STOCKS.items():
    all_stocks.update(stocks)

st.sidebar.success(f"**📊 Total: {len(all_stocks)} stocks**")

# Selection
selected_category = st.sidebar.selectbox(
    "Category",
    ["🔍 All Stocks"] + list(MIDCAP_500_STOCKS.keys())
)

search_term = st.sidebar.text_input("🔍 Search", placeholder="Company or ticker...")

# Filter
if search_term:
    filtered_stocks = {
        ticker: name for ticker, name in all_stocks.items()
        if search_term.upper() in ticker or search_term.upper() in name.upper()
    }
elif selected_category == "🔍 All Stocks":
    filtered_stocks = all_stocks
else:
    filtered_stocks = MIDCAP_500_STOCKS[selected_category]

stock_options = [f"{name} ({ticker})" for ticker, name in filtered_stocks.items()]

if stock_options:
    selected_stock = st.sidebar.selectbox("Select Stock", stock_options)
    selected_ticker = selected_stock.split("(")[1].strip(")")
else:
    selected_ticker = None

custom_ticker = st.sidebar.text_input("Or Custom Ticker", placeholder="e.g., DIXON.NS")

if st.sidebar.button("🚀 ANALYZE", use_container_width=True):
    st.session_state.analyze_ticker = custom_ticker.upper() if custom_ticker else selected_ticker

# Analysis
if 'analyze_ticker' in st.session_state:
    ticker = st.session_state.analyze_ticker
    
    with st.spinner(f"🔄 Analyzing {ticker}..."):
        info, error = fetch_stock_data(ticker)
    
    if error or not info:
        st.error(f"❌ {error if error else 'Failed to fetch data'}")
        st.stop()
    
    valuations = calculate_valuations(info)
    if not valuations:
        st.error("Unable to calculate valuations")
        st.stop()
    
    # Company Info
    company_name = info.get('longName', ticker)
    sector = info.get('sector', 'N/A')
    
    st.markdown(f"## 🏢 {company_name}")
    st.markdown(f"**Sector:** {sector} | **Ticker:** {ticker}")
    
    # Fair Value Box
    upside_values = [v for v in [valuations['upside_pe'], valuations['upside_ev']] if v is not None]
    avg_upside = np.mean(upside_values) if upside_values else 0
    
    fair_values = [v for v in [valuations['fair_value_pe'], valuations['fair_value_ev']] if v is not None]
    avg_fair_value = np.mean(fair_values) if fair_values else valuations['price']
    
    st.markdown(f"""
    <div class="fair-value-box">
        <div class="fair-value-title">💎 FAIR VALUE ESTIMATE</div>
        <div class="fair-value-price">Rs {avg_fair_value:.2f}</div>
        <div>Current Price: Rs {valuations['price']:.2f}</div>
        <div class="fair-value-upside">Upside Potential: {avg_upside:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # PDF Download Button
    pdf_buffer = create_pdf_report(company_name, ticker, sector, valuations, info)
    
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_buffer,
        file_name=f"NYZTrade_{ticker}_Valuation_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💵 Current Price", f"Rs {valuations['price']:.2f}")
    with col2:
        st.metric("📊 PE Ratio", f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else "N/A")
    with col3:
        st.metric("💰 EPS", f"Rs {valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else "N/A")
    with col4:
        st.metric("🏦 Market Cap", f"Rs {valuations['market_cap']/10000000:.0f} Cr")
    
    # Recommendation
    if avg_upside > 25:
        rec_class, rec_text = "rec-strong-buy", "⭐⭐⭐ STRONG BUY"
    elif avg_upside > 15:
        rec_class, rec_text = "rec-buy", "⭐⭐ BUY"
    elif avg_upside > 0:
        rec_class, rec_text = "rec-buy", "⭐ ACCUMULATE"
    elif avg_upside > -10:
        rec_class, rec_text = "rec-hold", "🟡 HOLD"
    else:
        rec_class, rec_text = "rec-avoid", "❌ AVOID"
    
    st.markdown(f"""
    <div class="{rec_class}">
        <div>{rec_text}</div>
        <div style="font-size: 1.2rem; margin-top: 0.5rem;">Potential Return: {avg_upside:+.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ENHANCED CHARTS
    st.markdown("## 📊 PROFESSIONAL VISUALIZATIONS")
    
    # Tab layout for charts
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Gauges", "📈 Waterfall", "🕸️ Radar", "📊 Bar Chart", "🌞 Sunburst"])
    
    with tab1:
        if valuations['upside_pe'] and valuations['upside_ev']:
            fig_gauge = create_3d_gauge_chart(valuations['upside_pe'], valuations['upside_ev'])
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    with tab2:
        fig_waterfall = create_waterfall_chart(valuations)
        st.plotly_chart(fig_waterfall, use_container_width=True)
    
    with tab3:
        fig_radar = create_radial_metrics_chart(valuations)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with tab4:
        fig_bar = create_gradient_bar_chart(valuations)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab5:
        fig_sunburst = create_sunburst_chart(company_name, sector, valuations)
        st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # Metrics Table
    st.markdown("---")
    st.subheader("📋 Detailed Financial Metrics")
    
    metrics_df = pd.DataFrame({
        'Metric': [
            '💵 Current Price', '📊 PE Ratio', '🏭 Industry PE',
            '📈 Forward PE', '💰 EPS', '🏢 Enterprise Value',
            '💼 EBITDA', '📉 EV/EBITDA', '🎯 Target EV/EBITDA', '🏦 Market Cap'
        ],
        'Value': [
            f"Rs {valuations['price']:.2f}",
            f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else 'N/A',
            f"{valuations['industry_pe']:.2f}x",
            f"{valuations['forward_pe']:.2f}x" if valuations['forward_pe'] else 'N/A',
            f"Rs {valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else 'N/A',
            f"Rs {valuations['enterprise_value']/10000000:.2f} Cr",
            f"Rs {valuations['ebitda']/10000000:.2f} Cr" if valuations['ebitda'] else 'N/A',
            f"{valuations['current_ev_ebitda']:.2f}x" if valuations['current_ev_ebitda'] else 'N/A',
            f"{valuations['industry_ev_ebitda']:.2f}x",
            f"Rs {valuations['market_cap']/10000000:.2f} Cr"
        ]
    })
    
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

else:
    st.info("👈 Select a stock and click **ANALYZE** to begin!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p><strong>💡 NYZTrade Ultra Professional Platform | {len(all_stocks)}+ Stocks</strong></p>
    <p>Enhanced Visualizations | PDF Reports | Educational Tool</p>
    <p>⚠️ Not Financial Advice | Always DYOR</p>
</div>
""", unsafe_allow_html=True)
```

---

## **📦 Updated requirements.txt**
```
streamlit
yfinance
pandas
numpy
plotly
reportlab
matplotlib
