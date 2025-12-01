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
    page_title="NYZTrade - Midcap Valuation",
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
    
    "💊 Pharma & Healthcare (100+)": {
        # Pharmaceuticals
        "AARTIDRUGS.NS": "Aarti Drugs", "ABBOTINDIA.NS": "Abbott India", "AJANTPHARM.NS": "Ajanta Pharma",
        "ALEMBICLTD.NS": "Alembic Pharma", "ALKEM.NS": "Alkem Laboratories", "ASTRAZEN.NS": "AstraZeneca Pharma",
        "AUROBINDO.NS": "Aurobindo Pharma", "BIOCON.NS": "Biocon", "CADILAHC.NS": "Cadila Healthcare",
        "CAPLIPOINT.NS": "Caplin Point", "CIPLA.NS": "Cipla", "DIVISLAB.NS": "Divi's Laboratories",
        "DRREDDY.NS": "Dr Reddy's Labs", "ERIS.NS": "Eris Lifesciences", "FINEORG.NS": "Fine Organic",
        "GLENMARK.NS": "Glenmark Pharma", "GLAXO.NS": "GlaxoSmithKline", "GRANULES.NS": "Granules India",
        "GUJGASLTD.NS": "Gujarat Gas", "HETERO.NS": "Hetero Drugs", "IPCALAB.NS": "IPCA Laboratories",
        "JBCHEPHARM.NS": "JB Chemicals", "LAUREATE.NS": "Laureate Education", "LUPIN.NS": "Lupin",
        "MANKIND.NS": "Mankind Pharma", "METROPOLIS.NS": "Metropolis Healthcare", "NATCOPHARM.NS": "Natco Pharma",
        "PFIZER.NS": "Pfizer", "PLNG.NS": "Petronet LNG", "SANOFI.NS": "Sanofi India",
        "SOLARA.NS": "Solara Active", "SUNPHARMA.NS": "Sun Pharma", "SYNGENE.NS": "Syngene International",
        "TORNTPHARM.NS": "Torrent Pharma", "VIMTA.NS": "Vimta Labs", "WOCKPHARMA.NS": "Wockhardt",
        "ZYDUSLIFE.NS": "Zydus Lifesciences", "ZYDUSWELL.NS": "Zydus Wellness",
        # Diagnostics & Healthcare Services
        "APOLLOHOSP.NS": "Apollo Hospitals", "FORTIS.NS": "Fortis Healthcare", "MAXHEALTH.NS": "Max Healthcare",
        "LALPATHLAB.NS": "Dr Lal PathLabs", "THYROCARE.NS": "Thyrocare", "KRSNAA.NS": "Krsnaa Diagnostics",
        "RAINBOW.NS": "Rainbow Children", "KIMS.NS": "KIMS Hospitals", "MEDANTA.NS": "Global Health (Medanta)",
        "SAHYADRI.NS": "Sahyadri Hospitals", "YATHARTH.NS": "Yatharth Hospital",
        # Medical Devices & Equipment
        "POLYMED.NS": "Poly Medicure", "STAR.NS": "Strides Pharma", "SUVEN.NS": "Suven Pharma",
        "SUVENPHAR.NS": "Suven Pharmaceuticals", "SEQUENT.NS": "Sequent Scientific", "SHILPAMED.NS": "Shilpa Medicare",
        "BLISSGVS.NS": "Bliss GVS Pharma", "INDOCO.NS": "Indoco Remedies", "JUBLPHARMA.NS": "Jubilant Pharma",
        "LAURUS.NS": "Laurus Labs", "MARKSANS.NS": "Marksans Pharma", "NEULANDLAB.NS": "Neuland Laboratories",
        "ORACLEFISH.NS": "Oracle Financial Services", "PANAMAPET.NS": "Panama Petrochem", "PENIND.NS": "Pennar Industries",
        "RADICO.NS": "Radico Khaitan", "RAJESHEXPO.NS": "Rajesh Exports", "RAMCOCEM.NS": "Ramco Cements",
        "RATNAMANI.NS": "Ratnamani Metals", "RECLTD.NS": "REC Limited", "RELAXO.NS": "Relaxo Footwears",
        "RESPONIND.NS": "Response Informatics", "RITES.NS": "RITES", "RVNL.NS": "Rail Vikas Nigam",
        "SANOFI.NS": "Sanofi India", "SCHAEFFLER.NS": "Schaeffler India", "SHARDACROP.NS": "Sharda Cropchem",
        "SHILPAMED.NS": "Shilpa Medicare", "SHOPERSTOP.NS": "Shoppers Stop", "SJVN.NS": "SJVN",
        "SKFINDIA.NS": "SKF India", "SOBHA.NS": "Sobha", "SOLARINDS.NS": "Solar Industries",
        "SONATSOFTW.NS": "Sonata Software", "SPARC.NS": "Sun Pharma Advanced", "SPICEJET.NS": "SpiceJet"
    },
    
    "🚗 Auto & Components (80+)": {
        # Auto Manufacturers
        "ASHOKLEY.NS": "Ashok Leyland", "BAJAJ-AUTO.NS": "Bajaj Auto", "BALKRISIND.NS": "Balkrishna Industries",
        "BHARATFORG.NS": "Bharat Forge", "BOSCHLTD.NS": "Bosch", "EICHERMOT.NS": "Eicher Motors",
        "ESCORTS.NS": "Escorts Kubota", "EXIDEIND.NS": "Exide Industries", "FORCEMOT.NS": "Force Motors",
        "HEROMOTOCO.NS": "Hero MotoCorp", "M&M.NS": "Mahindra & Mahindra", "MARUTI.NS": "Maruti Suzuki",
        "MRF.NS": "MRF", "TATAMOTORS.NS": "Tata Motors", "TVSMOTOR.NS": "TVS Motor",
        # Auto Components
        "AMARAJABAT.NS": "Amara Raja", "ANANTRAJ.NS": "Anant Raj", "APOLLOTYRE.NS": "Apollo Tyres",
        "CRAFTSMAN.NS": "Craftsman Automation", "ENDURANCE.NS": "Endurance Technologies", "FINCABLES.NS": "Finolex Cables",
        "JKTYRE.NS": "JK Tyre", "MAHINDCIE.NS": "Mahindra CIE", "MOTHERSON.NS": "Motherson Sumi",
        "SANDHAR.NS": "Sandhar Technologies", "SANSERA.NS": "Sansera Engineering", "SCHAEFFLER.NS": "Schaeffler India",
        "SKFINDIA.NS": "SKF India", "SPARC.NS": "Sun Pharma Advanced", "SWARAJENG.NS": "Swaraj Engines",
        "TIMKEN.NS": "Timken India", "TUBE.NS": "Tube Investments", "WHEELS.NS": "Wheels India",
        "AAVAS.NS": "Aavas Financiers", "AARTIIND.NS": "Aarti Industries", "AARVEEDEN.NS": "Aarvee Denims",
        "ABB.NS": "ABB India", "ABSLAMC.NS": "Aditya Birla Sun Life AMC", "ADANIENSOL.NS": "Adani Energy Solutions",
        "ADANIGAS.NS": "Adani Total Gas", "ADANIGREEN.NS": "Adani Green Energy", "ADANIPORTS.NS": "Adani Ports",
        "ADANITRANS.NS": "Adani Transmission", "AEGISCHEM.NS": "Aegis Logistics", "AFFLE.NS": "Affle India",
        "AGARIND.NS": "Agarwal Industrial", "AIAENG.NS": "AIA Engineering", "AIRAN.NS": "Airan",
        "AJANTPHARM.NS": "Ajanta Pharma", "AKZOINDIA.NS": "Akzo Nobel India", "ALEMBICLTD.NS": "Alembic Pharma",
        "ALICON.NS": "Alicon Castalloy", "ALKYLAMINE.NS": "Alkyl Amines", "ALLCARGO.NS": "Allcargo Logistics",
        "AMARAJABAT.NS": "Amara Raja Energy", "AMBER.NS": "Amber Enterprises", "AMBUJACEM.NS": "Ambuja Cements",
        "ANGELONE.NS": "Angel One", "ANURAS.NS": "Anuh Pharma", "APLAPOLLO.NS": "APL Apollo Tubes",
        "APOLLOHOSP.NS": "Apollo Hospitals", "APOLLOPIPE.NS": "Apollo Pipes", "APOLLOTYRE.NS": "Apollo Tyres",
        "APTUS.NS": "Aptus Value Housing", "ARVINDFASN.NS": "Arvind Fashions", "ASAHIINDIA.NS": "Asahi India Glass",
        "ASHIANA.NS": "Ashiana Housing", "ASHOKA.NS": "Ashoka Buildcon", "ASIANPAINT.NS": "Asian Paints",
        "ASTERDM.NS": "Aster DM Healthcare", "ASTRAL.NS": "Astral Poly", "ASTRAZEN.NS": "AstraZeneca Pharma",
        "ATUL.NS": "Atul Ltd", "AUBANK.NS": "AU Small Finance Bank", "AUROBINDO.NS": "Aurobindo Pharma"
    },
    
    "🍔 FMCG & Consumer (100+)": {
        # FMCG
        "ABSLAMC.NS": "Aditya Birla Sun Life AMC", "AKZOINDIA.NS": "Akzo Nobel", "AVANTIFEED.NS": "Avanti Feeds",
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
        "RELAXO.NS": "Relaxo Footwears", "SCHAEFFLER.NS": "Schaeffler", "SOLARINDS.NS": "Solar Industries",
        "SYMPHONY.NS": "Symphony", "TATACHEM.NS": "Tata Chemicals", "TATACONSUM.NS": "Tata Consumer",
        "TATAMETALI.NS": "Tata Metaliks", "TTKPRESTIG.NS": "TTK Prestige", "UBL.NS": "United Breweries",
        "VENKEYS.NS": "Venky's", "VSTIND.NS": "VST Industries", "WHIRLPOOL.NS": "Whirlpool India",
        "ZYDUSLIFE.NS": "Zydus Lifesciences", "ZYDUSWELL.NS": "Zydus Wellness",
        # Retail & Apparel
        "ABFRL.NS": "Aditya Birla Fashion", "AHLUCONT.NS": "Ahluwalia Contracts", "APPARELRES.NS": "Apparel Resources",
        "ARVINDFASN.NS": "Arvind Fashions", "CANTABIL.NS": "Cantabil Retail", "CENTURY.NS": "Century Textiles",
        "DOLLAR.NS": "Dollar Industries", "GOCOLORS.NS": "Go Colors", "INDIAMART.NS": "IndiaMART",
        "JUBLFOOD.NS": "Jubilant FoodWorks", "KEWAL.NS": "Kewal Kiran", "KPR.NS": "KPR Mill",
        "MANYAVAR.NS": "Vedant Fashions", "NYKAA.NS": "Nykaa", "PGEL.NS": "PG Electroplast",
        "POLICYBZR.NS": "PB Fintech", "PRAJIND.NS": "Praj Industries", "RAYMOND.NS": "Raymond",
        "RELAXO.NS": "Relaxo Footwears", "SAPPHIRE.NS": "Sapphire Foods", "SHOPERSTOP.NS": "Shoppers Stop",
        "SPENCERS.NS": "Spencer's Retail", "TATACOMM.NS": "Tata Communications", "TCNSBRANDS.NS": "TCNS Clothing",
        "TRENT.NS": "Trent", "VGUARD.NS": "V-Guard", "VIPIND.NS": "VIP Industries",
        "VMART.NS": "V-Mart Retail", "WESTLIFE.NS": "Westlife Development", "WONDERLA.NS": "Wonderla Holidays",
        # Food & Beverages
        "BARBEQUE.NS": "Barbeque Nation", "BIKAJI.NS": "Bikaji Foods", "BRITANNIA.NS": "Britannia",
        "CCL.NS": "CCL Products", "DEVYANI.NS": "Devyani International", "HATSUN.NS": "Hatsun Agro",
        "ITC.NS": "ITC", "JUBLFOOD.NS": "Jubilant FoodWorks", "KRBL.NS": "KRBL",
        "NESTLEIND.NS": "Nestle India", "RADICO.NS": "Radico Khaitan", "SAPPHIRE.NS": "Sapphire Foods",
        "TATACONSUM.NS": "Tata Consumer", "UBL.NS": "United Breweries", "USHAMART.NS": "Usha Martin",
        "VARUNBEV.NS": "Varun Beverages", "VBL.NS": "Varun Beverages", "VENKEYS.NS": "Venky's",
        "WESTLIFE.NS": "Westlife Development", "ZOMATO.NS": "Zomato"
    },
    
    "🏭 Industrial & Manufacturing (120+)": {
        # Construction & Infrastructure
        "APLAPOLLO.NS": "APL Apollo", "ASTRAL.NS": "Astral Poly", "CARYSIL.NS": "Carysil",
        "CASTROLIND.NS": "Castrol India", "CENTURYPLY.NS": "Century Plyboards", "CERA.NS": "Cera Sanitaryware",
        "DEEPAKNTR.NS": "Deepak Nitrite", "ELECON.NS": "Elecon Engineering", "FILATEX.NS": "Filatex India",
        "FLUOROCHEM.NS": "Gujarat Fluorochemicals", "GARFIBRES.NS": "Garware Technical", "GREAVESCOT.NS": "Greaves Cotton",
        "GRINDWELL.NS": "Grindwell Norton", "GSPL.NS": "Gujarat State Petronet", "HATHWAY.NS": "Hathway Cable",
        "HIL.NS": "HIL Limited", "IIFLWAM.NS": "IIFL Wealth", "INDIAMART.NS": "IndiaMART",
        "INOXWIND.NS": "Inox Wind", "JAGRAN.NS": "Jagran Prakashan", "JINDALSAW.NS": "Jindal Saw",
        "JKCEMENT.NS": "JK Cement", "JKLAKSHMI.NS": "JK Lakshmi", "KALPATPOWR.NS": "Kalpataru Power",
        "KANSAINER.NS": "Kansai Nerolac", "KCP.NS": "KCP Limited", "KEC.NS": "KEC International",
        "KEI.NS": "KEI Industries", "KIRLOSENG.NS": "Kirloskar Oil", "KIRIINDUS.NS": "Kiri Industries",
        "KRBL.NS": "KRBL", "L&TFH.NS": "L&T Finance Holdings", "LINDEINDIA.NS": "Linde India",
        "MANAPPURAM.NS": "Manappuram Finance", "MOIL.NS": "MOIL", "NESCO.NS": "NESCO",
        "NLCINDIA.NS": "NLC India", "PAGE.NS": "Page Industries", "PGEL.NS": "PG Electroplast",
        "PHILIPCARB.NS": "Phillips Carbon", "PRINCEPIPE.NS": "Prince Pipes", "PRSMJOHNSN.NS": "Prism Johnson",
        "RAIN.NS": "Rain Industries", "RATNAMANI.NS": "Ratnamani Metals", "RCF.NS": "Rashtriya Chemicals",
        "RESPONIND.NS": "Response Informatics", "RITES.NS": "RITES", "RVNL.NS": "Rail Vikas Nigam",
        "SADBHAV.NS": "Sadbhav Engineering", "SAIL.NS": "SAIL", "SHREECEM.NS": "Shree Cement",
        "SIMPLE.NS": "Simple Appliances", "SJVN.NS": "SJVN", "SOBHA.NS": "Sobha",
        "SOLARINDS.NS": "Solar Industries", "SRF.NS": "SRF", "STARCEMENT.NS": "Star Cement",
        "SUMICHEM.NS": "Sumitomo Chemical", "SUPRAJIT.NS": "Suprajit Engineering", "SUPREMEIND.NS": "Supreme Industries",
        "SUVENPHAR.NS": "Suven Pharma", "SWARAJENG.NS": "Swaraj Engines", "SYMPHONY.NS": "Symphony",
        "TATAINVEST.NS": "Tata Investment", "TATAMETALI.NS": "Tata Metaliks", "TATATECH.NS": "Tata Technologies",
        "TECHNOE.NS": "Techno Electric", "TIINDIA.NS": "Tube Investments", "TIMETECHNO.NS": "Time Technoplast",
        "TIRUMALCHM.NS": "Tirumalai Chemicals", "TREEHOUSE.NS": "Tree House Education", "TRITURBINE.NS": "Triveni Turbine",
        "UCOBANK.NS": "UCO Bank", "UNIPLY.NS": "Uniply Industries", "UPL.NS": "UPL",
        "VGUARD.NS": "V-Guard", "VINATIORGA.NS": "Vinati Organics", "WELCORP.NS": "Welspun Corp",
        "WELSPUNIND.NS": "Welspun India", "WESTLIFE.NS": "Westlife Development", "ZODIACLOTH.NS": "Zodiac Clothing",
        # Heavy Engineering & Machinery
        "ABB.NS": "ABB India", "AIAENG.NS": "AIA Engineering", "BEML.NS": "BEML",
        "BDL.NS": "Bharat Dynamics", "BHARATFORG.NS": "Bharat Forge", "BOSCHLTD.NS": "Bosch",
        "CARBORUNIV.NS": "Carborundum Universal", "CUMMINSIND.NS": "Cummins India", "GRINDWELL.NS": "Grindwell Norton",
        "HAL.NS": "Hindustan Aeronautics", "KALYANI.NS": "Kalyani Forge", "KIRLOSKAR.NS": "Kirloskar Brothers",
        "SIEMENS.NS": "Siemens", "SKFINDIA.NS": "SKF India", "THERMAX.NS": "Thermax",
        "TIMKEN.NS": "Timken India", "TRIVENI.NS": "Triveni Turbine", "VOLTAS.NS": "Voltas",
        # Chemicals & Materials
        "AARTI.NS": "Aarti Industries", "ALKYLAMINE.NS": "Alkyl Amines", "ATUL.NS": "Atul Ltd",
        "BASF.NS": "BASF India", "DEEPAKNTR.NS": "Deepak Nitrite", "FINEORG.NS": "Fine Organic",
        "FLUOROCHEM.NS": "Gujarat Fluorochemicals", "GNFC.NS": "GNFC", "GSFC.NS": "GSFC",
        "GUJALKALI.NS": "Gujarat Alkalies", "HERANBA.NS": "Heranba Industries", "NAVINFLUOR.NS": "Navin Fluorine",
        "NOCIL.NS": "NOCIL", "PIIND.NS": "PI Industries", "SRF.NS": "SRF",
        "SUMICHEM.NS": "Sumitomo Chemical", "TATACHEM.NS": "Tata Chemicals", "UPL.NS": "UPL",
        "VINATIORGA.NS": "Vinati Organics"
    },
    
    "⚡ Energy & Power (70+)": {
        # Oil & Gas
        "ADANIENSOL.NS": "Adani Energy Solutions", "ADANIGAS.NS": "Adani Total Gas", "ADANIGREEN.NS": "Adani Green Energy",
        "AEGISCHEM.NS": "Aegis Logistics", "ATGL.NS": "Adani Total Gas", "BPCL.NS": "BPCL",
        "GAIL.NS": "GAIL", "GMRINFRA.NS": "GMR Infrastructure", "GNFC.NS": "GNFC",
        "GSFC.NS": "GSFC", "GUJALKALI.NS": "Gujarat Alkalies", "GUJGASLTD.NS": "Gujarat Gas",
        "HINDPETRO.NS": "Hindustan Petroleum", "IOC.NS": "Indian Oil", "IGL.NS": "Indraprastha Gas",
        "MGL.NS": "Mahanagar Gas", "ONGC.NS": "ONGC", "OIL.NS": "Oil India",
        "PETRONET.NS": "Petronet LNG", "PLNG.NS": "Petronet LNG", "RELIANCE.NS": "Reliance Industries",
        # Power Generation & Distribution
        "ADANIPOWER.NS": "Adani Power", "ADANITRANS.NS": "Adani Transmission", "CESC.NS": "CESC",
        "JSWENERGY.NS": "JSW Energy", "NHPC.NS": "NHPC", "NLCINDIA.NS": "NLC India",
        "NTPC.NS": "NTPC", "PFC.NS": "Power Finance Corp", "POWERGRID.NS": "Power Grid",
        "RECLTD.NS": "REC Limited", "SJVN.NS": "SJVN", "TATAPOWER.NS": "Tata Power",
        "TORNTPOWER.NS": "Torrent Power", "TIDEWATER.NS": "Tidewater Oil", "TIINDIA.NS": "Tube Investments",
        # Renewable Energy
        "ADANIGREEN.NS": "Adani Green", "GIPCL.NS": "Gujarat Industries", "INOXWIND.NS": "Inox Wind",
        "JSWENERGY.NS": "JSW Energy", "ORIENTCEM.NS": "Orient Cement", "RPOWER.NS": "Reliance Power",
        "SUZLON.NS": "Suzlon Energy", "WEBELSOLAR.NS": "Websol Energy",
        # Coal & Mining
        "COALINDIA.NS": "Coal India", "GMDCLTD.NS": "Gujarat Mineral", "HINDALCO.NS": "Hindalco",
        "MOIL.NS": "MOIL", "NMDC.NS": "NMDC", "SAIL.NS": "SAIL",
        "VEDL.NS": "Vedanta", "WELCORP.NS": "Welspun Corp",
        # Fertilizers & Agro Chemicals
        "CHAMBLFERT.NS": "Chambal Fertilizers", "COROMANDEL.NS": "Coromandel International", "DEEPAKFERT.NS": "Deepak Fertilizers",
        "FACT.NS": "FACT", "GNFC.NS": "GNFC", "GSFC.NS": "GSFC",
        "ICICIGI.NS": "ICICI Lombard", "NFL.NS": "National Fertilizers", "RCF.NS": "Rashtriya Chemicals",
        "ZUARI.NS": "Zuari Agro Chemicals"
    },
    
    "🛒 Retail & E-commerce (60+)": {
        # E-commerce & Digital
        "AFFLE.NS": "Affle India", "CARTRADE.NS": "CarTrade Tech", "EASEMYTRIP.NS": "EaseMyTrip",
        "INDIAMART.NS": "IndiaMART", "JUSTDIAL.NS": "Just Dial", "MATRIMONY.NS": "Matrimony.com",
        "NAZARA.NS": "Nazara Technologies", "NYKAA.NS": "Nykaa", "PAYTM.NS": "Paytm",
        "POLICYBZR.NS": "PB Fintech", "ROUTE.NS": "Route Mobile", "ZOMATO.NS": "Zomato",
        # Retail Chains
        "BARBEQUE.NS": "Barbeque Nation", "CAMPUS.NS": "Campus Activewear", "DEVYANI.NS": "Devyani International",
        "DMART.NS": "Avenue Supermarts", "FIVESTAR.NS": "Five Star Business", "INDIAMART.NS": "IndiaMART",
        "JUBLFOOD.NS": "Jubilant FoodWorks", "KIMS.NS": "KIMS Hospitals", "RELAXO.NS": "Relaxo Footwears",
        "SAPPHIRE.NS": "Sapphire Foods", "SHOPERSTOP.NS": "Shoppers Stop", "SPENCERS.NS": "Spencer's Retail",
        "TATACOMM.NS": "Tata Communications", "TEAMLEASE.NS": "TeamLease Services", "TRENT.NS": "Trent",
        "VGUARD.NS": "V-Guard", "VIPIND.NS": "VIP Industries", "VMART.NS": "V-Mart Retail",
        "WESTLIFE.NS": "Westlife Development", "WONDERLA.NS": "Wonderla Holidays",
        # Fashion & Apparel
        "ABFRL.NS": "Aditya Birla Fashion", "ARVINDFASN.NS": "Arvind Fashions", "BATAINDIA.NS": "Bata India",
        "CANTABIL.NS": "Cantabil Retail", "DOLLAR.NS": "Dollar Industries", "GOCOLORS.NS": "Go Colors",
        "KEWAL.NS": "Kewal Kiran", "MANYAVAR.NS": "Vedant Fashions", "PGEL.NS": "PG Electroplast",
        "RAYMOND.NS": "Raymond", "RELAXO.NS": "Relaxo Footwears", "TCNSBRANDS.NS": "TCNS Clothing",
        "TRENT.NS": "Trent", "VIPIND.NS": "VIP Industries", "WONDERLA.NS": "Wonderla Holidays",
        # Food & Restaurant Chains
        "BARBEQUE.NS": "Barbeque Nation", "BIKAJI.NS": "Bikaji Foods", "DEVYANI.NS": "Devyani International",
        "JUBLFOOD.NS": "Jubilant FoodWorks", "SAPPHIRE.NS": "Sapphire Foods", "WESTLIFE.NS": "Westlife Development",
        "ZOMATO.NS": "Zomato"
    },
    
    "🏗️ Real Estate & Construction (60+)": {
        # Real Estate Developers
        "BRIGADE.NS": "Brigade Enterprises", "DLF.NS": "DLF", "GODREJPROP.NS": "Godrej Properties",
        "IBREALEST.NS": "Indiabulls Real Estate", "KOLTEPATIL.NS": "Kolte-Patil", "LODHA.NS": "Macrotech Developers",
        "MACROTECH.NS": "Macrotech Developers", "MAHLIFE.NS": "Mahindra Lifespace", "OBEROIRLTY.NS": "Oberoi Realty",
        "PHOENIXLTD.NS": "Phoenix Mills", "PRESTIGE.NS": "Prestige Estates", "RAYMOND.NS": "Raymond",
        "SIGNATURE.NS": "Signature Global", "SOBHA.NS": "Sobha",
        # Construction & EPC
        "AHLUCONT.NS": "Ahluwalia Contracts", "ASHOKA.NS": "Ashoka Buildcon", "HCC.NS": "Hindustan Construction",
        "IRB.NS": "IRB Infrastructure", "IRCON.NS": "IRCON International", "JWL.NS": "Jupiter Wagons",
        "KEC.NS": "KEC International", "NBCC.NS": "NBCC India", "NCCLTD.NS": "NCC Limited",
        "NHPC.NS": "NHPC", "NLCINDIA.NS": "NLC India", "PFC.NS": "Power Finance Corp",
        "PNCINFRA.NS": "PNC Infratech", "POWERGRID.NS": "Power Grid", "RECLTD.NS": "REC Limited",
        "RITES.NS": "RITES", "RVNL.NS": "Rail Vikas Nigam", "SADBHAV.NS": "Sadbhav Engineering",
        # Building Materials
        "ACC.NS": "ACC Cement", "AMBUJACEM.NS": "Ambuja Cements", "APLAPOLLO.NS": "APL Apollo Tubes",
        "ASTRAL.NS": "Astral Poly", "CENTURYPLY.NS": "Century Plyboards", "CERA.NS": "Cera Sanitaryware",
        "DALMIACEM.NS": "Dalmia Bharat", "GREENPLY.NS": "Greenply Industries", "JKCEMENT.NS": "JK Cement",
        "JKLAKSHMI.NS": "JK Lakshmi Cement", "KAJARIACER.NS": "Kajaria Ceramics", "ORIENTCEM.NS": "Orient Cement",
        "RAMCOCEM.NS": "Ramco Cements", "SHREECEM.NS": "Shree Cement", "STARCEMENT.NS": "Star Cement",
        "SUPREMEIND.NS": "Supreme Industries", "ULTRACEMCO.NS": "UltraTech Cement",
        # Infrastructure Support
        "CENTURYTEX.NS": "Century Textiles", "CMSINFO.NS": "CMS Info Systems", "DCBBANK.NS": "DCB Bank",
        "ESABINDIA.NS": "ESAB India", "FINCABLES.NS": "Finolex Cables", "GUJGASLTD.NS": "Gujarat Gas",
        "HUDCO.NS": "HUDCO", "LINDEINDIA.NS": "Linde India", "SALASAR.NS": "Salasar Techno",
        "SUNFLAG.NS": "Sunflag Iron"
    },
    
    "📺 Media & Entertainment (40+)": {
        # Broadcasting & Media
        "DB.NS": "DB Corp", "HATHWAY.NS": "Hathway Cable", "INOXLEISUR.NS": "Inox Leisure",
        "JAGRAN.NS": "Jagran Prakashan", "NAZARA.NS": "Nazara Technologies", "NETWORK18.NS": "Network18 Media",
        "PVR.NS": "PVR Inox", "PVRINOX.NS": "PVR Inox", "SAREGAMA.NS": "Saregama India",
        "SUNTV.NS": "Sun TV Network", "TIPS.NS": "Tips Industries", "TV18BRDCST.NS": "TV18 Broadcast",
        "TVTODAY.NS": "TV Today", "ZEEL.NS": "Zee Entertainment",
        # Publishing & Advertising
        "DB.NS": "DB Corp", "HT.NS": "HT Media", "JAGRAN.NS": "Jagran Prakashan",
        "MAHLOG.NS": "Mahindra Logistics", "NAVNETEDUL.NS": "Navneet Education", "TREEHOUSE.NS": "Tree House Education",
        # Gaming & Digital Entertainment
        "DELTACORP.NS": "Delta Corp", "NAZARA.NS": "Nazara Technologies", "ONMOBILE.NS": "OnMobile Global",
        "ROUTE.NS": "Route Mobile", "TANLA.NS": "Tanla Platforms",
        # Theme Parks & Leisure
        "BARBEQUE.NS": "Barbeque Nation", "INOXLEISUR.NS": "Inox Leisure", "PVR.NS": "PVR Inox",
        "WONDERLA.NS": "Wonderla Holidays",
        # Music & Entertainment Production
        "EROSMEDIA.NS": "Eros International", "SAREGAMA.NS": "Saregama India", "TIPS.NS": "Tips Industries",
        "YASHRAJ.NS": "Yash Raj Films",
        # Cable & DTH
        "DISHTV.NS": "Dish TV", "GTPL.NS": "GTPL Hathway", "HATHWAY.NS": "Hathway Cable",
        "SITI.NS": "Siti Networks"
    },
    
    "🌾 Agriculture & Chemicals (90+)": {
        # Agrochemicals
        "AARTIIND.NS": "Aarti Industries", "AARTIDRUGS.NS": "Aarti Drugs", "ATUL.NS": "Atul Ltd",
        "BASF.NS": "BASF India", "BHAGERIA.NS": "Bhageria Industries", "COROMANDEL.NS": "Coromandel International",
        "DEEPAKNTR.NS": "Deepak Nitrite", "EXCEL.NS": "Excel Crop Care", "FINEORG.NS": "Fine Organic",
        "FLUOROCHEM.NS": "Gujarat Fluorochemicals", "GNFC.NS": "GNFC", "GSFC.NS": "GSFC",
        "HERANBA.NS": "Heranba Industries", "INDOFIL.NS": "Indofil Industries", "INSECTICIDES.NS": "Insecticides India",
        "NAVINFLUOR.NS": "Navin Fluorine", "NOCIL.NS": "NOCIL", "PIIND.NS": "PI Industries",
        "RALLIS.NS": "Rallis India", "SHARDACROP.NS": "Sharda Cropchem", "SRF.NS": "SRF",
        "SUMICHEM.NS": "Sumitomo Chemical", "TATACHEM.NS": "Tata Chemicals", "UPL.NS": "UPL",
        "VINATIORGA.NS": "Vinati Organics", "ZUARI.NS": "Zuari Agro Chemicals",
        # Fertilizers
        "CHAMBLFERT.NS": "Chambal Fertilizers", "COROMANDEL.NS": "Coromandel International", "DEEPAKFERT.NS": "Deepak Fertilizers",
        "FACT.NS": "FACT", "GNFC.NS": "GNFC", "GSFC.NS": "GSFC",
        "INDIACEM.NS": "India Cements", "NFL.NS": "National Fertilizers", "RCF.NS": "Rashtriya Chemicals",
        "ZUARI.NS": "Zuari Agro",
        # Seeds & Agriculture Products
        "AVANTIFEED.NS": "Avanti Feeds", "BBTC.NS": "Bombay Burmah", "CENTURYTEXT.NS": "Century Textiles",
        "HINDOILEXP.NS": "Hindustan Oil", "JUBLCHEM.NS": "Jubilant Ingrevia", "KRBL.NS": "KRBL",
        "TATACOFFEE.NS": "Tata Coffee", "VENKEYS.NS": "Venky's",
        # Specialty Chemicals
        "AARTIDRUGS.NS": "Aarti Drugs", "ALKYLAMINE.NS": "Alkyl Amines", "ATUL.NS": "Atul Ltd",
        "BASF.NS": "BASF India", "DEEPAKNTR.NS": "Deepak Nitrite", "FINEORG.NS": "Fine Organic",
        "FLUOROCHEM.NS": "Gujarat Fluorochemicals", "GULFOILLUB.NS": "Gulf Oil Lubricants", "HERANBA.NS": "Heranba Industries",
        "KIRIINDUS.NS": "Kiri Industries", "NAVINFLUOR.NS": "Navin Fluorine", "NOCIL.NS": "NOCIL",
        "PIIND.NS": "PI Industries", "PRSMJOHNSN.NS": "Prism Johnson", "RAIN.NS": "Rain Industries",
        "SOLARINDS.NS": "Solar Industries", "SRF.NS": "SRF", "SUMICHEM.NS": "Sumitomo Chemical",
        "TATACHEM.NS": "Tata Chemicals", "TATACHEMICAL.NS": "Tata Chemicals", "VINATIORGA.NS": "Vinati Organics",
        # Paints & Coatings
        "AKZOINDIA.NS": "Akzo Nobel India", "ASIANPAINT.NS": "Asian Paints", "BERGER.NS": "Berger Paints",
        "INDIGO.NS": "Indigo Paints", "KANSAINER.NS": "Kansai Nerolac", "SHALPAINTS.NS": "Shalimar Paints",
        # Adhesives & Sealants
        "ASTRAL.NS": "Astral Poly", "FINEORG.NS": "Fine Organic", "PIDILITIND.NS": "Pidilite Industries",
        "SUPREMEIND.NS": "Supreme Industries"
    },
    
    "🔬 Specialty & Emerging Sectors (100+)": {
        # Logistics & Supply Chain
        "AEGISCHEM.NS": "Aegis Logistics", "ALLCARGO.NS": "Allcargo Logistics", "BLUEDART.NS": "Blue Dart Express",
        "CONCOR.NS": "Container Corporation", "GATI.NS": "Gati", "MAHLOG.NS": "Mahindra Logistics",
        "TCI.NS": "Transport Corporation", "TCIEXP.NS": "TCI Express", "VRL.NS": "VRL Logistics",
        # Education & Training
        "APTECH.NS": "Aptech", "CAREEREDGE.NS": "Career Point", "NAVNETEDUL.NS": "Navneet Education",
        "TREEHOUSE.NS": "Tree House Education", "ZEE.NS": "Zee Learn",
        # Hotels & Hospitality
        "CHALET.NS": "Chalet Hotels", "EIH.NS": "EIH", "INDHOTEL.NS": "Indian Hotels",
        "LEMONTREE.NS": "Lemon Tree Hotels", "MAHINDCIE.NS": "Mahindra Holidays", "TAJGVK.NS": "Taj GVK Hotels",
        # Travel & Tourism
        "COX&KINGS.NS": "Cox & Kings", "EASEMYTRIP.NS": "EaseMyTrip", "IRCTC.NS": "IRCTC",
        "SPICEJET.NS": "SpiceJet", "TBO.NS": "TBO Tek", "THOMASCOOK.NS": "Thomas Cook",
        # Security & Surveillance
        "CMSINFO.NS": "CMS Info Systems", "SIS.NS": "SIS Limited", "UNOMINDA.NS": "Uno Minda",
        # Packaging
        "AADHARHFC.NS": "Aadhar Housing", "AARTISURF.NS": "Aarti Surfactants", "EMAMIPAP.NS": "Emami Paper",
        "JKPAPER.NS": "JK Paper", "SESAGOA.NS": "Sesa Goa", "TNIDETF.NS": "TNPL",
        "WESTPAPER.NS": "West Coast Paper",
        # Defence & Aerospace
        "BDL.NS": "Bharat Dynamics", "BEL.NS": "Bharat Electronics", "GRSE.NS": "Garden Reach Shipbuilders",
        "HAL.NS": "Hindustan Aeronautics", "MAZDOCK.NS": "Mazagon Dock", "MIDHANI.NS": "Mishra Dhatu Nigam",
        # Textiles & Apparels
        "AARVEEDEN.NS": "Aarvee Denims", "ALOKTEXT.NS": "Alok Textile", "ARSS.NS": "ARSS Infrastructure",
        "BANSWRAS.NS": "Banswara Syntex", "CENTURYTEX.NS": "Century Textiles", "DOLLAR.NS": "Dollar Industries",
        "GOKEX.NS": "Gokaldas Exports", "KPR.NS": "KPR Mill", "NAHARINDUS.NS": "Nahar Industrial",
        "NITIN.NS": "Nitin Spinners", "RAYMOND.NS": "Raymond", "RSWM.NS": "RSWM",
        "SPENTEX.NS": "Spentex Industries", "SUTLEJTEX.NS": "Sutlej Textiles", "TRIDENT.NS": "Trident",
        "VARDHACRLC.NS": "Vardhman Textiles", "WELSPUNIND.NS": "Welspun India",
        # Glass & Ceramics
        "ASAHIINDIA.NS": "Asahi India Glass", "CERA.NS": "Cera Sanitaryware", "HGINFRA.NS": "HG Infra",
        "HLEGLAS.NS": "HLE Glascoat", "KAJARIACER.NS": "Kajaria Ceramics", "ORIENT.NS": "Orient Cement",
        "PRISM.NS": "Prism Johnson", "SOMANY.NS": "Somany Ceramics",
        # Pipes & Fittings
        "APLAPOLLO.NS": "APL Apollo Tubes", "APOLLOPIPE.NS": "Apollo Pipes", "ASTRAL.NS": "Astral Poly",
        "FINOLEX.NS": "Finolex Industries", "NAGREEKEXP.NS": "Nagreeka Exports", "PRINCEPIPE.NS": "Prince Pipes",
        "SUPREME.NS": "Supreme Industries", "VALIANTORG.NS": "Valiant Organics",
        # Bearings & Industrial Components
        "FAG.NS": "Schaeffler India", "NBC.NS": "National Bearings", "NRB.NS": "NRB Bearings",
        "SCHAEFFLER.NS": "Schaeffler India", "SKFINDIA.NS": "SKF India", "TIMKEN.NS": "Timken India",
        # Cables & Wires
        "FINCABLES.NS": "Finolex Cables", "GALAXYSURF.NS": "Galaxy Surfactants", "KEI.NS": "KEI Industries",
        "ORIENTELEC.NS": "Orient Electric", "POLYCAB.NS": "Polycab India", "VGUARD.NS": "V-Guard Industries",
        # Pumps & Motors
        "CESC.NS": "CESC", "CROMPTON.NS": "Crompton Greaves", "HAVELLS.NS": "Havells India",
        "KIRLOSENG.NS": "Kirloskar Oil", "KIRLFER.NS": "Kirloskar Ferrous", "KSB.NS": "KSB Pumps",
        "ORIENTELEC.NS": "Orient Electric", "SHAKTICP.NS": "Shakti Corporation"
    }
}

