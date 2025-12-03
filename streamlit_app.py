import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
from functools import wraps

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
# AUTHENTICATION
# ============================================================================

def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        
        users = {
            "demo": "demo123",
            "premium": "nyztrade12345",
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
# ENHANCED CUSTOM CSS - PROFESSIONAL DESIGN
# ============================================================================

st.markdown("""
<style>
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
    }
    
    /* Fair Value Highlight Box */
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
    
    /* Recommendation Cards */
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
    
    /* Risk Warning */
    .risk-warning {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 5px 20px rgba(255, 107, 107, 0.3);
    }
    
    /* Info Cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    /* Comparison Table */
    .comparison-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    /* Metrics Card */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(240, 147, 251, 0.2);
    }
    
    /* Button Styling */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# EXPANDED MIDCAP STOCK DATABASE - 800+ STOCKS
# ============================================================================

MIDCAP_500_STOCKS = {
    "🏦 Banking & Finance (80+)": {
        # NBFCs & Finance
        "ANGELONE.NS": "Angel One", "ANANDRATHI.NS": "Anand Rathi", "AAVAS.NS": "Aavas Financiers",
        "BAJAJFINSV.NS": "Bajaj Finserv", "CDSL.NS": "CDSL", "CHOLAFIN.NS": "Cholamandalam Investment",
        "CREDITACC.NS": "CreditAccess Grameen", "CRISIL.NS": "CRISIL", "CSB.NS": "CSB Bank",
        "EQUITAS.NS": "Equitas Holdings", "FEDERALBNK.NS": "Federal Bank", "FINOPB.NS": "Fino Payments",
        "HDFCAMC.NS": "HDFC AMC", "IIFL.NS": "IIFL Finance", "IIFLSEC.NS": "IIFL Securities",
        "IRFC.NS": "IRFC", "ISEC.NS": "ICICI Securities", "JMFINANCIL.NS": "JM Financial",
        "KALYANKJIL.NS": "Kalyan Jewellers", "KFINTECH.NS": "KFin Technologies", "LICHSGFIN.NS": "LIC Housing",
        "MASFIN.NS": "MAS Financial", "MOTILALOFS.NS": "Motilal Oswal", "MUTHOOTFIN.NS": "Muthoot Finance",
        "PNBHOUSING.NS": "PNB Housing", "RBL.NS": "RBL Bank", "SBFC.NS": "SBFC Finance",
        "STARHEALTH.NS": "Star Health", "UJJIVAN.NS": "Ujjivan Small Finance", "UTIAMC.NS": "UTI AMC",
        # Banks
        "AUBANK.NS": "AU Small Finance", "BANDHANBNK.NS": "Bandhan Bank", "IDFCFIRSTB.NS": "IDFC First Bank",
        "INDUSINDBK.NS": "IndusInd Bank", "BANKBARODA.NS": "Bank of Baroda", "CANBK.NS": "Canara Bank",
        "UNIONBANK.NS": "Union Bank", "CENTRALBK.NS": "Central Bank", "INDIANB.NS": "Indian Bank",
        "IOB.NS": "Indian Overseas Bank", "BANKINDIA.NS": "Bank of India", "MAHABANK.NS": "Bank of Maharashtra",
        "J&KBANK.NS": "Jammu & Kashmir Bank", "KARNATBNK.NS": "Karnataka Bank", "DCBBANK.NS": "DCB Bank",
        # Insurance & Asset Management
        "ICICIGI.NS": "ICICI Lombard", "ICICIPRULI.NS": "ICICI Prudential Life", "SBILIFE.NS": "SBI Life",
        "HDFCLIFE.NS": "HDFC Life", "MAXHEALTH.NS": "Max Healthcare", "POLICYBZR.NS": "PB Fintech",
        "NUVOCO.NS": "Nuvoco Vistas", "SPANDANA.NS": "Spandana Sphoorty", "SWANENERGY.NS": "Swan Energy",
        # Investment & Holding Companies
        "BAJAJHLDNG.NS": "Bajaj Holdings", "MAHLIFE.NS": "Mahindra Lifespace", "TATAINVEST.NS": "Tata Investment",
        "SUNDARMFIN.NS": "Sundaram Finance", "SHRIRAMFIN.NS": "Shriram Finance", "MANAPPURAM.NS": "Manappuram Finance",
        "PNBGILTS.NS": "PNB Gilts", "APTUS.NS": "Aptus Value Housing", "HOMEFIRST.NS": "Home First Finance",
        "AADHARHFC.NS": "Aadhar Housing", "CAPLIPOINT.NS": "Caplin Point", "CHOLA.NS": "Cholamandalam Financial",
        "CIEINDIA.NS": "CIE Automotive", "JSWHL.NS": "JSW Holdings", "MUTHOOTCAP.NS": "Muthoot Capital"
    },
    
    "💻 IT & Technology (90+)": {
        # IT Services & Consulting
        "COFORGE.NS": "Coforge", "CYIENT.NS": "Cyient", "ECLERX.NS": "eClerx Services",
        "HAPPSTMNDS.NS": "Happiest Minds", "INTELLECT.NS": "Intellect Design", "KPITTECH.NS": "KPIT Technologies",
        "LTIM.NS": "LTIMindtree", "MASTEK.NS": "Mastek", "MPHASIS.NS": "Mphasis",
        "NEWGEN.NS": "Newgen Software", "NIITLTD.NS": "NIIT Ltd", "OFSS.NS": "Oracle Financial",
        "PERSISTENT.NS": "Persistent Systems", "ZENSAR.NS": "Zensar Technologies", "ROUTE.NS": "Route Mobile",
        # Technology Products
        "DATAMATICS.NS": "Datamatics Global", "SONATSOFTW.NS": "Sonata Software", "SASKEN.NS": "Sasken Technologies",
        "TATAELXSI.NS": "Tata Elxsi", "TECHM.NS": "Tech Mahindra", "3MINDIA.NS": "3M India",
        "AFFLE.NS": "Affle India", "EASEMYTRIP.NS": "EaseMyTrip", "ZOMATO.NS": "Zomato",
        "NYKAA.NS": "Nykaa", "PAYTM.NS": "Paytm", "POLICYBZR.NS": "PB Fintech",
        # Electronics & Hardware
        "BLUESTARCO.NS": "Blue Star", "CAMPUS.NS": "Campus Activewear", "DIXON.NS": "Dixon Technologies",
        "HLEGLAS.NS": "HLE Glascoat", "HONAUT.NS": "Honeywell Automation", "LXCHEM.NS": "Laxmi Organic",
        "RPTECH.NS": "RP Tech India", "AMBER.NS": "Amber Enterprises", "SYMPHONY.NS": "Symphony",
        "VOLTAS.NS": "Voltas", "WHIRLPOOL.NS": "Whirlpool India", "VGUARD.NS": "V-Guard Industries",
        "CROMPTON.NS": "Crompton Greaves", "HAVELLS.NS": "Havells India", "ORIENTELEC.NS": "Orient Electric",
        "BAJAJHIND.NS": "Bajaj Hindusthan", "BLAL.NS": "BEML Land Assets", "BSOFT.NS": "BSOFT",
        # Software & Digital
        "INDIAMART.NS": "IndiaMART", "JUSTDIAL.NS": "Just Dial", "MATRIMONY.NS": "Matrimony.com",
        "NAZARA.NS": "Nazara Technologies", "SHOPERSTOP.NS": "Shoppers Stop", "TATACOMM.NS": "Tata Communications",
        "TATATECH.NS": "Tata Technologies", "TEAMLEASE.NS": "TeamLease Services", "CARTRADE.NS": "CarTrade Tech",
        "LATENTVIEW.NS": "LatentView Analytics", "MPSLTD.NS": "MPS Limited", "RAINBOW.NS": "Rainbow Children",
        "REDINGTON.NS": "Redington", "SPANDANA.NS": "Spandana Sphoorty", "STLTECH.NS": "Sterlite Technologies",
        "SUBROS.NS": "Subros", "SUPRAJIT.NS": "Suprajit Engineering", "SWARAJENG.NS": "Swaraj Engines",
        "TANLA.NS": "Tanla Platforms", "TCNSBRANDS.NS": "TCNS Clothing", "TIMKEN.NS": "Timken India",
        "TRIVENI.NS": "Triveni Turbine", "TTKHLTCARE.NS": "TTK Healthcare", "TTKPRESTIG.NS": "TTK Prestige",
        "UCOBANK.NS": "UCO Bank", "UNIONBANK.NS": "Union Bank", "VIPIND.NS": "VIP Industries",
        "VSTIND.NS": "VST Industries", "WELSPUNIND.NS": "Welspun India", "WESTLIFE.NS": "Westlife Development"
    },
    
    "💊 Pharma & Healthcare (70+)": {
        "AARTIDRUGS.NS": "Aarti Drugs", "ABBOTINDIA.NS": "Abbott India", "AJANTPHARM.NS": "Ajanta Pharma",
        "ALEMBICLTD.NS": "Alembic Pharma", "ALKEM.NS": "Alkem Laboratories", "ASTRAZEN.NS": "AstraZeneca Pharma",
        "AUROBINDO.NS": "Aurobindo Pharma", "BIOCON.NS": "Biocon", "CADILAHC.NS": "Cadila Healthcare",
        "CAPLIPOINT.NS": "Caplin Point", "CIPLA.NS": "Cipla", "DIVISLAB.NS": "Divi's Laboratories",
        "DRREDDY.NS": "Dr Reddy's Labs", "ERIS.NS": "Eris Lifesciences", "FINEORG.NS": "Fine Organic",
        "GLENMARK.NS": "Glenmark Pharma", "GLAXO.NS": "GlaxoSmithKline", "GRANULES.NS": "Granules India",
        "HETERO.NS": "Hetero Drugs", "IPCALAB.NS": "IPCA Laboratories", "JBCHEPHARM.NS": "JB Chemicals",
        "LUPIN.NS": "Lupin", "MANKIND.NS": "Mankind Pharma", "METROPOLIS.NS": "Metropolis Healthcare",
        "NATCOPHARM.NS": "Natco Pharma", "PFIZER.NS": "Pfizer", "SANOFI.NS": "Sanofi India",
        "SOLARA.NS": "Solara Active", "SUNPHARMA.NS": "Sun Pharma", "SYNGENE.NS": "Syngene International",
        "TORNTPHARM.NS": "Torrent Pharma", "VIMTA.NS": "Vimta Labs", "WOCKPHARMA.NS": "Wockhardt",
        "ZYDUSLIFE.NS": "Zydus Lifesciences", "ZYDUSWELL.NS": "Zydus Wellness",
        "APOLLOHOSP.NS": "Apollo Hospitals", "FORTIS.NS": "Fortis Healthcare", "MAXHEALTH.NS": "Max Healthcare",
        "LALPATHLAB.NS": "Dr Lal PathLabs", "THYROCARE.NS": "Thyrocare", "KRSNAA.NS": "Krsnaa Diagnostics",
        "RAINBOW.NS": "Rainbow Children", "KIMS.NS": "KIMS Hospitals", "MEDANTA.NS": "Global Health",
        "POLYMED.NS": "Poly Medicure", "STAR.NS": "Strides Pharma", "SUVEN.NS": "Suven Pharma",
        "SUVENPHAR.NS": "Suven Pharmaceuticals", "SEQUENT.NS": "Sequent Scientific", "SHILPAMED.NS": "Shilpa Medicare",
        "BLISSGVS.NS": "Bliss GVS Pharma", "INDOCO.NS": "Indoco Remedies", "JUBLPHARMA.NS": "Jubilant Pharma",
        "LAURUS.NS": "Laurus Labs", "MARKSANS.NS": "Marksans Pharma", "NEULANDLAB.NS": "Neuland Laboratories"
    },
    
    "🚗 Auto & Components (60+)": {
        "ASHOKLEY.NS": "Ashok Leyland", "BAJAJ-AUTO.NS": "Bajaj Auto", "BALKRISIND.NS": "Balkrishna Industries",
        "BHARATFORG.NS": "Bharat Forge", "BOSCHLTD.NS": "Bosch", "EICHERMOT.NS": "Eicher Motors",
        "ESCORTS.NS": "Escorts Kubota", "EXIDEIND.NS": "Exide Industries", "FORCEMOT.NS": "Force Motors",
        "HEROMOTOCO.NS": "Hero MotoCorp", "M&M.NS": "Mahindra & Mahindra", "MARUTI.NS": "Maruti Suzuki",
        "MRF.NS": "MRF", "TATAMOTORS.NS": "Tata Motors", "TVSMOTOR.NS": "TVS Motor",
        "AMARAJABAT.NS": "Amara Raja", "APOLLOTYRE.NS": "Apollo Tyres", "CRAFTSMAN.NS": "Craftsman Automation",
        "ENDURANCE.NS": "Endurance Technologies", "FINCABLES.NS": "Finolex Cables", "JKTYRE.NS": "JK Tyre",
        "MAHINDCIE.NS": "Mahindra CIE", "MOTHERSON.NS": "Motherson Sumi", "SANDHAR.NS": "Sandhar Technologies",
        "SANSERA.NS": "Sansera Engineering", "SCHAEFFLER.NS": "Schaeffler India", "SKFINDIA.NS": "SKF India",
        "SWARAJENG.NS": "Swaraj Engines", "TIMKEN.NS": "Timken India", "TUBE.NS": "Tube Investments",
        "WHEELS.NS": "Wheels India", "ABB.NS": "ABB India", "AIAENG.NS": "AIA Engineering",
        "ALICON.NS": "Alicon Castalloy", "AMBER.NS": "Amber Enterprises", "APOLLOPIPE.NS": "Apollo Pipes",
        "ASAHIINDIA.NS": "Asahi India Glass", "CEATLTD.NS": "CEAT", "CUMMINSIND.NS": "Cummins India",
        "ELGIRUBCO.NS": "Elgi Rubber", "GABRIEL.NS": "Gabriel India", "GREAVESCOT.NS": "Greaves Cotton",
        "JAMNAAUTO.NS": "Jamna Auto", "KALYANI.NS": "Kalyani Forge", "MAHSEAMLES.NS": "Maharashtra Seamless",
        "MAJESAUTO.NS": "Munjal Auto", "MFSL.NS": "Max Financial", "MHRIL.NS": "Mahindra Holidays",
        "ORIENTELEC.NS": "Orient Electric", "PHOENIXLTD.NS": "Phoenix Mills", "POLYMED.NS": "Poly Medicure",
        "RAMCOCEM.NS": "Ramco Cements", "RATNAMANI.NS": "Ratnamani Metals", "SHARDACROP.NS": "Sharda Cropchem"
    },
    
    "🍔 FMCG & Consumer (80+)": {
        "ABFRL.NS": "Aditya Birla Fashion", "AKZOINDIA.NS": "Akzo Nobel", "AVANTIFEED.NS": "Avanti Feeds",
        "BAJAJELEC.NS": "Bajaj Electricals", "BAJAJHLDNG.NS": "Bajaj Holdings", "BATAINDIA.NS": "Bata India",
        "BIKAJI.NS": "Bikaji Foods", "BRITANNIA.NS": "Britannia Industries", "CCL.NS": "CCL Products",
        "COLPAL.NS": "Colgate Palmolive", "DABUR.NS": "Dabur India", "EMAMILTD.NS": "Emami",
        "GILLETTE.NS": "Gillette India", "GODREJCP.NS": "Godrej Consumer", "GODFRYPHLP.NS": "Godfrey Phillips",
        "GUJALKALI.NS": "Gujarat Alkalies", "HAVELLS.NS": "Havells India", "HBLPOWER.NS": "HBL Power",
        "HINDUNILVR.NS": "Hindustan Unilever", "ITC.NS": "ITC", "JKLAKSHMI.NS": "JK Lakshmi Cement",
        "JKPAPER.NS": "JK Paper", "JUBLFOOD.NS": "Jubilant FoodWorks", "KAJARIACER.NS": "Kajaria Ceramics",
        "KPRMILL.NS": "KPR Mill", "MARICO.NS": "Marico", "MRPL.NS": "MRPL",
        "NAVINFLUOR.NS": "Navin Fluorine", "NESTLEIND.NS": "Nestle India", "ORIENTELEC.NS": "Orient Electric",
        "PAGEIND.NS": "Page Industries", "PCBL.NS": "PCBL", "PIIND.NS": "PI Industries",
        "POLYMED.NS": "Poly Medicure", "RADICO.NS": "Radico Khaitan", "RAJESHEXPO.NS": "Rajesh Exports",
        "RELAXO.NS": "Relaxo Footwears", "SOLARINDS.NS": "Solar Industries", "SYMPHONY.NS": "Symphony",
        "TATACHEM.NS": "Tata Chemicals", "TATACONSUM.NS": "Tata Consumer", "TATAMETALI.NS": "Tata Metaliks",
        "TTKPRESTIG.NS": "TTK Prestige", "UBL.NS": "United Breweries", "VENKEYS.NS": "Venky's",
        "VSTIND.NS": "VST Industries", "WHIRLPOOL.NS": "Whirlpool India", "ZYDUSLIFE.NS": "Zydus Lifesciences",
        "ZYDUSWELL.NS": "Zydus Wellness", "ARVINDFASN.NS": "Arvind Fashions", "CANTABIL.NS": "Cantabil Retail",
        "CENTURY.NS": "Century Textiles", "DOLLAR.NS": "Dollar Industries", "GOCOLORS.NS": "Go Colors",
        "INDIAMART.NS": "IndiaMART", "KEWAL.NS": "Kewal Kiran", "KPR.NS": "KPR Mill",
        "MANYAVAR.NS": "Vedant Fashions", "NYKAA.NS": "Nykaa", "PGEL.NS": "PG Electroplast",
        "PRAJIND.NS": "Praj Industries", "RAYMOND.NS": "Raymond", "SAPPHIRE.NS": "Sapphire Foods",
        "SHOPERSTOP.NS": "Shoppers Stop", "SPENCERS.NS": "Spencer's Retail", "TCNSBRANDS.NS": "TCNS Clothing",
        "TRENT.NS": "Trent", "VGUARD.NS": "V-Guard", "VIPIND.NS": "VIP Industries",
        "VMART.NS": "V-Mart Retail", "WESTLIFE.NS": "Westlife Development", "WONDERLA.NS": "Wonderla Holidays"
    },
    
    "🏭 Industrial & Manufacturing (100+)": {
        "APLAPOLLO.NS": "APL Apollo", "ASTRAL.NS": "Astral Poly", "CARYSIL.NS": "Carysil",
        "CASTROLIND.NS": "Castrol India", "CENTURYPLY.NS": "Century Plyboards", "CERA.NS": "Cera Sanitaryware",
        "DEEPAKNTR.NS": "Deepak Nitrite", "ELECON.NS": "Elecon Engineering", "FILATEX.NS": "Filatex India",
        "FLUOROCHEM.NS": "Gujarat Fluorochemicals", "GARFIBRES.NS": "Garware Technical", "GREAVESCOT.NS": "Greaves Cotton",
        "GRINDWELL.NS": "Grindwell Norton", "GSPL.NS": "Gujarat State Petronet", "HIL.NS": "HIL Limited",
        "INOXWIND.NS": "Inox Wind", "JINDALSAW.NS": "Jindal Saw", "JKCEMENT.NS": "JK Cement",
        "KALPATPOWR.NS": "Kalpataru Power", "KANSAINER.NS": "Kansai Nerolac", "KCP.NS": "KCP Limited",
        "KEC.NS": "KEC International", "KEI.NS": "KEI Industries", "KIRLOSENG.NS": "Kirloskar Oil",
        "LINDEINDIA.NS": "Linde India", "MOIL.NS": "MOIL", "NESCO.NS": "NESCO",
        "NLCINDIA.NS": "NLC India", "PHILIPCARB.NS": "Phillips Carbon", "PRINCEPIPE.NS": "Prince Pipes",
        "PRSMJOHNSN.NS": "Prism Johnson", "RAIN.NS": "Rain Industries", "RATNAMANI.NS": "Ratnamani Metals",
        "RCF.NS": "Rashtriya Chemicals", "RITES.NS": "RITES", "RVNL.NS": "Rail Vikas Nigam",
        "SAIL.NS": "SAIL", "SHREECEM.NS": "Shree Cement", "SJVN.NS": "SJVN",
        "SOBHA.NS": "Sobha", "SOLARINDS.NS": "Solar Industries", "SRF.NS": "SRF",
        "STARCEMENT.NS": "Star Cement", "SUMICHEM.NS": "Sumitomo Chemical", "SUPRAJIT.NS": "Suprajit Engineering",
        "SUPREMEIND.NS": "Supreme Industries", "SWARAJENG.NS": "Swaraj Engines", "TATAINVEST.NS": "Tata Investment",
        "TATATECH.NS": "Tata Technologies", "TECHNOE.NS": "Techno Electric", "TIINDIA.NS": "Tube Investments",
        "TIMETECHNO.NS": "Time Technoplast", "TRITURBINE.NS": "Triveni Turbine", "UCOBANK.NS": "UCO Bank",
        "UPL.NS": "UPL", "VINATIORGA.NS": "Vinati Organics", "WELCORP.NS": "Welspun Corp",
        "WELSPUNIND.NS": "Welspun India", "ABB.NS": "ABB India", "BEML.NS": "BEML",
        "BDL.NS": "Bharat Dynamics", "BHARATFORG.NS": "Bharat Forge", "BOSCHLTD.NS": "Bosch",
        "CARBORUNIV.NS": "Carborundum Universal", "CUMMINSIND.NS": "Cummins India", "HAL.NS": "Hindustan Aeronautics",
        "KALYANI.NS": "Kalyani Forge", "KIRLOSKAR.NS": "Kirloskar Brothers", "SIEMENS.NS": "Siemens",
        "THERMAX.NS": "Thermax", "TIMKEN.NS": "Timken India", "TRIVENI.NS": "Triveni Turbine",
        "VOLTAS.NS": "Voltas", "AARTI.NS": "Aarti Industries", "ALKYLAMINE.NS": "Alkyl Amines",
        "ATUL.NS": "Atul Ltd", "BASF.NS": "BASF India", "FINEORG.NS": "Fine Organic",
        "GNFC.NS": "GNFC", "GSFC.NS": "GSFC", "HERANBA.NS": "Heranba Industries",
        "NOCIL.NS": "NOCIL", "TATACHEM.NS": "Tata Chemicals"
    },
    
    "⚡ Energy & Power (50+)": {
        "ADANIENSOL.NS": "Adani Energy Solutions", "ADANIGAS.NS": "Adani Total Gas", "ADANIGREEN.NS": "Adani Green Energy",
        "AEGISCHEM.NS": "Aegis Logistics", "BPCL.NS": "BPCL", "GAIL.NS": "GAIL",
        "GMRINFRA.NS": "GMR Infrastructure", "GNFC.NS": "GNFC", "GSFC.NS": "GSFC",
        "GUJGASLTD.NS": "Gujarat Gas", "HINDPETRO.NS": "Hindustan Petroleum", "IOC.NS": "Indian Oil",
        "IGL.NS": "Indraprastha Gas", "MGL.NS": "Mahanagar Gas", "ONGC.NS": "ONGC",
        "OIL.NS": "Oil India", "PETRONET.NS": "Petronet LNG", "RELIANCE.NS": "Reliance Industries",
        "ADANIPOWER.NS": "Adani Power", "ADANITRANS.NS": "Adani Transmission", "CESC.NS": "CESC",
        "JSWENERGY.NS": "JSW Energy", "NHPC.NS": "NHPC", "NLCINDIA.NS": "NLC India",
        "NTPC.NS": "NTPC", "PFC.NS": "Power Finance Corp", "POWERGRID.NS": "Power Grid",
        "RECLTD.NS": "REC Limited", "SJVN.NS": "SJVN", "TATAPOWER.NS": "Tata Power",
        "TORNTPOWER.NS": "Torrent Power", "INOXWIND.NS": "Inox Wind", "SUZLON.NS": "Suzlon Energy",
        "COALINDIA.NS": "Coal India", "HINDALCO.NS": "Hindalco", "MOIL.NS": "MOIL",
        "NMDC.NS": "NMDC", "SAIL.NS": "SAIL", "VEDL.NS": "Vedanta",
        "CHAMBLFERT.NS": "Chambal Fertilizers", "COROMANDEL.NS": "Coromandel International", "DEEPAKFERT.NS": "Deepak Fertilizers",
        "FACT.NS": "FACT", "NFL.NS": "National Fertilizers", "RCF.NS": "Rashtriya Chemicals"
    },
    
    "🛒 Retail & E-commerce (40+)": {
        "AFFLE.NS": "Affle India", "CARTRADE.NS": "CarTrade Tech", "EASEMYTRIP.NS": "EaseMyTrip",
        "INDIAMART.NS": "IndiaMART", "JUSTDIAL.NS": "Just Dial", "MATRIMONY.NS": "Matrimony.com",
        "NAZARA.NS": "Nazara Technologies", "NYKAA.NS": "Nykaa", "PAYTM.NS": "Paytm",
        "POLICYBZR.NS": "PB Fintech", "ROUTE.NS": "Route Mobile", "ZOMATO.NS": "Zomato",
        "BARBEQUE.NS": "Barbeque Nation", "CAMPUS.NS": "Campus Activewear", "DEVYANI.NS": "Devyani International",
        "DMART.NS": "Avenue Supermarts", "FIVESTAR.NS": "Five Star Business", "JUBLFOOD.NS": "Jubilant FoodWorks",
        "KIMS.NS": "KIMS Hospitals", "RELAXO.NS": "Relaxo Footwears", "SAPPHIRE.NS": "Sapphire Foods",
        "SHOPERSTOP.NS": "Shoppers Stop", "SPENCERS.NS": "Spencer's Retail", "TATACOMM.NS": "Tata Communications",
        "TEAMLEASE.NS": "TeamLease Services", "TRENT.NS": "Trent", "VMART.NS": "V-Mart Retail",
        "WESTLIFE.NS": "Westlife Development", "WONDERLA.NS": "Wonderla Holidays", "ABFRL.NS": "Aditya Birla Fashion",
        "ARVINDFASN.NS": "Arvind Fashions", "BATAINDIA.NS": "Bata India", "CANTABIL.NS": "Cantabil Retail",
        "DOLLAR.NS": "Dollar Industries", "GOCOLORS.NS": "Go Colors", "MANYAVAR.NS": "Vedant Fashions",
        "RAYMOND.NS": "Raymond", "TCNSBRANDS.NS": "TCNS Clothing", "VIPIND.NS": "VIP Industries"
    },
    
    "🏗️ Real Estate & Construction (50+)": {
        "BRIGADE.NS": "Brigade Enterprises", "DLF.NS": "DLF", "GODREJPROP.NS": "Godrej Properties",
        "IBREALEST.NS": "Indiabulls Real Estate", "KOLTEPATIL.NS": "Kolte-Patil", "LODHA.NS": "Macrotech Developers",
        "MACROTECH.NS": "Macrotech Developers", "MAHLIFE.NS": "Mahindra Lifespace", "OBEROIRLTY.NS": "Oberoi Realty",
        "PHOENIXLTD.NS": "Phoenix Mills", "PRESTIGE.NS": "Prestige Estates", "RAYMOND.NS": "Raymond",
        "SIGNATURE.NS": "Signature Global", "SOBHA.NS": "Sobha", "AHLUCONT.NS": "Ahluwalia Contracts",
        "ASHOKA.NS": "Ashoka Buildcon", "HCC.NS": "Hindustan Construction", "IRB.NS": "IRB Infrastructure",
        "IRCON.NS": "IRCON International", "KEC.NS": "KEC International", "NBCC.NS": "NBCC India",
        "NCCLTD.NS": "NCC Limited", "PNCINFRA.NS": "PNC Infratech", "RITES.NS": "RITES",
        "RVNL.NS": "Rail Vikas Nigam", "ACC.NS": "ACC Cement", "AMBUJACEM.NS": "Ambuja Cements",
        "APLAPOLLO.NS": "APL Apollo Tubes", "ASTRAL.NS": "Astral Poly", "CENTURYPLY.NS": "Century Plyboards",
        "CERA.NS": "Cera Sanitaryware", "DALMIACEM.NS": "Dalmia Bharat", "GREENPLY.NS": "Greenply Industries",
        "JKCEMENT.NS": "JK Cement", "JKLAKSHMI.NS": "JK Lakshmi Cement", "KAJARIACER.NS": "Kajaria Ceramics",
        "ORIENTCEM.NS": "Orient Cement", "RAMCOCEM.NS": "Ramco Cements", "SHREECEM.NS": "Shree Cement",
        "STARCEMENT.NS": "Star Cement", "SUPREMEIND.NS": "Supreme Industries", "ULTRACEMCO.NS": "UltraTech Cement",
        "FINCABLES.NS": "Finolex Cables", "HUDCO.NS": "HUDCO", "LINDEINDIA.NS": "Linde India"
    }
}

# Industry Benchmarks
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
# ENHANCED RATE LIMIT HANDLING
# ============================================================================

def retry_with_backoff(retries=3, backoff_in_seconds=2):
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

@st.cache_data(ttl=7200)  # Cache for 2 HOURS (further increased)
@retry_with_backoff(retries=5, backoff_in_seconds=3)
def fetch_stock_data(ticker):
    """Enhanced data fetching with 2-hour cache and 5 retries"""
    try:
        time.sleep(1)  # Increased delay to 1 second
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or len(info) < 5:
            return None, "Unable to fetch data - stock may not exist"
        
        return info, None
        
    except Exception as e:
        error_msg = str(e)
        
        if "429" in error_msg or "rate" in error_msg.lower() or "limit" in error_msg.lower():
            return None, "⏱️ RATE LIMIT: Yahoo Finance API limit reached. Wait 3-5 minutes or try another stock."
        elif "404" in error_msg:
            return None, "❌ STOCK NOT FOUND: Invalid ticker symbol."
        elif "timeout" in error_msg.lower():
            return None, "⏰ TIMEOUT: Server is busy. Try again."
        else:
            return None, f"❌ ERROR: {error_msg[:100]}"

def calculate_valuations(info):
    """Calculate comprehensive valuations"""
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
        
        # PE Valuation
        if trailing_pe and trailing_pe > 0:
            historical_pe = trailing_pe * 0.9
        else:
            historical_pe = industry_pe
        
        blended_pe = (industry_pe + historical_pe) / 2
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
        # EV/EBITDA Valuation
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
        st.error(f"⚠️ Valuation error: {str(e)}")
        return None

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>📊 PROFESSIONAL MIDCAP VALUATION PLATFORM</h1>
    <p style="font-size: 1.3rem;">800+ Midcap Stocks • Real-time Analysis • Stock Comparison</p>
</div>
""", unsafe_allow_html=True)

# Smart Features Info
col1, col2, col3 = st.columns(3)
with col1:
    st.info("💡 **2-Hour Caching** - Instant reanalysis!")
with col2:
    st.success("📊 **Compare Stocks** - Side by side analysis")
with col3:
    st.warning("⚡ **Fair Value Alerts** - Top highlights")

# Logout
if st.sidebar.button("🚪 Logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ============================================================================
# SIDEBAR - STOCK SELECTION
# ============================================================================

st.sidebar.header("📈 Stock Selection")

# Mode Selection
analysis_mode = st.sidebar.radio(
    "**Analysis Mode:**",
    ["🔍 Single Stock", "⚖️ Compare Stocks"],
    horizontal=True
)

# Flatten stocks
all_stocks = {}
for category, stocks in MIDCAP_500_STOCKS.items():
    all_stocks.update(stocks)

st.sidebar.success(f"**📊 Total: {len(all_stocks)} stocks**")

# Category and Search
selected_category = st.sidebar.selectbox(
    "Category",
    ["🔍 All Stocks"] + list(MIDCAP_500_STOCKS.keys())
)

search_term = st.sidebar.text_input("🔍 Search", placeholder="Company or ticker...")

# Filter stocks
if search_term:
    filtered_stocks = {
        ticker: name for ticker, name in all_stocks.items()
        if search_term.upper() in ticker or search_term.upper() in name.upper()
    }
elif selected_category == "🔍 All Stocks":
    filtered_stocks = all_stocks
else:
    filtered_stocks = MIDCAP_500_STOCKS[selected_category]

if search_term or selected_category != "🔍 All Stocks":
    st.sidebar.info(f"Showing: {len(filtered_stocks)} stocks")

stock_options = [f"{name} ({ticker})" for ticker, name in filtered_stocks.items()]

# ============================================================================
# SINGLE STOCK ANALYSIS MODE
# ============================================================================

if analysis_mode == "🔍 Single Stock":
    if stock_options:
        selected_stock = st.sidebar.selectbox("Select Stock", stock_options)
        selected_ticker = selected_stock.split("(")[1].strip(")")
    else:
        st.sidebar.warning("No stocks found")
        selected_ticker = None
    
    custom_ticker = st.sidebar.text_input("Or Custom Ticker", placeholder="e.g., DIXON.NS")
    
    if st.sidebar.button("🚀 ANALYZE", use_container_width=True):
        st.session_state.analyze_ticker = custom_ticker.upper() if custom_ticker else selected_ticker
    
    # Analysis Section
    if 'analyze_ticker' in st.session_state:
        ticker = st.session_state.analyze_ticker
        
        with st.spinner(f"🔄 Analyzing {ticker}..."):
            info, error = fetch_stock_data(ticker)
        
        if error:
            st.error(f"❌ {error}")
            if "RATE LIMIT" in error:
                st.warning("""
                **💡 Solutions:**
                1. ⏰ Wait 3-5 minutes
                2. 🔄 Try a different stock (cached stocks load instantly!)
                3. 📊 Recently analyzed stocks don't use quota
                
                **Tip:** Analyze during off-peak hours for best experience!
                """)
            st.stop()
        
        if not info:
            st.error("Failed to fetch data")
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
        
        # === FAIR VALUE HIGHLIGHT BOX ===
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
            rec_desc = "Significantly undervalued - High potential"
        elif avg_upside > 15:
            rec_class, rec_text = "rec-buy", "⭐⭐ BUY"
            rec_desc = "Good value - Accumulate on dips"
        elif avg_upside > 0:
            rec_class, rec_text = "rec-buy", "⭐ ACCUMULATE"
            rec_desc = "Slightly undervalued"
        elif avg_upside > -10:
            rec_class, rec_text = "rec-hold", "🟡 HOLD"
            rec_desc = "Fairly valued"
        else:
            rec_class, rec_text = "rec-avoid", "❌ AVOID"
            rec_desc = "Overvalued - High risk"
        
        st.markdown(f"""
        <div class="{rec_class}">
            <div>{rec_text}</div>
            <div style="font-size: 1.2rem; margin-top: 0.5rem;">Potential Return: {avg_upside:+.2f}%</div>
            <div style="font-size: 1rem; margin-top: 0.5rem;">{rec_desc}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Gauges
        if valuations['upside_pe'] and valuations['upside_ev']:
            st.subheader("📈 Valuation Analysis")
            
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
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0}
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
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 0}
                }
            ), row=1, col=2)
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Bar Chart
        st.subheader("💰 Price Comparison")
        
        categories, current, fair, colors = [], [], [], []
        
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
        fig2.add_trace(go.Bar(name='Current Price', x=categories, y=current, marker_color='#3498db',
                              text=[f'Rs {p:.2f}' for p in current], textposition='outside'))
        fig2.add_trace(go.Bar(name='Fair Value', x=categories, y=fair, marker_color=colors,
                              text=[f'Rs {p:.2f}' for p in fair], textposition='outside'))
        fig2.update_layout(barmode='group', height=500, template='plotly_white')
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Metrics Table
        st.subheader("📋 Financial Metrics")
        
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
        
        col1, col2 = st.columns(2)
        with col1:
            st.success("""
            **🚀 Platform Features:**
            - 800+ Midcap stocks
            - Real-time analysis
            - Dual valuation methods
            - Stock comparison
            - Fair value highlights
            - Professional UI
            """)
        with col2:
            st.warning("""
            **💡 Pro Tips:**
            - Data cached for 2 hours
            - Compare multiple stocks
            - Check fair value box
            - Analyze off-peak hours
            - Use search function
            """)

# ============================================================================
# COMPARISON MODE
# ============================================================================

else:  # Compare Stocks
    st.sidebar.markdown("### Select Stocks to Compare")
    
    num_stocks = st.sidebar.radio("Number of stocks:", [2, 3], horizontal=True)
    
    compare_tickers = []
    for i in range(num_stocks):
        if stock_options:
            selected = st.sidebar.selectbox(f"Stock {i+1}", stock_options, key=f"compare_{i}")
            compare_tickers.append(selected.split("(")[1].strip(")"))
    
    if st.sidebar.button("⚖️ COMPARE NOW", use_container_width=True):
        st.session_state.compare_tickers = compare_tickers
    
    if 'compare_tickers' in st.session_state:
        tickers = st.session_state.compare_tickers
        
        st.markdown("""
        <div class="comparison-header">
            <h2>⚖️ STOCK COMPARISON ANALYSIS</h2>
        </div>
        """, unsafe_allow_html=True)
        
        comparison_data = []
        
        for ticker in tickers:
            with st.spinner(f"Fetching {ticker}..."):
                info, error = fetch_stock_data(ticker)
                
                if error or not info:
                    st.warning(f"⚠️ Could not fetch {ticker}")
                    continue
                
                valuations = calculate_valuations(info)
                if not valuations:
                    continue
                
                upside_values = [v for v in [valuations['upside_pe'], valuations['upside_ev']] if v is not None]
                avg_upside = np.mean(upside_values) if upside_values else 0
                
                comparison_data.append({
                    'Ticker': ticker,
                    'Company': info.get('longName', ticker),
                    'Price': valuations['price'],
                    'PE': valuations['trailing_pe'],
                    'EPS': valuations['trailing_eps'],
                    'Fair Value': np.mean([v for v in [valuations['fair_value_pe'], valuations['fair_value_ev']] if v]),
                    'Upside %': avg_upside,
                    'Market Cap (Cr)': valuations['market_cap']/10000000
                })
        
        if comparison_data:
            # Comparison Table
            comp_df = pd.DataFrame(comparison_data)
            
            st.markdown("### 📊 Comparison Summary")
            st.dataframe(comp_df.style.format({
                'Price': 'Rs {:.2f}',
                'PE': '{:.2f}x',
                'EPS': 'Rs {:.2f}',
                'Fair Value': 'Rs {:.2f}',
                'Upside %': '{:+.2f}%',
                'Market Cap (Cr)': 'Rs {:.0f}'
            }), use_container_width=True, hide_index=True)
            
            # Comparison Charts
            st.markdown("### 📈 Visual Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = go.Figure()
                fig1.add_trace(go.Bar(
                    x=comp_df['Company'],
                    y=comp_df['Upside %'],
                    marker_color=['#00C853' if x > 0 else '#e74c3c' for x in comp_df['Upside %']],
                    text=[f'{x:+.1f}%' for x in comp_df['Upside %']],
                    textposition='outside'
                ))
                fig1.update_layout(title="Upside Potential", height=400)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=comp_df['Company'],
                    y=comp_df['PE'],
                    marker_color='#667eea',
                    text=[f'{x:.1f}x' for x in comp_df['PE']],
                    textposition='outside'
                ))
                fig2.update_layout(title="PE Ratio Comparison", height=400)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Best Pick
            best_idx = comp_df['Upside %'].idxmax()
            best_stock = comp_df.loc[best_idx]
            
            st.markdown(f"""
            <div class="fair-value-box">
                <div class="fair-value-title">🏆 BEST VALUE PICK</div>
                <div style="font-size: 2rem; margin: 1rem 0;">{best_stock['Company']}</div>
                <div class="fair-value-upside">Upside Potential: {best_stock['Upside %']:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.error("Unable to compare stocks. Try different selections.")
    
    else:
        st.info("👈 Select stocks to compare and click **COMPARE NOW**!")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p><strong>💡 NYZTrade Professional Midcap Platform | {len(all_stocks)}+ Stocks</strong></p>
    <p>Educational Tool | Not Financial Advice | Powered by yfinance</p>
    <p>⚠️ Always DYOR before investing</p>
</div>
""", unsafe_allow_html=True)
