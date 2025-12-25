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
# PROFESSIONAL CSS STYLING - DARK/LIGHT MODE COMPATIBLE
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
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
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
    color: #e2e8f0;
}

/* Company Header Card - FIXED FOR DARK/LIGHT MODE */
.company-header {
    background: linear-gradient(135deg, #7c3aed 0%, #6366f1 50%, #8b5cf6 100%);
    border: none;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 40px rgba(124, 58, 237, 0.3);
}

.company-name {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff !important;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.company-meta {
    display: flex;
    gap: 1rem;
    margin-top: 0.8rem;
    flex-wrap: wrap;
}

.meta-badge {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.9rem;
    color: #ffffff !important;
    font-weight: 500;
    border: 1px solid rgba(255,255,255,0.3);
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
    color: #ffffff;
}

.fair-value-amount {
    font-size: 3rem;
    font-weight: 700;
    margin: 0.5rem 0;
    font-family: 'JetBrains Mono', monospace;
    color: #ffffff;
}

.current-price {
    font-size: 1rem;
    opacity: 0.85;
    color: #ffffff;
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
    color: #ffffff;
}

/* Recommendation Boxes */
.rec-container {
    margin: 1.5rem 0;
}

.rec-strong-buy {
    background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
    color: white !important;
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
    color: white !important;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(20, 184, 166, 0.35);
}

.rec-hold {
    background: linear-gradient(135deg, #d97706 0%, #f59e0b 50%, #fbbf24 100%);
    color: white !important;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    box-shadow: 0 15px 35px rgba(245, 158, 11, 0.35);
}

.rec-avoid {
    background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f87171 100%);
    color: white !important;
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
    color: white !important;
}

/* Metric Cards - DARK/LIGHT MODE COMPATIBLE */
.metric-card {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border: none;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(99, 102, 241, 0.4);
}

.metric-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace;
}

.metric-label {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.85) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 0.3rem;
}

/* Section Headers - DARK/LIGHT MODE */
.section-header {
    font-size: 1.4rem;
    font-weight: 600;
    color: #a78bfa;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #7c3aed;
    display: inline-block;
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
    color: white !important;
    padding: 0.8rem 1.2rem;
    border-radius: 12px;
    text-align: center;
    margin: 1rem 0;
    font-weight: 600;
}