# Industry Benchmarks - Higher multiples for midcaps
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
# IMPROVED VALUATION FUNCTIONS WITH RATE LIMIT HANDLING
# ============================================================================

def retry_with_backoff(retries=3, backoff_in_seconds=2):
    """
    Decorator for retrying function calls with exponential backoff
    Helps avoid rate limiting by spacing out requests
    """
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

@st.cache_data(ttl=3600)  # Cache for 1 HOUR (increased from 5 minutes)
@retry_with_backoff(retries=3, backoff_in_seconds=2)
def fetch_stock_data(ticker):
    """
    Fetch stock data with retry logic and extended caching
    
    Rate Limit Strategy:
    - Cache data for 1 hour to reduce API calls
    - Add 0.5 second delay between requests
    - Retry 3 times with exponential backoff
    - Better error messages for users
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
    
    Returns:
        tuple: (stock_info_dict, error_message)
    """
    try:
        # Small delay to avoid hitting rate limits
        time.sleep(0.5)
        
        # Fetch stock data
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Validate data
        if not info or len(info) < 5:
            return None, "Unable to fetch data - stock may not exist or data unavailable"
        
        return info, None
        
    except Exception as e:
        error_msg = str(e)
        
        # Parse different error types
        if "429" in error_msg or "rate" in error_msg.lower() or "limit" in error_msg.lower():
            return None, "⏱️ RATE LIMIT REACHED: Yahoo Finance API limit hit. Please wait 2-3 minutes and try again, or analyze a different stock."
        elif "404" in error_msg:
            return None, "❌ STOCK NOT FOUND: Please check the ticker symbol and try again."
        elif "timeout" in error_msg.lower():
            return None, "⏰ REQUEST TIMEOUT: Server is slow. Please try again in a moment."
        elif "connection" in error_msg.lower():
            return None, "🌐 CONNECTION ERROR: Please check your internet connection."
        else:
            return None, f"❌ ERROR: {error_msg[:150]}"

