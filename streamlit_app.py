import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
from functools import wraps
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

st.set_page_config(
    page_title="NYZTrade Pro Valuation", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PROFESSIONAL CSS STYLING
# ============================================================================
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Styles */
.stApp {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main Header */
.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2.5rem 3rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(160, 32, 240, 0.1) 50%, transparent 60%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 0.8; }
}

.main-header h1 {
    font-size: 2.8rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(90deg, #00d4ff, #7c3aed, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
    z-index: 1;
}

.main-header p {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-top: 0.5rem;
    position: relative;
    z-index: 1;
}

/* Company Header Card */
.company-header {
    background: linear-gradient(135deg, #ffffff 100%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.company-name {
    font-size: 1.8rem;
    font-weight: 700;
    color: #7e1cc9;
    margin: 0;
}

.company-meta {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}

.meta-badge {
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    color: #475569;
    font-weight: 500;
}

/* Fair Value Box */
.fair-value-card {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #c084fc 100%);
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin: 1.5rem 0;
    box-shadow: 0 20px 40px rgba(124, 58, 237, 0.3);
    position: relative;
    overflow: hidden;
}

.fair-value-card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
    border-radius: 50%;
    transform: translate(30%, -30%);
}

.fair-value-label {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    opacity: 0.9;
    margin-bottom: 0.5rem;
}

.fair-value-amount {
    font-size: 3rem;
    font-weight: 700;
    margin: 0.5rem 0;
    font-family: 'JetBrains Mono', monospace;
}

.current-price {
    font-size: 1rem;
    opacity: 0.85;
}

.upside-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 0.5rem 1.5rem;
    border-radius: 30px;
    margin-top: 1rem;
    font-weight: 600;
    font-size: 1.2rem;
    backdrop-filter: blur(10px);
}

/* Recommendation Boxes */
.rec-container {
    margin: 1.5rem 0;
}

.rec-strong-buy {
    background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(16, 185, 129, 0.35);
    position: relative;
    overflow: hidden;
}

.rec-buy {
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 50%, #2dd4bf 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(20, 184, 166, 0.35);
}

.rec-hold {
    background: linear-gradient(135deg, #d97706 0%, #f59e0b 50%, #fbbf24 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(245, 158, 11, 0.35);
}

.rec-avoid {
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f87171 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(239, 68, 68, 0.35);
}

.rec-subtitle {
    font-size: 1rem;
    font-weight: 500;
    opacity: 0.9;
    margin-top: 0.3rem;
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.12);
}

.metric-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1e293b;
    font-family: 'JetBrains Mono', monospace;
}

.metric-label {
    font-size: 0.85rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.3rem;
}

/* Section Headers */
.section-header {
    font-size: 1.4rem;
    font-weight: 600;
    color: #1e293b;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #7c3aed;
    display: inline-block;
}