/* Valuation Method Cards - DARK/LIGHT MODE */
.valuation-method {
    background: linear-gradient(135deg, #312e81 0%, #3730a3 100%);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #a78bfa;
    box-shadow: 0 8px 25px rgba(55, 48, 163, 0.3);
}

.method-title {
    font-weight: 600;
    color: #ffffff !important;
    font-size: 1.1rem;
    margin-bottom: 1rem;
}

.method-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.method-label {
    color: rgba(255,255,255,0.7) !important;
}

.method-value {
    font-weight: 600;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem;
    color: #a78bfa;
    font-size: 0.9rem;
    margin-top: 3rem;
    border-top: 1px solid rgba(167, 139, 250, 0.3);
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
    animation: fadeIn 0.6s ease forwards;
}

/* Info Box - DARK MODE */
.info-box {
    background: linear-gradient(135deg, #312e81 0%, #3730a3 100%);
    border: 1px solid #6366f1;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    color: #ffffff !important;
    margin: 1rem 0;
}

.info-box h3 {
    color: #a78bfa !important;
    margin-bottom: 0.5rem;
}

.info-box p, .info-box li {
    color: rgba(255,255,255,0.9) !important;
}

/* Warning Box */
.warning-box {
    background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
    border: 1px solid #f59e0b;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #fef3c7 !important;
    margin: 1rem 0;
}

/* 52 Week Range Card */
.range-card {
    background: linear-gradient(135deg, #312e81 0%, #3730a3 100%);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(55, 48, 163, 0.3);
}

.range-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.range-low {
    color: #34d399;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.range-high {
    color: #f87171;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.range-bar-container {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    height: 20px;
    position: relative;
    overflow: hidden;
}

.range-bar-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #34d399, #fbbf24, #f87171);
}

.range-current {
    text-align: center;
    margin-top: 1rem;
    color: #ffffff;
    font-size: 1.2rem;
    font-weight: 600;
}

.range-current span {
    color: #a78bfa;
    font-family: 'JetBrains Mono', monospace;
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
        users = {"demo": "value", "premium": "1nV3st!ng", "niyas": "buffet"}
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
    "Advertising Agencies": {
        "PRESSMN.NS": "Pressman Advertising Limited"
    },

    "Aerospace/Defense - Major Diversified": {
        "ABGSHIP.NS": "ABG Shipyard Limited",
        "BEL.NS": "Bharat Electronics Limited",
        "BHARATIDIL.NS": "Bharati Defence And Infrastructure Limited",
        "RDEL.NS": "Reliance Defence and Engineering Limited"
    },

    "Agricultural Chemicals": {
        "AGRITECH.NS": "Agri-Tech (India) Ltd",
        "ARIES.NS": "Aries Agro Limited",
        "BAYERCROP.NS": "Bayer CropScience Limited",
        "BHARATRAS.NS": "Bharat Rasayan Limited",
        "CHAMBLFERT.NS": "Chambal Fertilisers and Chemicals Limited",
        "COROMANDEL.NS": "Coromandel International Limited",
        "DEEPAKFERT.NS": "Deepak Fertilisers And Petrochemicals Corporation Limited",
        "DHANUKA.NS": "Dhanuka Agritech Limited",
        "EXCELCROP.NS": "Excel Crop Care Limited",
        "FACT.NS": "The Fertilisers And Chemicals Travancore Limited",
        "GNFC.NS": "Gujarat Narmada Valley Fertilizers & Chemicals Limited",
        "GREENFIRE.NS": "Proseed India Limited",
        "GSFC.NS": "Gujarat State Fertilizers & Chemicals Limited",
        "INSECTICID.NS": "Insecticides (India) Limited",
        "MADRASFERT.NS": "Madras Fertilizers Limited",
        "MANGCHEFER.NS": "Mangalore Chemicals & Fertilizers Limited",
        "MEGH.NS": "Meghmani Organics Limited",
        "MONSANTO.NS": "Monsanto India Limited",
        "NATHBIOGEN.NS": "Nath Bio-Genes (India) Limited",
        "NFL.NS": "National Fertilizers Limited",
        "PIIND.NS": "PI Industries Limited",
        "RALLIS.NS": "Rallis India Limited",
        "RCF.NS": "Rashtriya Chemicals And Fertilizers Limited",
        "SHARDACROP.NS": "Sharda Cropchem Limited",
        "SPIC.NS": "Southern Petrochemical Industries Corporation Limited",
        "UPL.NS": "UPL Limited",
        "ZUARI.NS": "Zuari Agro Chemicals Limited",
        "ZUARIGLOB.NS": "Zuari Global Limited"
    },

    "Air Delivery & Freight Services": {
        "ALLCARGO.NS": "Allcargo Logistics Limited",
        "ARSHIYA.NS": "Arshiya Limited",
        "BLUEDART.NS": "Blue Dart Express Limited",
        "CONCOR.NS": "Container Corporation of India Limited",
        "GATI.NS": "Gati Limited",
        "GDL.NS": "Gateway Distriparks Limited",
        "NAVKARCORP.NS": "Navkar Corporation Limited",
        "PATINTLOG.NS": "Patel Integrated Logistics Limited",
        "SICAL.NS": "Sical Logistics Limited",
        "SNOWMAN.NS": "Snowman Logistics Limited",
        "TCI.NS": "Transport Corporation of India Limited"
    },

    "Air Services, Other": {
        "GLOBALVECT.NS": "Global Vectra Helicorp Limited",
        "GVKPIL.NS": "GVK Power & Infrastructure Limited"
    },

    "Aluminum": {
        "CENTEXT.NS": "Century Extrusions Limited",
        "HINDALCO.NS": "Hindalco Industries Limited",
        "MAANALU.NS": "Maan Aluminium Limited",
        "NATIONALUM.NS": "National Aluminium Company Limited",
        "MANAKALUCO.NS": "Manaksia Aluminium Limited"
    },

    "Apparel Stores": {
        "FLFL.NS": "Future Lifestyle Fashions Limited",
        "TRENT.NS": "Trent Limited"
    },

    "Asset Management": {
        "ATNINTER.NS": "ATN International Ltd.",
        "BAJAJHLDNG.NS": "Bajaj Holdings & Investment Limited",
        "BFINVEST.NS": "BF Investment Limited",
        "BINDALAGRO.NS": "Oswal Greentech Limited",
        "CREST.NS": "Crest Ventures Limited",
        "INDBANK.NS": "Indbank Merchant Banking Services Limited",
        "IVC.NS": "IL&FS Investment Managers Limited",
        "JPOLYINVST.NS": "Jindal Poly Investment and Finance Company Limited",
        "JSWHL.NS": "JSW Holdings Limited",
        "KICL.NS": "Kalyani Investment Company Limited",
        "KIRLOSIND.NS": "Kirloskar Industries Limited",
        "LFIC.NS": "Lakshmi Finance & Industrial Corporation Limited",
        "MCX.NS": "Multi Commodity Exchange of India Limited",
        "MOTILALOFS.NS": "Motilal Oswal Financial Services Limited",
        "NAHARCAP.NS": "Nahar Capital and Financial Services Limited",
        "NSIL.NS": "Nalwa Sons Investments Limited",
        "PILANIINVS.NS": "Pilani Investment and Industries Corporation Limited",
        "PNBGILTS.NS": "PNB Gilts Ltd.",
        "RELCAPITAL.NS": "Reliance Capital Limited",
        "SILINV.NS": "SIL Investments Ltd.",
        "TIMESGTY.NS": "Times Guaranty Ltd.",
        "WILLAMAGOR.NS": "Williamson Magor & Co. Limited",
        "DHUNINV.NS": "Dhunseri Investments Limited"
    },

    "Auto Manufacturers - Major": {
        "ASHOKLEY.NS": "Ashok Leyland Limited",
        "ATULAUTO.NS": "Atul Auto Limited",
        "BAJAJ-AUTO.NS": "Bajaj Auto Limited",
        "EICHERMOT.NS": "Eicher Motors Limited",
        "HEROMOTOCO.NS": "Hero MotoCorp Limited",
        "HINDMOTORS.NS": "Hindustan Motors Limited",
        "LML.NS": "LML Limited",
        "M&M.NS": "Mahindra & Mahindra Limited",
        "MARUTI.NS": "Maruti Suzuki India Limited",
        "SMLISUZU.NS": "SML Isuzu Limited",
        "TATAMOTORS.NS": "Tata Motors Limited",
        "TATAMTRDVR.NS": "Tata Motors Limited DVR",
        "TVSMOTOR.NS": "TVS Motor Company Limited"
    },

    "Auto Parts": {
        "AMTEKAUTO.NS": "Amtek Auto Limited",
        "ANGIND.NS": "ANG Industries Limited",
        "ASAHIINDIA.NS": "Asahi India Glass Limited",
        "ASAL.NS": "Automotive Stampings and Assemblies Limited",
        "AUTOAXLES.NS": "Automotive Axles Limited",
        "AUTOIND.NS": "Autoline Industries Limited",
        "AUTOLITIND.NS": "Autolite (India) Limited",
        "BANCOINDIA.NS": "Banco Products (India) Limited",
        "BHARATFORG.NS": "Bharat Forge Limited",
        "BHARATGEAR.NS": "Bharat Gears Limited",
        "BOSCHLTD.NS": "Bosch Limited",
        "CASTEXTECH.NS": "Castex Technologies Limited",
        "DYNAMATECH.NS": "Dynamatic Technologies Limited",
        "EXIDEIND.NS": "Exide Industries Limited",
        "FIEMIND.NS": "Fiem Industries Limited",
        "FMGOETZE.NS": "Federal-Mogul Goetze (India) Limited",
        "GABRIEL.NS": "Gabriel India Limited",
        "HARITASEAT.NS": "Harita Seating Systems Limited",
        "HINDCOMPOS.NS": "Hindustan Composites Limited",
        "HINDUJAFO.NS": "Hinduja Foundries Limited",
        "HITECHGEAR.NS": "The Hi-Tech Gears Limited",
        "IGARASHI.NS": "Igarashi Motors India Limited",
        "IMPAL.NS": "India Motor Parts and Accessories Limited",
        "INDNIPPON.NS": "India Nippon Electricals Limited",
        "JAMNAAUTO.NS": "Jamna Auto Industries Limited",
        "JAYBARMARU.NS": "Jay Bharat Maruti Limited",
        "JBMA.NS": "JBM Auto Limited",
        "JMA.NS": "Jullundur Motor Agency (Delhi) Limited",
        "JMTAUTOLTD.NS": "JMT Auto Limited",
        "KALYANIFRG.NS": "Kalyani Forge Limited",
        "LGBBROSLTD.NS": "L.G. Balakrishnan & Bros Limited",
        "LUMAXAUTO.NS": "Lumax Automotive Systems Limited",
        "LUMAXIND.NS": "Lumax Industries Limited",
        "LUMAXTECH.NS": "Lumax Auto Technologies Limited",
        "MAHSCOOTER.NS": "Maharashtra Scooters Limited",
        "MENONBE.NS": "Menon Bearings Limited",
        "MINDACORP.NS": "Minda Corporation Limited",
        "MOTHERSUMI.NS": "Motherson Sumi Systems Limited",
        "MUNJALAU.NS": "Munjal Auto Industries Limited",
        "MUNJALSHOW.NS": "Munjal Showa Limited",
        "NRBBEARING.NS": "NRB Bearings Limited",
        "OMAXAUTO.NS": "Omax Autos Limited",
        "PPAP.NS": "PPAP Automotive Limited",
        "PRECAM.NS": "Precision Camshafts Limited",
        "RANEENGINE.NS": "Rane Engine Valve Limited",
        "RANEHOLDIN.NS": "Rane Holdings Limited",
        "RBL.NS": "Rane Brake Lining Limited",
        "REMSONSIND.NS": "Remsons Industries Limited",
        "RICOAUTO.NS": "Rico Auto Industries Limited",
        "RML.NS": "Rane (Madras) Limited",
        "SHIVAMAUTO.NS": "Shivam Autotech Limited",
        "SONASTEER.NS": "Sona Koyo Steering Systems Limited",
        "SSWL.NS": "Steel Strips Wheels Limited",
        "SUBROS.NS": "Subros",
        "SUNCLAYLTD.NS": "Sundaram-Clayton Limited",
        "SUNDRMBRAK.NS": "Sundaram Brake Linings Limited",
        "SUNDRMFAST.NS": "Sundram Fasteners Limited",
        "SUPRAJIT.NS": "Suprajit Engineering Limited",
        "SWARAJENG.NS": "Swaraj Engines Limited",
        "TALBROAUTO.NS": "Talbros Automotive Components Limited",
        "TUBEINVEST.NS": "TI Financial Holdings Limited",
        "UCALFUEL.NS": "Ucal Fuel Systems Limited",
        "WABCOINDIA.NS": "Wabco India Limited",
        "WHEELS.NS": "Wheels India Limited",
        "FAGBEARING.NS": "Schaeffler India Limited",
        "MINDAIND.NS": "Minda Industries Limited",
        "CLUTCHAUTO.NS": "Clutch Auto Limited",
        "PRICOL.NS": "Pricol Limited"
    },

    "Beverages - Brewers": {
        "EDL.NS": "Empee Distilleries Limited",
        "SDBL.NS": "Som Distilleries & Breweries Limited",
        "UBHOLDINGS.NS": "United Breweries (Holdings) Limited",
        "UBL.NS": "United Breweries Limited"
    },

    "Beverages - Soft Drinks": {
        "MANPASAND.NS": "Manpasand Beverages Limited",
        "UNITEDTEA.NS": "The United Nilgiri Tea Estates Company Limited"
    },

    "Beverages - Wineries & Distillers": {
        "GLOBUSSPR.NS": "Globus Spirits Limited",
        "GMBREW.NS": "G.M.Breweries Limited",
        "IFBAGRO.NS": "IFB Agro Industries Limited",
        "PIONDIST.NS": "Pioneer Distilleries Limited",
        "RKDL.NS": "Ravi Kumar Distilleries Limited",
        "TI.NS": "Tilaknagar Industries Ltd.",
        "RADICO.NS": "Radico Khaitan Limited"
    },

    "Biotechnology": {
        "CELESTIAL.NS": "Celestial Biolabs Limited",
        "DISHMAN.NS": "Dishman Pharmaceuticals and Chemicals Limited",
        "LYKALABS.NS": "Lyka Labs Limited",
        "PANACEABIO.NS": "Panacea Biotec Limited",
        "SEQUENT.NS": "Sequent Scientific Limited",
        "STERLINBIO.NS": "Sterling Biotech Limited",
        "BIOCON.NS": "Biocon Limited",
        "SYNGENE.NS": "Syngene International Limited"
    },

    "Broadcasting - Radio": {
        "ENIL.NS": "Entertainment Network (India) Limited"
    },

    "Broadcasting - TV": {
        "DEN.NS": "DEN Networks Limited",
        "JAINSTUDIO.NS": "Jain Studios Limited",
        "NDTV.NS": "New Delhi Television Limited",
        "NETWORK18.NS": "Network18 Media & Investments Limited",
        "RAJTV.NS": "Raj Television Network Limited",
        "SABTN.NS": "Sri Adhikari Brothers Television Network Limited",
        "SUNTV.NS": "Sun TV Network Limited",
        "TV18BRDCST.NS": "TV18 Broadcast Limited",
        "TVTODAY.NS": "T.V. Today Network Limited",
        "ZEEL.NS": "Zee Entertainment Enterprises Limited",
        "ZEEMEDIA.NS": "Zee Media Corporation Limited"
    },

    "Business Equipment": {
        "KOKUYOCMLN.NS": "Kokuyo Camlin Limited",
        "TODAYS.NS": "Todays Writing Instruments Limited"
    },

    "Business Services": {
        "ALANKIT.NS": "Alankit Limited",
        "ALLSEC.NS": "Allsec Technologies Limited",
        "CURATECH.NS": "CURA Technologies Limited",
        "DATAMATICS.NS": "Datamatics Global Services Limited",
        "ECLERX.NS": "eClerx Services Limited",
        "FSL.NS": "Firstsource Solutions Limited",
        "GKWLIMITED.NS": "GKW Limited",
        "HEXATRADEX.NS": "Hexa Tradex Limited",
        "KTIL.NS": "Kesar Terminals & Infrastructure Limited",
        "NESCO.NS": "Nesco Limited",
        "REPRO.NS": "Repro India Limited"
    },

    "Business Software & Services": {
        "AGCNET.NS": "AGC Networks Limited",
        "AURIONPRO.NS": "aurionPro Solutions Limited",
        "KELLTONTEC.NS": "Kellton Tech Solutions Limited",
        "MELSTAR.NS": "Melstar Information Technologies Limited",
        "OFSS.NS": "Oracle Financial Services Software Limited",
        "PERSISTENT.NS": "Persistent Systems Limited",
        "POLARIS.NS": "Polaris Consulting & Services Limited",
        "CIGNITITEC.NS": "Cigniti Technologies Limited"
    },

    "CATV Systems": {
        "DISHTV.NS": "Dish TV India Limited",
        "HATHWAY.NS": "Hathway Cable & Datacom Limited",
        "HINDUJAVEN.NS": "Hinduja Ventures Limited",
        "ORTEL.NS": "Ortel Communications Limited",
        "SITICABLE.NS": "SITI Networks Limited"
    },

    "Chemicals - Major Diversified": {
        "ANDHRSUGAR.NS": "The Andhra Sugars Limited",
        "ASAHISONG.NS": "Asahi Songwon Colors Limited",
        "ASTEC.NS": "Astec LifeSciences Limited",
        "ATUL.NS": "Atul Ltd",
        "BASF.NS": "BASF India Limited",
        "BEPL.NS": "Bhansali Engineering Polymers Limited",
        "DCW.NS": "DCW Limited",
        "DICIND.NS": "DIC India Limited",
        "FOSECOIND.NS": "Foseco India Limited",
        "GHCL.NS": "GHCL Limited",
        "GUJALKALI.NS": "Gujarat Alkalies and Chemicals Limited",
        "GUJFLUORO.NS": "Gujarat Fluorochemicals Limited",
        "GULPOLY.NS": "Gulshan Polyols Limited",
        "HIKAL.NS": "Hikal Limited",
        "HOCL.NS": "Hindustan Organic Chemicals Limited",
        "INDIAGLYCO.NS": "India Glycols Limited",
        "JOCIL.NS": "Jocil Limited",
        "KANORICHEM.NS": "Kanoria Chemicals & Industries Limited",
        "KOTHARIPET.NS": "Kothari Petrochemicals Limited",
        "MANALIPETC.NS": "Manali Petrochemicals Limited",
        "NAVINFLUOR.NS": "Navin Fluorine International Limited",
        "NOCIL.NS": "NOCIL Limited",
        "PHILIPCARB.NS": "Phillips Carbon Black Limited",
        "PUNJABCHEM.NS": "Punjab Chemicals and Crop Protection Limited",
        "RAIN.NS": "Rain Industries Limited",
        "REFEX.NS": "Refex Industries Limited",
        "SHALPAINTS.NS": "Shalimar Paints Limited",
        "SHREEPUSHK.NS": "Shree Pushkar Chemicals & Fertilisers Limited",
        "SRHHYPOLTD.NS": "Sree Rayalaseema Hi-Strength Hypo Limited",
        "SUPPETRO.NS": "Supreme Petrochem Limited",
        "TATACHEM.NS": "Tata Chemicals Limited",
        "TNPETRO.NS": "Tamilnadu Petroproducts Limited",
        "VINATIORGA.NS": "Vinati Organics Limited",
        "DEEPAKNTR.NS": "Deepak Nitrite Limited"
    },

    "Communication Equipment": {
        "AKSHOPTFBR.NS": "Aksh Optifibre Limited",
        "ASTRAMICRO.NS": "Astra Microwave Products Limited",
        "DLINKINDIA.NS": "D-Link (India) Limited",
        "GEMINI.NS": "Gemini Communication Limited",
        "GTLINFRA.NS": "GTL Infrastructure Limited",
        "HFCL.NS": "Himachal Futuristic Communications Limited",
        "ITI.NS": "ITI Limited",
        "KAVVERITEL.NS": "Kavveri Telecom Products Limited",
        "MRO-TEK.NS": "MRO-TEK Realty Limited",
        "NELCO.NS": "Nelco Limited",
        "PARACABLES.NS": "Paramount Communications Limited",
        "SHYAMTEL.NS": "Shyam Telecom Limited",
        "SMARTLINK.NS": "Smartlink Network Systems Limited",
        "SPICEMOBI.NS": "Spice Mobility Limited",
        "STRTECH.NS": "Sterlite Technologies Limited",
        "TNTELE.NS": "Tamilnadu Telecommunications Limited",
        "VINDHYATEL.NS": "Vindhya Telelinks Limited"
    },

    "Computer Based Systems": {
        "CEREBRAINT.NS": "Cerebra Integrated Technologies Limited",
        "HCL-INSYS.NS": "HCL Infosystems Limited",
        "TVSELECT.NS": "TVS Electronics Limited"
    },

    "Confectioners": {
        "BAJAJHIND.NS": "Bajaj Hindusthan Sugar Limited",
        "BALRAMCHIN.NS": "Balrampur Chini Mills Limited",
        "BANARISUG.NS": "Bannari Amman Sugars Limited",
        "DALMIASUG.NS": "Dalmia Bharat Sugar and Industries Limited",
        "DWARKESH.NS": "Dwarikesh Sugar Industries Limited",
        "EIDPARRY.NS": "E.I.D.-Parry (India) Limited",
        "KCPSUGIND.NS": "K.C.P. Sugar and Industries Corporation Limited",
        "KHAITANLTD.NS": "Khaitan (India) Limited",
        "KMSUGAR.NS": "K M Sugar Mills Limited",
        "KOTARISUG.NS": "Kothari Sugars and Chemicals Limited",
        "MAWANASUG.NS": "Mawana Sugars Limited",
        "OUDHSUG.NS": "The Oudh Sugar Mills Limited",
        "PARRYSUGAR.NS": "Parrys Sugar Industries Limited",
        "PONNIERODE.NS": "Ponni Sugars (Erode) Limited",
        "RAJSREESUG.NS": "Rajshree Sugars and Chemicals Limited",
        "RANASUG.NS": "Rana Sugars Limited",
        "RENUKA.NS": "Shree Renuka Sugars Limited",
        "SAKHTISUG.NS": "Sakthi Sugars Limited",
        "SIMBHALS.NS": "Simbhaoli Sugars Limited",
        "SKMEGGPROD.NS": "SKM Egg Products Export (India) Limited",
        "THIRUSUGAR.NS": "Thiru Arooran Sugars Limited",
        "TRIVENI.NS": "Triveni Engineering & Industries Limited",
        "UGARSUGAR.NS": "The Ugar Sugar Works Limited",
        "UPERGANGES.NS": "Upper Ganges Sugar & Industries Limited",
        "DHARSUGAR.NS": "Dharani Sugars and Chemicals Limited",
        "DHAMPURSUG.NS": "Dhampur Sugar Mills Limited",
        "UTTAMSUGAR.NS": "Uttam Sugar Mills Limited",
        "SRICHAMUND.NS": "Chamundeswari Sugar Limited"
    },

    "Conglomerates": {
        "3MINDIA.NS": "3M India Limited",
        "ABIRLANUVO.NS": "Aditya Birla Nuvo Limited",
        "ALCHEM.NS": "Alchemist Limited",
        "BALMLAWRIE.NS": "Balmer Lawrie & Co. Limited",
        "DCMSHRIRAM.NS": "DCM Shriram Limited",
        "HOTELRUGBY.NS": "Hotel Rugby Limited",
        "MANAKSIA.NS": "Manaksia Limited",
        "SHK.NS": "S H Kelkar and Company Limited",
        "WELENT.NS": "Welspun Enterprises Limited",
        "GODREJIND.NS": "Godrej Industries Limited"
    },

    "Copper": {
        "CUBEXTUB.NS": "Cubex Tubings Limited",
        "HINDCOPPER.NS": "Hindustan Copper Limited",
        "PRECWIRE.NS": "Precision Wires India Ltd.",
        "NCOPPER.NS": "Nissan Copper Limited"
    },

    "Credit Services": {
        "BAJFINANCE.NS": "Bajaj Finance Limited",
        "CAPF.NS": "Capital First Limited",
        "CGCL.NS": "Capri Global Capital Limited",
        "CHOLAFIN.NS": "Cholamandalam Investment and Finance Company Limited",
        "GLFL.NS": "Gujarat Lease Financing Limited",
        "IDFC.NS": "IDFC Limited",
        "IFCI.NS": "IFCI Limited",
        "IITL.NS": "Industrial Investment Trust Limited",
        "L&TFH.NS": "L&T Finance Holdings Limited",
        "M&MFIN.NS": "Mahindra & Mahindra Financial Services Limited",
        "MAGMA.NS": "Magma Fincorp Limited",
        "MANAPPURAM.NS": "Manappuram Finance Limited",
        "MUTHOOTFIN.NS": "Muthoot Finance Limited",
        "PFC.NS": "Power Finance Corporation Limited",
        "RECLTD.NS": "Rural Electrification Corporation Limited",
        "SATIN.NS": "Satin Creditcare Network Limited",
        "SEINV.NS": "S.E. Investments Limited",
        "SHRIRAMCIT.NS": "Shriram City Union Finance Limited",
        "SRTRANSFIN.NS": "Shriram Transport Finance Company Limited",
        "SUNDARMFIN.NS": "Sundaram Finance Limited",
        "TCIFINANCE.NS": "TCI Finance Limited",
        "TFCILTD.NS": "Tourism Finance Corporation of India Limited",
        "VHL.NS": "Vardhman Holdings Limited",
        "MUTHOOTCAP.NS": "Muthoot Capital Services Limited",
        "SKSMICRO.NS": "Bharat Financial Inclusion Limited",
        "PFS.NS": "PTC India Financial Services Limited",
        "LAKSHMIFIN.NS": "Lakshmi Finance & Industrial Corporation Limited"
    },

    "Data Storage Devices": {
        "EUROMULTI.NS": "Euro Multivision Limited",
        "MOSERBAER.NS": "Moser Baer India Limited"
    },

    "Department Stores": {
        "SHOPERSTOP.NS": "Shoppers Stop Limited",
        "V2RETAIL.NS": "V2 Retail Limited",
        "VMART.NS": "V-Mart Retail Limited"
    },

    "Diversified Electronics": {
        "APARINDS.NS": "Apar Industries Limited",
        "BHAGYNAGAR.NS": "Bhagyanagar India Limited",
        "CENTUM.NS": "Centum Electronics Limited",
        "CORDSCABLE.NS": "Cords Cable Industries Limited",
        "DENORA.NS": "De Nora India Limited",
        "EVEREADY.NS": "Eveready Industries India Limited",
        "FINCABLES.NS": "Finolex Cables Limited",
        "GENUSPOWER.NS": "Genus Power Infrastructures Limited",
        "HBLPOWER.NS": "HBL Power Systems Limited",
        "HEG.NS": "HEG Limited",
        "HIRECT.NS": "Hind Rectifiers Limited",
        "INDOTECH.NS": "Indo Tech Transformers Limited",
        "KEI.NS": "KEI Industries Limited",
        "MIC.NS": "MIC Electronics Limited",
        "NIPPOBATRY.NS": "Indo National Limited",
        "SAMTEL.NS": "Samtel Color Limited",
        "VETO.NS": "Veto Switchgears and Cables Limited"
    },

    "Diversified Machinery": {
        "ABB.NS": "ABB India Limited",
        "ADORWELD.NS": "Ador Welding Limited",
        "AIAENG.NS": "AIA Engineering Limited",
        "AMARAJABAT.NS": "Amara Raja Batteries Limited",
        "BBL.NS": "Bharat Bijlee Limited",
        "BEML.NS": "BEML Limited",
        "BHEL.NS": "Bharat Heavy Electricals Limited",
        "BILPOWER.NS": "Bilpower Limited",
        "CUMMINSIND.NS": "Cummins India Limited",
        "DELTAMAGNT.NS": "Delta Magnets Limited",
        "DIAPOWER.NS": "Diamond Power Infrastructure Limited",
        "EASUNREYRL.NS": "Easun Reyrolle Limited",
        "ECEIND.NS": "ECE Industries Limited",
        "EIMCOELECO.NS": "Eimco Elecon (India) Limited",
        "EKC.NS": "Everest Kanto Cylinder Limited",
        "ELECON.NS": "Elecon Engineering Company Limited",
        "ELGIEQUIP.NS": "ELGI Equipments Limited",
        "EMCO.NS": "EMCO Limited",
        "EON.NS": "Eon Electric Limited",
        "GEINDSYS.NS": "GEI Industrial Systems Limited",
        "GOLDINFRA.NS": "Goldstone Infratech Limited",
        "GRAPHITE.NS": "Graphite India Limited",
        "GREAVESCOT.NS": "Greaves Cotton Limited",
        "HAVELLS.NS": "Havells India Limited",
        "HERCULES.NS": "Hercules Hoists Limited",
        "HONAUT.NS": "Honeywell Automation India Limited",
        "HONDAPOWER.NS": "Honda Siel Power Products Limited",
        "IFBIND.NS": "IFB Industries Limited",
        "INDLMETER.NS": "IMP Powers Limited",
        "INGERRAND.NS": "Ingersoll-Rand (India) Limited",
        "INOXWIND.NS": "Inox Wind Limited",
        "KABRAEXTRU.NS": "Kabra Extrusiontechnik Limited",
        "KCP.NS": "The KCP Limited",
        "KECL.NS": "Kirloskar Electric Company Limited",
        "KIRLOSBROS.NS": "Kirloskar Brothers Limited",
        "KIRLOSENG.NS": "Kirloskar Oil Engines Limited",
        "KSBPUMPS.NS": "KSB Pumps Limited",
        "LAXMIMACH.NS": "Lakshmi Machine Works Limited",
        "LOKESHMACH.NS": "Lokesh Machines Limited",
        "MANUGRAPH.NS": "Manugraph India Limited",
        "NEPCMICON.NS": "NEPC India Limited",
        "NICCO.NS": "Nicco Corporation Limited",
        "PAEL.NS": "PAE Limited",
        "PREMIER.NS": "Premier Limited",
        "SANGHVIFOR.NS": "Sanghvi Forging & Engineering Limited",
        "SCHNEIDER.NS": "Schneider Electric Infrastructure Limited",
        "SHAKTIPUMP.NS": "Shakti Pumps (India) Limited",
        "SHANTIGEAR.NS": "Shanthi Gears Limited",
        "SIEMENS.NS": "Siemens Limited",
        "SKFINDIA.NS": "SKF India Limited",
        "SUZLON.NS": "Suzlon Energy Limited",
        "TARAPUR.NS": "Tarapur Transformers Limited",
        "TDPOWERSYS.NS": "TD Power Systems Limited",
        "TEXRAIL.NS": "Texmaco Rail & Engineering Limited",
        "THERMAX.NS": "Thermax Limited",
        "TIL.NS": "TIL Limited",
        "TIMKEN.NS": "Timken India Limited",
        "TRF.NS": "TRF Limited",
        "TRIL.NS": "Transformers & Rectifiers (India) Limited",
        "TRITURBINE.NS": "Triveni Turbine Limited",
        "VESUVIUS.NS": "Vesuvius India Limited",
        "VOLTAMP.NS": "Voltamp Transformers Limited",
        "WINDMACHIN.NS": "Windsor Machines Limited"
    },

    "Diversified Utilities": {
        "ADANIPOWER.NS": "Adani Power Limited",
        "CESC.NS": "CESC Limited",
        "INDOSOLAR.NS": "Indosolar Limited",
        "JPPOWER.NS": "Jaiprakash Power Ventures Limited",
        "JSWENERGY.NS": "JSW Energy Limited",
        "KEC.NS": "KEC International Limited",
        "LITL.NS": "Lanco Infratech Limited",
        "NTPC.NS": "NTPC Limited",
        "PTC.NS": "PTC India Limited",
        "RPOWER.NS": "Reliance Power Limited",
        "RTNINFRA.NS": "RattanIndia Infrastructure Limited",
        "SURANASOL.NS": "Surana Solar Limited",
        "SURANAT&P.NS": "Surana Telecom and Power Limited",
        "SWELECTES.NS": "Swelect Energy Systems Limited",
        "TATAPOWER.NS": "The Tata Power Company Limited",
        "UJAAS.NS": "Ujaas Energy Ltd.",
        "WEBELSOLAR.NS": "Websol Energy System Limited",
        "XLENERGY.NS": "XL Energy Limited"
    },

    "Drug Manufacturers - Major": {
        "AARTIDRUGS.NS": "Aarti Drugs Limited",
        "ABBOTINDIA.NS": "Abbott India Limited",
        "AJANTPHARM.NS": "Ajanta Pharma Limited",
        "ASTRAZEN.NS": "AstraZeneca Pharma India Limited",
        "BAFNAPHARM.NS": "Bafna Pharmaceuticals Limited",
        "BLISSGVS.NS": "Bliss Gvs Pharma Limited",
        "BROOKS.NS": "Brooks Laboratories Limited",
        "CIPLA.NS": "Cipla Limited",
        "FDC.NS": "FDC Limited",
        "GLAXO.NS": "GlaxoSmithkline Pharmaceuticals Limited",
        "GRANULES.NS": "Granules India Limited",
        "HESTERBIO.NS": "Hester Biosciences Limited",
        "INDSWFTLAB.NS": "Ind-Swift Laboratories Limited",
        "JAGSNPHARM.NS": "Jagsonpal Pharmaceuticals Limited",
        "JBCHEPHARM.NS": "J. B. Chemicals & Pharmaceuticals Limited",
        "JUBILANT.NS": "Jubilant Life Sciences Limited",
        "KILITCH.NS": "Kilitch Drugs (India) Limited",
        "KOPRAN.NS": "Kopran Limited",
        "MOREPENLAB.NS": "Morepen Laboratories Limited",
        "NATCOPHARM.NS": "Natco Pharma Limited",
        "NECLIFE.NS": "Nectar Lifesciences Limited",
        "ORCHIDPHAR.NS": "Orchid Pharma Limited",
        "PEL.NS": "Piramal Enterprises Limited",
        "PFIZER.NS": "Pfizer Limited",
        "SHARONBIO.NS": "Sharon Bio-Medicine Ltd.",
        "SMSPHARMA.NS": "SMS Pharmaceuticals Limited",
        "TORNTPHARM.NS": "Torrent Pharmaceuticals Limited",
        "UNICHEMLAB.NS": "Unichem Laboratories Limited",
        "VENUSREM.NS": "Venus Remedies Limited",
        "WANBURY.NS": "Wanbury Limited",
        "WOCKPHARMA.NS": "Wockhardt Limited",
        "SANOFI.NS": "Sanofi India Limited"
    },

    "Drugs - Generic": {
        "ALEMBICLTD.NS": "Alembic Limited",
        "ALKEM.NS": "Alkem Laboratories Limited",
        "ALPA.NS": "Alpa Laboratories Limited",
        "AMRUTANJAN.NS": "Amrutanjan Health Care Limited",
        "APLLTD.NS": "Alembic Pharmaceuticals Limited",
        "AUROPHARMA.NS": "Aurobindo Pharma Limited",
        "BALPHARMA.NS": "Bal Pharma Limited",
        "CADILAHC.NS": "Cadila Healthcare Limited",
        "DIVISLAB.NS": "Divi's Laboratories Limited",
        "DRREDDY.NS": "Dr. Reddy's Laboratories Limited",
        "GLENMARK.NS": "Glenmark Pharmaceuticals Limited",
        "GUFICBIO.NS": "Gufic Biosciences Limited",
        "INDOCO.NS": "Indoco Remedies Limited",
        "INDSWFTLTD.NS": "Ind-Swift Limited",
        "IOLCP.NS": "IOL Chemicals and Pharmaceuticals Limited",
        "IPCALAB.NS": "Ipca Laboratories Limited",
        "LUPIN.NS": "Lupin Limited",
        "MANGALAM.NS": "Mangalam Drugs & Organics Limited",
        "MERCK.NS": "Merck Limited",
        "NEULANDLAB.NS": "Neuland Laboratories Limited",
        "PARABDRUGS.NS": "Parabolic Drugs Limited",
        "PIRPHYTO.NS": "Piramal Phytocare Limited",
        "RPGLIFE.NS": "RPG Life Sciences Limited",
        "SHILPAMED.NS": "Shilpa Medicare Limited",
        "SPARC.NS": "Sun Pharma Advanced Research Company Limited",
        "STAR.NS": "Strides Shasun Limited",
        "SUNPHARMA.NS": "Sun Pharmaceutical Industries Limited",
        "SUVEN.NS": "Suven Life Sciences Limited",
        "SYNCOM.NS": "Syncom Healthcare Limited",
        "THEMISMED.NS": "Themis Medicare Limited",
        "LINCOLN.NS": "Lincoln Pharma Limited",
        "ORCHIDCHEM.NS": "Orchid Chemicals & Pharmaceuticals Limited",
        "MARKSANS.NS": "Marksans Pharma Limited",
        "ELDERPHARM.NS": "Elder Pharmaceuticals Limited",
        "DRDATSONS.NS": "Dr.Datsons Labs Limited",
        "KOPDRUGS.NS": "KDL Biotech Limited",
        "PLETHICO.NS": "Plethico Pharmaceuticals Limited",
        "SHASUNPHAR.NS": "Shasun Pharmaceuticals Limited"
    },

    "Education & Training Services": {
        "APTECHT.NS": "Aptech Limited",
        "CAREERP.NS": "Career Point Limited",
        "COMPUSOFT.NS": "Compucom Software Limited",
        "EDUCOMP.NS": "Educomp Solutions Limited",
        "LCCINFOTEC.NS": "LCC Infotech Limited",
        "MTEDUCARE.NS": "MT Educare Limited",
        "TREEHOUSE.NS": "Tree House Education & Accessories Limited",
        "UMESLTD.NS": "Usha Martin Education & Solutions Limited",
        "VISUINTL.NS": "Ed & Tech international Limited",
        "ZEELEARN.NS": "Zee Learn Limited",
        "ZENTEC.NS": "Zen Technologies Limited",
        "COREEDUTEC.NS": "CORE Education and Technologies Limited",
        "EVERONN.NS": "Everonn Education Limited"
    },

    "Electric Utilities": {
        "ADANITRANS.NS": "Adani Transmissions Limited",
        "AMTL.NS": "Advance Metering Technology Limited",
        "DPSCLTD.NS": "India Power Corporation Limited",
        "ENERGYDEV.NS": "Energy Development Company Limited",
        "GIPCL.NS": "Gujarat Industries Power Company Limited",
        "GREENPOWER.NS": "Orient Green Power Company Limited",
        "INDOWIND.NS": "Indowind Energy Limited",
        "JYOTISTRUC.NS": "Jyoti Structures Limited",
        "KALPATPOWR.NS": "Kalpataru Power Transmission Limited",
        "KARMAENG.NS": "Karma Energy Limited",
        "KSK.NS": "KSK Energy Ventures Limited",
        "NBVENTURES.NS": "Nava Bharat Ventures Limited",
        "NHPC.NS": "NHPC Limited",
        "POWERGRID.NS": "Power Grid Corporation of India Limited",
        "RELINFRA.NS": "Reliance Infrastructure Limited",
        "RTNPOWER.NS": "RattanIndia Power Limited",
        "SEPOWER.NS": "S. E. Power Limited",
        "SJVN.NS": "SJVN Limited",
        "TORNTPOWER.NS": "Torrent Power Limited"
    },

    "Electronic Equipment": {
        "BAJAJELEC.NS": "Bajaj Electricals Limited",
        "BPL.NS": "BPL Limited",
        "BUTTERFLY.NS": "Butterfly Gandhimathi Appliances Limited",
        "KHAITANELE.NS": "Khaitan Electricals Limited",
        "MIRCELECTR.NS": "MIRC Electronics Limited",
        "NOESISIND.NS": "Noesis Industries Limited",
        "PGEL.NS": "PG Electroplast Limited",
        "PHOENIXLL.NS": "Phoenix Lamps Limited",
        "SALORAINTL.NS": "Salora International Limited",
        "SYMPHONY.NS": "Symphony Limited",
        "VALUEIND.NS": "Value Industries Limited",
        "VGUARD.NS": "V-Guard Industries Limited",
        "VIDEOIND.NS": "Videocon Industries Limited",
        "WHIRLPOOL.NS": "Whirlpool of India Limited",
        "BLUESTARCO.NS": "Blue Star Limited",
        "HITACHIHOM.NS": "Johnson Controls - Hitachi Air Conditioning India Limited",
        "PANASONIC.NS": "Panasonic Appliances India Company Limited"
    },

    "Electronics Wholesale": {
        "SHILPI.NS": "Shilpi Cable Technologies Limited"
    },

    "Entertainment - Diversified": {
        "ADLABS.NS": "Adlabs Entertainment Limited",
        "BAGFILMS.NS": "B.A.G. Films and Media Limited",
        "BALAJITELE.NS": "Balaji Telefilms Limited",
        "CINEVISTA.NS": "Cinevista Limited",
        "CREATIVEYE.NS": "Creative Eye Limited",
        "EROSMEDIA.NS": "Eros International Media Limited",
        "INOXLEISUR.NS": "Inox Leisure Limited",
        "KSERASERA.NS": "KSS Limited",
        "MUKTAARTS.NS": "Mukta Arts Limited",
        "PFOCUS.NS": "Prime Focus Limited",
        "PNC.NS": "Pritish Nandy Communications Ltd",
        "PVR.NS": "PVR Limited",
        "RADAAN.NS": "Radaan Mediaworks India Limited",
        "SAREGAMA.NS": "Saregama India Limited",
        "SHEMAROO.NS": "Shemaroo Entertainment Limited",
        "TIPSINDLTD.NS": "Tips Industries Limited",
        "UFO.NS": "UFO Moviez India Limited"
    },

    "Farm & Construction Machinery": {
        "ACE.NS": "Action Construction Equipment Limited",
        "ESCORTS.NS": "Escorts Limited",
        "GUJAPOLLO.NS": "Gujarat Apollo Industries Limited",
        "HMT.NS": "HMT Limited",
        "JISLDVREQS.NS": "Jain Irrigation Systems Limited",
        "JISLJALEQS.NS": "Jain Irrigation Systems Limited",
        "REVATHI.NS": "Revathi Equipment Limited",
        "SANGHVIMOV.NS": "Sanghvi Movers Limited",
        "VSTTILLERS.NS": "V.S.T. Tillers Tractors Limited"
    },

    "Farm Products": {
        "AGRODUTCH.NS": "Agro Dutch Industries Limited",
        "ANANDAMRUB.NS": "The Anandam Rubber Company Limited",
        "ASSAMCO.NS": "Assam Company India Limited",
        "BBTC.NS": "The Bombay Burmah Trading Corporation, Limited",
        "DHAMPURSUG.NS": "Dhampur Sugar Mills Limited",
        "DHARSUGAR.NS": "Dharani Sugars and Chemicals Limited",
        "HARRMALAYA.NS": "Harrisons Malayalam Limited",
        "KGL.NS": "Karuturi Global Limited",
        "KSCL.NS": "Kaveri Seed Company Limited",
        "NKIND.NS": "N.K Industries Limited",
        "NORBTEAEXP.NS": "Norben Tea & Exports Ltd",
        "PKTEA.NS": "The Peria Karamalai Tea and Produce Company Limited",
        "POCHIRAJU.NS": "Pochiraju Industries Limited",
        "RUCHINFRA.NS": "Ruchi Infrastructure Limited",
        "SAKUMA.NS": "Sakuma Exports Limited",
        "SANWARIA.NS": "Sanwaria Agro Oils Limited",
        "SITASHREE.NS": "Sita Shree Food Products Limited",
        "STEL.NS": "STEL Holdings Limited",
        "USHERAGRO.NS": "Usher Agro Limited",
        "JAYSREETEA.NS": "Jayshree Tea Limited",
        "PERIATEA.NS": "Peria Karamalai Tea & Produce Co. Ltd."
    },

    "Food - Major Diversified": {
        "ADFFOODS.NS": "ADF Foods Limited",
        "ATFL.NS": "Agro Tech Foods Limited",
        "BRITANNIA.NS": "Britannia Industries Limited",
        "CCL.NS": "CCL Products (India) Limited",
        "DAAWAT.NS": "LT Foods Limited",
        "FARMAXIND.NS": "Farmax India Limited",
        "GAEL.NS": "Gujarat Ambuja Exports Limited",
        "GOKUL.NS": "Gokul Refoils & Solvent Ltd",
        "GOKULAGRO.NS": "Gokul Agro Resources Limited",
        "GSKCONS.NS": "GlaxoSmithKline Consumer Healthcare Limited",
        "HATSUN.NS": "Hatsun Agro Product Limited",
        "JVLAGRO.NS": "JVL Agro Industries Limited",
        "KOHINOOR.NS": "Kohinoor Foods Limited",
        "KRBL.NS": "KRBL Limited",
        "KWALITY.NS": "Kwality Limited",
        "MCLEODRUSS.NS": "McLeod Russel India Limited",
        "NESTLEIND.NS": "Nestlé India Limited",
        "PRABHAT.NS": "Prabhat Dairy Limited",
        "RAJOIL.NS": "Raj Oil Mills Limited",
        "RASOYPR.NS": "Rasoya Proteins Limited",
        "REIAGROLTD.NS": "REI Agro Limited",
        "ROSSELLIND.NS": "Rossell India Limited",
        "RUCHISOYA.NS": "Ruchi Soya Industries Limited",
        "TATACOFFEE.NS": "Tata Coffee Limited",
        "TATAGLOBAL.NS": "Tata Global Beverages Limited",
        "VADILALIND.NS": "Vadilal Industries Limited",
        "VIMALOIL.NS": "Vimal Oil & Foods Limited",
        "UMANGDAIRY.NS": "Umang Dairies Limited",
        "AVANTIFEED.NS": "Avanti Feeds Limited",
        "VIDHIDYE.NS": "Vidhi Specialty Food Ingredients Limited"
    },

    "Food Wholesale": {
        "ANIKINDS.NS": "Anik Industries Limited",
        "HERITGFOOD.NS": "Heritage Foods Limited"
    },

    "Gas Utilities": {
        "GAIL.NS": "GAIL (India) Limited",
        "GSPL.NS": "Gujarat State Petronet Limited",
        "IGL.NS": "Indraprastha Gas Limited",
        "GUJGASLTD.NS": "Gujarat Gas Limited"
    },

    "General Building Materials": {
        "ACC.NS": "ACC Limited",
        "AMBUJACEM.NS": "Ambuja Cements Limited",
        "ANDHRACEMT.NS": "Andhra Cements Limited",
        "AROGRANITE.NS": "Aro Granite Industries Limited",
        "ASIANTILES.NS": "Asian Granito India Limited",
        "BEARDSELL.NS": "Beardsell Limited",
        "BINANIIND.NS": "Edayar Zinc Limited",
        "BIRLACORPN.NS": "Birla Corporation Limited",
        "BURNPUR.NS": "Burnpur Cement Limited",
        "BVCL.NS": "Barak Valley Cements Limited",
        "CARBORUNIV.NS": "Carborundum Universal Limited",
        "CENTURYTEX.NS": "Century Textiles and Industries Limited",
        "CERA.NS": "Cera Sanitaryware Limited",
        "DALMIABHA.NS": "Dalmia Bharat Limited",
        "DECCANCE.NS": "Deccan Cements Limited",
        "ELECTCAST.NS": "Electrosteel Castings Limited",
        "EUROCERA.NS": "Euro Ceramics Limited",
        "EVERESTIND.NS": "Everest Industries Limited",
        "GRASIM.NS": "Grasim Industries Limited",
        "GREENPLY.NS": "Greenply Industries Limited",
        "GRINDWELL.NS": "Grindwell Norton Limited",
        "GSCLCEMENT.NS": "Gujarat Sidhee Cement Limited",
        "HEIDELBERG.NS": "HeidelbergCement India Limited",
        "HIL.NS": "HIL Limited",
        "HSIL.NS": "HSIL Limited",
        "IFGLREFRAC.NS": "IFGL Refractories Limited",
        "INDIACEM.NS": "The India Cements Limited",
        "JENSONICOL.NS": "Jenson & Nicholson (India) Limited",
        "JKCEMENT.NS": "J.K. Cement Limited",
        "JKLAKSHMI.NS": "JK Lakshmi Cement Limited",
        "KAJARIACER.NS": "Kajaria Ceramics Limited",
        "KAKATCEM.NS": "Kakatiya Cement Sugar and Industries Limited",
        "MADHAV.NS": "Madhav Marbles and Granites Limited",
        "MANGLMCEM.NS": "Mangalam Cement Limited",
        "MURUDCERA.NS": "Murudeshwar Ceramics Limited",
        "NCLIND.NS": "NCL Industries Limited",
        "NITCO.NS": "Nitco Limited",
        "OCL.NS": "OCL India Limited",
        "ORIENTALTL.NS": "Oriental Trimex Limited",
        "ORIENTBELL.NS": "Orient Bell Limited",
        "ORIENTCEM.NS": "Orient Cement Limited",
        "PRISMCEM.NS": "Prism Cement Limited",
        "RAMCOIND.NS": "Ramco Industries Limited",
        "REGENCERAM.NS": "Regency Ceramics Limited",
        "SANGHIIND.NS": "Sanghi Industries Limited",
        "SEZAL.NS": "Sejal Glass Limited",
        "SFCL.NS": "Star Ferro and Cement Limited",
        "SHREECEM.NS": "Shree Cement Limited",
        "SICAGEN.NS": "Sicagen India Limited",
        "SINTEX.NS": "Sintex Industries Limited",
        "SOMANYCERA.NS": "Somany Ceramics Limited",
        "ULTRACEMCO.NS": "UltraTech Cement Limited",
        "VISAKAIND.NS": "Visaka Industries Limited",
        "RAMCOCEM.NS": "The Ramco Cements Limited",
        "GREENLAM.NS": "Greenlam Industries Limited"
    },

    "General Contractors": {
        "A2ZINFRA.NS": "A2Z Infra Engineering Limited",
        "AHLUCONT.NS": "Ahluwalia Contracts (India) Limited",
        "ASHOKA.NS": "Ashoka Buildcon Limited",
        "AXISCADES.NS": "AXISCADES Engineering Technologies Limited",
        "BFUTILITIE.NS": "BF Utilities Limited",
        "BGRENERGY.NS": "BGR Energy Systems Limited",
        "BLKASHYAP.NS": "B.L. Kashyap and Sons Limited",
        "BSLIMITED.NS": "BS Limited",
        "CANDC.NS": "C & C Constructions Limited",
        "CCCL.NS": "Consolidated Construction Consortium Limited",
        "ENGINERSIN.NS": "Engineers India Limited",
        "EXCEL.NS": "Excel Realty N Infra Limited",
        "GAMMONIND.NS": "Gammon India Limited",
        "GAYAPROJ.NS": "Gayatri Projects Limited",
        "GISOLUTION.NS": "GI Engineering Solutions Limited",
        "HCC.NS": "Hindustan Construction Company Limited",
        "HINDDORROL.NS": "Hindustan Dorr-Oliver Limited",
        "IL&FSENGG.NS": "IL&FS Engineering and Construction Company Limited",
        "INDIANHUME.NS": "The Indian Hume Pipe Company Limited",
        "ITDCEM.NS": "ITD Cementation India Limited",
        "IVRCLINFRA.NS": "IVRCL Limited",
        "JAIHINDPRO.NS": "Jaihind Projects Limited",
        "JKIL.NS": "J. Kumar Infraprojects Limited",
        "JMCPROJECT.NS": "JMC Projects (India) Limited",
        "JPASSOCIAT.NS": "Jaiprakash Associates Limited",
        "KAUSHALYA.NS": "Kaushalya Infrastructure Development Corporation Limited",
        "KNRCON.NS": "KNR Constructions Limited",
        "LT.NS": "Larsen & Toubro Limited",
        "MADHUCON.NS": "Madhucon Projects Limited",
        "MANINFRA.NS": "Man Infraconstruction Limited",
        "MBECL.NS": "McNally Bharat Engineering Company Limited",
        "MBLINFRA.NS": "MBL Infrastructures Limited",
        "MUKANDENGG.NS": "Mukand Engineers Limited",
        "NBCC.NS": "NBCC (India) Limited",
        "NCC.NS": "NCC Limited",
        "NOIDATOLL.NS": "Noida Toll Bridge Company Limited",
        "OMMETALS.NS": "Om Metals Infraprojects Limited",
        "PATELENG.NS": "Patel Engineering Limited",
        "PBAINFRA.NS": "PBA Infrastructure Limited",
        "PETRONENGG.NS": "Petron Engineering Construction Limited",
        "POWERMECH.NS": "Power Mech Projects Limited",
        "PRAJIND.NS": "Praj Industries Limited",
        "PRAKASHCON.NS": "Prakash Constrowell Limited",
        "PRATIBHA.NS": "Pratibha Industries Limited",
        "PUNJLLOYD.NS": "Punj Lloyd Limited",
        "PURVA.NS": "Puravankara Limited",
        "RAMKY.NS": "Ramky Infrastructure Limited",
        "RIIL.NS": "Reliance Industrial Infrastructure Limited",
        "RPPINFRA.NS": "RPP Infra Projects Limited",
        "SADBHAV.NS": "Sadbhav Engineering Limited",
        "SADBHIN.NS": "Sadbhav Infrastructure Project Limited",
        "SHRIRAMEPC.NS": "Shriram EPC Limited",
        "SIMPLEX.NS": "Simplex Projects Limited",
        "SIMPLEXINF.NS": "Simplex Infrastructures Limited",
        "SKIL.NS": "SKIL Infrastructure Limited",
        "SKIPPER.NS": "Skipper Limited",
        "SPMLINFRA.NS": "SPML Infra Limited",
        "SUNILHITEC.NS": "Sunil Hitech Engineers Limited",
        "SUPREMEINF.NS": "Supreme Infrastructure India Limited",
        "TANTIACONS.NS": "Tantia Constructions Limited",
        "TARMAT.NS": "Tarmat Limited",
        "TECHNO.NS": "Techno Electric & Engineering Company Limited",
        "TECHNOFAB.NS": "Technofab Engineering Limited",
        "UNITY.NS": "Unity Infraprojects Limited",
        "VALECHAENG.NS": "Valecha Engineering Limited",
        "VKSPL.NS": "VKS Projects Limited",
        "VOLTAS.NS": "Voltas Limited",
        "WALCHANNAG.NS": "Walchandnagar Industries Limited",
        "PNCINFRA.NS": "PNC Infratech Limited"
    },

    "Gold": {
        "SHIRPUR-G.NS": "Shirpur Gold Refinery Limited"
    },

    "Grocery Stores": {
        "REISIXTEN.NS": "REI Six Ten Retail Limited"
    },

    "Heavy Construction": {
        "ARSSINFRA.NS": "ARSS Infrastructure Projects Limited",
        "ATLANTA.NS": "Atlanta Limited",
        "GAMMNINFRA.NS": "Gammon Infrastructure Projects Limited",
        "GMRINFRA.NS": "GMR Infrastructure Limited",
        "IL&FSTRANS.NS": "IL&FS Transportation Networks Limited",
        "IRB.NS": "IRB Infrastructure Developers Limited",
        "JPINFRATEC.NS": "Jaypee Infratech Limited",
        "MEP.NS": "MEP Infrastructure Developers Limited"
    },

    "Home Furnishings & Fixtures": {
        "BLUESTARCO.NS": "Blue Star Limited",
        "JIKIND.NS": "JIK Industries Limited",
        "LAOPALA.NS": "La Opala RG Limited",
        "ORIENTPPR.NS": "Orient Paper & Industries Limited",
        "PILITA.NS": "PIL ITALICA LIFESTYLE LIMITED",
        "RUSHIL.NS": "Rushil Décor Limited",
        "TTKPRESTIG.NS": "TTK Prestige Limited"
    },

    "Hospitals": {
        "APOLLOHOSP.NS": "Apollo Hospitals Enterprise Limited",
        "FORTIS.NS": "Fortis Healthcare Limited",
        "HCG.NS": "HealthCare Global Enterprises Limited",
        "INDRAMEDCO.NS": "Indraprastha Medical Corporation Limited",
        "NH.NS": "Narayana Hrudayalaya Limited",
        "PTL.NS": "PTL Enterprises Limited",
        "KOVAI.NS": "Kovai Medical Center & Hospital Limited"
    },

    "Independent Oil & Gas": {
        "HINDOILEXP.NS": "Hindustan Oil Exploration Company Limited",
        "OIL.NS": "Oil India Limited",
        "SELAN.NS": "Selan Exploration Technology Limited",
        "SVOGL.NS": "SVOGL Oil Gas and Energy Limited"
    },

    "Industrial Equipment Wholesale": {
        "LGBFORGE.NS": "LGB Forge Limited",
        "RKFORGE.NS": "Ramkrishna Forgings Limited",
        "UNIVCABLES.NS": "Universal Cables Limited"
    },

    "Industrial Metals & Minerals": {
        "20MICRONS.NS": "20 Microns Limited",
        "ADANIENT.NS": "Adani Enterprises Limited",
        "ASHAPURMIN.NS": "Ashapura Minechem Limited",
        "AUSTRAL.NS": "Greenearth Resources & Projects Limited",
        "COALINDIA.NS": "Coal India Limited",
        "GMDCLTD.NS": "Gujarat Mineral Development Corporation Limited",
        "GUJNRECOKE.NS": "Gujarat NRE Coke Ltd.",
        "HINDZINC.NS": "Hindustan Zinc Limited",
        "IMPEXFERRO.NS": "Impex Ferro Tech Limited",
        "KOTHARIPRO.NS": "Kothari Products Limited",
        "MERCATOR.NS": "Mercator Limited",
        "METKORE.NS": "Metkore Alloys & Industries Limited",
        "MMTC.NS": "MMTC Limited",
        "MOIL.NS": "MOIL Limited",
        "ORISSAMINE.NS": "The Orissa Minerals Development Company Limited",
        "RMMIL.NS": "Resurgere Mines & Minerals India Limited",
        "STCINDIA.NS": "The State Trading Corporation of India Limited",
        "VEDL.NS": "Vedanta Limited"
    },

    "Information Technology Services": {
        "3IINFOTECH.NS": "3i Infotech Limited",
        "ACCELYA.NS": "Accelya Kale Solutions Limited",
        "ACROPETAL.NS": "Acropetal Technologies Limited",
        "ADSL.NS": "Allied Digital Services Ltd",
        "AFL.NS": "Accel Frontline Limited",
        "CTE.NS": "Cambridge Technology Enterprises Limited",
        "CYBERTECH.NS": "CyberTech Systems and Software Limited",
        "CYIENT.NS": "Cyient Limited",
        "DSSL.NS": "Dynacons Systems & Solutions Limited",
        "FCSSOFT.NS": "FCS Software Solutions Limited",
        "GENESYS.NS": "Genesys International Corporation Limited",
        "GOLDTECH.NS": "Goldstone Technologies Limited",
        "GSS.NS": "GSS Infotech Limited",
        "GTL.NS": "GTL Limited",
        "HCLTECH.NS": "HCL Technologies Limited",
        "HEXAWARE.NS": "Hexaware Technologies Limited",
        "HOVS.NS": "HOV Services Limited",
        "INFINITE.NS": "Infinite Computer Solutions (India) Limited",
        "INFY.NS": "Infosys Limited",
        "INTELLECT.NS": "Intellect Design Arena Limited",
        "IZMO.NS": "IZMO Limited",
        "KPIT.NS": "KPIT Technologies Limited",
        "MASTEK.NS": "Mastek Limited",
        "MINDTREE.NS": "Mindtree Limited",
        "MPHASIS.NS": "MphasiS Limited",
        "NIITLTD.NS": "NIIT Limited",
        "NIITTECH.NS": "NIIT Technologies Limited",
        "NUCLEUS.NS": "Nucleus Software Exports Limited",
        "OMNITECH.NS": "Omnitech Infosolutions Ltd",
        "ONWARDTEC.NS": "Onward Technologies Limited",
        "PALRED.NS": "Palred Technologies Limited",
        "PANORAMUNI.NS": "Panoramic Universal Limited",
        "QUINTEGRA.NS": "Quintegra Solutions Limited",
        "RAMCOSYS.NS": "Ramco Systems Limited",
        "REDINGTON.NS": "Redington (India) Limited",
        "ROLTA.NS": "Rolta India Limited",
        "SAKSOFT.NS": "Saksoft Limited",
        "SOFTTECHGR.NS": "STG Lifecare Limited",
        "SPHEREGSL.NS": "Sphere Global Services Limited",
        "TAKE.NS": "TAKE Solutions Limited",
        "TCS.NS": "Tata Consultancy Services Limited",
        "TECHM.NS": "Tech Mahindra Limited",
        "TRICOM.NS": "Tricom India Limited",
        "VISESHINFO.NS": "MPS Infotecnics Limited",
        "WIPRO.NS": "Wipro Limited",
        "XCHANGING.NS": "Xchanging Solutions Limited",
        "ZENSARTECH.NS": "Zensar Technologies Limited",
        "8KMILES.NS": "8K Miles Software Services Limited",
        "BGLOBAL.NS": "Bharatiya Global Infomedia Limited",
        "CALSOFT.NS": "California Software Company Limited",
        "FINANTECH.NS": "63 Moons Technologies Limited",
        "ICSA.NS": "ICSA (India) Limited",
        "KERNEX.NS": "Kernex Microsystems (India) Limited",
        "MEGASOFT.NS": "Megasoft Limited",
        "RSSOFTWARE.NS": "R. S. Software (India) Limited",
        "SASKEN.NS": "Sasken Technologies Limited",
        "SQSBFSI.NS": "SQS India BFSI Limited",
        "SUBEX.NS": "Subex Limited",
        "TANLA.NS": "Tanla Solutions Limited",
        "TATAELXSI.NS": "Tata Elxsi Limited",
        "TRIGYN.NS": "Trigyn Technologies Limited",
        "VAKRANGEE.NS": "Vakrangee Limited",
        "ZYLOG.NS": "Zylog Systems Limited",
        "CMC.NS": "CMC Limited",
        "GEOMETRIC.NS": "Geometric Limited",
        "HUSYS.NS": "Husys Consulting Limited",
        "RSYSTEMS.NS": "R Systems International Limited",
        "SONATSOFTW.NS": "Sonata Software Limited",
        "QUICKHEAL.NS": "Quick Heal Technologies Limited",
        "INFOBEANS.NS": "InfoBeans Technologies Limited",
        "BODHTREE.NS": "Bodhtree Consulting Limited",
        "GLODYNE.NS": "Glodyne Technoserve Limited",
        "HELIOSMATH.NS": "Helios and Matheson Information Technology Limited"
    },

    "Internet Information Providers": {
        "ISFT.NS": "IntraSoft Technologies Limited",
        "LYCOS.NS": "Lycos Internet Limited",
        "NAUKRI.NS": "Info Edge (India) Limited",
        "NET4.NS": "Net 4 India Limited",
        "JUSTDIAL.NS": "Just Dial Limited"
    },

    "Investment Brokerage - National": {
        "ALMONDZ.NS": "Almondz Global Securities Limited",
        "AUSOMENT.NS": "Ausom Enterprise Limited",
        "BIRLAMONEY.NS": "Aditya Birla Money Limited",
        "BLBLIMITED.NS": "BLB Limited",
        "BLUECHIP.NS": "Blue Chip India Limited",
        "CARERATING.NS": "CARE Ratings Limited",
        "CONSOFINVT.NS": "Consolidated Finvest & Holdings Limited",
        "CRISIL.NS": "CRISIL Limited",
        "DBSTOCKBRO.NS": "DB (International) Stock Brokers Ltd",
        "DHUNINV.NS": "Dhunseri Investments Limited",
        "DPL.NS": "Dhunseri Petrochem Limited",
        "EDELWEISS.NS": "Edelweiss Financial Services Limited",
        "EMKAY.NS": "Emkay Global Financial Services Limited",
        "HBSTOCK.NS": "HB Stockholdings Limited",
        "IBVENTURES.NS": "Indiabulls Ventures Limited",
        "ICRA.NS": "ICRA Limited",
        "IIFL.NS": "IIFL Holdings Limited",
        "INDOTHAI.NS": "Indo Thai Securities Limited",
        "INVENTURE.NS": "Inventure Growth & Securities Limited",
        "JMFINANCIL.NS": "JM Financial Limited",
        "KEYCORPSER.NS": "Keynote Corporate Services Limited",
        "KHANDSE.NS": "Khandwala Securities Limited",
        "MCDHOLDING.NS": "McDowell Holdings Limited",
        "ONELIFECAP.NS": "Onelife Capital Advisors Limited",
        "PRIMESECU.NS": "Prime Securities Limited",
        "RELIGARE.NS": "Religare Enterprises Limited",
        "SUMMITSEC.NS": "Summit Securities Limited",
        "TATAINVEST.NS": "Tata Investment Corporation Limited",
        "VLSFINANCE.NS": "VLS Finance Limited",
        "WEIZFOREX.NS": "Weizmann Forex Limited",
        "GEOJITBNPP.NS": "Geojit Financial Services Limited",
        "MICROSEC.NS": "Sastasundar Ventures Limited"
    },

    "Jewelry Stores": {
        "GITANJALI.NS": "Gitanjali Gems Limited",
        "GOENKA.NS": "Goenka Diamond and Jewels Limited",
        "GOLDIAM.NS": "Goldiam International Limited",
        "KDDL.NS": "KDDL Limited",
        "LYPSAGEMS.NS": "Lypsa Gems & Jewellery Limited",
        "PCJEWELLER.NS": "PC Jeweller Limited",
        "RAJESHEXPO.NS": "Rajesh Exports Limited",
        "RJL.NS": "Renaissance Jewellery Limited",
        "SGJHL.NS": "Shree Ganesh Jewellery House (I) Limited",
        "SHRENUJ.NS": "Shrenuj & Company Limited",
        "SRSLTD.NS": "SRS Limited",
        "SURANACORP.NS": "Surana Corporation Limited",
        "TARAJEWELS.NS": "Tara Jewels Limited",
        "TBZ.NS": "Tribhovandas Bhimji Zaveri Limited",
        "THANGAMAYL.NS": "Thangamayil Jewellery Limited",
        "TITAN.NS": "Titan Company Limited",
        "VAIBHAVGBL.NS": "Vaibhav Global Limited",
        "ZODJRDMKJ.NS": "Zodiac-JRD-MKJ Limited"
    },

    "Life Insurance": {
        "MFSL.NS": "Max Financial Services Limited",
        "MAX.NS": "Max Financial Services Limited"
    },

    "Lodging": {
        "ADVANIHOTR.NS": "Advani Hotels & Resorts (India) Limited",
        "AHLEAST.NS": "Asian Hotels (East) Limited",
        "AHLWEST.NS": "Asian Hotels (West) Limited",
        "APOLSINHOT.NS": "Apollo Sindoori Hotels Limited",
        "ASIANHOTNR.NS": "Asian Hotels (North) Limited",
        "BLUECOAST.NS": "Blue Coast Hotels Limited",
        "EIHAHOTELS.NS": "EIH Associated Hotels Limited",
        "EIHOTEL.NS": "EIH Limited",
        "HOTELEELA.NS": "Hotel Leelaventure Limited",
        "INDHOTEL.NS": "The Indian Hotels Company Limited",
        "KAMATHOTEL.NS": "Kamat Hotels (India) Limited",
        "ORIENTHOT.NS": "Oriental Hotels Limited",
        "ROHLTD.NS": "Royal Orchid Hotels Limited",
        "TAJGVK.NS": "TAJGVK Hotels & Resorts Limited",
        "TGBHOTELS.NS": "TGB Banquets And Hotels Limited",
        "THEBYKE.NS": "The Byke Hospitality Limited",
        "VICEROY.NS": "Viceroy Hotels Limited",
        "SAYAJIHOTL.NS": "Sayaji Hotels Limited"
    },

    "Lumber, Wood Production": {
        "ARCHIDPLY.NS": "Archidply Industries Limited",
        "CENTURYPLY.NS": "Century Plyboards (India) Limited",
        "MANGTIMBER.NS": "Mangalam Timber Products Limited",
        "UNIPLY.NS": "Uniply Industries Limited"
    },

    "Machine Tools & Accessories": {
        "ESABINDIA.NS": "ESAB India Limited",
        "LAKPRE.NS": "Lakshmi Precision Screws Limited",
        "NIBL.NS": "NRB Industrial Bearings Limited",
        "STERTOOLS.NS": "Sterling Tools Limited",
        "TIIL.NS": "Technocraft Industries (India) Limited",
        "WENDT.NS": "Wendt (India) Limited"
    },

    "Major Airlines": {
        "INDIGO.NS": "InterGlobe Aviation Limited",
        "JETAIRWAYS.NS": "Jet Airways (India) Limited",
        "KFA.NS": "Kingfisher Airlines Limited"
    },

    "Major Integrated Oil & Gas": {
        "CAIRN.NS": "Cairn India Limited",
        "ONGC.NS": "Oil and Natural Gas Corporation Limited"
    },

    "Medical Appliances & Equipment": {
        "OPTOCIRCUI.NS": "Opto Circuits (India) Ltd"
    },

    "Medical Instruments & Supplies": {
        "POLYMED.NS": "Poly Medicure Limited"
    },

    "Medical Laboratories & Research": {
        "LALPATHLAB.NS": "Dr. Lal PathLabs Limited",
        "VIMTALABS.NS": "Vimta Labs Limited",
        "LOTUSEYE.NS": "Lotus Eye Hospital and Institute Limited"
    },

    "Metal Fabrication": {
        "ALICON.NS": "Alicon Castalloy Limited",
        "ARCOTECH.NS": "Arcotech Limited",
        "BILENERGY.NS": "Bil Energy Systems Limited",
        "ELECTHERM.NS": "Electrotherm (India) Limited",
        "GANDHITUBE.NS": "Gandhi Special Tubes Limited",
        "GOODLUCK.NS": "Goodluck India Limited",
        "GRAVITA.NS": "Gravita India Limited",
        "HILTON.NS": "Hilton Metal Forging Limited",
        "MAHINDCIE.NS": "Mahindra CIE Automotive Limited",
        "METALFORGE.NS": "Metalyst Forgings Limited",
        "MMFL.NS": "MM Forgings Limited",
        "NELCAST.NS": "Nelcast Limited",
        "ORIENTREF.NS": "Orient Refractories Limited",
        "PENPEBS.NS": "Pennar Engineered Building Systems Limited",
        "PSL.NS": "PSL Limited",
        "ROHITFERRO.NS": "Rohit Ferro-Tech Limited",
        "SGFL.NS": "Shree Ganesh Forgings Limited",
        "SRIPIPES.NS": "Srikalahasthi Pipes Limited",
        "ZENITHBIR.NS": "Zenith Birla (India) Limited",
        "MANAKCOAT.NS": "Manaksia Coated Metals Limited",
        "MANAKINDST.NS": "Manaksia Industries Limited",
        "MANAKSTEEL.NS": "Manaksia Steels Limited"
    },

    "Money Center Banks": {
        "ALBK.NS": "Allahabad Bank",
        "ANDHRABANK.NS": "Andhra Bank",
        "AXISBANK.NS": "Axis Bank Limited",
        "BANKBARODA.NS": "Bank of Baroda",
        "BANKINDIA.NS": "Bank of India Limited",
        "CANBK.NS": "Canara Bank",
        "CENTRALBK.NS": "Central Bank of India",
        "CORPBANK.NS": "Corporation Bank",
        "CUB.NS": "City Union Bank Limited",
        "DCBBANK.NS": "DCB Bank Limited",
        "DENABANK.NS": "Dena Bank",
        "DHANBANK.NS": "Dhanlaxmi Bank Limited",
        "FEDERALBNK.NS": "The Federal Bank Limited",
        "HDFCBANK.NS": "HDFC Bank Limited",
        "ICICIBANK.NS": "ICICI Bank Limited",
        "IDBI.NS": "IDBI Bank Limited",
        "IDFCBANK.NS": "IDFC Bank Limited",
        "INDIANB.NS": "Indian Bank",
        "INDUSINDBK.NS": "IndusInd Bank Limited",
        "IOB.NS": "Indian Overseas Bank",
        "J&KBANK.NS": "The Jammu and Kashmir Bank Limited",
        "KARURVYSYA.NS": "The Karur Vysya Bank Limited",
        "KOTAKBANK.NS": "Kotak Mahindra Bank Limited",
        "KTKBANK.NS": "The Karnataka Bank Limited",
        "LAKSHVILAS.NS": "The Lakshmi Vilas Bank Limited",
        "MAHABANK.NS": "Bank of Maharashtra",
        "ORIENTBANK.NS": "Oriental Bank of Commerce",
        "PNB.NS": "Punjab National Bank",
        "PSB.NS": "Punjab & Sind Bank",
        "SBIN.NS": "State Bank of India",
        "SOUTHBANK.NS": "The South Indian Bank Limited",
        "SYNDIBANK.NS": "Syndicate Bank",
        "UCOBANK.NS": "UCO Bank",
        "UNIONBANK.NS": "Union Bank of India",
        "UNITEDBNK.NS": "United Bank of India",
        "VIJAYABANK.NS": "Vijaya Bank",
        "YESBANK.NS": "Yes Bank Limited",
        "SBBJ.NS": "State Bank of Bikaner & Jaipur",
        "SBT.NS": "State Bank of Travancore",
        "MYSOREBANK.NS": "State Bank of Mysore"
    },

    "Mortgage Investment": {
        "CANFINHOME.NS": "Can Fin Homes Limited",
        "DHFL.NS": "Dewan Housing Finance Corporation Limited",
        "GICHSGFIN.NS": "GIC Housing Finance Limited",
        "GRUH.NS": "GRUH Finance Limited",
        "HDFC.NS": "Housing Development Finance Corporation Limited",
        "IBULHSGFIN.NS": "Indiabulls Housing Finance Limited",
        "LICHSGFIN.NS": "LIC Housing Finance Limited",
        "REPCOHOME.NS": "Repco Home Finance Limited",
        "SREINFRA.NS": "SREI Infrastructure Finance Limited",
        "TFL.NS": "Transwarranty Finance Limited"
    },

    "Multimedia & Graphics Software": {
        "DQE.NS": "DQ Entertainment (International) Limited"
    },

    "Oil & Gas Drilling & Exploration": {
        "ABAN.NS": "Aban Offshore Limited",
        "JINDRILL.NS": "Jindal Drilling & Industries Limited"
    },

    "Oil & Gas Equipment & Services": {
        "ALPHAGEO.NS": "Alphageo (India) Limited",
        "DEEPIND.NS": "Deep Industries Limited",
        "DOLPHINOFF.NS": "Dolphin Offshore Enterprises (India) Limited",
        "GTOFFSHORE.NS": "GOL Offshore Limited",
        "OILCOUNTUB.NS": "Oil Country Tubular Limited"
    },

    "Oil & Gas Refining & Marketing": {
        "BPCL.NS": "Bharat Petroleum Corporation Limited",
        "CHENNPETRO.NS": "Chennai Petroleum Corporation Limited",
        "GULFOILLUB.NS": "Gulf Oil Lubricants India Limited",
        "GULFPETRO.NS": "GP Petroleums Limited",
        "IOC.NS": "Indian Oil Corporation Limited",
        "MRPL.NS": "Mangalore Refinery and Petrochemicals Limited",
        "NAGAROIL.NS": "Nagarjuna Oil Refinery Limited",
        "PANAMAPET.NS": "Panama Petrochem Limited",
        "PETRONET.NS": "Petronet LNG Limited",
        "RELIANCE.NS": "Reliance Industries Limited",
        "TIDEWATER.NS": "Tide Water Oil Co. (India), Ltd.",
        "HINDPETRO.NS": "Hindustan Petroleum Corporation Limited",
        "ESSAROIL.NS": "Essar Oil Limited",
        "SAHPETRO.NS": "GP Petroleums Limited"
    },

    "Packaging & Containers": {
        "AMDIND.NS": "AMD Industries Limited",
        "ANTGRAPHIC.NS": "Antarctica Limited",
        "COSMOFILMS.NS": "Cosmo Films Limited",
        "EMMBI.NS": "Emmbi Industries Limited",
        "ESSDEE.NS": "Ess Dee Aluminium Limited",
        "HINDNATGLS.NS": "Hindusthan National Glass & Industries Limited",
        "NAHARPOLY.NS": "Nahar Poly Films Limited",
        "ORIENTLTD.NS": "Orient Press Limited",
        "PAPERPROD.NS": "Huhtamaki PPL Limited",
        "PARAPRINT.NS": "Paramount Printpackaging Limited",
        "PDMJEPAPER.NS": "Pudumjee Paper Products Limited",
        "PEARLPOLY.NS": "Pearl Polymers Limited",
        "POLYPLEX.NS": "Polyplex Corporation Limited",
        "RMCL.NS": "Radha Madhav Corporation Limited",
        "SHREERAMA.NS": "Shree Rama Multi-Tech Limited",
        "TIMETECHNO.NS": "Time Technoplast Limited",
        "UFLEX.NS": "Uflex Limited",
        "ESSELPACK.NS": "Essel Propack Limited"
    },

    "Paper & Paper Products": {
        "BALLARPUR.NS": "Ballarpur Industries Limited",
        "GENUSPAPER.NS": "Genus Paper & Boards Limited",
        "IPAPPM.NS": "International Paper APPM Limited",
        "JKPAPER.NS": "JK Paper Limited",
        "MAGNUM.NS": "Magnum Ventures Limited",
        "MALUPAPER.NS": "Malu Paper Mills Limited",
        "PDUMJEPULP.NS": "Pudumjee Pulp & Paper Mills Limited",
        "RAINBOWPAP.NS": "Rainbow Papers Limited",
        "RAMANEWS.NS": "Shree Rama Newsprint Limited",
        "RUCHIRA.NS": "Ruchira Papers Limited",
        "SERVALL.NS": "Servalakshmi Paper Limited",
        "SESHAPAPER.NS": "Seshasayee Paper and Boards Limited",
        "SHREYANIND.NS": "Shreyans Industries Limited",
        "STARPAPER.NS": "Star Paper Mills Limited",
        "SUNDARAM.NS": "Sundaram Multi Pap Limited",
        "TNPL.NS": "Tamil Nadu Newsprint and Papers Limited",
        "WSTCSTPAPR.NS": "West Coast Paper Mills Limited",
        "NIRVIKARA.NS": "Balkrishna Paper Mills Limited",
        "SIRPAPER.NS": "Sirpur Paper Mills Ltd."
    },

    "Personal Products": {
        "BAJAJCORP.NS": "Bajaj Corp Limited",
        "COLPAL.NS": "Colgate-Palmolive (India) Limited",
        "DABUR.NS": "Dabur India Limited",
        "EMAMILTD.NS": "Emami Limited",
        "GILLETTE.NS": "Gillette India Limited",
        "HINDUNILVR.NS": "Hindustan Unilever Limited",
        "JHS.NS": "JHS Svendgaard Laboratories Limited",
        "JYOTHYLAB.NS": "Jyothy Laboratories Limited",
        "KAYA.NS": "Kaya Limited",
        "MARICO.NS": "Marico Limited",
        "PGHH.NS": "Procter & Gamble Hygiene and Health Care Limited",
        "ZYDUSWELL.NS": "Zydus Wellness Limited",
        "GODREJCP.NS": "Godrej Consumer Products Limited",
        "TTKHLTCARE.NS": "TTK Healthcare Limited"
    },

    "Property & Casualty Insurance": {
        "BAJAJFINSV.NS": "Bajaj Finserv Limited"
    },

    "Property Management": {
        "AJMERA.NS": "Ajmera Realty & Infra India Limited",
        "ANANTRAJ.NS": "Anant Raj Limited",
        "ANSALHSG.NS": "Ansal Housing & Construction Limited",
        "BRIGADE.NS": "Brigade Enterprises Limited",
        "CINELINE.NS": "Cineline India Limited",
        "EMAMIINFRA.NS": "Emami Infrastructure Limited",
        "FMNL.NS": "Future Market Networks Limited",
        "IBREALEST.NS": "Indiabulls Real Estate Limited",
        "MOTOGENFIN.NS": "The Motor & General Finance Limited",
        "OBEROIRLTY.NS": "Oberoi Realty Limited",
        "PDUMJEIND.NS": "Pudumjee Industries Limited",
        "TEXINFRA.NS": "Texmaco Infrastructure & Holdings Limited"
    },

    "Publishing - Newspapers": {
        "CYBERMEDIA.NS": "Cyber Media (India) Limited",
        "DBCORP.NS": "D. B. Corp Limited",
        "HMVL.NS": "Hindustan Media Ventures Limited",
        "HTMEDIA.NS": "HT Media Limited",
        "INFOMEDIA.NS": "Infomedia Press Limited",
        "JAGRAN.NS": "Jagran Prakashan Limited",
        "MPSLTD.NS": "MPS Limited",
        "NAVNETEDUL.NS": "Navneet Education Limited",
        "NEXTMEDIA.NS": "Next Mediaworks Limited",
        "SAMBHAAV.NS": "Sambhaav Media Limited",
        "SANDESH.NS": "The Sandesh Limited"
    },

    "Railroads": {
        "CEBBCO.NS": "Commercial Engineers & Body Builders Co Limited",
        "NECCLTD.NS": "North Eastern Carrying Corporation Limited",
        "TWL.NS": "Titagarh Wagons Limited"
    },

    "Real Estate Development": {
        "ANSALAPI.NS": "Ansal Properties & Infrastructure Limited",
        "ARIHANT.NS": "Arihant Foundations & Housing Limited",
        "ASHIANA.NS": "Ashiana Housing Limited",
        "BSELINFRA.NS": "BSEL Infrastructure Realty Limited",
        "COUNCODOS.NS": "Country Condo'S Limited",
        "DBREALTY.NS": "DB Realty Ltd",
        "DLF.NS": "DLF Limited",
        "DSKULKARNI.NS": "D.S. Kulkarni Developers Limited",
        "GANESHHOUC.NS": "Ganesh Housing Corporation Limited",
        "GEECEE.NS": "GeeCee Ventures Limited",
        "GODREJPROP.NS": "Godrej Properties Limited",
        "HDIL.NS": "Housing Development and Infrastructure Limited",
        "HUBTOWN.NS": "Hubtown Limited",
        "KOLTEPATIL.NS": "Kolte-Patil Developers Limited",
        "LPDC.NS": "Landmark Property Development Company Limited",
        "MAHLIFE.NS": "Mahindra Lifespace Developers Limited",
        "MVL.NS": "MVL Limited",
        "NITESHEST.NS": "Nitesh Estates Limited",
        "OMAXE.NS": "Omaxe Limited",
        "ORBITCORP.NS": "Orbit Corporation Limited",
        "PENINLAND.NS": "Peninsula Land Limited",
        "PHOENIXLTD.NS": "The Phoenix Mills Limited",
        "PRAENG.NS": "Prajay Engineers Syndicate Limited",
        "PRESTIGE.NS": "Prestige Estates Projects Limited",
        "PROZONINTU.NS": "Prozone Intu Properties Limited",
        "PVP.NS": "PVP Ventures Limited",
        "SOBHA.NS": "Sobha Limited",
        "SUNTECK.NS": "Sunteck Realty Limited",
        "TCIDEVELOP.NS": "TCI Developers Limited",
        "TECHIN.NS": "Techindia Nirman Limited",
        "UNITECH.NS": "Unitech Limited",
        "VIPUL.NS": "Vipul Limited",
        "ZANDUREALT.NS": "Zandu Realty Limited",
        "PARSVNATH.NS": "Parsvnath Developers Limited",
        "VASCONEQ.NS": "Vascon Engineers Limited",
        "VIPULLTD.NS": "Vipul Limited"
    },

    "Recreational Goods, Other": {
        "ATLASCYCLE.NS": "Atlas Cycles (Haryana) Limited",
        "COX&KINGS.NS": "Cox & Kings Limited",
        "JINDALPHOT.NS": "Jindal Photo Limited",
        "KANANIIND.NS": "Kanani Industries Limited",
        "TALWALKARS.NS": "Talwalkars Better Value Fitness Limited",
        "THOMASCOOK.NS": "Thomas Cook (India) Limited",
        "WONDERLA.NS": "Wonderla Holidays Limited"
    },

    "Residential Construction": {
        "BDR.NS": "BDR Buildcon Limited",
        "VIJSHAN.NS": "Vijay Shanthi Builders Limited"
    },

    "Resorts & Casinos": {
        "CCHHL.NS": "Country Club Hospitality & Holidays Limited",
        "DELTACORP.NS": "Delta Corp Limited",
        "GIRRESORTS.NS": "GIR Natureview Resorts Limited",
        "MHRIL.NS": "Mahindra Holidays & Resorts India Limited"
    },

    "Restaurants": {
        "COFFEEDAY.NS": "Coffee Day Enterprises Limited",
        "JUBLFOOD.NS": "Jubilant FoodWorks Limited",
        "SPECIALITY.NS": "Speciality Restaurants Limited"
    },

    "Rubber & Plastics": {
        "APCOTEXIND.NS": "Apcotex Industries Limited",
        "APOLLOTYRE.NS": "Apollo Tyres Limited",
        "ASTRAL.NS": "Astral Poly Technik Limited",
        "BALKRISIND.NS": "Balkrishna Industries Limited",
        "CEATLTD.NS": "CEAT Limited",
        "ELGIRUBCO.NS": "Elgi Rubber Company Limited",
        "ESTER.NS": "Ester Industries Limited",
        "FLEXITUFF.NS": "Flexituff International Limited",
        "GRPLTD.NS": "GRP Limited",
        "JAICORPLTD.NS": "Jai Corp Limited",
        "JUBLINDS.NS": "Jubilant Industries Limited",
        "KEMROCK.NS": "Kemrock Industries and Exports Limited",
        "KESORAMIND.NS": "Kesoram Industries Limited",
        "MRF.NS": "MRF Limited",
        "NILKAMAL.NS": "Nilkamal Limited",
        "PITTILAM.NS": "Pitti Laminations Limited",
        "PREMIERPOL.NS": "Premier Polyfilm Ltd.",
        "RESPONIND.NS": "Responsive Industries Limited",
        "SIGNETIND.NS": "Signet Industries Limited",
        "SUPREMEIND.NS": "The Supreme Industries Limited",
        "TAINWALCHM.NS": "Tainwala Chemicals and Plastics (India) Limited",
        "TEXMOPIPES.NS": "Texmo Pipes and Products Limited",
        "TIJARIA.NS": "Tijaria Polypipes Limited",
        "TOKYOPLAST.NS": "Tokyo Plast International Limited",
        "TULSI.NS": "Tulsi Extrusions Limited",
        "TVSSRICHAK.NS": "TVS Srichakra"
    },

    "Scientific & Technical Instruments": {
        "BARTRONICS.NS": "Bartronics India Limited"
    },

    "Security & Protection Services": {
        "NITINFIRE.NS": "Nitin Fire Protection Industries Limited",
        "ZICOM.NS": "Zicom Electronic Security Systems Limited"
    },

    "Shipping": {
        "ADANIPORTS.NS": "Adani Ports and Special Economic Zone Limited",
        "DREDGECORP.NS": "Dredging Corporation of India Limited",
        "ESSARSHPNG.NS": "Essar Shipping Limited",
        "GESHIP.NS": "The Great Eastern Shipping Company Limited",
        "GLOBOFFS.NS": "Global Offshore Services Limited",
        "GPPL.NS": "Gujarat Pipavav Port Limited",
        "SCI.NS": "The Shipping Corporation of India Limited",
        "SEAMECLTD.NS": "Seamec Limited",
        "SHREYAS.NS": "Shreyas Shipping and Logistics Limited",
        "VARUNSHIP.NS": "Varun Shipping Co. Ltd."
    },

    "Specialty Chemicals": {
        "AARTIIND.NS": "Aarti Industries Limited",
        "AGARIND.NS": "Agarwal Industrial Corporation Ltd.",
        "AKZOINDIA.NS": "Akzo Nobel India Limited",
        "ALKALI.NS": "Alkali Metals Limited",
        "ALKYLAMINE.NS": "Alkyl Amines Chemicals Limited",
        "ASIANPAINT.NS": "Asian Paints Limited",
        "AVTNPL.NS": "AVT Natural Products Limited",
        "BALAMINES.NS": "Balaji Amines Limited",
        "BERGEPAINT.NS": "Berger Paints India Limited",
        "BODALCHEM.NS": "Bodal Chemicals Limited",
        "CASTROLIND.NS": "Castrol India Limited",
        "CHEMFALKAL.NS": "Chemfab Alkalis Limited",
        "CHROMATIC.NS": "Chromatic India Limited",
        "CLNINDIA.NS": "Clariant Chemicals (India) Limited",
        "EXCELINDUS.NS": "Excel Industries Limited",
        "GOACARBON.NS": "Goa Carbon Limited",
        "IGPL.NS": "I G Petrochemicals Limited",
        "IVP.NS": "IVP Limited",
        "JAYAGROGN.NS": "Jayant Agro-Organics Limited",
        "JINDALPOLY.NS": "Jindal Poly Films Limited",
        "KANSAINER.NS": "Kansai Nerolac Paints Limited",
        "KIRIINDUS.NS": "Kiri Industries Limited",
        "LINDEINDIA.NS": "Linde India Limited",
        "OMKARCHEM.NS": "Omkar Speciality Chemicals Limited",
        "ORIENTABRA.NS": "Orient Abrasives Limited",
        "PIDILITIND.NS": "Pidilite Industries Limited",
        "PLASTIBLEN.NS": "Plastiblends India Ltd.",
        "SHRIASTER.NS": "Shri Aster Silicates Limited",
        "SOTL.NS": "Savita Oil Technologies Limited",
        "SUDARSCHEM.NS": "Sudarshan Chemical Industries Limited",
        "TIRUMALCHM.NS": "Thirumalai Chemicals Limited",
        "VIKASECO.NS": "Vikas EcoTech Limited",
        "VINYLINDIA.NS": "Vinyl Chemicals India Ltd.",
        "VISHNU.NS": "Vishnu Chemicals Limited",
        "VIVIMEDLAB.NS": "Vivimed Labs Limited",
        "XPROINDIA.NS": "Xpro India Limited",
        "STYABS.NS": "INEOS Styrolution India Limited"
    },

    "Specialty Retail, Other": {
        "ARCHIES.NS": "Archies Limited"
    },

    "Staffing & Outsourcing Services": {
        "HGS.NS": "Hinduja Global Solutions Limited",
        "TEAMLEASE.NS": "TeamLease Services Limited"
    },

    "Steel & Iron": {
        "ADHUNIK.NS": "Adhunik Metaliks Limited",
        "ANKITMETAL.NS": "Ankit Metal & Power Limited",
        "APLAPOLLO.NS": "APL Apollo Tubes Limited",
        "BEDMUTHA.NS": "Bedmutha Industries Limited",
        "BHARATWIRE.NS": "Bharat Wire Ropes Limited",
        "BHUSANSTL.NS": "Bhushan Steel Limited",
        "ESL.NS": "Electrosteel Steels Limited",
        "GAL.NS": "Gyscoal Alloys Limited",
        "GALLANTT.NS": "Gallantt Metal Limited",
        "GALLISPAT.NS": "Gallantt Ispat Limited",
        "GPIL.NS": "Godawari Power & Ispat Limited",
        "IMFA.NS": "Indian Metals and Ferro Alloys Limited",
        "ISMTLTD.NS": "ISMT Limited",
        "JAIBALAJI.NS": "Jai Balaji Industries Limited",
        "JAYNECOIND.NS": "Jayaswal Neco Industries Limited",
        "JINDALSAW.NS": "Jindal Saw Limited",
        "JINDALSTEL.NS": "Jindal Steel & Power Limited",
        "JSL.NS": "Jindal Stainless Limited",
        "JSLHISAR.NS": "Jindal Stainless (Hisar) Limited",
        "KAMDHENU.NS": "Kamdhenu Limited",
        "KSL.NS": "Kalyani Steels Limited",
        "MAHSEAMLES.NS": "Maharashtra Seamless Limited",
        "MAITHANALL.NS": "Maithan Alloys Limited",
        "MANINDS.NS": "Man Industries (India) Limited",
        "MONNETISPA.NS": "Monnet Ispat and Energy Limited",
        "MSPL.NS": "MSP Steel & Power Limited",
        "MUKANDLTD.NS": "Mukand Limited",
        "NATNLSTEEL.NS": "National Steel and Agro Industries Limited",
        "NMDC.NS": "NMDC Limited",
        "OISL.NS": "OCL Iron & Steel Limited",
        "PENIND.NS": "Pennar Industries Limited",
        "PRAKASH.NS": "Prakash Industries Limited",
        "PRAKASHSTL.NS": "Prakash Steelage Limited",
        "RAMASTEEL.NS": "Rama Steel Tubes Limited",
        "RAMSARUP.NS": "Ramsarup Industries Limited",
        "RATNAMANI.NS": "Ratnamani Metals & Tubes Limited",
        "SAIL.NS": "Steel Authority of India Limited",
        "SALSTEEL.NS": "S.A.L. Steel Limited",
        "SARDAEN.NS": "Sarda Energy & Minerals Limited",
        "SATHAISPAT.NS": "Sathavahana Ispat Limited",
        "SHAHALLOYS.NS": "Shah Alloys Limited",
        "SMPL.NS": "Splendid Metal Products Limited",
        "SUJANAUNI.NS": "Sujana Universal Industries Limited",
        "SUNFLAG.NS": "Sunflag Iron And Steel Company Limited",
        "SURANAIND.NS": "Surana Industries Limited",
        "SURYAROSNI.NS": "Surya Roshni Limited",
        "TATAMETALI.NS": "Tata Metaliks Limited",
        "TATASPONGE.NS": "Tata Sponge Iron Limited",
        "TATASTEEL.NS": "Tata Steel Limited",
        "TINPLATE.NS": "The Tinplate Company Of India Limited",
        "USHAMART.NS": "Usha Martin Limited",
        "UTTAMSTL.NS": "Uttam Galva Steels Limited",
        "UTTAMVALUE.NS": "Uttam Value Steels Limited",
        "VASWANI.NS": "Vaswani Industries Limited",
        "VISASTEEL.NS": "VISA Steel Limited",
        "VSSL.NS": "Vardhman Special Steels Limited",
        "WELCORP.NS": "Welspun Corp Limited",
        "JSWSTEEL.NS": "JSW Steel Limited",
        "HCIL.NS": "Himadri Speciality Chemical Limited",
        "KIL.NS": "Kamdhenu Limited",
        "SOUISPAT.NS": "Southern Ispat & Energy Limited"
    },

    "Technical & System Software": {
        "8KMILES.NS": "8K Miles Software Services Limited",
        "BGLOBAL.NS": "Bharatiya Global Infomedia Limited",
        "CALSOFT.NS": "California Software Company Limited",
        "FINANTECH.NS": "63 Moons Technologies Limited",
        "ICSA.NS": "ICSA (India) Limited",
        "KERNEX.NS": "Kernex Microsystems (India) Limited",
        "MEGASOFT.NS": "Megasoft Limited",
        "RSSOFTWARE.NS": "R. S. Software (India) Limited",
        "SASKEN.NS": "Sasken Technologies Limited",
        "SQSBFSI.NS": "SQS India BFSI Limited",
        "SUBEX.NS": "Subex Limited",
        "TANLA.NS": "Tanla Solutions Limited",
        "TATAELXSI.NS": "Tata Elxsi Limited",
        "TRIGYN.NS": "Trigyn Technologies Limited",
        "VAKRANGEE.NS": "Vakrangee Limited",
        "ZYLOG.NS": "Zylog Systems Limited"
    },

    "Textile - Apparel Clothing": {
        "ABFRL.NS": "Aditya Birla Fashion and Retail Limited",
        "AIFL.NS": "Ashapura Intimates Fashion Limited",
        "BANG.NS": "Bang Overseas Limited",
        "CANTABIL.NS": "Cantabil Retail India Limited",
        "CELEBRITY.NS": "Celebrity Fashions Limited",
        "GOKEX.NS": "Gokaldas Exports Limited",
        "INDTERRAIN.NS": "Indian Terrain Fashions Limited",
        "INTEGRA.NS": "Integra Garments and Textiles Limited",
        "KITEX.NS": "Kitex Garments Limited",
        "KKCL.NS": "Kewal Kiran Clothing Limited",
        "KPRMILL.NS": "K.P.R. Mill Limited",
        "LOVABLE.NS": "Lovable Lingerie Limited",
        "LUXIND.NS": "Lux Industries Limited",
        "MANDHANA.NS": "Mandhana Industries Limited",
        "MONTECARLO.NS": "Monte Carlo Fashions Limited",
        "PAGEIND.NS": "Page Industries Limited",
        "PDSMFL.NS": "PDS Multinational Fashions Limited",
        "PGIL.NS": "Pearl Global Industries Limited",
        "PROVOGE.NS": "Provogue (India) Limited",
        "RUPA.NS": "Rupa & Company Limited",
        "SELMCL.NS": "SEL Manufacturing Company Limited",
        "SPLIL.NS": "SPL Industries Limited",
        "SUDAR.NS": "Sudar Industries Limited",
        "THOMASCOTT.NS": "Thomas Scott (India) Limited",
        "ZODIACLOTH.NS": "Zodiac Clothing Company Limited",
        "PFRL.NS": "Aditya Birla Fashion and Retail Limited"
    },

    "Textile - Apparel Footwear & Accessories": {
        "BANARBEADS.NS": "Banaras Beads Limited",
        "BATAINDIA.NS": "Bata India Limited",
        "BIL.NS": "Bhartiya International Limited",
        "LIBERTSHOE.NS": "Liberty Shoes Limited",
        "MIRZAINT.NS": "Mirza International Limited",
        "RELAXO.NS": "Relaxo Footwears Limited",
        "SREEL.NS": "Sreeleathers Limited",
        "SUPERHOUSE.NS": "Superhouse Limited",
        "VIPIND.NS": "VIP Industries Limited"
    },

    "Textile Industrial": {
        "AARVEEDEN.NS": "Aarvee Denims and Exports Limited",
        "AICHAMP.NS": "AI Champdany Industries Limited",
        "ALOKTEXT.NS": "Alok Industries Limited",
        "ALPSINDUS.NS": "Alps Industries Limited",
        "AMBIKCO.NS": "Ambika Cotton Mills Limited",
        "ARROWTEX.NS": "Arrow Textiles Limited",
        "ARVIND.NS": "Arvind Limited",
        "ASHIMASYN.NS": "Ashima Limited",
        "ASIL.NS": "Amit Spinning Industries Limited",
        "AYMSYNTEX.NS": "AYM Syntex Limited",
        "BANSWRAS.NS": "Banswara Syntex Limited",
        "BASML.NS": "Bannari Amman Spinning Mills Limited",
        "BIRLACOT.NS": "Birla Cotsyn (India) Limited",
        "BOMDYEING.NS": "The Bombay Dyeing and Manufacturing Company Limited",
        "BSL.NS": "BSL Limited",
        "CENTENKA.NS": "Century Enka Limited",
        "CNOVAPETRO.NS": "CIL Nova Petrochemicals Limited",
        "DCM.NS": "DCM Limited",
        "DONEAR.NS": "Donear Industries Limited",
        "EASTSILK.NS": "Eastern Silk Industries Limited",
        "ELAND.NS": "E-Land Apparel Limited",
        "EUROTEXIND.NS": "Eurotex Industries and Exports Limited",
        "FILATEX.NS": "Filatex India Limited",
        "FIRSTWIN.NS": "First Winner Industries Limited",
        "GANGOTRI.NS": "Gangotri Textiles Limited",
        "GARDENSILK.NS": "Garden Silk Mills Limited",
        "GARWALLROP.NS": "Garware-Wall Ropes Limited",
        "GILLANDERS.NS": "Gillanders Arbuthnot and Company Limited",
        "GINNIFILA.NS": "Ginni Filaments Limited",
        "GTNTEX.NS": "GTN Textiles Limited",
        "HANUNG.NS": "Hanung Toys and Textiles Limited",
        "HIMATSEIDE.NS": "Himatsingka Seide Limited",
        "HINDSYNTEX.NS": "Hind Syntex Limited",
        "ICIL.NS": "Indo Count Industries Limited",
        "INDIANCARD.NS": "The Indian Card Clothing Company Limited",
        "INDORAMA.NS": "Indo Rama Synthetics (India) Limited",
        "JBFIND.NS": "JBF Industries Limited",
        "JINDCOT.NS": "Jindal Cotex Limited",
        "JINDWORLD.NS": "Jindal Worldwide Limited",
        "LAMBODHARA.NS": "Lambodhara Textiles Limited",
        "MALWACOTT.NS": "Malwa Cotton Spinning Mills Limited",
        "MARALOVER.NS": "Maral Overseas Limited",
        "MAYURUNIQ.NS": "Mayur Uniquoters Limited",
        "MOHITIND.NS": "Mohit Industries Limited",
        "MORARJEE.NS": "Morarjee Textiles Limited",
        "NAGREEKEXP.NS": "Nagreeka Exports Limited",
        "NAHARINDUS.NS": "Nahar Industrial Enterprises Limited",
        "NAHARSPING.NS": "Nahar Spinning Mills Ltd",
        "NAKODA.NS": "Nakoda Limited",
        "NDL.NS": "Nandan Denim Limited",
        "NITINSPIN.NS": "Nitin Spinners Ltd.",
        "ORBTEXP.NS": "Orbit Exports Limited",
        "PARASPETRO.NS": "Paras Petrofils Ltd",
        "PATSPINLTD.NS": "Patspin India Limited",
        "PIONEEREMB.NS": "Pioneer Embroideries Limited",
        "PRADIP.NS": "Pradip Overseas Limited",
        "PRECOT.NS": "Precot Meridian Limited",
        "RAIREKMOH.NS": "The Rai Saheb Rekhchand Mohota Spinning & Weaving Mills Ltd.",
        "RAJRAYON.NS": "Raj Rayon Industries Limited",
        "RAJVIR.NS": "Rajvir Industries Limited",
        "RAYMOND.NS": "Raymond Limited",
        "RSWM.NS": "RSWM Limited",
        "RUBYMILLS.NS": "The Ruby Mills Limited",
        "SALONACOT.NS": "Salona Cotspin Limited",
        "SANGAMIND.NS": "Sangam (India) Limited",
        "SARLAPOLY.NS": "Sarla Performance Fibers Limited",
        "SGL.NS": "STL Global Limited",
        "SHIVTEX.NS": "Shiva Texyarn Limited",
        "SIL.NS": "Standard Industries Limited",
        "SIYSIL.NS": "Siyaram Silk Mills Limited",
        "SOMATEX.NS": "Soma Textiles & Industries Limited",
        "SPENTEX.NS": "Spentex Industries Limited",
        "SPYL.NS": "Shekhawati Poly-Yarn Limited",
        "SRF.NS": "SRF Limited",
        "STINDIA.NS": "STI India Limited",
        "SUMEETINDS.NS": "Sumeet Industries Limited.",
        "SUPERSPIN.NS": "Super Spinning Mills Limited",
        "SUPREMETEX.NS": "Supreme Tex Mart Limited",
        "SURYAJYOTI.NS": "Suryajyoti Spinning Mills Limited",
        "SURYALAXMI.NS": "Suryalakshmi Cotton Mills Limited",
        "SUTLEJTEX.NS": "Sutlej Textiles and Industries Limited",
        "SWANENERGY.NS": "Swan Energy Limited",
        "TRIDENT.NS": "Trident Limited",
        "TTL.NS": "T.T. Limited",
        "VARDHACRLC.NS": "Vardhman Acrylics Limited",
        "VARDMNPOLY.NS": "Vardhman Polytex Limited",
        "VIVIDHA.NS": "Visagar Polytex Limited",
        "VTL.NS": "Vardhman Textiles Limited",
        "WEIZMANIND.NS": "Weizmann Limited",
        "WELINV.NS": "Welspun Investments and Commercials Limited",
        "WELSPUNIND.NS": "Welspun India Limited",
        "WINSOME.NS": "Winsome Yarns Limited",
        "ZENITHEXPO.NS": "Zenith Exports Limited",
        "SHLAKSHMI.NS": "Shri Lakshmi Cotsyn Limited",
        "GTNIND.NS": "GTN Industries Limited",
        "WELPROJ.NS": "Welspun Enterprises Limited",
        "WELSYNTEX.NS": "Welspun Syntex"
    },

    "Tobacco Products, Other": {
        "GODFRYPHLP.NS": "Godfrey Phillips India Limited",
        "GOLDENTOBC.NS": "Golden Tobacco Limited",
        "ITC.NS": "ITC Limited",
        "VSTIND.NS": "VST Industries Limited"
    },

    "Trucking": {
        "VRLLOG.NS": "VRL Logistics Limited"
    },

    "Waste Management": {
        "GANECOS.NS": "Ganesha Ecosphere Limited",
        "WABAG.NS": "VA Tech Wabag Limited"
    },

    "Wireless Communications": {
        "BHARTIARTL.NS": "Bharti Airtel Limited",
        "IDEA.NS": "Idea Cellular Limited",
        "INFRATEL.NS": "Bharti Infratel Limited",
        "MTNL.NS": "Mahanagar Telephone Nigam Limited",
        "NUTEK.NS": "Nu Tek India Limited",
        "ONMOBILE.NS": "OnMobile Global Limited",
        "RCOM.NS": "Reliance Communications Limited",
        "TATACOMM.NS": "Tata Communications Limited",
        "TTML.NS": "Tata Teleservices (Maharashtra) Limited",
        "TULIP.NS": "Tulip Telecom Limited"
    },

    "Exchange Traded Funds (ETFs)": {
        "AXISGOLD.NS": "Axis Gold ETF",
        "BANKBEES.NS": "Goldman Sachs Bank BeES ETF",
        "EBANK.NS": "Edelweiss ETF - Nifty Bank",
        "GOLDBEES.NS": "Goldman Sachs Gold BeES ETF",
        "GOLDSHARE.NS": "UTI Gold ETF",
        "HNGSNGBEES.NS": "Goldman Sachs Hang Seng BeES ETF",
        "ICNX100.NS": "ICICI Prudential Nifty100 ETF",
        "IDBIGOLD.NS": "IDBI Gold ETF",
        "IGOLD.NS": "ICICI Prudential GOLD ETF",
        "INFRABEES.NS": "RELIANCE NIPPON LIFE Infrastructure ETF",
        "INIFTY.NS": "ICICI Prudential Nifty ETF",
        "IPGETF.NS": "ICICI Prudential GOLD ETF",
        "ISENSEX.NS": "ICICI Prudential Sensex ETF",
        "JUNIORBEES.NS": "Goldman Sachs Junior BeES ETF",
        "KOTAKBKETF.NS": "Kotak Banking ETF",
        "KOTAKGOLD.NS": "Kotak Gold ETF",
        "KOTAKNIFTY.NS": "Kotak Nifty ETF",
        "KOTAKNV20.NS": "Kotak NV 20 ETF",
        "KOTAKPSUBK.NS": "Kotak PSU Bank ETF",
        "LIQUIDBEES.NS": "Goldman Sachs Liquid BeES ETF",
        "M100.NS": "Motilal Oswal MOSt Shares Midcap 100 ETF",
        "M50.NS": "Motilal Oswal MOSt Shares M50 ETF",
        "N100.NS": "Motilal Oswal MOSt Shares NASDAQ 100 ETF",
        "NIFTYBEES.NS": "Goldman Sachs Nifty BeES ETF",
        "NIFTYEES.NS": "Edelweiss ETF - Nifty 50",
        "PSUBNKBEES.NS": "Goldman Sachs PSU Bank BeES ETF",
        "QGOLDHALF.NS": "Quantum Gold ETF",
        "QNIFTY.NS": "Quantum Index ETF",
        "RELBANK.NS": "R* Shares Banking ETF",
        "RELCNX100.NS": "R* Shares CNX 100 ETF",
        "RELCONS.NS": "R*Shares Consumption ETF",
        "RELDIVOPP.NS": "R*Shares Dividend Opportunities ETF",
        "RELGOLD.NS": "R* Shares Gold ETF",
        "RELGRNIFTY.NS": "Invesco India Nifty ETF",
        "RELIGAREGO.NS": "Invesco India Gold ETF",
        "RELNIFTY.NS": "R* Shares Nifty ETF",
        "RELNV20.NS": "R*Shares NV20 ETF",
        "SHARIABEES.NS": "Goldman Sachs Shariah BeES ETF",
        "UTINIFTETF.NS": "UTI Nifty ETF",
        "UTISENSETF.NS": "UTI Sensex ETF",
        "BSLGOLDETF.NS": "Birla Sun Life Gold ETF",
        "BSLNIFTY.NS": "Birla Sun Life Nifty ETF",
        "CPSEETF.NS": "Goldman Sachs CPSE ETF",
        "CRMFGETF.NS": "Canara Robeco Gold ETF",
        "HDFCMFGETF.NS": "HDFC Gold ETF",
        "HDFCNIFETF.NS": "HDFC Nifty ETF",
        "HDFCSENETF.NS": "HDFC Sensex ETF",
        "LICNFENGP.NS": "LIC MF ETF Nifty 50",
        "SETFBANK.NS": "SBI ETF Bank",
        "SETFGOLD.NS": "SBI MUTUAL FUND SBI-ETF GOLD",
        "SETFNIF50.NS": "SBI MUTUAL FUND SBI-ETF NIFTY 50",
        "SETFNIFBK.NS": "SBI MUTUAL FUND SBI-ETF NIFTY BANK",
        "SETFNIFJR.NS": "SBI ETF Nifty Next 50",
        "SETFNIFTY.NS": "SBI ETF Nifty 50",
        "SETFNN50.NS": "SBI MUTUAL FUND SBI-ETF NIFTY NEXT 50"
    },

    "Diversified": {
        "ABCIL.NS": "Aditya Birla Chemicals (India) Limited",
        "ABHISHEK.NS": "Abhishek Corporation Ltd",
        "ADI.NS": "ADI Finechem Limited",
        "ADVANTA.NS": "Advanta Limited",
        "AEGISCHEM.NS": "Aegis Logistics Limited",
        "AFTEK.NS": "Aftek Limited",
        "AIL.NS": "GE Power India Limited",
        "ALSTOMT&D.NS": "GE T&D India Limited",
        "AMTEKINDIA.NS": "Amtek India Limited",
        "ARVINDREM.NS": "Arvind Remedies Limited",
        "ARVINFRA.NS": "Arvind SmartSpaces Limited",
        "ASIANELEC.NS": "Asian Electronics Limited",
        "BLUEBLENDS.NS": "Blue Blends (India) Limited",
        "BLUESTINFO.NS": "Blue Star Infotech Ltd.",
        "BRANDHOUSE.NS": "Brandhouse Retails Limited",
        "BROADCAST.NS": "Broadcast Initiatives Limited",
        "BRFL.NS": "Bombay Rayon Fashions Limited",
        "CAMLINFINE.NS": "Camlin Fine Sciences Limited",
        "CAPLIPOINT.NS": "Caplin Point Laboratories Limited",
        "CLASSIC.NS": "Classic Diamonds (India) Limited",
        "CMAHENDRA.NS": "C. Mahendra Exports Limited",
        "CROMPGREAV.NS": "CG Power and Industrial Solutions Limited",
        "DECOLIGHT.NS": "Decolight Ceramics Ltd.",
        "DIGJAM.NS": "Digjam Limited",
        "DTIL.NS": "Dhunseri Tea & Industries Limited",
        "DUNCANSLTD.NS": "Duncans Industries Limited",
        "DYNATECH.NS": "Ducon Infratechnolgies Limited",
        "ELITE.NS": "Elite Conductors Limited",
        "ENTEGRA.NS": "Entegra Limited",
        "ERAINFRA.NS": "Era Infra Engineering Limited",
        "EXCELINFO.NS": "Excel Realty N Infra Limited",
        "FCEL.NS": "Future Consumer Limited",
        "FCL.NS": "Fineotex Chemical Limited",
        "FEDDERLOYD.NS": "Fedders Electric and Engineering Limited",
        "FIRSTLEASE.NS": "First Leasing Company of India Limited",
        "FRL.NS": "Future Enterprises Limited",
        "FRLDVR.NS": "Future Enterprises Limited DVR",
        "GENECOS.NS": "Ganesha Ecosphere Limited",
        "GOCLCORP.NS": "GOCL Corporation Limited",
        "IBWSL.NS": "SORIL Holdings and Ventures Limited",
        "INNOIND.NS": "Innoventive Industries Limited",
        "JEYPORE.NS": "Jeypore Sugar Company Ltd.",
        "JCTEL.NS": "JCT Electronics Limited",
        "JKTYRE.NS": "JK Tyre & Industries Limited",
        "JUMBO.NS": "Jumbo Bag Limited",
        "KALINDEE.NS": "Kalindee Rail Nirman (Engineers) Limited",
        "KBIL.NS": "Kirloskar Brothers Investments Ltd.",
        "KESARENT.NS": "Kesar Enterprises Limited",
        "KITPLYIND.NS": "Kitply Industries Limited",
        "KRIDHANINF.NS": "Kridhan Infra Limited",
        "KRISHNAENG.NS": "Krishna Engineering Works Limited",
        "LAKSHMIEFL.NS": "Lakshmi Energy & Foods Limited",
        "LINCPEN.NS": "Linc Pen & Plastics Limited",
        "LLOYDELENG.NS": "LEEL Electricals Limited",
        "LLOYDFIN.NS": "Lloyds Finance Limited",
        "MAXWELL.NS": "VIP Clothing Limited",
        "MMNL.NS": "Mig Media Neurons Limited",
        "MOLDTKPAC.NS": "Mold-Tek Packaging Limited",
        "MURLIIND.NS": "Murli Industries Ltd.",
        "NAGREEKCAP.NS": "Nagreeka Capital & Infrastructure Limited",
        "NGCT.NS": "Spacenet Enterprises India Limited",
        "NILAINFRA.NS": "Nila Infrastructures Limited",
        "OCCL.NS": "Oriental Carbon & Chemicals Limited",
        "ORTINLABSS.NS": "Ortin Laboratories Limited",
        "PALREDTECH.NS": "Palred Technologies Limited",
        "PARAL.NS": "Parekh Aluminium Limited",
        "PDPL.NS": "Parenteral Drugs (India) Limited",
        "PEPL.NS": "Pearl Engineering Polymers Limited",
        "PILIND.NS": "PIL Italica Lifestyle Limited",
        "PNEUMATIC.NS": "Pneumatic Holdings Limited",
        "PRITHVISO.NS": "Prithvi Softech Limited",
        "RAJPALAYA.NS": "Rajapalayam Mills Ltd.",
        "RANBAXY.NS": "Ranbaxy Laboratories Ltd.",
        "RANKLIN.NS": "Ranklin Solutions Ltd.",
        "SAGCEM.NS": "Sagar Cements Limited",
        "SALZERELEC.NS": "Salzer Electronics Limited",
        "SAMBANDAM.NS": "Sambandam Spinning Mills Ltd.",
        "SAMINDUS.NS": "Sam Industries Ltd",
        "SARTHAKIND.NS": "Sarthak Industries Ltd",
        "SAVERA.NS": "Savera Industries Limited",
        "SB&TINTL.NS": "SB & T International Limited",
        "SHARDAMOTR.NS": "Sharda Motor Industries Limited",
        "SHIV-VANI.NS": "SVOGL Oil Gas and Energy Limited",
        "SHYAMCENT.NS": "Shyam Century Ferrous Limited",
        "SKUMARSYNF.NS": "S Kumars Nationwide Limited",
        "SKUMARSYN.NS": "S. Kumars Nationwide Ltd.",
        "SOLARINDS.NS": "Solar Industries India Limited",
        "SPECTACLE.NS": "Spectacle Ventures Limited",
        "SRGINFOTEC.NS": "PAN India Corporation Limited",
        "SSLT.NS": "Vedanta Limited",
        "STOREONE.NS": "SORIL Infra Resources Limited",
        "SUJANATWR.NS": "Neueon Towers Limited",
        "SUPER.NS": "Super Sales India Ltd.",
        "SURYAPHARM.NS": "Surya Pharmaceutical Limited",
        "TCPLTD.NS": "TCP Limited",
        "TECPRO.NS": "Tecpro Systems Limited",
        "TIMBOR.NS": "Timbor Home Limited",
        "TPLPLASTEH.NS": "TPL Plastech Limited",
        "UBENGG.NS": "UB Engineering Limited",
        "UNIENTER.NS": "Uniphos Enterprises Ltd.",
        "VARUN.NS": "Varun Industries Limited",
        "VENKEYS.NS": "Venky's (India) Limited",
        "VIKASHMET.NS": "Vikas Global One Limited",
        "VTMLTD.NS": "VTM Limited",
        "WSI.NS": "WS Industries (India)",
        "ZENITHCOMP.NS": "Zenith Computers Limited",
        "CIMMCO.NS": "Cimmco Limited",
        "NEYVELILIG.NS": "Neyveli Lignite Corporation Limited",
        "BIRLAPOWER.NS": "Birla Power Solutions Limited",
        "HECINFRA.NS": "HEC Infra Projects Limited",
        "HITECHPLAS.NS": "Hitech Corporation Limited"
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
        number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "PE Multiple", 'font': {'size': 16, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#7c3aed", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=1)
    
    # EV/EBITDA Gauge
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=upside_ev if upside_ev else 0,
        number={'suffix': "%", 'font': {'size': 36, 'color': '#e2e8f0', 'family': 'Inter'}},
        delta={'reference': 0, 'increasing': {'color': "#34d399"}, 'decreasing': {'color': "#f87171"}},
        title={'text': "EV/EBITDA", 'font': {'size': 16, 'color': '#a78bfa', 'family': 'Inter'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 2, 'tickcolor': "#64748b", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': "#ec4899", 'thickness': 0.75},
            'bgcolor': "#1e1b4b",
            'borderwidth': 2,
            'bordercolor': "#4c1d95",
            'steps': [
                {'range': [-50, -20], 'color': '#7f1d1d'},
                {'range': [-20, 0], 'color': '#78350f'},
                {'range': [0, 20], 'color': '#14532d'},
                {'range': [20, 50], 'color': '#065f46'}
            ],
            'threshold': {
                'line': {'color': "#f472b6", 'width': 4},
                'thickness': 0.8,
                'value': 0
            }
        }
    ), row=1, col=2)
    
    fig.update_layout(
        height=350,
        margin=dict(l=30, r=30, t=60, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': '#e2e8f0'}
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
            color='#6366f1',
            line=dict(color='#818cf8', width=2),
        ),
        text=[f'₹{v:,.2f}' for v in current_vals],
        textposition='outside',
        textfont=dict(size=14, color='#e2e8f0', family='JetBrains Mono')
    ))
    
    # Fair Value bars
    colors = ['#34d399' if fv > cv else '#f87171' for fv, cv in zip(fair_vals, current_vals)]
    fig.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair_vals,
        marker=dict(
            color=colors,
            line=dict(color=['#6ee7b7' if c == '#34d399' else '#fca5a5' for c in colors], width=2),
        ),
        text=[f'₹{v:,.2f}' for v in fair_vals],
        textposition='outside',
        textfont=dict(size=14, color='#e2e8f0', family='JetBrains Mono')
    ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', size=12, color='#e2e8f0'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color='#e2e8f0')
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#4c1d95',
            tickfont=dict(size=14, color='#e2e8f0')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(167, 139, 250, 0.2)',
            showline=False,
            tickprefix='₹',
            tickfont=dict(size=12, color='#a78bfa')
        ),
        margin=dict(l=60, r=40, t=60, b=40)
    )
    
    return fig

def create_52week_range_display(vals):
    """Create 52-week price range display using HTML/CSS instead of Plotly"""
    low = vals.get('52w_low', 0)
    high = vals.get('52w_high', 0)
    current = vals.get('price', 0)
    
    if not all([low, high, current]) or high <= low:
        return None
    
    # Calculate position percentage
    position = ((current - low) / (high - low)) * 100
    position = max(0, min(100, position))  # Clamp between 0-100
    
    html = f'''
    <div class="range-card">
        <div class="range-header">
            <div class="range-low">52W Low: ₹{low:,.2f}</div>
            <div class="range-high">52W High: ₹{high:,.2f}</div>
        </div>
        <div class="range-bar-container">
            <div class="range-bar-fill" style="width: {position}%;"></div>
        </div>
        <div class="range-current">
            Current Price: <span>₹{current:,.2f}</span> ({position:.1f}% of range)
        </div>
    </div>
    '''
    return html

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
        fillcolor='rgba(124, 58, 237, 0.3)',
        line=dict(color='#a78bfa', width=2),
        marker=dict(size=8, color='#c4b5fd')
    ))
    
    # Add benchmark line
    fig.add_trace(go.Scatterpolar(
        r=[50, 50, 50, 50, 50, 50],
        theta=categories + [categories[0]],
        fill='none',
        line=dict(color='#6366f1', width=2, dash='dash'),
        name='Benchmark'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                gridcolor='rgba(167, 139, 250, 0.2)',
                linecolor='rgba(167, 139, 250, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#a78bfa'),
                linecolor='rgba(167, 139, 250, 0.3)',
                gridcolor='rgba(167, 139, 250, 0.2)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        height=350,
        margin=dict(l=60, r=60, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0')
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
    <p>📊 2800+Stocks | Professional Multi-Factor Analysis | Real-Time Data</p>
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
    
    # Company Header - FIXED VISIBILITY
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
            rec_class, rec_text, rec_icon = "rec-strong-buy", "Highly Undervalued", "🚀"
        elif avg_up > 15:
            rec_class, rec_text, rec_icon = "rec-buy", "Undervalued", "✅"
        elif avg_up > 0:
            rec_class, rec_text, rec_icon = "rec-buy", "Fairly Valued", "📥"
        elif avg_up > -10:
            rec_class, rec_text, rec_icon = "rec-hold", "HOLD", "⏸️"
        else:
            rec_class, rec_text, rec_icon = "rec-avoid", "Overvalued", "⚠️"
        
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
        range_html = create_52week_range_display(vals)
        if range_html:
            st.markdown(range_html, unsafe_allow_html=True)
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
        if vals['fair_value_pe'] and vals['trailing_pe']:
            upside_color = '#34d399' if vals['upside_pe'] and vals['upside_pe'] > 0 else '#f87171'
            fair_color = '#34d399' if vals['fair_value_pe'] > vals['price'] else '#f87171'
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
                    <span class="method-value" style="color: {fair_color}">₹{vals['fair_value_pe']:,.2f}</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Upside (PE)</span>
                    <span class="method-value" style="color: {upside_color}">{vals['upside_pe']:+.2f}%</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.info("PE valuation not available")
    
    with val_col2:
        if vals['fair_value_ev'] and vals['current_ev_ebitda']:
            upside_color_ev = '#34d399' if vals['upside_ev'] and vals['upside_ev'] > 0 else '#f87171'
            fair_color_ev = '#34d399' if vals['fair_value_ev'] > vals['price'] else '#f87171'
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
                    <span class="method-value" style="color: {fair_color_ev}">₹{vals['fair_value_ev']:,.2f}</span>
                </div>
                <div class="method-row">
                    <span class="method-label">Upside (EV)</span>
                    <span class="method-value" style="color: {upside_color_ev}">{vals['upside_ev']:+.2f}%</span>
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