def calculate_valuations(info):
    """
    Calculate stock valuations using dual methodology:
    1. PE Multiple Valuation
    2. EV/EBITDA Valuation
    
    Returns comprehensive valuation metrics for analysis
    """
    try:
        # Extract key metrics
        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        trailing_eps = info.get('trailingEps', 0)
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        market_cap = info.get('marketCap', 0)
        shares = info.get('sharesOutstanding', 1)
        sector = info.get('sector', 'Default')
        
        # Get industry benchmarks
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        
        # ===== PE VALUATION METHOD =====
        
        # Calculate historical PE (conservative: 90% of current)
        if trailing_pe and trailing_pe > 0:
            historical_pe = trailing_pe * 0.9
        else:
            historical_pe = industry_pe
        
        # Blended PE: Average of industry and historical
        blended_pe = (industry_pe + historical_pe) / 2
        
        # Calculate fair values
        fair_value_industry = trailing_eps * industry_pe if trailing_eps else None
        fair_value_blended = trailing_eps * blended_pe if trailing_eps else None
        
        # Average fair value from PE method
        fair_values_pe = [fv for fv in [fair_value_industry, fair_value_blended] if fv]
        fair_value_pe = np.mean(fair_values_pe) if fair_values_pe else None
        
        # Calculate upside percentage
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
        # ===== EV/EBITDA VALUATION METHOD =====
        
        # Calculate current EV/EBITDA multiple
        current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
        
        # Determine target EV/EBITDA
        if current_ev_ebitda and 0 < current_ev_ebitda < 50:
            target_ev_ebitda = (industry_ev_ebitda + current_ev_ebitda * 0.9) / 2
        else:
            target_ev_ebitda = industry_ev_ebitda
        
        # Calculate fair value from EV/EBITDA
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
        
        # Return comprehensive valuation dictionary
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
        
    except Exception as e:
        st.error(f"⚠️ Error calculating valuations: {str(e)}")
        return None

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>📊 MIDCAP 800+ STOCK VALUATION DASHBOARD</h1>
    <p>High Growth Potential • 800+ Midcap Stocks • Real-time Analysis</p>