/* Data Table Styling */
.styled-table {
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* Stock Count Badge */
.stock-count {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    color: white;
    padding: 0.8rem 1.2rem;
    border-radius: 12px;
    text-align: center;
    margin: 1rem 0;
    font-weight: 600;
}

/* Download Button */
.download-btn {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.download-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

/* Valuation Method Cards */
.valuation-method {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #7c3aed;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.method-title {
    font-weight: 600;
    color: #1e293b;
    font-size: 1.1rem;
    margin-bottom: 1rem;
}

.method-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f1f5f9;
}

.method-label {
    color: #64748b;
}

.method-value {
    font-weight: 600;
    color: #1e293b;
    font-family: 'JetBrains Mono', monospace;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem;
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 3rem;
    border-top: 1px solid #e2e8f0;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
    animation: fadeIn 0.6s ease forwards;
}

/* Info Box */
.info-box {
    background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
    border: 1px solid #93c5fd;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #1e40af;
    margin: 1rem 0;
}

/* Warning Box */
.warning-box {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border: 1px solid #fbbf24;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #92400e;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PASSWORD AUTHENTICATION
# ============================================================================
def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        users = {"demo": "demo123", "premium": "premium123", "niyas": "nyztrade123"}
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
                    padding: 4rem; border-radius: 24px; text-align: center; margin: 2rem auto; max-width: 500px;
                    box-shadow: 0 25px 50px rgba(0,0,0,0.3);'>
            <h1 style='color: white; font-size: 2.5rem; margin-bottom: 0.5rem;'>
                <span style='background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                    NYZTrade Pro
                </span>
            </h1>
            <p style='color: rgba(255,255,255,0.7); margin-bottom: 2rem;'>Professional Stock Valuation Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("👤 Username", key="username", placeholder="Enter username")
            st.text_input("🔒 Password", type="password", key="password", placeholder="Enter password")
            st.button("🚀 Login", on_click=password_entered, use_container_width=True, type="primary")
            st.info("💡 Demo: demo/demo123")
        return False
    elif not st.session_state["password_correct"]:
        st.error("❌ Incorrect credentials. Please try again.")
        return False
    return True

if not check_password():
    st.stop()

# ============================================================================
# COMPREHENSIVE INDIAN STOCKS DATABASE
# Combined: NIFTY 500 + MIDCAP + SMALLCAP
# Total Categories: 50+ sector-wise classifications
# ============================================================================

INDIAN_STOCKS = {
    # ========================================================================
    # NIFTY 50 - LARGE CAP BLUE CHIPS
    # ========================================================================
    "💎 NIFTY 50": {
        "ADANIENT.NS": "Adani Enterprises", "ADANIPORTS.NS": "Adani Ports", "APOLLOHOSP.NS": "Apollo Hospitals",
        "ASIANPAINT.NS": "Asian Paints", "AXISBANK.NS": "Axis Bank", "BAJAJ-AUTO.NS": "Bajaj Auto",
        "BAJFINANCE.NS": "Bajaj Finance", "BAJAJFINSV.NS": "Bajaj Finserv", "BHARTIARTL.NS": "Bharti Airtel",
        "BPCL.NS": "BPCL", "BRITANNIA.NS": "Britannia", "CIPLA.NS": "Cipla",
        "COALINDIA.NS": "Coal India", "DIVISLAB.NS": "Divi's Labs", "DRREDDY.NS": "Dr Reddy's",
        "EICHERMOT.NS": "Eicher Motors", "GRASIM.NS": "Grasim", "HCLTECH.NS": "HCL Tech",
        "HDFCBANK.NS": "HDFC Bank", "HDFCLIFE.NS": "HDFC Life", "HEROMOTOCO.NS": "Hero MotoCorp",
        "HINDALCO.NS": "Hindalco", "HINDUNILVR.NS": "Hindustan Unilever", "ICICIBANK.NS": "ICICI Bank",
        "INDUSINDBK.NS": "IndusInd Bank", "INFY.NS": "Infosys", "ITC.NS": "ITC",
        "JSWSTEEL.NS": "JSW Steel", "KOTAKBANK.NS": "Kotak Bank", "LT.NS": "L&T",
        "M&M.NS": "M&M", "MARUTI.NS": "Maruti Suzuki", "NESTLEIND.NS": "Nestle India",
        "NTPC.NS": "NTPC", "ONGC.NS": "ONGC", "POWERGRID.NS": "Power Grid",
        "RELIANCE.NS": "Reliance", "SBILIFE.NS": "SBI Life", "SBIN.NS": "SBI",
        "SUNPHARMA.NS": "Sun Pharma", "TATAMOTORS.NS": "Tata Motors", "TATASTEEL.NS": "Tata Steel",
        "TCS.NS": "TCS", "TECHM.NS": "Tech Mahindra", "TITAN.NS": "Titan",
        "ULTRACEMCO.NS": "UltraTech Cement", "UPL.NS": "UPL", "WIPRO.NS": "Wipro"
    },

    # ========================================================================
    # BANKING & FINANCE
    # ========================================================================
    "🏦 Banking Finance - Large Cap": {
        "AUBANK.NS": "AU Small Finance", "BANDHANBNK.NS": "Bandhan Bank", "BANKBARODA.NS": "Bank of Baroda",
        "CANBK.NS": "Canara Bank", "CHOLAFIN.NS": "Cholamandalam", "FEDERALBNK.NS": "Federal Bank",
        "HDFCAMC.NS": "HDFC AMC", "ICICIGI.NS": "ICICI Lombard", "ICICIPRULI.NS": "ICICI Prudential",
        "IDFCFIRSTB.NS": "IDFC First Bank", "MUTHOOTFIN.NS": "Muthoot Finance", "PFC.NS": "Power Finance",
        "PNB.NS": "Punjab National Bank", "RECLTD.NS": "REC Limited", "SBICARD.NS": "SBI Card",
        "SHRIRAMFIN.NS": "Shriram Finance", "UNIONBANK.NS": "Union Bank"
    },
    
    "🏦 Banking Finance - Midcap 1": {
        "ANGELONE.NS": "Angel One", "ANANDRATHI.NS": "Anand Rathi", "AAVAS.NS": "Aavas Financiers",
        "CDSL.NS": "CDSL", "CREDITACC.NS": "CreditAccess Grameen", "CRISIL.NS": "CRISIL",
        "CSB.NS": "CSB Bank", "EQUITAS.NS": "Equitas Holdings", "FINOPB.NS": "Fino Payments",
        "IIFL.NS": "IIFL Finance", "IIFLSEC.NS": "IIFL Securities", "IRFC.NS": "IRFC",
        "ISEC.NS": "ICICI Securities", "JMFINANCIL.NS": "JM Financial", "KALYANKJIL.NS": "Kalyan Jewellers",
        "KFINTECH.NS": "KFin Technologies"
    },
    
    "🏦 Banking Finance - Midcap 2": {
        "LICHSGFIN.NS": "LIC Housing", "MASFIN.NS": "MAS Financial", "MOTILALOFS.NS": "Motilal Oswal",
        "PNBHOUSING.NS": "PNB Housing", "RBL.NS": "RBL Bank", "SBFC.NS": "SBFC Finance",
        "STARHEALTH.NS": "Star Health", "UJJIVAN.NS": "Ujjivan Small Finance", "UTIAMC.NS": "UTI AMC",
        "CENTRALBK.NS": "Central Bank", "INDIANB.NS": "Indian Bank", "IOB.NS": "Indian Overseas Bank"
    },
    
    "🏦 Banking Finance - Midcap 3": {
        "BANKINDIA.NS": "Bank of India", "MAHABANK.NS": "Bank of Maharashtra", "J&KBANK.NS": "Jammu Kashmir Bank",
        "KARNATBNK.NS": "Karnataka Bank", "DCBBANK.NS": "DCB Bank", "POLICYBZR.NS": "PB Fintech",
        "NUVOCO.NS": "Nuvoco Vistas", "SPANDANA.NS": "Spandana Sphoorty", "SWANENERGY.NS": "Swan Energy",
        "BAJAJHLDNG.NS": "Bajaj Holdings", "MAHLIFE.NS": "Mahindra Lifespace", "TATAINVEST.NS": "Tata Investment",
        "SUNDARMFIN.NS": "Sundaram Finance", "MANAPPURAM.NS": "Manappuram Finance"
    },
    
    "🏦 Banking Finance - Midcap 4": {
        "PNBGILTS.NS": "PNB Gilts", "APTUS.NS": "Aptus Value Housing", "HOMEFIRST.NS": "Home First Finance",
        "AADHARHFC.NS": "Aadhar Housing", "CAPLIPOINT.NS": "Caplin Point", "CHOLA.NS": "Cholamandalam Financial",
        "CIEINDIA.NS": "CIE Automotive", "JSWHL.NS": "JSW Holdings", "MUTHOOTCAP.NS": "Muthoot Capital",
        "ABSLAMC.NS": "Aditya Birla Sun Life AMC", "L&TFH.NS": "L&T Finance Holdings", "CHOLAHLDNG.NS": "Cholamandalam Holdings",
        "IIFLWAM.NS": "IIFL Wealth", "INDUSIND.NS": "IndusInd Bank"
    },

    # ========================================================================
    # IT & TECHNOLOGY
    # ========================================================================
    "💻 IT Technology - Large Cap": {
        "COFORGE.NS": "Coforge", "LTTS.NS": "L&T Technology", "MPHASIS.NS": "Mphasis",
        "PERSISTENT.NS": "Persistent Systems", "SONATSOFTW.NS": "Sonata Software", "TATAELXSI.NS": "Tata Elxsi"
    },
    
    "💻 IT Technology - Midcap 1": {
        "CYIENT.NS": "Cyient", "ECLERX.NS": "eClerx Services", "HAPPSTMNDS.NS": "Happiest Minds",
        "INTELLECT.NS": "Intellect Design", "KPITTECH.NS": "KPIT Technologies", "LTIM.NS": "LTIMindtree",
        "MASTEK.NS": "Mastek", "NEWGEN.NS": "Newgen Software", "NIITLTD.NS": "NIIT Ltd",
        "OFSS.NS": "Oracle Financial", "ZENSAR.NS": "Zensar Technologies", "ROUTE.NS": "Route Mobile",
        "DATAMATICS.NS": "Datamatics Global", "SASKEN.NS": "Sasken Technologies"
    },
    
    "💻 IT Technology - Midcap 2": {
        "3MINDIA.NS": "3M India", "AFFLE.NS": "Affle India", "EASEMYTRIP.NS": "EaseMyTrip",
        "ZOMATO.NS": "Zomato", "NYKAA.NS": "Nykaa", "PAYTM.NS": "Paytm",
        "BLUESTARCO.NS": "Blue Star", "CAMPUS.NS": "Campus Activewear", "DIXON.NS": "Dixon Technologies",
        "HLEGLAS.NS": "HLE Glascoat", "HONAUT.NS": "Honeywell Automation", "LXCHEM.NS": "Laxmi Organic",
        "RPTECH.NS": "RP Tech India", "AMBER.NS": "Amber Enterprises", "SYMPHONY.NS": "Symphony",
        "VOLTAS.NS": "Voltas", "WHIRLPOOL.NS": "Whirlpool India", "VGUARD.NS": "V-Guard Industries",
        "CROMPTON.NS": "Crompton Greaves"
    },
    
    "💻 IT Technology - Midcap 3": {
        "HAVELLS.NS": "Havells India", "ORIENTELEC.NS": "Orient Electric", "INDIAMART.NS": "IndiaMART",
        "JUSTDIAL.NS": "Just Dial", "MATRIMONY.NS": "Matrimony.com", "NAZARA.NS": "Nazara Technologies",
        "SHOPERSTOP.NS": "Shoppers Stop", "TATACOMM.NS": "Tata Communications", "TATATECH.NS": "Tata Technologies",
        "TEAMLEASE.NS": "TeamLease Services", "CARTRADE.NS": "CarTrade Tech", "LATENTVIEW.NS": "LatentView Analytics",
        "MPSLTD.NS": "MPS Limited", "RAINBOW.NS": "Rainbow Children", "REDINGTON.NS": "Redington",
        "STLTECH.NS": "Sterlite Technologies", "SUBROS.NS": "Subros", "SUPRAJIT.NS": "Suprajit Engineering",
        "TANLA.NS": "Tanla Platforms", "POLYCAB.NS": "Polycab India"
    },
    
    "💻 IT Technology - Midcap 4": {
        "TCNSBRANDS.NS": "TCNS Clothing", "TIMKEN.NS": "Timken India", "TRIVENI.NS": "Triveni Turbine",
        "TTKHLTCARE.NS": "TTK Healthcare", "TTKPRESTIG.NS": "TTK Prestige", "VIPIND.NS": "VIP Industries",
        "VSTIND.NS": "VST Industries", "WELSPUNIND.NS": "Welspun India", "WESTLIFE.NS": "Westlife Development",
        "LTI.NS": "LTI", "MINDTREE.NS": "Mindtree", "HEXAWARE.NS": "Hexaware Technologies",
        "L&TTS.NS": "L&T Technology"
    },

    # ========================================================================
    # PHARMA & HEALTHCARE
    # ========================================================================
    "💊 Pharma Healthcare - Large Cap": {
        "AUROPHARMA.NS": "Aurobindo Pharma", "BIOCON.NS": "Biocon", "ALKEM.NS": "Alkem Labs",
        "FORTIS.NS": "Fortis Healthcare", "GLENMARK.NS": "Glenmark", "IPCALAB.NS": "IPCA Labs",
        "LAURUSLABS.NS": "Laurus Labs", "LUPIN.NS": "Lupin", "MAXHEALTH.NS": "Max Healthcare",
        "TORNTPHARM.NS": "Torrent Pharma"
    },
    
    "💊 Pharma Healthcare - Midcap 1": {
        "AARTIDRUGS.NS": "Aarti Drugs", "ABBOTINDIA.NS": "Abbott India", "AJANTPHARM.NS": "Ajanta Pharma",
        "ALEMBICLTD.NS": "Alembic Pharma", "ASTRAZEN.NS": "AstraZeneca Pharma", "AUROBINDO.NS": "Aurobindo Pharma",
        "CADILAHC.NS": "Cadila Healthcare", "ERIS.NS": "Eris Lifesciences", "FINEORG.NS": "Fine Organic",
        "GLAXO.NS": "GlaxoSmithKline", "GRANULES.NS": "Granules India", "HETERO.NS": "Hetero Drugs"
    },
    
    "💊 Pharma Healthcare - Midcap 2": {
        "JBCHEPHARM.NS": "JB Chemicals", "MANKIND.NS": "Mankind Pharma", "METROPOLIS.NS": "Metropolis Healthcare",
        "NATCOPHARM.NS": "Natco Pharma", "PFIZER.NS": "Pfizer", "SANOFI.NS": "Sanofi India",
        "SOLARA.NS": "Solara Active", "SYNGENE.NS": "Syngene International", "VIMTA.NS": "Vimta Labs",
        "WOCKPHARMA.NS": "Wockhardt", "ZYDUSLIFE.NS": "Zydus Lifesciences", "ZYDUSWELL.NS": "Zydus Wellness",
        "LALPATHLAB.NS": "Dr Lal PathLabs", "THYROCARE.NS": "Thyrocare"
    },
    
    "💊 Pharma Healthcare - Midcap 3": {
        "KRSNAA.NS": "Krsnaa Diagnostics", "KIMS.NS": "KIMS Hospitals", "MEDANTA.NS": "Global Health Medanta",
        "POLYMED.NS": "Poly Medicure", "STAR.NS": "Strides Pharma", "SUVEN.NS": "Suven Pharma",
        "SUVENPHAR.NS": "Suven Pharmaceuticals", "SEQUENT.NS": "Sequent Scientific", "SHILPAMED.NS": "Shilpa Medicare",
        "BLISSGVS.NS": "Bliss GVS Pharma", "INDOCO.NS": "Indoco Remedies", "JUBLPHARMA.NS": "Jubilant Pharma",
        "LAURUS.NS": "Laurus Labs", "MARKSANS.NS": "Marksans Pharma", "NEULANDLAB.NS": "Neuland Laboratories",
        "ALEMBIC.NS": "Alembic Pharmaceuticals", "BERGER.NS": "Berger Paints"
    },

    # ========================================================================
    # AUTO & COMPONENTS
    # ========================================================================
    "🚗 Auto Components - Large Cap": {
        "APOLLOTYRE.NS": "Apollo Tyres", "ASHOKLEY.NS": "Ashok Leyland", "BALKRISIND.NS": "Balkrishna Industries",
        "BHARATFORG.NS": "Bharat Forge", "BOSCHLTD.NS": "Bosch", "CEAT.NS": "CEAT",
        "ESCORTS.NS": "Escorts", "EXIDEIND.NS": "Exide Industries", "MOTHERSUMI.NS": "Motherson Sumi",
        "MRF.NS": "MRF", "TVSMOTOR.NS": "TVS Motor"
    },
    
    "🚗 Auto Components - Midcap 1": {
        "FORCEMOT.NS": "Force Motors", "AMARAJABAT.NS": "Amara Raja", "CRAFTSMAN.NS": "Craftsman Automation",
        "ENDURANCE.NS": "Endurance Technologies", "FINCABLES.NS": "Finolex Cables"
    },
    
    "🚗 Auto Components - Midcap 2": {
        "JKTYRE.NS": "JK Tyre", "MAHINDCIE.NS": "Mahindra CIE", "MOTHERSON.NS": "Motherson Sumi",
        "SANDHAR.NS": "Sandhar Technologies", "SANSERA.NS": "Sansera Engineering", "SCHAEFFLER.NS": "Schaeffler India",
        "SKFINDIA.NS": "SKF India", "SWARAJENG.NS": "Swaraj Engines", "TUBE.NS": "Tube Investments",
        "WHEELS.NS": "Wheels India", "ABB.NS": "ABB India", "AIAENG.NS": "AIA Engineering",
        "ALICON.NS": "Alicon Castalloy", "APOLLOPIPE.NS": "Apollo Pipes", "ASAHIINDIA.NS": "Asahi India Glass",
        "CEATLTD.NS": "CEAT", "CUMMINSIND.NS": "Cummins India", "ELGIRUBCO.NS": "Elgi Rubber"
    },
    
    "🚗 Auto Components - Midcap 3": {
        "GABRIEL.NS": "Gabriel India", "GREAVESCOT.NS": "Greaves Cotton", "JAMNAAUTO.NS": "Jamna Auto",
        "KALYANI.NS": "Kalyani Forge", "MAHSEAMLES.NS": "Maharashtra Seamless", "MAJESAUTO.NS": "Munjal Auto",
        "MFSL.NS": "Max Financial", "MHRIL.NS": "Mahindra Holidays", "RAMCOCEM.NS": "Ramco Cements",
        "RATNAMANI.NS": "Ratnamani Metals", "SHARDACROP.NS": "Sharda Cropchem", "TIINDIA.NS": "Tube Investments"
    },

    # ========================================================================
    # FMCG & CONSUMER
    # ========================================================================
    "🍔 FMCG Consumer - Large Cap": {
        "BATAINDIA.NS": "Bata India", "BERGEPAINT.NS": "Berger Paints", "COLPAL.NS": "Colgate",
        "DABUR.NS": "Dabur", "EMAMILTD.NS": "Emami", "GODREJCP.NS": "Godrej Consumer",
        "JYOTHYLAB.NS": "Jyothy Labs", "MARICO.NS": "Marico", "TATACONSUM.NS": "Tata Consumer",
        "UBL.NS": "United Breweries", "VBL.NS": "Varun Beverages"
    },
    
    "🍔 FMCG Consumer - Midcap 1": {
        "ABFRL.NS": "Aditya Birla Fashion", "AKZOINDIA.NS": "Akzo Nobel", "AVANTIFEED.NS": "Avanti Feeds",
        "BAJAJELEC.NS": "Bajaj Electricals", "BIKAJI.NS": "Bikaji Foods", "CCL.NS": "CCL Products",
        "GILLETTE.NS": "Gillette India", "GODFRYPHLP.NS": "Godfrey Phillips", "GUJALKALI.NS": "Gujarat Alkalies",
        "HBLPOWER.NS": "HBL Power"
    },
    
    "🍔 FMCG Consumer - Midcap 2": {
        "JKLAKSHMI.NS": "JK Lakshmi Cement", "JKPAPER.NS": "JK Paper", "JUBLFOOD.NS": "Jubilant FoodWorks",
        "KAJARIACER.NS": "Kajaria Ceramics", "KPRMILL.NS": "KPR Mill", "MRPL.NS": "MRPL",
        "NAVINFLUOR.NS": "Navin Fluorine", "PAGEIND.NS": "Page Industries", "PCBL.NS": "PCBL",
        "PIIND.NS": "PI Industries", "RADICO.NS": "Radico Khaitan", "RAJESHEXPO.NS": "Rajesh Exports",
        "RELAXO.NS": "Relaxo Footwears", "SOLARINDS.NS": "Solar Industries", "TATACHEM.NS": "Tata Chemicals"
    },
    
    "🍔 FMCG Consumer - Midcap 3": {
        "TATAMETALI.NS": "Tata Metaliks", "VENKEYS.NS": "Venky's", "ARVINDFASN.NS": "Arvind Fashions",
        "CANTABIL.NS": "Cantabil Retail", "CENTURY.NS": "Century Textiles", "DOLLAR.NS": "Dollar Industries",
        "GOCOLORS.NS": "Go Colors", "KEWAL.NS": "Kewal Kiran", "KPR.NS": "KPR Mill",
        "MANYAVAR.NS": "Vedant Fashions", "PGEL.NS": "PG Electroplast"
    },
    
    "🍔 FMCG Consumer - Midcap 4": {
        "PRAJIND.NS": "Praj Industries", "RAYMOND.NS": "Raymond", "SAPPHIRE.NS": "Sapphire Foods",
        "SPENCERS.NS": "Spencer's Retail", "TRENT.NS": "Trent", "VMART.NS": "V-Mart Retail",
        "WONDERLA.NS": "Wonderla Holidays", "BARBEQUE.NS": "Barbeque Nation", "DEVYANI.NS": "Devyani International",
        "HATSUN.NS": "Hatsun Agro"
    },

    # ========================================================================
    # INDUSTRIAL & CEMENT
    # ========================================================================
    "🏭 Industrial Cement - Large Cap": {
        "AMBUJACEM.NS": "Ambuja Cements", "BEL.NS": "Bharat Electronics",
        "JKCEMENT.NS": "JK Cement", "SHREECEM.NS": "Shree Cement", "SIEMENS.NS": "Siemens",
        "THERMAX.NS": "Thermax"
    },
    
    "🏭 Industrial - Midcap 1": {
        "APLAPOLLO.NS": "APL Apollo", "ASTRAL.NS": "Astral Poly", "CARYSIL.NS": "Carysil",
        "CASTROLIND.NS": "Castrol India", "CENTURYPLY.NS": "Century Plyboards", "CERA.NS": "Cera Sanitaryware",
        "DEEPAKNTR.NS": "Deepak Nitrite", "ELECON.NS": "Elecon Engineering", "FILATEX.NS": "Filatex India",
        "FLUOROCHEM.NS": "Gujarat Fluorochemicals", "GARFIBRES.NS": "Garware Technical", "GRINDWELL.NS": "Grindwell Norton",
        "GSPL.NS": "Gujarat State Petronet", "HIL.NS": "HIL Limited", "INOXWIND.NS": "Inox Wind",
        "JINDALSAW.NS": "Jindal Saw", "KALPATPOWR.NS": "Kalpataru Power", "KANSAINER.NS": "Kansai Nerolac"
    },
    
    "🏭 Industrial - Midcap 2": {
        "KCP.NS": "KCP Limited", "KEC.NS": "KEC International", "KEI.NS": "KEI Industries",
        "KIRLOSENG.NS": "Kirloskar Oil", "LINDEINDIA.NS": "Linde India", "MOIL.NS": "MOIL",
        "NESCO.NS": "NESCO", "NLCINDIA.NS": "NLC India", "PHILIPCARB.NS": "Phillips Carbon",
        "PRINCEPIPE.NS": "Prince Pipes", "PRSMJOHNSN.NS": "Prism Johnson", "RAIN.NS": "Rain Industries",
        "RCF.NS": "Rashtriya Chemicals", "RITES.NS": "RITES", "RVNL.NS": "Rail Vikas Nigam",
        "SAIL.NS": "SAIL", "SJVN.NS": "SJVN", "SOBHA.NS": "Sobha"
    },
    
    "🏭 Industrial - Midcap 3": {
        "SRF.NS": "SRF", "STARCEMENT.NS": "Star Cement", "SUMICHEM.NS": "Sumitomo Chemical",
        "SUPREMEIND.NS": "Supreme Industries", "TECHNOE.NS": "Techno Electric", "TIMETECHNO.NS": "Time Technoplast",
        "TRITURBINE.NS": "Triveni Turbine", "UCOBANK.NS": "UCO Bank", "VINATIORGA.NS": "Vinati Organics",
        "WELCORP.NS": "Welspun Corp"
    },
    
    "🏭 Industrial - Midcap 4": {
        "BEML.NS": "BEML", "BDL.NS": "Bharat Dynamics", "CARBORUNIV.NS": "Carborundum Universal",
        "HAL.NS": "Hindustan Aeronautics", "KIRLOSKAR.NS": "Kirloskar Brothers", "AARTI.NS": "Aarti Industries",
        "ALKYLAMINE.NS": "Alkyl Amines", "ATUL.NS": "Atul Ltd", "BASF.NS": "BASF India", "GNFC.NS": "GNFC"
    },

    # ========================================================================
    # ENERGY & POWER
    # ========================================================================
    "⚡ Energy Power - Large Cap": {
        "ADANIGREEN.NS": "Adani Green", "ADANIPOWER.NS": "Adani Power", "GAIL.NS": "GAIL",
        "HINDPETRO.NS": "HPCL", "IOC.NS": "Indian Oil", "IGL.NS": "Indraprastha Gas",
        "PETRONET.NS": "Petronet LNG", "TATAPOWER.NS": "Tata Power", "TORNTPOWER.NS": "Torrent Power"
    },
    
    "⚡ Energy Power - Midcap 1": {
        "ADANIENSOL.NS": "Adani Energy", "ADANIGAS.NS": "Adani Total Gas", "AEGISCHEM.NS": "Aegis Logistics",
        "GMRINFRA.NS": "GMR Infrastructure", "GSFC.NS": "GSFC", "GUJGASLTD.NS": "Gujarat Gas",
        "MGL.NS": "Mahanagar Gas", "OIL.NS": "Oil India", "ADANITRANS.NS": "Adani Transmission"
    },
    
    "⚡ Energy Power - Midcap 2": {
        "CESC.NS": "CESC", "JSWENERGY.NS": "JSW Energy", "NHPC.NS": "NHPC",
        "SUZLON.NS": "Suzlon Energy", "VEDL.NS": "Vedanta", "CHAMBLFERT.NS": "Chambal Fertilizers"
    },
    
    "⚡ Energy Power - Midcap 3": {
        "COROMANDEL.NS": "Coromandel International", "DEEPAKFERT.NS": "Deepak Fertilizers", "FACT.NS": "FACT",
        "NFL.NS": "National Fertilizers", "ADANIPORTS.NS": "Adani Ports", "CONCOR.NS": "Container Corporation",
        "IRCTC.NS": "IRCTC", "ALLCARGO.NS": "Allcargo Logistics", "BLUEDART.NS": "Blue Dart Express",
        "GATI.NS": "Gati", "MAHLOG.NS": "Mahindra Logistics", "TCI.NS": "Transport Corporation",
        "TCIEXP.NS": "TCI Express", "VRL.NS": "VRL Logistics"
    },

    # ========================================================================
    # RETAIL & ECOMMERCE
    # ========================================================================
    "🛒 Retail Ecommerce - Large Cap": {
        "DMART.NS": "Avenue Supermarts"
    },
    
    "🛒 Retail Ecommerce - Midcap 1": {
        "FIVESTAR.NS": "Five Star Business"
    },
    
    "🛒 Retail Ecommerce - Midcap 2": {
        "ARVINDFASN.NS": "Arvind Fashions"
    },

    # ========================================================================
    # REAL ESTATE
    # ========================================================================
    "🏗️ Real Estate - Large Cap": {
        "DLF.NS": "DLF", "GODREJPROP.NS": "Godrej Properties", "OBEROIRLTY.NS": "Oberoi Realty",
        "PRESTIGE.NS": "Prestige Estates"
    },
    
    "🏗️ Real Estate - Midcap 1": {
        "BRIGADE.NS": "Brigade Enterprises", "IBREALEST.NS": "Indiabulls Real Estate", "KOLTEPATIL.NS": "Kolte-Patil",
        "LODHA.NS": "Macrotech Developers", "MACROTECH.NS": "Macrotech Developers", "PHOENIXLTD.NS": "Phoenix Mills",
        "SIGNATURE.NS": "Signature Global", "AHLUCONT.NS": "Ahluwalia Contracts", "ASHOKA.NS": "Ashoka Buildcon",
        "HCC.NS": "Hindustan Construction", "IRB.NS": "IRB Infrastructure", "IRCON.NS": "IRCON International"
    },
    
    "🏗️ Real Estate - Midcap 2": {
        "NBCC.NS": "NBCC India", "NCCLTD.NS": "NCC Limited", "PNCINFRA.NS": "PNC Infratech",
        "ACC.NS": "ACC Cement", "DALMIACEM.NS": "Dalmia Bharat", "GREENPLY.NS": "Greenply Industries",
        "ORIENTCEM.NS": "Orient Cement"
    },
    
    "🏗️ Real Estate - Midcap 3": {
        "HUDCO.NS": "HUDCO", "SALASAR.NS": "Salasar Techno", "SUNFLAG.NS": "Sunflag Iron",
        "CENTURYTEX.NS": "Century Textiles", "CMSINFO.NS": "CMS Info Systems", "ESABINDIA.NS": "ESAB India",
        "JWL.NS": "Jupiter Wagons"
    },

    # ========================================================================
    # MEDIA & ENTERTAINMENT
    # ========================================================================
    "📺 Media Entertainment": {
        "DB.NS": "DB Corp", "HATHWAY.NS": "Hathway Cable", "INOXLEISUR.NS": "Inox Leisure",
        "JAGRAN.NS": "Jagran Prakashan", "NETWORK18.NS": "Network18 Media", "PVR.NS": "PVR Inox",
        "PVRINOX.NS": "PVR Inox", "SAREGAMA.NS": "Saregama India", "SUNTV.NS": "Sun TV Network",
        "TIPS.NS": "Tips Industries", "TV18BRDCST.NS": "TV18 Broadcast", "TVTODAY.NS": "TV Today",
        "ZEEL.NS": "Zee Entertainment", "HT.NS": "HT Media", "NAVNETEDUL.NS": "Navneet Education",
        "TREEHOUSE.NS": "Tree House Education", "DELTACORP.NS": "Delta Corp", "ONMOBILE.NS": "OnMobile Global"
    },

    # ========================================================================
    # AGRICULTURE & CHEMICALS
    # ========================================================================
    "🌾 Agriculture Chemicals 1": {
        "AARTIIND.NS": "Aarti Industries", "BHAGERIA.NS": "Bhageria Industries",
        "EXCEL.NS": "Excel Crop Care", "HERANBA.NS": "Heranba Industries", "INDOFIL.NS": "Indofil Industries",
        "INSECTICIDES.NS": "Insecticides India", "NOCIL.NS": "NOCIL", "RALLIS.NS": "Rallis India"
    },
    
    "🌾 Agriculture Chemicals 2": {
        "ZUARI.NS": "Zuari Agro Chemicals", "BBTC.NS": "Bombay Burmah", "CENTURYTEXT.NS": "Century Textiles",
        "HINDOILEXP.NS": "Hindustan Oil", "JUBLCHEM.NS": "Jubilant Ingrevia", "KRBL.NS": "KRBL",
        "TATACOFFEE.NS": "Tata Coffee"
    },

    # ========================================================================
    # SPECIALTY & EMERGING
    # ========================================================================
    "🎯 Specialty Emerging 1": {
        "APTECH.NS": "Aptech", "CAREEREDGE.NS": "Career Point", "ZEE.NS": "Zee Learn",
        "CHALET.NS": "Chalet Hotels", "EIH.NS": "EIH", "INDHOTEL.NS": "Indian Hotels",
        "LEMONTREE.NS": "Lemon Tree Hotels", "TAJGVK.NS": "Taj GVK Hotels"
    },
    
    "🎯 Specialty Emerging 2": {
        "COX&KINGS.NS": "Cox & Kings", "SPICEJET.NS": "SpiceJet", "TBO.NS": "TBO Tek",
        "THOMASCOOK.NS": "Thomas Cook", "SIS.NS": "SIS Limited", "UNOMINDA.NS": "Uno Minda",
        "EMAMIPAP.NS": "Emami Paper", "SESAGOA.NS": "Sesa Goa", "TNIDETF.NS": "TNPL",
        "WESTPAPER.NS": "West Coast Paper", "GRSE.NS": "Garden Reach Shipbuilders",
        "MAZDOCK.NS": "Mazagon Dock", "MIDHANI.NS": "Mishra Dhatu Nigam"
    },

    # ========================================================================
    # TEXTILES & APPARELS
    # ========================================================================
    "👔 Textiles Apparels": {
        "AARVEEDEN.NS": "Aarvee Denims", "ALOKTEXT.NS": "Alok Textile", "ARSS.NS": "ARSS Infrastructure",
        "BANSWRAS.NS": "Banswara Syntex", "GOKEX.NS": "Gokaldas Exports", "NAHARINDUS.NS": "Nahar Industrial",
        "NITIN.NS": "Nitin Spinners", "RSWM.NS": "RSWM", "SPENTEX.NS": "Spentex Industries",
        "SUTLEJTEX.NS": "Sutlej Textiles", "TRIDENT.NS": "Trident", "VARDHACRLC.NS": "Vardhman Textiles"
    },

    # ========================================================================
    # DIVERSIFIED
    # ========================================================================
    "🔄 Diversified 1": {
        "HGINFRA.NS": "HG Infra", "ORIENT.NS": "Orient Cement", "PRISM.NS": "Prism Johnson",
        "SOMANY.NS": "Somany Ceramics", "FINOLEX.NS": "Finolex Industries", "NAGREEKEXP.NS": "Nagreeka Exports",
        "SUPREME.NS": "Supreme Industries", "VALIANTORG.NS": "Valiant Organics", "FAG.NS": "Schaeffler India",
        "NBC.NS": "National Bearings", "NRB.NS": "NRB Bearings"
    },
    
    "🔄 Diversified 2": {
        "GALAXYSURF.NS": "Galaxy Surfactants", "KIRLFER.NS": "Kirloskar Ferrous", "KSB.NS": "KSB Pumps",
        "SHAKTICP.NS": "Shakti Corporation", "ACCELYA.NS": "Accelya Kale", "ACI.NS": "Archean Chemical"
    },

    # ========================================================================
    # SMALLCAP - ENGINEERING & MANUFACTURING
    # ========================================================================
    "🔧 Smallcap Engineering 1": {
        "AARTISURF.NS": "Aarti Surfactants", "ABSORB.NS": "Absorb Plus", "ACCURACY.NS": "Accuracy Shipping",
        "ACRYSIL.NS": "Acrysil", "ADVENZYMES.NS": "Advanced Enzymes", "AEROFLEX.NS": "Aeroflex Industries",
        "AETHER.NS": "Aether Industries", "AGCNET.NS": "AGC Networks", "AHLEAST.NS": "Asian Hotels East",
        "AIIL.NS": "Ashapura Intimates", "AIRAN.NS": "Airan Ltd", "AKASH.NS": "Akash Infra-Projects",
        "AKSHARCHEM.NS": "Akshar Chem", "ALPA.NS": "Alpa Laboratories", "ALPHAGEO.NS": "Alphageo India",
        "ALPSINDUS.NS": "Alps Industries"
    },
    
    "🔧 Smallcap Engineering 2": {
        "AMIABLE.NS": "Amiable Logistics", "AMJLAND.NS": "AMJ Land Holdings", "AMRUTANJAN.NS": "Amrutanjan Health",
        "ANANTRAJ.NS": "Anant Raj", "ANDHRSUGAR.NS": "Andhra Sugars", "ANMOL.NS": "Anmol Industries",
        "ANUP.NS": "Anupam Rasayan", "APARINDS.NS": "Apar Industries", "APCL.NS": "Anjani Portland",
        "APCOTEXIND.NS": "Apcotex Industries", "APEX.NS": "Apex Frozen Foods", "APOLLO.NS": "Apollo Micro Systems",
        "APTECHT.NS": "Aptech", "ARASU.NS": "Arasu Cable", "ARCHIDPLY.NS": "Archidply Industries",
        "ARCHIES.NS": "Archies Ltd", "ARL.NS": "Apar Industries", "ARMANFIN.NS": "Arman Financial",
        "ARROWGREEN.NS": "Arrow Greentech"
    },
    
    "🔧 Smallcap Engineering 3": {
        "ARSHIYA.NS": "Arshiya", "ARTNIRMAN.NS": "Art Nirman", "ASAHISONG.NS": "Asahi Songwon",
        "ASAL.NS": "Automotive Stampings", "ASALCBR.NS": "Associated Alcohols", "ASHIANA.NS": "Ashiana Housing",
        "ASHIMASYN.NS": "Ashima Ltd", "ASIANENE.NS": "Asian Energy Services", "ASIANHOTNR.NS": "Asian Hotels North",
        "ASPINWALL.NS": "Aspinwall", "ASTEC.NS": "Astec LifeSciences", "ASTERDM.NS": "Aster DM Healthcare",
        "ASTRAMICRO.NS": "Astra Microwave", "ATAM.NS": "Atam Valves", "ATNINTER.NS": "ATN International",
        "ATULAUTO.NS": "Atul Auto"
    },
    
    "🔧 Smallcap Engineering 4": {
        "AURIONPRO.NS": "Aurionpro Solutions", "AUSOMENT.NS": "Ausom Enterprise", "AUSTRAL.NS": "Austral Coke",
        "AUTOAXLES.NS": "Automotive Axles", "AUTOIND.NS": "Autoline Industries", "AVALON.NS": "Avalon Technologies",
        "AVTNPL.NS": "AVT Natural Products", "AWL.NS": "Adani Wilmar", "AXISCADES.NS": "Axiscades Engineering",
        "AXISGOLD.NS": "Axis Gold", "AYMSYNTEX.NS": "AYM Syntex", "AZAD.NS": "Azad Engineering",
        "BAGFILMS.NS": "BAG Films", "BAJAJHIND.NS": "Bajaj Hindusthan Sugar", "BALAJITELE.NS": "Balaji Telefilms",
        "BALAXI.NS": "Balaxi Ventures", "BALKRISHNA.NS": "Balkrishna Paper", "BALMLAWRIE.NS": "Balmer Lawrie",
        "BALPHARMA.NS": "Bal Pharma", "BANCOINDIA.NS": "Banco Products", "BANG.NS": "Bang Overseas"
    },

    # ========================================================================
    # SMALLCAP - CHEMICALS & PHARMACEUTICALS
    # ========================================================================
    "🧪 Smallcap Chemicals 1": {
        "BBOX.NS": "Black Box", "BBL.NS": "Bharat Bijlee", "BCG.NS": "Brightcom Group",
        "BCP.NS": "Banco Products", "BEEKAY.NS": "Beekay Steel", "BELSTAR.NS": "Belstar Microfinance",
        "BEPL.NS": "Bhansali Engineering", "BFINVEST.NS": "BF Investment", "BGRENERGY.NS": "BGR Energy Systems",
        "BHAGYANGR.NS": "Bhagiradha Chemicals", "BHANDARI.NS": "Bhandari Hosiery", "BHARATGEAR.NS": "Bharat Gears"
    },
    
    "🧪 Smallcap Chemicals 2": {
        "BHARATWIRE.NS": "Bharat Wire Ropes", "BHEL.NS": "BHEL", "BILENERGY.NS": "Bil Energy Systems",
        "BIRLACABLE.NS": "Birla Cable", "BIRLAMONEY.NS": "Aditya Birla Money", "BIRLACORPN.NS": "Birla Corporation",
        "BIRLATYRE.NS": "Birla Tyres", "BKM.NS": "Bkmindspace", "BLACKROSE.NS": "Blackrose Industries",
        "BLAL.NS": "BEML Land Assets", "BLKASHYAP.NS": "B L Kashyap", "BLUEBLENDS.NS": "Blue Blends",
        "BLUECOAST.NS": "Blue Coast Hotels", "BLUEJET.NS": "Blue Jet Healthcare", "BODALCHEM.NS": "Bodal Chemicals",
        "BOMDYEING.NS": "Bombay Dyeing", "BOROLTD.NS": "Borosil Ltd"
    },
    
    "🧪 Smallcap Chemicals 3": {
        "BRFL.NS": "Bombay Rayon", "BRO.NS": "Brigade Road", "BSE.NS": "BSE Ltd",
        "BSHSL.NS": "Bombay Super Hybrid", "BSL.NS": "BSL Ltd", "BSOFT.NS": "Birlasoft",
        "BTML.NS": "Bodal Trading", "BURNPUR.NS": "Burnpur Cement", "BUTTERFLY.NS": "Butterfly Gandhimathi",
        "CADSYS.NS": "Cadsys India", "CALSOFT.NS": "California Software", "CAMLINFINE.NS": "Camlin Fine Sciences",
        "CANFINHOME.NS": "Can Fin Homes", "CAPF.NS": "Capital First", "CAPTRUST.NS": "Capital Trust",
        "CARERATING.NS": "CARE Ratings"
    },
    
    "🧪 Smallcap Chemicals 4": {
        "CARGEN.NS": "Cargen Drugs", "CCCL.NS": "Consolidated Construction", "CELEBRITY.NS": "Celebrity Fashions",
        "CELLO.NS": "Cello World", "CENTENKA.NS": "Century Enka", "CENTUM.NS": "Centum Electronics",
        "CEREBRAINT.NS": "Cerebra Integrated", "CGCL.NS": "Capri Global", "CGPOWER.NS": "CG Power",
        "CHEMBOND.NS": "Chembond Chemicals", "CHEMCON.NS": "Chemcon Speciality", "CHEMFAB.NS": "Chemfab Alkalis",
        "CHEMPLASTS.NS": "Chemplast Sanmar", "CHENNPETRO.NS": "Chennai Petroleum"
    },

    # ========================================================================
    # SMALLCAP - TEXTILES & CONSUMER GOODS
    # ========================================================================
    "👕 Smallcap Textiles 1": {
        "CIGNITITEC.NS": "Cigniti Technologies", "CINELINE.NS": "Cineline India", "CINEVISTA.NS": "Cinevista",
        "CLNINDIA.NS": "Clariant Chemicals", "CLSEL.NS": "Chaman Lal Setia", "CMICABLES.NS": "CMI Ltd",
        "COASTCORP.NS": "Coastal Corporation", "COFFEEDAY.NS": "Coffee Day Enterprises", "COMPINFO.NS": "Compuage Infocom",
        "COMPUSOFT.NS": "Compucom Software", "CONFIPET.NS": "Confidence Petroleum", "CONSOFINVT.NS": "Consolidated Finvest",
        "CONTROLS.NS": "Control Print", "COOKCAST.NS": "Cookcast"
    },
    
    "👕 Smallcap Textiles 2": {
        "CORALFINAC.NS": "Coral India Finance", "CORDSCABLE.NS": "Cords Cable", "COROENGG.NS": "Coromandel Engineering",
        "CORPBANK.NS": "Corporation Bank", "COSMOFILMS.NS": "Cosmo Films", "COUNCODOS.NS": "Country Condo's",
        "CPSEETEC.NS": "CPS EeeTech", "CREATIVE.NS": "Creative Newtech", "CREATIVEYE.NS": "Creative Eye",
        "CREST.NS": "Crest Ventures", "CRIMSONLOG.NS": "Crimson Logistics", "CROSSING.NS": "Crossing Republic",
        "CRSBWARDR.NS": "CRISIL Board", "CUBEXTUB.NS": "Cubex Tubings", "CUREXAUTO.NS": "Curex Pharmaceuticals",
        "CURATECH.NS": "Cura Technologies", "CUB.NS": "City Union Bank", "CYBERTECH.NS": "Cybertech Systems"
    },
    
    "👕 Smallcap Textiles 3": {
        "CYBERMEDIA.NS": "Cybermedia India", "DAICHISANK.NS": "Daiichi Sankyo", "DALMIASUG.NS": "Dalmia Bharat Sugar",
        "DANGEE.NS": "Dangee Dums", "DATAPATTNS.NS": "Data Patterns", "DBOL.NS": "Dhampur Bio Organics",
        "DBL.NS": "Dilip Buildcon", "DBREALTY.NS": "DB Realty", "DBSTOCKBRO.NS": "DB Stock Brokers",
        "DCAST.NS": "Diecast", "DCB.NS": "DCB Bank", "DCHL.NS": "Deccan Chronicle",
        "DCM.NS": "DCM Ltd", "DCMSHRIRAM.NS": "DCM Shriram", "DCMSRL.NS": "DCM Shriram",
        "DCW.NS": "DCW Ltd", "DCXINDIA.NS": "DCX Systems", "DDL.NS": "Dhunseri Ventures",
        "DEBOCK.NS": "De Nora India"
    },
    
    "👕 Smallcap Textiles 4": {
        "DEEPIND.NS": "Deepak Spinners", "DENDRO.NS": "Dendro Technologies", "DENORA.NS": "De Nora India",
        "DENZYME.NS": "Dezyne E-Commerce", "DHANBANK.NS": "Dhanalakshmi Bank", "DHANUKA.NS": "Dhanuka Agritech",
        "DHARAMSI.NS": "Dharamsi Morarji", "DHAMPURSUG.NS": "Dhampur Sugar", "DHANVARSHA.NS": "Dhanvarsha Finvest",
        "DHUNINV.NS": "Dhunseri Investments", "DIACABS.NS": "Diamond Cables", "DIAMINESQ.NS": "Diamines Chemicals",
        "DIGJAM.NS": "Digjamlimited", "DIGISPICE.NS": "DiGiSPICE Technologies", "DIGJAMLMTD.NS": "Digjamlimited",
        "DION.NS": "Dion Global Solutions", "DISHMAN.NS": "Dishman Carbogen", "DIVGIITTS.NS": "Divgi TorqTransfer",
        "DISHTV.NS": "Dish TV India"
    },

    # ========================================================================
    # SMALLCAP - IT & SOFTWARE SERVICES
    # ========================================================================
    "💾 Smallcap IT 1": {
        "DLINKINDIA.NS": "D-Link India", "DMCC.NS": "DMCC Speciality", "DOLAT.NS": "Dolat Investments",
        "DONEAR.NS": "Donear Industries", "DOUBLECON.NS": "Double Con", "DREDGECORP.NS": "Dredging Corporation",
        "DUCON.NS": "Ducon Infratechnologies", "DUCOL.NS": "Ducol Organics", "DUMMETT.NS": "Dummett Coote",
        "DWARKESH.NS": "Dwarkesh Sugar", "DYNAMATECH.NS": "Dynamatic Technologies", "DYNAMIND.NS": "Dynamatic Technologies",
        "EASTSILK.NS": "Eastern Silk", "EASUNREYRL.NS": "Easun Reyrolle", "EBBCO.NS": "EbbCo Ventures",
        "ECLFINANCE.NS": "Edelweiss Capital", "ECOBOARD.NS": "Eco Board", "EDELWEISS.NS": "Edelweiss Financial",
        "EDUCOMP.NS": "Educomp Solutions"
    },
    
    "💾 Smallcap IT 2": {
        "EIDPARRY.NS": "EID Parry", "EIFFL.NS": "Euro India Fresh Foods", "EIHAHOTELS.NS": "EIH Associated Hotels",
        "EIHOTEL.NS": "EIH Ltd", "EIMCOELECO.NS": "Eimco Elecon", "EKENNIS.NS": "Ekennis Software",
        "ELECTROCAST.NS": "Electrocast Sales", "ELECTHERM.NS": "Electrotherm India", "ELGIEQUIP.NS": "Elgi Equipments",
        "ELIN.NS": "Elin Electronics", "EMAMIPAP.NS": "Emami Paper", "EMAMIREAL.NS": "Emami Realty",
        "EMIRATE.NS": "Emirate Securities", "EMMBI.NS": "Emmbi Industries", "EMSLIMITED.NS": "EMS Ltd",
        "ENIL.NS": "Entertainment Network", "EPACK.NS": "Epack Durables", "EQUIPPP.NS": "Equippp Social"
    },
    
    "💾 Smallcap IT 3": {
        "EROSMEDIA.NS": "Eros International", "ESSARSHPNG.NS": "Essar Shipping", "ESTER.NS": "Ester Industries",
        "ETECHNO.NS": "Electrotherm Technologies", "EUROCERA.NS": "Euro Ceramics", "EUROTEXIND.NS": "Eurotex Industries",
        "EVEREADY.NS": "Eveready Industries", "EVERESTIND.NS": "Everest Industries", "EXCELINDUS.NS": "Excel Industries",
        "EXPLEOSOL.NS": "Expleo Solutions", "FAGBEARING.NS": "Schaeffler India", "FAIRCHEM.NS": "Fairchem Speciality",
        "FAZE3.NS": "Faze Three", "FCL.NS": "Fineotex Chemical", "FEL.NS": "Future Enterprises",
        "FELDVR.NS": "Future Enterprises DVR", "FENTURA.NS": "Fentura Financial", "FCSSOFT.NS": "FCS Software"
    },
    
    "💾 Smallcap IT 4": {
        "FIBERWEB.NS": "Fiberweb India", "FIEMIND.NS": "Fiem Industries", "FINPIPE.NS": "Finolex Industries",
        "FINKURVE.NS": "Finkurve Financial", "FINOL.NS": "Finolex Industries", "FIRSTCRY.NS": "FirstCry Baby",
        "FIRSTSOUR.NS": "Firstsource Solutions", "FLFL.NS": "Future Lifestyle", "FLIP.NS": "Flip Media",
        "FOCUSLIGHT.NS": "Focus Lighting", "FOMENTO.NS": "Fomento Resorts", "FOODSIN.NS": "Foods & Inns",
        "FORCE.NS": "Force Motors", "FOSECOIND.NS": "Foseco India", "FRETAIL.NS": "Future Retail",
        "FRIEDBERG.NS": "Friedberg Direct"
    },

    # ========================================================================
    # SMALLCAP - INFRASTRUCTURE & REAL ESTATE
    # ========================================================================
    "🏢 Smallcap Infra 1": {
        "FSC.NS": "Future Supply Chain", "FSL.NS": "Firstsource Solutions", "GAEL.NS": "Gujarat Ambuja Exports",
        "GALLANTT.NS": "Gallantt Ispat", "GANDHAR.NS": "Gandhar Oil Refinery", "GANDHITUBE.NS": "Gandhi Special Tubes",
        "GANESHHOUC.NS": "Ganesh Housing", "GANECOS.NS": "Ganesha Ecosphere", "GANESHBE.NS": "Ganesh Benzoplast",
        "GATECABLE.NS": "Gate Way Distriparks", "GATEWAY.NS": "Gateway Distriparks", "GAYAHWS.NS": "Gayatri Highways",
        "GDL.NS": "Gateway Distriparks", "GENCON.NS": "Generic Pharma", "GENSOL.NS": "Gensol Engineering",
        "GEOJITFSL.NS": "Geojit Financial", "GEPIL.NS": "GE Power India", "GESHIP.NS": "Great Eastern Shipping",
        "GHCL.NS": "GHCL Ltd"
    },
    
    "🏢 Smallcap Infra 2": {
        "GHCLTEXTIL.NS": "GHCL Textiles", "GICHSGFIN.NS": "GIC Housing Finance", "GICRE.NS": "GIC Re",
        "GILLANDERS.NS": "Gillanders Arbuthnot", "GINNIFILA.NS": "Ginni Filaments", "GIPCL.NS": "Gujarat Industries",
        "GISOLUTION.NS": "GI Engineering Solutions", "GITANJALI.NS": "Gitanjali Gems", "GKWLIMITED.NS": "GKW Ltd",
        "GLAND.NS": "Gland Pharma", "GLFL.NS": "Gujarat Lease Financing", "GLOBALPET.NS": "Global Pet Industries",
        "GLOBOFFS.NS": "Global Offshore", "GLOBALVECT.NS": "Global Vectra", "GLOBUSSPR.NS": "Globus Spirits",
        "GLORY.NS": "Glory Polyfilms", "GMBREW.NS": "GM Breweries", "GMDCLTD.NS": "Gujarat Mineral",
        "GMMPFAUDLR.NS": "GMM Pfaudler", "GNA.NS": "GNA Axles"
    },
    
    "🏢 Smallcap Infra 3": {
        "GOACARBON.NS": "Goa Carbon", "GODREJAGRO.NS": "Godrej Agrovet", "GODREJIND.NS": "Godrej Industries",
        "GOENKA.NS": "Goenka Business", "GOKUL.NS": "Gokul Refoils", "GOKULMECH.NS": "Gokul Agro",
        "GOLDBEES.NS": "Gold BeES", "GOLDTECH.NS": "Goldstone Technologies", "GOODLUCK.NS": "Goodluck India",
        "GOODYEAR.NS": "Goodyear India", "GPIL.NS": "Godawari Power", "GPTINFRA.NS": "GPT Infraprojects",
        "GPPL.NS": "Gujarat Pipavav", "GRABALALK.NS": "Grasim Industries", "GRAUWEIL.NS": "Grauer Weil India",
        "GRAVITA.NS": "Gravita India", "GREENLAM.NS": "Greenlam Industries"
    },
    
    "🏢 Smallcap Infra 4": {
        "GREENPOWER.NS": "Greenpower Motor", "GRMOVER.NS": "GRM Overseas", "GRPLTD.NS": "GRP Ltd",
        "GRUH.NS": "Gruh Finance", "GTL.NS": "GTL Ltd", "GTLINFRA.NS": "GTL Infrastructure",
        "GTMLIMITED.NS": "GTM Ltd", "GTPL.NS": "GTPL Hathway", "GUFICBIO.NS": "Gufic Biosciences",
        "GUJAPOLLO.NS": "Gujarat Apollo", "GUJNREDVR.NS": "Gujarat NRE Coke", "GUJRAFFIA.NS": "Gujarat Raffia",
        "GULFOILLUB.NS": "Gulf Oil Lubricants", "GULFPETRO.NS": "GP Petroleums", "GVKPIL.NS": "GVK Power",
        "GVPTECH.NS": "GVP Infotech", "HALONIX.NS": "Halonix Technologies"
    },

    # ========================================================================
    # SMALLCAP - ENERGY & UTILITIES
    # ========================================================================
    "⚡ Smallcap Energy 1": {
        "HAMSUNDAR.NS": "Hamsund Enterprise", "HARDWYN.NS": "Hardwyn India", "HARRMALAYA.NS": "Harrisons Malayalam",
        "HARSHA.NS": "Harsha Engineers", "HBSL.NS": "HB Stockholdings", "HEG.NS": "HEG Ltd",
        "HEIDELBERG.NS": "HeidelbergCement India", "HELIOS.NS": "Helios Matheson", "HERCULES.NS": "Hercules Hoists",
        "HERITGFOOD.NS": "Heritage Foods", "HESTERBIO.NS": "Hester Biosciences", "HEUBACHIND.NS": "Heubach Colorants",
        "HEXATRADEX.NS": "Hexa Tradex", "HFCL.NS": "HFCL Ltd"
    },
    
    "⚡ Smallcap Energy 2": {
        "HGS.NS": "Hinduja Global", "HIKAL.NS": "Hikal Ltd", "HILTON.NS": "Hilton Metal",
        "HIMATSEIDE.NS": "Himatsingka Seide", "HINDCOMPOS.NS": "Hindustan Composites", "HINDCOPPER.NS": "Hindustan Copper",
        "HINDDORROL.NS": "Hinddorrol", "HINDMOTORS.NS": "Hindustan Motors", "HINDNATGLS.NS": "Hindon Natural",
        "HINDWAREAP.NS": "Hindware Appliances", "HINDZINC.NS": "Hindustan Zinc", "HIRECT.NS": "Hind Rectifiers",
        "HITECH.NS": "Hitech Corporation", "HITECHCORP.NS": "Hitech Corporation", "HITECHGEAR.NS": "Hitachi Energy",
        "HMT.NS": "HMT Ltd", "HMVL.NS": "Hindustan Media", "HNDFDS.NS": "Hindustan Foods"
    },
    
    "⚡ Smallcap Energy 3": {
        "HONDAPOWER.NS": "Honda Power", "HOTELRUGBY.NS": "Hotel Rugby", "HOVS.NS": "HOV Services",
        "HPAL.NS": "HP Adhesives", "HPL.NS": "HPL Electric", "HSCL.NS": "Himadri Speciality",
        "HTMEDIA.NS": "HT Media", "HUHTAMAKI.NS": "Huhtamaki India", "ICIL.NS": "Indo Count",
        "ICRA.NS": "ICRA Ltd", "IDBI.NS": "IDBI Bank", "IDEA.NS": "Vodafone Idea",
        "IDFC.NS": "IDFC Ltd", "IEX.NS": "Indian Energy Exchange", "IFBAGRO.NS": "IFB Agro",
        "IFBIND.NS": "IFB Industries", "IFCI.NS": "IFCI Ltd", "IFGLEXPOR.NS": "IFGL Refractories"
    },
    
    "⚡ Smallcap Energy 4": {
        "IGARASHI.NS": "Igarashi Motors", "IGPL.NS": "IG Petrochemicals", "IITL.NS": "Industrial Investment",
        "IMAGICAA.NS": "Imagicaa World", "IMFA.NS": "Indian Metals", "IMPAL.NS": "India Cements",
        "INANI.NS": "Inani Marbles", "INCA.NS": "India Nippon", "INDBANK.NS": "Indbank Merchant",
        "INDIANCARD.NS": "Indian Card", "INDIANHUME.NS": "Indian Hume Pipe", "INDIASHLTR.NS": "India Shelter",
        "INDIGO.NS": "InterGlobe Aviation", "INDIGOPNTS.NS": "Indigo Paints", "INDITNX.NS": "India Nivesh",
        "INDNIPPON.NS": "India Nippon", "INDOAMIN.NS": "Indo Amines"
    },

    # ========================================================================
    # SMALLCAP - BANKING & FINANCIAL SERVICES
    # ========================================================================
    "🏛️ Smallcap Finance 1": {
        "INDOBORAX.NS": "Indo Borax", "INDOCOUNT.NS": "Indo Count", "INDOKEM.NS": "Indokem Ltd",
        "INDOMETAL.NS": "Indo Metal", "INDORAMA.NS": "Indo Rama Synthetics", "INDOSOLAR.NS": "Indosolar",
        "INDOSTAR.NS": "IndoStar Capital", "INDOTECH.NS": "Indo Tech", "INDOTHAI.NS": "Indo Thai Securities",
        "INDOWIND.NS": "Indowind Energy", "INDRAMEDCO.NS": "Indraprastha Medical", "INDSWFTLAB.NS": "Ind-Swift Laboratories",
        "INDSWFTLTD.NS": "Ind-Swift Ltd", "INDTERRAIN.NS": "Indian Terrain", "INDUSTOWER.NS": "Indus Towers",
        "INEOSSTYRO.NS": "INEOS Styrolution", "INFOMEDIA.NS": "Infomedia Press", "INGERRAND.NS": "Ingersoll Rand",
        "INNOVACAP.NS": "Innovatus Capital", "INOXGREEN.NS": "Inox Green"
    },
    
    "🏛️ Smallcap Finance 2": {
        "INSECTICID.NS": "Insecticides India", "INTENTECH.NS": "Intense Technologies", "INTLCONV.NS": "International Conveyors",
        "IOLCP.NS": "IOL Chemicals", "IPAPPM.NS": "Intrasoft Technologies", "IPL.NS": "India Pesticides",
        "IRISDOREME.NS": "Iris Clothings", "IRISENERGY.NS": "Iris Energy", "ISFT.NS": "Intrasoft Technologies",
        "ISMTLTD.NS": "ISMT Ltd", "ITDCEM.NS": "ITD Cementation", "ITELGREEN.NS": "ITEL Greentech"
    },
    
    "🏛️ Smallcap Finance 3": {
        "ITI.NS": "ITI Ltd", "ITNL.NS": "IL&FS Transportation", "IVRCL.NS": "IVRCL Ltd",
        "IVP.NS": "IVP Ltd", "IWEL.NS": "Innotech Solutions", "IZMO.NS": "IZMO Ltd",
        "JAGSNPHARM.NS": "Jagsonpal Pharma", "JAIBALAJI.NS": "Jai Balaji Industries", "JAICORPLTD.NS": "Jaicorp Ltd",
        "JAIHINDPRO.NS": "Jaihind Projects", "JAIPURKURT.NS": "Nandani Creation", "JAYSREETEA.NS": "Jayshree Tea",
        "JBFIND.NS": "JBF Industries", "JBMA.NS": "JBM Auto", "JCHAC.NS": "Johnson Controls",
        "JETAIRWAYS.NS": "Jet Airways", "JETFREIGHT.NS": "Jet Freight Logistics", "JETINFRA.NS": "Jet Infrastructure",
        "JFLLIFE.NS": "JFL Life Sciences", "JIKIND.NS": "JIK Industries", "JINDALPHOT.NS": "Jindal Photo"
    },
    
    "🏛️ Smallcap Finance 4": {
        "JINDALPOLY.NS": "Jindal Poly Films", "JINDALSAWNS": "Jindal Saw", "JINDALSTEL.NS": "Jindal Steel",
        "JINDWORLD.NS": "Jindal Worldwide", "JISLDVREQS.NS": "Jainam Share", "JISLJALEQS.NS": "Jainam Jalaram",
        "JITFINFRA.NS": "JITF Infralogistics", "JMA.NS": "Jullundur Motor", "JMTAUTOLTD.NS": "JMT Auto",
        "JOCIL.NS": "Jocil Ltd", "JONENG.NS": "Jones Engineering", "JPOLYINVST.NS": "Jindal Poly Investment",
        "JSL.NS": "Jindal Stainless", "JSLHISAR.NS": "Jindal Stainless Hisar", "JSWISPL.NS": "JSW Ispat",
        "JTEKTINDIA.NS": "JTEKT India"
    },

    # ========================================================================
    # SMALLCAP - FOOD, BEVERAGES & AGRICULTURE
    # ========================================================================
    "🍎 Smallcap Food 1": {
        "JTLIND.NS": "JTL Industries", "JUBLINDS.NS": "Jubilant Industries", "JUGGILAL.NS": "Juggilal Kamlapat",
        "JUMBOAG.NS": "Jumbo Bag", "JUMPNET.NS": "Jumpnet Technologies", "JVLAGRO.NS": "JVL Agro",
        "JYOTISTRUC.NS": "Jyoti Structures", "KABRAEXTRU.NS": "Kabra Extrusion", "KAKATCEM.NS": "Kakatiya Cement",
        "KAMDHENU.NS": "Kamdhenu Ltd", "KAMOPAINTS.NS": "Kamdhenu Paints", "KANANIIND.NS": "Kanani Industries",
        "KANORICHEM.NS": "Kanoria Chemicals", "KANPRPLA.NS": "Kanchenjunga Tea", "KARDA.NS": "Karda Constructions"
    },
    
    "🍎 Smallcap Food 2": {
        "KARMAENG.NS": "Karma Energy", "KARNIMATA.NS": "Karni Industries", "KARNINVEST.NS": "Karni Investment",
        "KARURVYSYA.NS": "Karur Vysya Bank", "KAUSHALYA.NS": "Kausalya Infrastructure", "KAVVERITEL.NS": "Kavveri Telecom",
        "KAYPITFIN.NS": "Kaypee Financing", "KAYCEEI.NS": "Kayceei Industries", "KCPSUGIND.NS": "KCP Sugar",
        "KDIL.NS": "Karnimata Data", "KELLTONTEC.NS": "Kellton Tech", "KERNEX.NS": "Kernex Microsystems",
        "KESARWIRES.NS": "Kesar Wires", "KEWAUNEE.NS": "Kewaunee Scientific", "KEYFINSERV.NS": "Keynote Financial",
        "KEYTONE.NS": "Keytone Leasing", "KHANDSE.NS": "Khandwala Securities", "KHAIPULSE.NS": "Khaitanpulse",
        "KICL.NS": "Kalyani Investment", "KILITCH.NS": "Kilitch Drugs", "KIMBERLY.NS": "Kimberly Clark"
    },
    
    "🍎 Smallcap Food 3": {
        "KINGFA.NS": "Kingfa Science", "KIRIINDUS.NS": "Kiri Industries", "KIRLOSBROS.NS": "Kirloskar Brothers",
        "KIRLOSIND.NS": "Kirloskar Industries", "KITEX.NS": "Kitex Garments", "KKCL.NS": "Kewal Kiran Clothing",
        "KKC.NS": "KKR & Co", "KMSUGAR.NS": "KM Sugar Mills", "KNAGRI.NS": "KN Agri Resources",
        "KNRCON.NS": "KNR Constructions", "KODYTECH.NS": "Kody Technolab", "KOKUYOCMLN.NS": "Kokuyo Camlin",
        "KOPRAN.NS": "Kopran Ltd", "KOSMOTEC.NS": "Kosmo e-Technology", "KOTARISUG.NS": "Kothari Sugars",
        "KPIGREEN.NS": "KPI Green Energy", "KREBSBIO.NS": "Krebs Biochemicals", "KRIINFRA.NS": "K Raheja"
    },
    
    "🍎 Smallcap Food 4": {
        "KRIDHANINF.NS": "Kridhan Infra", "KRISHANA.NS": "Krishana Phoschem", "KRITI.NS": "Kriti Industries",
        "KRITIKA.NS": "Kritika Wires", "KRITINUT.NS": "Kriti Nutrients", "KRONS.NS": "Kronox Lab Sciences",
        "KUMARASWA.NS": "Kumar Swamy Construction", "KUMARKS.NS": "Kumar Swamy", "KUMBHAT.NS": "Kumbhat Financial",
        "KUNDANCARE.NS": "Kundan Care", "KUPRIYA.NS": "Kupriya Industries", "KUSTODIAN.NS": "Kustodian Securities",
        "KWALITY.NS": "Kwality Ltd", "KWALIT.NS": "Kwalitex Industries", "L&TFHIN.NS": "L&T Finance",
        "LA.NS": "Laurus Labs"
    },

    # ========================================================================
    # SMALLCAP - RETAIL & MEDIA
    # ========================================================================
    "🛍️ Smallcap Retail 1": {
        "LAKPRE.NS": "Lakshmi Precision", "LAKSHMIEFL.NS": "Lakshmi Energy", "LAMBODHARA.NS": "Lambodhara Textiles",
        "LANCER.NS": "Lancer Container", "LANDMARK.NS": "Landmark Property", "LAOPALA.NS": "La Opala RG",
        "LASA.NS": "Lasa Supergenerics", "LAXMIMACH.NS": "Lakshmi Machine", "LCCINFOTEC.NS": "LCC Infotech",
        "LCC.NS": "LCC Infotech", "LEXUS.NS": "Lexus Granito", "LFIC.NS": "Lakshmi Finance",
        "LG.NS": "LG Balakrishnan", "LGBBROSLTD.NS": "LG Balakrishnan", "LGBFORGE.NS": "LG Balakrishnan Forge",
        "LGHL.NS": "LG Balakrishnan", "LIBAS.NS": "Libas Designs", "LIBERTSHOE.NS": "Liberty Shoes",
        "LICNETFN50.NS": "LIC MF Nifty 50"
    },
    
    "🛍️ Smallcap Retail 2": {
        "LINCPEN.NS": "Lincoln Pharmaceuticals", "LINKINTIME.NS": "Link Intime", "LKINVESTING.NS": "LKP Finance",
        "LLOYDSME.NS": "Lloyds Metals", "LLOYDS.NS": "Lloyds Enterprises", "LOKESHMACH.NS": "Lokesh Machines",
        "LOTUSEYE.NS": "Lotus Eye Care", "LPDC.NS": "Landmark Property", "LTFOODS.NS": "LT Foods",
        "LUMAXIND.NS": "Lumax Industries", "LUMAXTECH.NS": "Lumax Auto Tech"
    }
}

# ============================================================================
# INDUSTRY BENCHMARKS - CONSOLIDATED
# ============================================================================

INDUSTRY_BENCHMARKS = {
    # Large Cap Benchmarks
    'Technology': {'pe': 25, 'ev_ebitda': 15},
    'Financial Services': {'pe': 18, 'ev_ebitda': 12},
    'Consumer Cyclical': {'pe': 30, 'ev_ebitda': 14},
    'Consumer Defensive': {'pe': 35, 'ev_ebitda': 16},
    'Healthcare': {'pe': 28, 'ev_ebitda': 14},
    'Industrials': {'pe': 22, 'ev_ebitda': 12},
    'Energy': {'pe': 15, 'ev_ebitda': 8},
    'Basic Materials': {'pe': 18, 'ev_ebitda': 10},
    'Communication Services': {'pe': 20, 'ev_ebitda': 12},
    'Real Estate': {'pe': 25, 'ev_ebitda': 18},
    'Utilities': {'pe': 16, 'ev_ebitda': 10},
    'Default': {'pe': 20, 'ev_ebitda': 12}
}

# Midcap specific benchmarks (slightly higher multiples)
MIDCAP_BENCHMARKS = {
    'Technology': {'pe': 28, 'ev_ebitda': 16},
    'Financial Services': {'pe': 20, 'ev_ebitda': 14},
    'Consumer Cyclical': {'pe': 32, 'ev_ebitda': 16},
    'Consumer Defensive': {'pe': 38, 'ev_ebitda': 18},
    'Healthcare': {'pe': 30, 'ev_ebitda': 16},
    'Industrials': {'pe': 25, 'ev_ebitda': 14},
    'Energy': {'pe': 18, 'ev_ebitda': 10},
    'Basic Materials': {'pe': 20, 'ev_ebitda': 12},
    'Real Estate': {'pe': 28, 'ev_ebitda': 20},
    'Default': {'pe': 22, 'ev_ebitda': 14}
}

# Smallcap specific benchmarks (higher growth expectations)
SMALLCAP_BENCHMARKS = {
    'Technology': {'pe': 30, 'ev_ebitda': 18},
    'Financial Services': {'pe': 18, 'ev_ebitda': 12},
    'Consumer Cyclical': {'pe': 35, 'ev_ebitda': 18},
    'Consumer Defensive': {'pe': 40, 'ev_ebitda': 20},
    'Healthcare': {'pe': 32, 'ev_ebitda': 18},
    'Industrials': {'pe': 28, 'ev_ebitda': 16},
    'Energy': {'pe': 20, 'ev_ebitda': 12},
    'Basic Materials': {'pe': 22, 'ev_ebitda': 14},
    'Real Estate': {'pe': 30, 'ev_ebitda': 22},
    'Default': {'pe': 24, 'ev_ebitda': 16}
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_stocks():
    """Returns a flat dictionary of all stocks with their names"""
    all_stocks = {}
    for category, stocks in INDIAN_STOCKS.items():
        all_stocks.update(stocks)
    return all_stocks

def get_stock_count():
    """Returns total count of unique stocks"""
    return len(get_all_stocks())

def get_categories():
    """Returns list of all categories"""
    return list(INDIAN_STOCKS.keys())

def search_stock(query):
    """Search for stocks by ticker or name"""
    query = query.upper()
    results = {}
    for category, stocks in INDIAN_STOCKS.items():
        for ticker, name in stocks.items():
            if query in ticker.upper() or query in name.upper():
                results[ticker] = {'name': name, 'category': category}
    return results

def get_stocks_by_category(category_keyword):
    """Get stocks from categories matching keyword"""
    results = {}
    for category, stocks in INDIAN_STOCKS.items():
        if category_keyword.lower() in category.lower():
            results[category] = stocks
    return results

def get_benchmark(sector, cap_type='large'):
    """Get benchmark PE and EV/EBITDA for a sector"""
    if cap_type == 'midcap':
        benchmarks = MIDCAP_BENCHMARKS
    elif cap_type == 'smallcap':
        benchmarks = SMALLCAP_BENCHMARKS
    else:
        benchmarks = INDUSTRY_BENCHMARKS
    
    return benchmarks.get(sector, benchmarks.get('Default'))

# ============================================================================
# QUICK STATS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("INDIAN STOCKS DATABASE - SUMMARY")
    print("=" * 60)
    print(f"Total Categories: {len(get_categories())}")
    print(f"Total Unique Stocks: {get_stock_count()}")
    print("-" * 60)
    print("\nCategories:")
    for cat in get_categories():
        count = len(INDIAN_STOCKS[cat])
        print(f"  {cat}: {count} stocks")
    print("=" * 60)
# ============================================================================
# UTILITY FUNCTIONS
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
                    time.sleep(backoff_in_seconds * 2 ** x)
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
            return None, "Rate limit reached"
        return None, str(e)[:100]

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
        book_value = info.get('bookValue', 0)
        revenue = info.get('totalRevenue', 0)
        
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        
        # PE-based valuation
        historical_pe = trailing_pe * 0.9 if trailing_pe and trailing_pe > 0 else industry_pe
        blended_pe = (industry_pe + historical_pe) / 2
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
        # EV/EBITDA-based valuation
        current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
        target_ev_ebitda = (industry_ev_ebitda + current_ev_ebitda * 0.9) / 2 if current_ev_ebitda and 0 < current_ev_ebitda < 50 else industry_ev_ebitda
        
        if ebitda and ebitda > 0:
            fair_ev = ebitda * target_ev_ebitda
            net_debt = (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0)
            fair_mcap = fair_ev - net_debt
            fair_value_ev = fair_mcap / shares if shares else None
            upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
        else:
            fair_value_ev = None
            upside_ev = None
        
        # Price to Book valuation
        pb_ratio = price / book_value if book_value and book_value > 0 else None
        
        # Price to Sales
        ps_ratio = market_cap / revenue if revenue and revenue > 0 else None
        
        return {
            'price': price, 'trailing_pe': trailing_pe, 'forward_pe': forward_pe,
            'trailing_eps': trailing_eps, 'industry_pe': industry_pe,
            'fair_value_pe': fair_value_pe, 'upside_pe': upside_pe,
            'enterprise_value': enterprise_value, 'ebitda': ebitda,
            'market_cap': market_cap, 'current_ev_ebitda': current_ev_ebitda,
            'industry_ev_ebitda': industry_ev_ebitda,
            'fair_value_ev': fair_value_ev, 'upside_ev': upside_ev,
            'pb_ratio': pb_ratio, 'ps_ratio': ps_ratio,
            'book_value': book_value, 'revenue': revenue,
            'net_debt': (info.get('totalDebt', 0) or 0) - (info.get('totalCash', 0) or 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'roe': info.get('returnOnEquity', 0),
            'profit_margin': info.get('profitMargins', 0),
            '52w_high': info.get('fiftyTwoWeekHigh', 0),
            '52w_low': info.get('fiftyTwoWeekLow', 0),
        }
    except:
        return None

# ============================================================================
# PROFESSIONAL CHART FUNCTIONS
# ============================================================================
def create_gauge_chart(upside_pe, upside_ev):
    """Create professional dual gauge chart for valuations"""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        horizontal_spacing=0.15
    )
    
    # PE Multiple Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_pe if upside_pe else 0,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#1e293b', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
        title={'text': "PE Multiple", 'font': {'size': 18, 'color': '#64748b', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b"},
            'bar': {'color': "#7c3aed", 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [-50, -20], 'color': '#fee2e2'},
                {'range': [-20, 0], 'color': '#fef3c7'},
                {'range': [0, 20], 'color': '#d1fae5'},
                {'range': [20, 50], 'color': '#a7f3d0'}
            ],
            'threshold': {
                'line': {'color': "#1e293b", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=1)
    
    # EV/EBITDA Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_ev if upside_ev else 0,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#1e293b', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#ef4444"}},
        title={'text': "EV/EBITDA", 'font': {'size': 18, 'color': '#64748b', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b"},
            'bar': {'color': "#ec4899", 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [-50, -20], 'color': '#fee2e2'},
                {'range': [-20, 0], 'color': '#fef3c7'},
                {'range': [0, 20], 'color': '#d1fae5'},
                {'range': [20, 50], 'color': '#a7f3d0'}
            ],
            'threshold': {
                'line': {'color': "#1e293b", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=350,
        margin=dict(l=30, r=30, t=60, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter'}
    )
    return fig

def create_valuation_comparison_chart(vals):
    """Create professional bar chart comparing current vs fair values"""
    categories = []
    current_vals = []
    fair_vals = []
    
    if vals['fair_value_pe']:
        categories.append('PE Multiple')
        current_vals.append(vals['price'])
        fair_vals.append(vals['fair_value_pe'])
    
    if vals['fair_value_ev']:
        categories.append('EV/EBITDA')
        current_vals.append(vals['price'])
        fair_vals.append(vals['fair_value_ev'])
    
    if not categories:
        return None
    
    fig = go.Figure()
    
    # Current Price bars
    fig.add_trace(go.Bar(
        name='Current Price',
        x=categories,
        y=current_vals,
        marker=dict(
            color='#3b82f6',
            line=dict(color='#1d4ed8', width=2),
            cornerradius=8
        ),
        text=[f'₹{v:,.2f}' for v in current_vals],
        textposition='outside',
        textfont=dict(size=14, color='#1e293b', family='JetBrains Mono')
    ))
    
    # Fair Value bars
    colors = ['#10b981' if fv > cv else '#ef4444' for fv, cv in zip(fair_vals, current_vals)]
    fig.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair_vals,
        marker=dict(
            color=colors,
            line=dict(color=['#059669' if c == '#10b981' else '#dc2626' for c in colors], width=2),
            cornerradius=8
        ),
        text=[f'₹{v:,.2f}' for v in fair_vals],
        textposition='outside',
        textfont=dict(size=14, color='#1e293b', family='JetBrains Mono')
    ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=14)
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#e2e8f0',
            tickfont=dict(size=14, color='#1e293b')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f1f5f9',
            showline=False,
            tickprefix='₹',
            tickfont=dict(size=12, color='#64748b')
        ),
        margin=dict(l=60, r=40, t=60, b=40)
    )
    
    return fig

def create_52week_range_chart(vals):
    """Create 52-week price range indicator"""
    low = vals['52w_low']
    high = vals['52w_high']
    current = vals['price']
    
    if not all([low, high, current]) or high <= low:
        return None
    
    position = (current - low) / (high - low) * 100
    
    fig = go.Figure()
    
    # Background range bar
    fig.add_trace(go.Bar(
        x=[100],
        y=['52W Range'],
        orientation='h',
        marker=dict(
            color='#f1f5f9',
            line=dict(color='#e2e8f0', width=1)
        ),
        showlegend=False,
        hoverinfo='none'
    ))
    
    # Position indicator
    fig.add_trace(go.Bar(
        x=[position],
        y=['52W Range'],
        orientation='h',
        marker=dict(
            color='linear-gradient(90deg, #10b981, #3b82f6, #ef4444)',
        ),
        showlegend=False,
        hoverinfo='none'
    ))
    
    # Add annotations
    fig.add_annotation(x=0, y='52W Range', text=f"₹{low:,.0f}", showarrow=False, xanchor='right', xshift=-10, font=dict(size=12, color='#10b981'))
    fig.add_annotation(x=100, y='52W Range', text=f"₹{high:,.0f}", showarrow=False, xanchor='left', xshift=10, font=dict(size=12, color='#ef4444'))
    fig.add_annotation(x=position, y='52W Range', text=f"₹{current:,.0f}", showarrow=True, ay=-30, font=dict(size=14, color='#7c3aed', weight='bold'))
    
    fig.update_layout(
        height=120,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=80, r=80, t=30, b=20),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-5, 105]),
        yaxis=dict(showticklabels=False, showgrid=False),
        barmode='overlay'
    )
    
    return fig

def create_radar_chart(vals):
    """Create radar chart for key metrics comparison"""
    categories = ['PE Ratio', 'EV/EBITDA', 'P/B Ratio', 'Profit Margin', 'ROE']
    
    # Normalize values (0-100 scale)
    pe_score = max(0, min(100, 100 - (vals['trailing_pe'] / vals['industry_pe'] * 50))) if vals['trailing_pe'] and vals['industry_pe'] else 50
    ev_score = max(0, min(100, 100 - (vals['current_ev_ebitda'] / vals['industry_ev_ebitda'] * 50))) if vals['current_ev_ebitda'] and vals['industry_ev_ebitda'] else 50
    pb_score = max(0, min(100, 100 - (vals['pb_ratio'] * 20))) if vals['pb_ratio'] else 50
    margin_score = vals['profit_margin'] * 500 if vals['profit_margin'] else 50
    roe_score = vals['roe'] * 300 if vals['roe'] else 50
    
    values = [pe_score, ev_score, pb_score, margin_score, roe_score]
    values = [max(0, min(100, v)) for v in values]  # Clamp values
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(124, 58, 237, 0.2)',
        line=dict(color='#7c3aed', width=2),
        marker=dict(size=8, color='#7c3aed')
    ))
    
    # Add benchmark line
    fig.add_trace(go.Scatterpolar(
        r=[50, 50, 50, 50, 50, 50],
        theta=categories + [categories[0]],
        fill='none',
        line=dict(color='#94a3b8', width=1, dash='dash'),
        name='Benchmark'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                gridcolor='#e2e8f0'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#64748b')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        height=350,
        margin=dict(l=60, r=60, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# ============================================================================
# PDF REPORT GENERATION
# ============================================================================
def create_pdf_report(company, ticker, sector, vals):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title', 
        parent=styles['Heading1'], 
        fontSize=28, 
        textColor=colors.HexColor('#7c3aed'), 
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    story = []
    story.append(Paragraph("NYZTrade Pro", title_style))
    story.append(Paragraph("Professional Valuation Report", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Company Info
    story.append(Paragraph(f"<b>{company}</b>", styles['Heading2']))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", styles['Normal']))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Calculate averages
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    # Fair Value Summary
    fair_data = [
        ['Metric', 'Value'],
        ['Fair Value', f"₹ {avg_fair:,.2f}"],
        ['Current Price', f"₹ {vals['price']:,.2f}"],
        ['Potential Upside', f"{avg_up:+.2f}%"]
    ]
    fair_table = Table(fair_data, colWidths=[3*inch, 2.5*inch])
    fair_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(fair_table)
    story.append(Spacer(1, 25))
    
    # Detailed Metrics
    story.append(Paragraph("<b>Valuation Metrics</b>", styles['Heading3']))
    metrics_data = [
        ['Metric', 'Current', 'Industry Benchmark'],
        ['PE Ratio', f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A', f"{vals['industry_pe']:.2f}x"],
        ['EV/EBITDA', f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else 'N/A', f"{vals['industry_ev_ebitda']:.2f}x"],
        ['P/B Ratio', f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else 'N/A', '-'],
        ['EPS', f"₹ {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A', '-'],
        ['Market Cap', f"₹ {vals['market_cap']/10000000:,.0f} Cr", '-'],
    ]
    metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 30))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        spaceBefore=20
    )
    story.append(Paragraph(
        "<b>DISCLAIMER:</b> This report is for educational purposes only and does not constitute financial advice. "
        "Always consult a qualified financial advisor before making investment decisions. Past performance is not "
        "indicative of future results.",
        disclaimer_style
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Header
st.markdown('''
<div class="main-header">
    <h1>STOCK VALUATION PRO</h1>
    <p>📊 1,143+ Stocks | Professional Multi-Factor Analysis | Real-Time Data</p>
</div>
''', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔐 Account")
    st.markdown(f"**User:** {st.session_state.get('authenticated_user', 'Guest').title()}")
    
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📈 Stock Selection")
    
    # Aggregate all stocks
    all_stocks = {}
    for cat, stocks in INDIAN_STOCKS.items():
        all_stocks.update(stocks)
    
    st.markdown(f'''
    <div class="stock-count">
        📊 {len(all_stocks):,} Stocks Available
    </div>
    ''', unsafe_allow_html=True)
    
    # Category selection
    category = st.selectbox(
        "🏷️ Category",
        ["📋 All Stocks"] + list(INDIAN_STOCKS.keys()),
        help="Filter stocks by category"
    )
    
    # Search
    search = st.text_input(
        "🔍 Search",
        placeholder="Company name or ticker...",
        help="Search by company name or ticker symbol"
    )
    
    # Filter stocks
    if search:
        search_upper = search.upper()
        filtered = {t: n for t, n in all_stocks.items() 
                   if search_upper in t.upper() or search_upper in n.upper()}
    elif category == "📋 All Stocks":
        filtered = all_stocks
    else:
        filtered = INDIAN_STOCKS.get(category, {})
    
    # Stock selection
    if filtered:
        options = sorted([f"{n} ({t})" for t, n in filtered.items()])
        selected = st.selectbox(
            "🎯 Select Stock",
            options,
            help="Choose a stock to analyze"
        )
        ticker = selected.split("(")[1].strip(")")
    else:
        ticker = None
        st.warning("⚠️ No stocks found matching your criteria")
    
    # Custom ticker
    st.markdown("---")
    custom = st.text_input(
        "✏️ Custom Ticker",
        placeholder="e.g., TATAMOTORS.NS",
        help="Enter any NSE/BSE ticker manually"
    )
    
    # Analyze button
    st.markdown("---")
    analyze_clicked = st.button("🚀 ANALYZE STOCK", use_container_width=True, type="primary")

# Main content
if analyze_clicked:
    st.session_state.analyze = custom.upper() if custom else ticker

if 'analyze' in st.session_state and st.session_state.analyze:
    t = st.session_state.analyze
    
    # Fetch data with progress
    with st.spinner(f"🔄 Fetching data for {t}..."):
        info, error = fetch_stock_data(t)
    
    if error or not info:
        st.error(f"❌ Error: {error if error else 'Failed to fetch stock data'}")
        st.markdown('''
        <div class="warning-box">
            <strong>Troubleshooting Tips:</strong><br>
            • Verify the ticker symbol is correct (e.g., RELIANCE.NS for NSE)<br>
            • Check your internet connection<br>
            • Try again in a few moments (API rate limits may apply)
        </div>
        ''', unsafe_allow_html=True)
        st.stop()
    
    vals = calculate_valuations(info)
    if not vals:
        st.error("❌ Unable to calculate valuations for this stock")
        st.stop()
    
    # Extract company info
    company = info.get('longName', t)
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    
    # Company Header
    st.markdown(f'''
    <div class="company-header">
        <h2 class="company-name">{company}</h2>
        <div class="company-meta">
            <span class="meta-badge">🏷️ {t}</span>
            <span class="meta-badge">🏢 {sector}</span>
            <span class="meta-badge">🏭 {industry}</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Calculate average values
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    # Main metrics row
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Fair Value Card
        st.markdown(f'''
        <div class="fair-value-card">
            <div class="fair-value-label">📊 Calculated Fair Value</div>
            <div class="fair-value-amount">₹{avg_fair:,.2f}</div>
            <div class="current-price">Current Price: ₹{vals["price"]:,.2f}</div>
            <div class="upside-badge">{"📈" if avg_up > 0 else "📉"} {avg_up:+.2f}% Potential</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        # Recommendation
        if avg_up > 25:
            rec_class, rec_text, rec_icon = "rec-strong-buy", "STRONG BUY", "🚀"
        elif avg_up > 15:
            rec_class, rec_text, rec_icon = "rec-buy", "BUY", "✅"
        elif avg_up > 0:
            rec_class, rec_text, rec_icon = "rec-buy", "ACCUMULATE", "📥"
        elif avg_up > -10:
            rec_class, rec_text, rec_icon = "rec-hold", "HOLD", "⏸️"
        else:
            rec_class, rec_text, rec_icon = "rec-avoid", "AVOID", "⚠️"
        
        st.markdown(f'''
        <div class="rec-container">
            <div class="{rec_class}">
                {rec_icon} {rec_text}
                <div class="rec-subtitle">Expected Return: {avg_up:+.2f}%</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # PDF Download
        pdf = create_pdf_report(company, t, sector, vals)
        st.download_button(
            "📥 Download PDF Report",
            data=pdf,
            file_name=f"NYZTrade_{t}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Key Metrics Cards
    st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
    
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    
    with m1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">₹{vals['price']:,.2f}</div>
            <div class="metric-label">Current Price</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m2:
        pe_val = f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else "N/A"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-value">{pe_val}</div>
            <div class="metric-label">PE Ratio</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m3:
        eps_val = f"₹{vals['trailing_eps']:.2f}" if vals['trailing_eps'] else "N/A"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">💵</div>
            <div class="metric-value">{eps_val}</div>
            <div class="metric-label">EPS (TTM)</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m4:
        mcap_val = f"₹{vals['market_cap']/10000000:,.0f}Cr"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">🏦</div>
            <div class="metric-value">{mcap_val}</div>
            <div class="metric-label">Market Cap</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m5:
        ev_ebitda = f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else "N/A"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{ev_ebitda}</div>
            <div class="metric-label">EV/EBITDA</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with m6:
        pb_val = f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else "N/A"
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-icon">📚</div>
            <div class="metric-value">{pb_val}</div>
            <div class="metric-label">P/B Ratio</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Charts Section
    st.markdown("---")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown('<div class="section-header">🎯 Valuation Gauges</div>', unsafe_allow_html=True)
        if vals['upside_pe'] is not None or vals['upside_ev'] is not None:
            fig_gauge = create_gauge_chart(
                vals['upside_pe'] if vals['upside_pe'] else 0,
                vals['upside_ev'] if vals['upside_ev'] else 0
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.info("Insufficient data for gauge charts")
    
    with chart_col2:
        st.markdown('<div class="section-header">📊 Price vs Fair Value</div>', unsafe_allow_html=True)
        fig_bar = create_valuation_comparison_chart(vals)
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Insufficient data for comparison chart")
    
    # Additional Charts Row
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown('<div class="section-header">📍 52-Week Range</div>', unsafe_allow_html=True)
        fig_range = create_52week_range_chart(vals)
        if fig_range:
            st.plotly_chart(fig_range, use_container_width=True)
        else:
            st.info("52-week data not available")
    
    with chart_col4:
        st.markdown('<div class="section-header">🎯 Metrics Radar</div>', unsafe_allow_html=True)
        fig_radar = create_radar_chart(vals)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Detailed Valuation Methods
    st.markdown("---")
    st.markdown('<div class="section-header">📋 Valuation Breakdown</div>', unsafe_allow_html=True)
    
    val_col1, val_col2 = st.columns(2)
    
    with val_col1:
        st.markdown(f'''
        <div class="valuation-method">
            <div class="method-title">📈 PE Multiple Method</div>
            <div class="method-row">
                <span class="method-label">Current PE</span>
                <span class="method-value">{vals['trailing_pe']:.2f}x</span>
            </div>
            <div class="method-row">
                <span class="method-label">Industry PE</span>
                <span class="method-value">{vals['industry_pe']:.2f}x</span>
            </div>
            <div class="method-row">
                <span class="method-label">EPS (TTM)</span>
                <span class="method-value">₹{vals['trailing_eps']:.2f}</span>
            </div>
            <div class="method-row">
                <span class="method-label">Fair Value (PE)</span>
                <span class="method-value" style="color: {'#10b981' if vals['fair_value_pe'] and vals['fair_value_pe'] > vals['price'] else '#ef4444'}">
                    ₹{vals['fair_value_pe']:,.2f}
                </span>
            </div>
            <div class="method-row">
                <span class="method-label">Upside (PE)</span>
                <span class="method-value" style="color: {'#10b981' if vals['upside_pe'] and vals['upside_pe'] > 0 else '#ef4444'}">
                    {vals['upside_pe']:+.2f}%
                </span>
            </div>
        </div>
        ''', unsafe_allow_html=True) if vals['fair_value_pe'] else st.info("PE valuation not available")
    
    with val_col2:
        if vals['fair_value_ev']:
            st.markdown(f'''
            <div class="valuation-method">
                <div class="method-title">💼 EV/EBITDA Method</div>
                <div class="method-row">
                    <span class="method-label">Current EV/EBITDA</span>
                    <span class="method-value">{vals['current_ev_ebitda']:.2f}x</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Industry EV/EBITDA</span>
                    <span class="method-value">{vals['industry_ev_ebitda']:.2f}x</span>
                </div>
                <div class="method-row">
                    <span class="method-label">EBITDA</span>
                    <span class="method-value">₹{vals['ebitda']/10000000:,.0f} Cr</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Fair Value (EV)</span>
                    <span class="method-value" style="color: {'#10b981' if vals['fair_value_ev'] > vals['price'] else '#ef4444'}">
                        ₹{vals['fair_value_ev']:,.2f}
                    </span>
                </div>
                <div class="method-row">
                    <span class="method-label">Upside (EV)</span>
                    <span class="method-value" style="color: {'#10b981' if vals['upside_ev'] and vals['upside_ev'] > 0 else '#ef4444'}">
                        {vals['upside_ev']:+.2f}%
                    </span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.info("EV/EBITDA valuation not available")
    
    # Financial Data Table
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Complete Financial Summary</div>', unsafe_allow_html=True)
    
    financial_data = pd.DataFrame({
        'Metric': [
            'Current Price', 'Market Cap', 'Enterprise Value', 
            'PE Ratio (TTM)', 'Forward PE', 'EV/EBITDA',
            'P/B Ratio', 'P/S Ratio', 'EPS (TTM)',
            'EBITDA', 'Book Value', 'Net Debt',
            '52W High', '52W Low', 'Beta',
            'Dividend Yield', 'ROE', 'Profit Margin'
        ],
        'Value': [
            f"₹{vals['price']:,.2f}",
            f"₹{vals['market_cap']/10000000:,.0f} Cr",
            f"₹{vals['enterprise_value']/10000000:,.0f} Cr" if vals['enterprise_value'] else 'N/A',
            f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A',
            f"{vals['forward_pe']:.2f}x" if vals['forward_pe'] else 'N/A',
            f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else 'N/A',
            f"{vals['pb_ratio']:.2f}x" if vals['pb_ratio'] else 'N/A',
            f"{vals['ps_ratio']:.2f}x" if vals['ps_ratio'] else 'N/A',
            f"₹{vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A',
            f"₹{vals['ebitda']/10000000:,.0f} Cr" if vals['ebitda'] else 'N/A',
            f"₹{vals['book_value']:.2f}" if vals['book_value'] else 'N/A',
            f"₹{vals['net_debt']/10000000:,.0f} Cr",
            f"₹{vals['52w_high']:,.2f}" if vals['52w_high'] else 'N/A',
            f"₹{vals['52w_low']:,.2f}" if vals['52w_low'] else 'N/A',
            f"{vals['beta']:.2f}" if vals['beta'] else 'N/A',
            f"{vals['dividend_yield']*100:.2f}%" if vals['dividend_yield'] else 'N/A',
            f"{vals['roe']*100:.2f}%" if vals['roe'] else 'N/A',
            f"{vals['profit_margin']*100:.2f}%" if vals['profit_margin'] else 'N/A'
        ]
    })
    
    st.dataframe(
        financial_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric": st.column_config.TextColumn("📊 Metric", width="medium"),
            "Value": st.column_config.TextColumn("📈 Value", width="medium")
        }
    )

else:
    # Welcome screen
    st.markdown('''
    <div class="info-box">
        <h3>👋 Welcome to NYZTrade Pro Valuation</h3>
        <p>Select a stock from the sidebar and click <strong>ANALYZE STOCK</strong> to get started.</p>
        <br>
        <strong>Features:</strong>
        <ul>
            <li>📊 Multi-factor valuation (PE, EV/EBITDA, P/B)</li>
            <li>📈 Professional charts and visualizations</li>
            <li>📥 Downloadable PDF reports</li>
            <li>🎯 Buy/Sell recommendations</li>
            <li>📋 Complete financial metrics</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)

# Footer
st.markdown('''
<div class="footer">
    <p><strong>NYZTrade Pro</strong> | Professional Stock Valuation Platform</p>
    <p style="font-size: 0.8rem; color: #94a3b8;">
        ⚠️ Disclaimer: This tool is for educational purposes only. 
        Always consult a qualified financial advisor before making investment decisions.
    </p>
</div>
''', unsafe_allow_html=True)