</div>
""", unsafe_allow_html=True)

# Smart Caching Info
st.info("""
💡 **Smart Caching Active:** Stock data is cached for 1 hour after first fetch. 
Re-analyzing the same stock within 1 hour is instant and doesn't use API quota! 
""")

# Risk Warning
st.markdown("""
<div class="risk-warning">
    ⚠️ MIDCAP RISK WARNING: Midcap stocks are more volatile than largecaps. Higher growth potential comes with higher risk.
</div>
""", unsafe_allow_html=True)

# Logout Button
if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ============================================================================
# STOCK SELECTION SIDEBAR
# ============================================================================

st.sidebar.header("📈 Stock Selection")

# Flatten all stocks for searching
all_stocks = {}
for category, stocks in MIDCAP_500_STOCKS.items():
    all_stocks.update(stocks)

# Total stock count
st.sidebar.success(f"**📊 Total Stocks: {len(all_stocks)}**")

# Category selection
selected_category = st.sidebar.selectbox(
    "Category",
    ["🔍 All Stocks"] + list(MIDCAP_500_STOCKS.keys())
)

# Search functionality
search_term = st.sidebar.text_input("🔍 Search Stock", placeholder="Type company name or ticker...")

# Filter stocks based on selection
if search_term:
    filtered_stocks = {
        ticker: name for ticker, name in all_stocks.items()
        if search_term.upper() in ticker or search_term.upper() in name.upper()
    }
elif selected_category == "🔍 All Stocks":
    filtered_stocks = all_stocks
else:
    filtered_stocks = MIDCAP_500_STOCKS[selected_category]

# Show filtered count
if search_term:
    st.sidebar.info(f"Found: {len(filtered_stocks)} stocks")
elif selected_category != "🔍 All Stocks":
    st.sidebar.info(f"Category: {len(filtered_stocks)} stocks")

# Stock selection dropdown
stock_options = [f"{name} ({ticker})" for ticker, name in filtered_stocks.items()]

if stock_options:
    selected_stock = st.sidebar.selectbox("Select Stock", stock_options)
    selected_ticker = selected_stock.split("(")[1].strip(")")
else:
    st.sidebar.warning("No stocks found matching your search")
    selected_ticker = None

# Custom ticker input
st.sidebar.markdown("---")
custom_ticker = st.sidebar.text_input(
    "Or Enter Custom Ticker", 
    placeholder="e.g., DIXON.NS"
)

# Rate Limit Guidelines
with st.sidebar.expander("📊 Rate Limit Guidelines"):
    st.markdown("""
    **To Avoid Rate Limits:**
    
    ✅ **DO:**
    - Wait 1-2 seconds between stocks
    - Re-analyze same stock within 1 hour (instant!)
    - Analyze during off-peak hours
    
    ❌ **DON'T:**
    - Analyze 10+ stocks rapidly
    - Refresh page repeatedly
    - Have multiple tabs open
    
    ⏰ **If limit reached:** Wait 2-3 minutes
    """)

# Analyze Button
if st.sidebar.button("🚀 ANALYZE STOCK", use_container_width=True):
    if custom_ticker:
        st.session_state.analyze_ticker = custom_ticker.upper()
    elif selected_ticker:
        st.session_state.analyze_ticker = selected_ticker
    else:
        st.error("Please select or enter a stock ticker")

# ============================================================================
# MAIN ANALYSIS SECTION
# ============================================================================

if 'analyze_ticker' in st.session_state:
    ticker = st.session_state.analyze_ticker
    
    # Show analysis in progress
    with st.spinner(f"🔄 Fetching data for {ticker}... Please wait..."):
        info, error = fetch_stock_data(ticker)
    
    # Handle errors
    if error:
        st.error(f"❌ {error}")
        
        # Show helpful tips for rate limit errors
        if "RATE LIMIT" in error:
            st.warning("""
            **💡 What to do:**
            1. ⏰ Wait 2-3 minutes
            2. 🔄 Try again or analyze a different stock
            3. 📊 Check if data is cached (stocks analyzed in last hour load instantly)
            
            **Why this happens:**
            - Yahoo Finance has free API limits (2,000 requests/hour)
            - Multiple users accessing simultaneously
            - Too many rapid requests
            
            **Tip:** Analyze stocks during off-peak hours for better experience!
            """)
        st.stop()
    
    if info is None:
        st.error("❌ Failed to fetch stock data. Please try another stock.")
        st.stop()
    
    # Calculate valuations
    valuations = calculate_valuations(info)
    
    if valuations is None:
        st.error("❌ Unable to calculate valuations for this stock.")
        st.stop()
    
    # ========================================================================
    # COMPANY INFORMATION
    # ========================================================================
    
    company_name = info.get('longName', ticker)
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    
    st.markdown(f"## 🏢 {company_name}")
    st.markdown(f"**Sector:** {sector} | **Industry:** {industry} | **Ticker:** {ticker}")
    
    st.markdown("---")
    
    # ========================================================================
    # KEY METRICS ROW
    # ========================================================================
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Current Price", f"Rs {valuations['price']:.2f}")
    
    with col2:
        pe_display = f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else "N/A"
        st.metric("📊 PE Ratio", pe_display)
    
    with col3:
        eps_display = f"Rs {valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else "N/A"
        st.metric("💰 EPS (TTM)", eps_display)
    
    with col4:
        mcap_cr = valuations['market_cap'] / 10000000
        st.metric("🏦 Market Cap", f"Rs {mcap_cr:.0f} Cr")
    
    # ========================================================================
    # RECOMMENDATION
    # ========================================================================
    
    # Calculate average upside
    upside_values = []
    if valuations['upside_pe'] is not None:
        upside_values.append(valuations['upside_pe'])
    if valuations['upside_ev'] is not None:
        upside_values.append(valuations['upside_ev'])
    
    avg_upside = np.mean(upside_values) if upside_values else 0
    
    # Determine recommendation (adjusted for midcaps)
    if avg_upside > 25:
        rec_class = "rec-strong-buy"
        rec_text = "⭐⭐⭐ STRONG BUY"
        rec_desc = "High growth potential - Significantly undervalued for midcap"
    elif avg_upside > 15:
        rec_class = "rec-buy"
        rec_text = "⭐⭐ BUY"
        rec_desc = "Good value - Accumulate on dips"
    elif avg_upside > 0:
        rec_class = "rec-buy"
        rec_text = "⭐ ACCUMULATE"
        rec_desc = "Slightly undervalued - Consider small position"
    elif avg_upside > -10:
        rec_class = "rec-hold"
        rec_text = "🟡 HOLD"
        rec_desc = "Fairly valued - Wait for better entry"
    else:
        rec_class = "rec-avoid"
        rec_text = "❌ AVOID"
        rec_desc = "Overvalued - High risk of correction"
    
    st.markdown(f"""
    <div class="{rec_class}">
        <div>{rec_text}</div>
        <div style="font-size: 1.2rem; margin-top: 0.5rem;">Potential Return: {avg_upside:+.2f}%</div>
        <div style="font-size: 1rem; margin-top: 0.5rem;">{rec_desc}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================================================
    # GAUGE CHARTS
    # ========================================================================
    
    if valuations['upside_pe'] is not None and valuations['upside_ev'] is not None:
        st.subheader("📈 Upside/Downside Analysis")
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=("PE Multiple Valuation", "EV/EBITDA Valuation")
        )
        
        # PE Gauge
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
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            }
        ), row=1, col=1)
        
        # EV/EBITDA Gauge
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
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            }
        ), row=1, col=2)
        
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # VALUATION COMPARISON BAR CHART
    # ========================================================================
    
    st.subheader("💰 Current Price vs Fair Value")
    
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
        xaxis_title="Valuation Method",
        yaxis_title="Price (Rs)",
        template='plotly_white',
        showlegend=True
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # ========================================================================
    # FINANCIAL METRICS TABLE
    # ========================================================================
    
    st.subheader("📋 Detailed Financial Metrics")
    
    metrics_data = {
        'Metric': [
            '💵 Current Price',
            '📊 PE Ratio (TTM)',
            '🏭 Industry PE Benchmark',
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
    
    # ========================================================================
    # EDUCATIONAL CONTENT
    # ========================================================================
    
    st.markdown("---")
    st.markdown("### 💡 Understanding This Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **Why Invest in Midcaps?**
        - 🚀 Higher growth potential than largecaps
        - 💎 More stable than smallcaps
        - 📈 Can become future bluechips
        - 💰 Better risk-reward ratio
        - 🎯 Sweet spot for wealth creation
        """)
    
    with col2:
        st.warning("""
        **Midcap Risks to Consider:**
        - 📉 More volatile than largecaps
        - 💧 Lower liquidity
        - 🔍 Less analyst coverage
        - ⚡ Vulnerable in market crashes
        - ⏰ Requires patience (3-5 years)
        """)
    
    st.info("""
    **📊 This Dashboard Uses:**
    
    1. **PE Multiple Valuation**: Compares company's PE to industry average
    2. **EV/EBITDA Valuation**: Enterprise value based approach
    3. **Blended Approach**: Combines both methods for robust analysis
    
    **⚠️ Important Notes:**
    - This is **educational content**, not financial advice
    - Always do your own research before investing
    - Consider company fundamentals, management quality, and future prospects
    - Past performance doesn't guarantee future results
    - Consult a financial advisor for personalized advice
    """)
    
else:
    # ========================================================================
    # DEFAULT VIEW (No Stock Selected)
    # ========================================================================
    
    st.info("👈 Select a midcap stock from the sidebar and click **ANALYZE STOCK** to begin!")
    
    st.markdown("### 🚀 Why Invest in Midcaps?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **Benefits:**
        - **Growth Potential**: 15-25% annual returns possible
        - **Stability**: More established than smallcaps
        - **Opportunities**: Under-researched gems
        - **Future Leaders**: Tomorrow's largecaps
        - **Diversification**: Balance between risk and reward
        """)
    
    with col2:
        st.warning("""
        **Considerations:**
        - **Volatility**: More fluctuations than largecaps
        - **Research**: Requires thorough analysis
        - **Patience**: 3-5 year investment horizon
        - **Risk**: Can underperform in bear markets
        - **Liquidity**: Lower than largecaps
        """)
    
    st.markdown(f"### 📊 Total Midcap Stocks Available: **{len(all_stocks)}**")
    
    # Success stories
    st.markdown("### 💎 Historical Midcap Success Stories")
    st.info("""
    **Companies that grew from midcaps to largecaps:**
    - **Asian Paints**: 50x returns in 15 years
    - **Page Industries**: 100x returns in 12 years
    - **Bajaj Finance**: From midcap to financial giant
    - **Avenue Supermarts (DMart)**: Retail success story
    - **PI Industries**: Chemicals sector winner
    
    **The key?** Identifying quality businesses early!
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p><strong>💡 NYZTrade Midcap Valuation Dashboard | {len(all_stocks)}+ Stocks</strong></p>
    <p>Educational Tool | Not Financial Advice | Powered by yfinance</p>
    <p>⚠️ Always do your own research before investing</p>
</div>
""", unsafe_allow_html=True)
