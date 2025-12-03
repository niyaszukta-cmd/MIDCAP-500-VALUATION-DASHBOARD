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

st.set_page_config(page_title="NYZTrade Midcap", page_icon="📊", layout="wide")

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
        st.markdown("<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; text-align: center;'><h1 style='color: white;'>NYZTrade Pro</h1></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.button("Login", on_click=password_entered, use_container_width=True)
            st.info("demo/demo123")
        return False
    elif not st.session_state["password_correct"]:
        st.error("Incorrect")
        return False
    return True

if not check_password():
    st.stop()

st.markdown("""
<style>
.main-header{background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);padding:2.5rem;border-radius:20px;text-align:center;color:white;margin-bottom:2rem;}
.fair-value-box{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:2rem;border-radius:15px;text-align:center;color:white;margin:2rem 0;}
.rec-strong-buy{background: linear-gradient(135deg, #00C853 0%, #64DD17 100%);color:white;padding:2rem;border-radius:15px;text-align:center;font-size:2rem;font-weight:bold;}
.rec-buy{background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);color:white;padding:2rem;border-radius:15px;text-align:center;font-size:2rem;font-weight:bold;}
.rec-hold{background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);color:white;padding:2rem;border-radius:15px;text-align:center;font-size:2rem;font-weight:bold;}
.rec-avoid{background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);color:white;padding:2rem;border-radius:15px;text-align:center;font-size:2rem;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

MIDCAP_STOCKS = {
    "Banking Finance 1": {
        "ANGELONE.NS":"Angel One","ANANDRATHI.NS":"Anand Rathi","AAVAS.NS":"Aavas Financiers","BAJAJFINSV.NS":"Bajaj Finserv",
        "CDSL.NS":"CDSL","CHOLAFIN.NS":"Cholamandalam Investment","CREDITACC.NS":"CreditAccess Grameen","CRISIL.NS":"CRISIL",
        "CSB.NS":"CSB Bank","EQUITAS.NS":"Equitas Holdings","FEDERALBNK.NS":"Federal Bank","FINOPB.NS":"Fino Payments",
        "HDFCAMC.NS":"HDFC AMC","IIFL.NS":"IIFL Finance","IIFLSEC.NS":"IIFL Securities","IRFC.NS":"IRFC",
        "ISEC.NS":"ICICI Securities","JMFINANCIL.NS":"JM Financial","KALYANKJIL.NS":"Kalyan Jewellers","KFINTECH.NS":"KFin Technologies"
    },
    "Banking Finance 2": {
        "LICHSGFIN.NS":"LIC Housing","MASFIN.NS":"MAS Financial","MOTILALOFS.NS":"Motilal Oswal","MUTHOOTFIN.NS":"Muthoot Finance",
        "PNBHOUSING.NS":"PNB Housing","RBL.NS":"RBL Bank","SBFC.NS":"SBFC Finance","STARHEALTH.NS":"Star Health",
        "UJJIVAN.NS":"Ujjivan Small Finance","UTIAMC.NS":"UTI AMC","AUBANK.NS":"AU Small Finance","BANDHANBNK.NS":"Bandhan Bank",
        "IDFCFIRSTB.NS":"IDFC First Bank","INDUSINDBK.NS":"IndusInd Bank","BANKBARODA.NS":"Bank of Baroda","CANBK.NS":"Canara Bank",
        "UNIONBANK.NS":"Union Bank","CENTRALBK.NS":"Central Bank","INDIANB.NS":"Indian Bank","IOB.NS":"Indian Overseas Bank"
    },
    "Banking Finance 3": {
        "BANKINDIA.NS":"Bank of India","MAHABANK.NS":"Bank of Maharashtra","J&KBANK.NS":"Jammu Kashmir Bank","KARNATBNK.NS":"Karnataka Bank",
        "DCBBANK.NS":"DCB Bank","ICICIGI.NS":"ICICI Lombard","ICICIPRULI.NS":"ICICI Prudential Life","SBILIFE.NS":"SBI Life",
        "HDFCLIFE.NS":"HDFC Life","MAXHEALTH.NS":"Max Healthcare","POLICYBZR.NS":"PB Fintech","NUVOCO.NS":"Nuvoco Vistas",
        "SPANDANA.NS":"Spandana Sphoorty","SWANENERGY.NS":"Swan Energy","BAJAJHLDNG.NS":"Bajaj Holdings","MAHLIFE.NS":"Mahindra Lifespace",
        "TATAINVEST.NS":"Tata Investment","SUNDARMFIN.NS":"Sundaram Finance","SHRIRAMFIN.NS":"Shriram Finance","MANAPPURAM.NS":"Manappuram Finance"
    },
    "Banking Finance 4": {
        "PNBGILTS.NS":"PNB Gilts","APTUS.NS":"Aptus Value Housing","HOMEFIRST.NS":"Home First Finance","AADHARHFC.NS":"Aadhar Housing",
        "CAPLIPOINT.NS":"Caplin Point","CHOLA.NS":"Cholamandalam Financial","CIEINDIA.NS":"CIE Automotive","JSWHL.NS":"JSW Holdings",
        "MUTHOOTCAP.NS":"Muthoot Capital","ABSLAMC.NS":"Aditya Birla Sun Life AMC","L&TFH.NS":"L&T Finance Holdings","CHOLAHLDNG.NS":"Cholamandalam Holdings",
        "IIFLWAM.NS":"IIFL Wealth","BAJFINANCE.NS":"Bajaj Finance","HDFCBANK.NS":"HDFC Bank","KOTAKBANK.NS":"Kotak Mahindra",
        "AXISBANK.NS":"Axis Bank","ICICIBANK.NS":"ICICI Bank","SBIN.NS":"State Bank","INDUSIND.NS":"IndusInd Bank"
    },
    "IT Technology 1": {
        "COFORGE.NS":"Coforge","CYIENT.NS":"Cyient","ECLERX.NS":"eClerx Services","HAPPSTMNDS.NS":"Happiest Minds",
        "INTELLECT.NS":"Intellect Design","KPITTECH.NS":"KPIT Technologies","LTIM.NS":"LTIMindtree","MASTEK.NS":"Mastek",
        "MPHASIS.NS":"Mphasis","NEWGEN.NS":"Newgen Software","NIITLTD.NS":"NIIT Ltd","OFSS.NS":"Oracle Financial",
        "PERSISTENT.NS":"Persistent Systems","ZENSAR.NS":"Zensar Technologies","ROUTE.NS":"Route Mobile","DATAMATICS.NS":"Datamatics Global",
        "SONATSOFTW.NS":"Sonata Software","SASKEN.NS":"Sasken Technologies","TATAELXSI.NS":"Tata Elxsi","TECHM.NS":"Tech Mahindra"
    },
    "IT Technology 2": {
        "3MINDIA.NS":"3M India","AFFLE.NS":"Affle India","EASEMYTRIP.NS":"EaseMyTrip","ZOMATO.NS":"Zomato",
        "NYKAA.NS":"Nykaa","PAYTM.NS":"Paytm","POLICYBZR.NS":"PB Fintech","BLUESTARCO.NS":"Blue Star",
        "CAMPUS.NS":"Campus Activewear","DIXON.NS":"Dixon Technologies","HLEGLAS.NS":"HLE Glascoat","HONAUT.NS":"Honeywell Automation",
        "LXCHEM.NS":"Laxmi Organic","RPTECH.NS":"RP Tech India","AMBER.NS":"Amber Enterprises","SYMPHONY.NS":"Symphony",
        "VOLTAS.NS":"Voltas","WHIRLPOOL.NS":"Whirlpool India","VGUARD.NS":"V-Guard Industries","CROMPTON.NS":"Crompton Greaves"
    },
    "IT Technology 3": {
        "HAVELLS.NS":"Havells India","ORIENTELEC.NS":"Orient Electric","INDIAMART.NS":"IndiaMART","JUSTDIAL.NS":"Just Dial",
        "MATRIMONY.NS":"Matrimony.com","NAZARA.NS":"Nazara Technologies","SHOPERSTOP.NS":"Shoppers Stop","TATACOMM.NS":"Tata Communications",
        "TATATECH.NS":"Tata Technologies","TEAMLEASE.NS":"TeamLease Services","CARTRADE.NS":"CarTrade Tech","LATENTVIEW.NS":"LatentView Analytics",
        "MPSLTD.NS":"MPS Limited","RAINBOW.NS":"Rainbow Children","REDINGTON.NS":"Redington","STLTECH.NS":"Sterlite Technologies",
        "SUBROS.NS":"Subros","SUPRAJIT.NS":"Suprajit Engineering","SWARAJENG.NS":"Swaraj Engines","TANLA.NS":"Tanla Platforms"
    },
    "IT Technology 4": {
        "TCNSBRANDS.NS":"TCNS Clothing","TIMKEN.NS":"Timken India","TRIVENI.NS":"Triveni Turbine","TTKHLTCARE.NS":"TTK Healthcare",
        "TTKPRESTIG.NS":"TTK Prestige","VIPIND.NS":"VIP Industries","VSTIND.NS":"VST Industries","WELSPUNIND.NS":"Welspun India",
        "WESTLIFE.NS":"Westlife Development","WIPRO.NS":"Wipro","INFY.NS":"Infosys","TCS.NS":"TCS",
        "HCLTECH.NS":"HCL Technologies","LTI.NS":"LTI","MINDTREE.NS":"Mindtree","TECHM.NS":"Tech Mahindra",
        "HEXAWARE.NS":"Hexaware Technologies","CYIENT.NS":"Cyient","L&TTS.NS":"L&T Technology","POLYCAB.NS":"Polycab India"
    },
    "Pharma Healthcare 1": {
        "AARTIDRUGS.NS":"Aarti Drugs","ABBOTINDIA.NS":"Abbott India","AJANTPHARM.NS":"Ajanta Pharma","ALEMBICLTD.NS":"Alembic Pharma",
        "ALKEM.NS":"Alkem Laboratories","ASTRAZEN.NS":"AstraZeneca Pharma","AUROBINDO.NS":"Aurobindo Pharma","BIOCON.NS":"Biocon",
        "CADILAHC.NS":"Cadila Healthcare","CAPLIPOINT.NS":"Caplin Point","CIPLA.NS":"Cipla","DIVISLAB.NS":"Divi's Laboratories",
        "DRREDDY.NS":"Dr Reddy's Labs","ERIS.NS":"Eris Lifesciences","FINEORG.NS":"Fine Organic","GLENMARK.NS":"Glenmark Pharma",
        "GLAXO.NS":"GlaxoSmithKline","GRANULES.NS":"Granules India","HETERO.NS":"Hetero Drugs","IPCALAB.NS":"IPCA Laboratories"
    },
    "Pharma Healthcare 2": {
        "JBCHEPHARM.NS":"JB Chemicals","LUPIN.NS":"Lupin","MANKIND.NS":"Mankind Pharma","METROPOLIS.NS":"Metropolis Healthcare",
        "NATCOPHARM.NS":"Natco Pharma","PFIZER.NS":"Pfizer","SANOFI.NS":"Sanofi India","SOLARA.NS":"Solara Active",
        "SUNPHARMA.NS":"Sun Pharma","SYNGENE.NS":"Syngene International","TORNTPHARM.NS":"Torrent Pharma","VIMTA.NS":"Vimta Labs",
        "WOCKPHARMA.NS":"Wockhardt","ZYDUSLIFE.NS":"Zydus Lifesciences","ZYDUSWELL.NS":"Zydus Wellness","APOLLOHOSP.NS":"Apollo Hospitals",
        "FORTIS.NS":"Fortis Healthcare","MAXHEALTH.NS":"Max Healthcare","LALPATHLAB.NS":"Dr Lal PathLabs","THYROCARE.NS":"Thyrocare"
    },
    "Pharma Healthcare 3": {
        "KRSNAA.NS":"Krsnaa Diagnostics","RAINBOW.NS":"Rainbow Children","KIMS.NS":"KIMS Hospitals","MEDANTA.NS":"Global Health Medanta",
        "POLYMED.NS":"Poly Medicure","STAR.NS":"Strides Pharma","SUVEN.NS":"Suven Pharma","SUVENPHAR.NS":"Suven Pharmaceuticals",
        "SEQUENT.NS":"Sequent Scientific","SHILPAMED.NS":"Shilpa Medicare","BLISSGVS.NS":"Bliss GVS Pharma","INDOCO.NS":"Indoco Remedies",
        "JUBLPHARMA.NS":"Jubilant Pharma","LAURUS.NS":"Laurus Labs","MARKSANS.NS":"Marksans Pharma","NEULANDLAB.NS":"Neuland Laboratories",
        "AADHARHFC.NS":"Aadhar Housing","ALEMBIC.NS":"Alembic Pharmaceuticals","ASIANPAINT.NS":"Asian Paints","BERGER.NS":"Berger Paints"
    },
    "Auto Components 1": {
        "ASHOKLEY.NS":"Ashok Leyland","BAJAJ-AUTO.NS":"Bajaj Auto","BALKRISIND.NS":"Balkrishna Industries","BHARATFORG.NS":"Bharat Forge",
        "BOSCHLTD.NS":"Bosch","EICHERMOT.NS":"Eicher Motors","ESCORTS.NS":"Escorts Kubota","EXIDEIND.NS":"Exide Industries",
        "FORCEMOT.NS":"Force Motors","HEROMOTOCO.NS":"Hero MotoCorp","M&M.NS":"Mahindra & Mahindra","MARUTI.NS":"Maruti Suzuki",
        "MRF.NS":"MRF","TATAMOTORS.NS":"Tata Motors","TVSMOTOR.NS":"TVS Motor","AMARAJABAT.NS":"Amara Raja",
        "APOLLOTYRE.NS":"Apollo Tyres","CRAFTSMAN.NS":"Craftsman Automation","ENDURANCE.NS":"Endurance Technologies","FINCABLES.NS":"Finolex Cables"
    },
    "Auto Components 2": {
        "JKTYRE.NS":"JK Tyre","MAHINDCIE.NS":"Mahindra CIE","MOTHERSON.NS":"Motherson Sumi","SANDHAR.NS":"Sandhar Technologies",
        "SANSERA.NS":"Sansera Engineering","SCHAEFFLER.NS":"Schaeffler India","SKFINDIA.NS":"SKF India","SWARAJENG.NS":"Swaraj Engines",
        "TIMKEN.NS":"Timken India","TUBE.NS":"Tube Investments","WHEELS.NS":"Wheels India","ABB.NS":"ABB India",
        "AIAENG.NS":"AIA Engineering","ALICON.NS":"Alicon Castalloy","AMBER.NS":"Amber Enterprises","APOLLOPIPE.NS":"Apollo Pipes",
        "ASAHIINDIA.NS":"Asahi India Glass","CEATLTD.NS":"CEAT","CUMMINSIND.NS":"Cummins India","ELGIRUBCO.NS":"Elgi Rubber"
    },
    "Auto Components 3": {
        "GABRIEL.NS":"Gabriel India","GREAVESCOT.NS":"Greaves Cotton","JAMNAAUTO.NS":"Jamna Auto","KALYANI.NS":"Kalyani Forge",
        "MAHSEAMLES.NS":"Maharashtra Seamless","MAJESAUTO.NS":"Munjal Auto","MFSL.NS":"Max Financial","MHRIL.NS":"Mahindra Holidays",
        "RAMCOCEM.NS":"Ramco Cements","RATNAMANI.NS":"Ratnamani Metals","SHARDACROP.NS":"Sharda Cropchem","SUPRAJIT.NS":"Suprajit Engineering",
        "TIINDIA.NS":"Tube Investments","WHEELS.NS":"Wheels India","MUTHOOTFIN.NS":"Muthoot Finance","BAJAJHLDNG.NS":"Bajaj Holdings",
        "CHOLAHLDNG.NS":"Cholamandalam Holdings","SUNDARMFIN.NS":"Sundaram Finance","SHRIRAMFIN.NS":"Shriram Finance","MANAPPURAM.NS":"Manappuram Finance"
    },
    "FMCG Consumer 1": {
        "ABFRL.NS":"Aditya Birla Fashion","AKZOINDIA.NS":"Akzo Nobel","AVANTIFEED.NS":"Avanti Feeds","BAJAJELEC.NS":"Bajaj Electricals",
        "BAJAJHLDNG.NS":"Bajaj Holdings","BATAINDIA.NS":"Bata India","BIKAJI.NS":"Bikaji Foods","BRITANNIA.NS":"Britannia Industries",
        "CCL.NS":"CCL Products","COLPAL.NS":"Colgate Palmolive","DABUR.NS":"Dabur India","EMAMILTD.NS":"Emami",
        "GILLETTE.NS":"Gillette India","GODREJCP.NS":"Godrej Consumer","GODFRYPHLP.NS":"Godfrey Phillips","GUJALKALI.NS":"Gujarat Alkalies",
        "HAVELLS.NS":"Havells India","HBLPOWER.NS":"HBL Power","HINDUNILVR.NS":"Hindustan Unilever","ITC.NS":"ITC"
    },
    "FMCG Consumer 2": {
        "JKLAKSHMI.NS":"JK Lakshmi Cement","JKPAPER.NS":"JK Paper","JUBLFOOD.NS":"Jubilant FoodWorks","KAJARIACER.NS":"Kajaria Ceramics",
        "KPRMILL.NS":"KPR Mill","MARICO.NS":"Marico","MRPL.NS":"MRPL","NAVINFLUOR.NS":"Navin Fluorine",
        "NESTLEIND.NS":"Nestle India","ORIENTELEC.NS":"Orient Electric","PAGEIND.NS":"Page Industries","PCBL.NS":"PCBL",
        "PIIND.NS":"PI Industries","POLYMED.NS":"Poly Medicure","RADICO.NS":"Radico Khaitan","RAJESHEXPO.NS":"Rajesh Exports",
        "RELAXO.NS":"Relaxo Footwears","SOLARINDS.NS":"Solar Industries","SYMPHONY.NS":"Symphony","TATACHEM.NS":"Tata Chemicals"
    },
    "FMCG Consumer 3": {
        "TATACONSUM.NS":"Tata Consumer","TATAMETALI.NS":"Tata Metaliks","TTKPRESTIG.NS":"TTK Prestige","UBL.NS":"United Breweries",
        "VENKEYS.NS":"Venky's","VSTIND.NS":"VST Industries","WHIRLPOOL.NS":"Whirlpool India","ZYDUSLIFE.NS":"Zydus Lifesciences",
        "ZYDUSWELL.NS":"Zydus Wellness","ARVINDFASN.NS":"Arvind Fashions","CANTABIL.NS":"Cantabil Retail","CENTURY.NS":"Century Textiles",
        "DOLLAR.NS":"Dollar Industries","GOCOLORS.NS":"Go Colors","INDIAMART.NS":"IndiaMART","KEWAL.NS":"Kewal Kiran",
        "KPR.NS":"KPR Mill","MANYAVAR.NS":"Vedant Fashions","NYKAA.NS":"Nykaa","PGEL.NS":"PG Electroplast"
    },
    "FMCG Consumer 4": {
        "PRAJIND.NS":"Praj Industries","RAYMOND.NS":"Raymond","SAPPHIRE.NS":"Sapphire Foods","SHOPERSTOP.NS":"Shoppers Stop",
        "SPENCERS.NS":"Spencer's Retail","TCNSBRANDS.NS":"TCNS Clothing","TRENT.NS":"Trent","VGUARD.NS":"V-Guard",
        "VIPIND.NS":"VIP Industries","VMART.NS":"V-Mart Retail","WESTLIFE.NS":"Westlife Development","WONDERLA.NS":"Wonderla Holidays",
        "BARBEQUE.NS":"Barbeque Nation","BIKAJI.NS":"Bikaji Foods","BRITANNIA.NS":"Britannia","CCL.NS":"CCL Products",
        "DEVYANI.NS":"Devyani International","HATSUN.NS":"Hatsun Agro","ITC.NS":"ITC","JUBLFOOD.NS":"Jubilant FoodWorks"
    },
    "Industrial 1": {
        "APLAPOLLO.NS":"APL Apollo","ASTRAL.NS":"Astral Poly","CARYSIL.NS":"Carysil","CASTROLIND.NS":"Castrol India",
        "CENTURYPLY.NS":"Century Plyboards","CERA.NS":"Cera Sanitaryware","DEEPAKNTR.NS":"Deepak Nitrite","ELECON.NS":"Elecon Engineering",
        "FILATEX.NS":"Filatex India","FLUOROCHEM.NS":"Gujarat Fluorochemicals","GARFIBRES.NS":"Garware Technical","GREAVESCOT.NS":"Greaves Cotton",
        "GRINDWELL.NS":"Grindwell Norton","GSPL.NS":"Gujarat State Petronet","HIL.NS":"HIL Limited","INOXWIND.NS":"Inox Wind",
        "JINDALSAW.NS":"Jindal Saw","JKCEMENT.NS":"JK Cement","KALPATPOWR.NS":"Kalpataru Power","KANSAINER.NS":"Kansai Nerolac"
    },
    "Industrial 2": {
        "KCP.NS":"KCP Limited","KEC.NS":"KEC International","KEI.NS":"KEI Industries","KIRLOSENG.NS":"Kirloskar Oil",
        "LINDEINDIA.NS":"Linde India","MOIL.NS":"MOIL","NESCO.NS":"NESCO","NLCINDIA.NS":"NLC India",
        "PHILIPCARB.NS":"Phillips Carbon","PRINCEPIPE.NS":"Prince Pipes","PRSMJOHNSN.NS":"Prism Johnson","RAIN.NS":"Rain Industries",
        "RATNAMANI.NS":"Ratnamani Metals","RCF.NS":"Rashtriya Chemicals","RITES.NS":"RITES","RVNL.NS":"Rail Vikas Nigam",
        "SAIL.NS":"SAIL","SHREECEM.NS":"Shree Cement","SJVN.NS":"SJVN","SOBHA.NS":"Sobha"
    },
    "Industrial 3": {
        "SOLARINDS.NS":"Solar Industries","SRF.NS":"SRF","STARCEMENT.NS":"Star Cement","SUMICHEM.NS":"Sumitomo Chemical",
        "SUPRAJIT.NS":"Suprajit Engineering","SUPREMEIND.NS":"Supreme Industries","SWARAJENG.NS":"Swaraj Engines","TATAINVEST.NS":"Tata Investment",
        "TATATECH.NS":"Tata Technologies","TECHNOE.NS":"Techno Electric","TIINDIA.NS":"Tube Investments","TIMETECHNO.NS":"Time Technoplast",
        "TRITURBINE.NS":"Triveni Turbine","UCOBANK.NS":"UCO Bank","UPL.NS":"UPL","VINATIORGA.NS":"Vinati Organics",
        "WELCORP.NS":"Welspun Corp","WELSPUNIND.NS":"Welspun India","WESTLIFE.NS":"Westlife Development","ABB.NS":"ABB India"
    },
    "Industrial 4": {
        "BEML.NS":"BEML","BDL.NS":"Bharat Dynamics","BHARATFORG.NS":"Bharat Forge","BOSCHLTD.NS":"Bosch",
        "CARBORUNIV.NS":"Carborundum Universal","CUMMINSIND.NS":"Cummins India","HAL.NS":"Hindustan Aeronautics","KALYANI.NS":"Kalyani Forge",
        "KIRLOSKAR.NS":"Kirloskar Brothers","SIEMENS.NS":"Siemens","THERMAX.NS":"Thermax","TIMKEN.NS":"Timken India",
        "TRIVENI.NS":"Triveni Turbine","VOLTAS.NS":"Voltas","AARTI.NS":"Aarti Industries","ALKYLAMINE.NS":"Alkyl Amines",
        "ATUL.NS":"Atul Ltd","BASF.NS":"BASF India","FINEORG.NS":"Fine Organic","GNFC.NS":"GNFC"
    },
    "Energy Power 1": {
        "ADANIENSOL.NS":"Adani Energy","ADANIGAS.NS":"Adani Total Gas","ADANIGREEN.NS":"Adani Green","AEGISCHEM.NS":"Aegis Logistics",
        "BPCL.NS":"BPCL","GAIL.NS":"GAIL","GMRINFRA.NS":"GMR Infrastructure","GNFC.NS":"GNFC",
        "GSFC.NS":"GSFC","GUJGASLTD.NS":"Gujarat Gas","HINDPETRO.NS":"Hindustan Petroleum","IOC.NS":"Indian Oil",
        "IGL.NS":"Indraprastha Gas","MGL.NS":"Mahanagar Gas","ONGC.NS":"ONGC","OIL.NS":"Oil India",
        "PETRONET.NS":"Petronet LNG","RELIANCE.NS":"Reliance Industries","ADANIPOWER.NS":"Adani Power","ADANITRANS.NS":"Adani Transmission"
    },
    "Energy Power 2": {
        "CESC.NS":"CESC","JSWENERGY.NS":"JSW Energy","NHPC.NS":"NHPC","NLCINDIA.NS":"NLC India",
        "NTPC.NS":"NTPC","PFC.NS":"Power Finance Corp","POWERGRID.NS":"Power Grid","RECLTD.NS":"REC Limited",
        "SJVN.NS":"SJVN","TATAPOWER.NS":"Tata Power","TORNTPOWER.NS":"Torrent Power","INOXWIND.NS":"Inox Wind",
        "SUZLON.NS":"Suzlon Energy","COALINDIA.NS":"Coal India","HINDALCO.NS":"Hindalco","MOIL.NS":"MOIL",
        "NMDC.NS":"NMDC","SAIL.NS":"SAIL","VEDL.NS":"Vedanta","CHAMBLFERT.NS":"Chambal Fertilizers"
    },
    "Energy Power 3": {
        "COROMANDEL.NS":"Coromandel International","DEEPAKFERT.NS":"Deepak Fertilizers","FACT.NS":"FACT","NFL.NS":"National Fertilizers",
        "RCF.NS":"Rashtriya Chemicals","ADANIPORTS.NS":"Adani Ports","CONCOR.NS":"Container Corporation","IRCTC.NS":"IRCTC",
        "AEGISCHEM.NS":"Aegis Logistics","ALLCARGO.NS":"Allcargo Logistics","BLUEDART.NS":"Blue Dart Express","GATI.NS":"Gati",
        "MAHLOG.NS":"Mahindra Logistics","TCI.NS":"Transport Corporation","TCIEXP.NS":"TCI Express","VRL.NS":"VRL Logistics",
        "BPCL.NS":"Bharat Petroleum","HINDPETRO.NS":"Hindustan Petroleum","IOC.NS":"Indian Oil Corp","MRPL.NS":"MRPL"
    },
    "Retail Ecommerce 1": {
        "AFFLE.NS":"Affle India","CARTRADE.NS":"CarTrade Tech","EASEMYTRIP.NS":"EaseMyTrip","INDIAMART.NS":"IndiaMART",
        "JUSTDIAL.NS":"Just Dial","MATRIMONY.NS":"Matrimony.com","NAZARA.NS":"Nazara Technologies","NYKAA.NS":"Nykaa",
        "PAYTM.NS":"Paytm","POLICYBZR.NS":"PB Fintech","ROUTE.NS":"Route Mobile","ZOMATO.NS":"Zomato",
        "BARBEQUE.NS":"Barbeque Nation","CAMPUS.NS":"Campus Activewear","DEVYANI.NS":"Devyani International","DMART.NS":"Avenue Supermarts",
        "FIVESTAR.NS":"Five Star Business","JUBLFOOD.NS":"Jubilant FoodWorks","KIMS.NS":"KIMS Hospitals","RELAXO.NS":"Relaxo Footwears"
    },
    "Retail Ecommerce 2": {
        "SAPPHIRE.NS":"Sapphire Foods","SHOPERSTOP.NS":"Shoppers Stop","SPENCERS.NS":"Spencer's Retail","TATACOMM.NS":"Tata Communications",
        "TEAMLEASE.NS":"TeamLease Services","TRENT.NS":"Trent","VMART.NS":"V-Mart Retail","WESTLIFE.NS":"Westlife Development",
        "WONDERLA.NS":"Wonderla Holidays","ABFRL.NS":"Aditya Birla Fashion","ARVINDFASN.NS":"Arvind Fashions","BATAINDIA.NS":"Bata India",
        "CANTABIL.NS":"Cantabil Retail","DOLLAR.NS":"Dollar Industries","GOCOLORS.NS":"Go Colors","MANYAVAR.NS":"Vedant Fashions",
        "RAYMOND.NS":"Raymond","TCNSBRANDS.NS":"TCNS Clothing","VIPIND.NS":"VIP Industries","WONDERLA.NS":"Wonderla Holidays"
    },
    "Real Estate 1": {
        "BRIGADE.NS":"Brigade Enterprises","DLF.NS":"DLF","GODREJPROP.NS":"Godrej Properties","IBREALEST.NS":"Indiabulls Real Estate",
        "KOLTEPATIL.NS":"Kolte-Patil","LODHA.NS":"Macrotech Developers","MACROTECH.NS":"Macrotech Developers","MAHLIFE.NS":"Mahindra Lifespace",
        "OBEROIRLTY.NS":"Oberoi Realty","PHOENIXLTD.NS":"Phoenix Mills","PRESTIGE.NS":"Prestige Estates","RAYMOND.NS":"Raymond",
        "SIGNATURE.NS":"Signature Global","SOBHA.NS":"Sobha","AHLUCONT.NS":"Ahluwalia Contracts","ASHOKA.NS":"Ashoka Buildcon",
        "HCC.NS":"Hindustan Construction","IRB.NS":"IRB Infrastructure","IRCON.NS":"IRCON International","KEC.NS":"KEC International"
    },
    "Real Estate 2": {
        "NBCC.NS":"NBCC India","NCCLTD.NS":"NCC Limited","PNCINFRA.NS":"PNC Infratech","RITES.NS":"RITES",
        "RVNL.NS":"Rail Vikas Nigam","ACC.NS":"ACC Cement","AMBUJACEM.NS":"Ambuja Cements","APLAPOLLO.NS":"APL Apollo Tubes",
        "ASTRAL.NS":"Astral Poly","CENTURYPLY.NS":"Century Plyboards","CERA.NS":"Cera Sanitaryware","DALMIACEM.NS":"Dalmia Bharat",
        "GREENPLY.NS":"Greenply Industries","JKCEMENT.NS":"JK Cement","JKLAKSHMI.NS":"JK Lakshmi Cement","KAJARIACER.NS":"Kajaria Ceramics",
        "ORIENTCEM.NS":"Orient Cement","RAMCOCEM.NS":"Ramco Cements","SHREECEM.NS":"Shree Cement","STARCEMENT.NS":"Star Cement"
    },
    "Real Estate 3": {
        "SUPREMEIND.NS":"Supreme Industries","ULTRACEMCO.NS":"UltraTech Cement","FINCABLES.NS":"Finolex Cables","HUDCO.NS":"HUDCO",
        "LINDEINDIA.NS":"Linde India","SALASAR.NS":"Salasar Techno","SUNFLAG.NS":"Sunflag Iron","CENTURYTEX.NS":"Century Textiles",
        "CMSINFO.NS":"CMS Info Systems","DCBBANK.NS":"DCB Bank","ESABINDIA.NS":"ESAB India","GUJGASLTD.NS":"Gujarat Gas",
        "JWL.NS":"Jupiter Wagons","KOLTEPATIL.NS":"Kolte-Patil","MAHLIFE.NS":"Mahindra Lifespace","PHOENIXLTD.NS":"Phoenix Mills",
        "PRESTIGE.NS":"Prestige Estates","BRIGADE.NS":"Brigade Enterprises","SOBHA.NS":"Sobha Limited","RAYMOND.NS":"Raymond Limited"
    },
    "Media Entertainment": {
        "DB.NS":"DB Corp","HATHWAY.NS":"Hathway Cable","INOXLEISUR.NS":"Inox Leisure","JAGRAN.NS":"Jagran Prakashan",
        "NAZARA.NS":"Nazara Technologies","NETWORK18.NS":"Network18 Media","PVR.NS":"PVR Inox","PVRINOX.NS":"PVR Inox",
        "SAREGAMA.NS":"Saregama India","SUNTV.NS":"Sun TV Network","TIPS.NS":"Tips Industries","TV18BRDCST.NS":"TV18 Broadcast",
        "TVTODAY.NS":"TV Today","ZEEL.NS":"Zee Entertainment","HT.NS":"HT Media","NAVNETEDUL.NS":"Navneet Education",
        "TREEHOUSE.NS":"Tree House Education","DELTACORP.NS":"Delta Corp","ONMOBILE.NS":"OnMobile Global","WONDERLA.NS":"Wonderla Holidays"
    },
    "Agriculture Chemicals 1": {
        "AARTIIND.NS":"Aarti Industries","AARTIDRUGS.NS":"Aarti Drugs","ATUL.NS":"Atul Ltd","BASF.NS":"BASF India",
        "BHAGERIA.NS":"Bhageria Industries","COROMANDEL.NS":"Coromandel International","DEEPAKNTR.NS":"Deepak Nitrite","EXCEL.NS":"Excel Crop Care",
        "FINEORG.NS":"Fine Organic","FLUOROCHEM.NS":"Gujarat Fluorochemicals","GNFC.NS":"GNFC","GSFC.NS":"GSFC",
        "HERANBA.NS":"Heranba Industries","INDOFIL.NS":"Indofil Industries","INSECTICIDES.NS":"Insecticides India","NAVINFLUOR.NS":"Navin Fluorine",
        "NOCIL.NS":"NOCIL","PIIND.NS":"PI Industries","RALLIS.NS":"Rallis India","SHARDACROP.NS":"Sharda Cropchem"
    },
    "Agriculture Chemicals 2": {
        "SRF.NS":"SRF","SUMICHEM.NS":"Sumitomo Chemical","TATACHEM.NS":"Tata Chemicals","UPL.NS":"UPL",
        "VINATIORGA.NS":"Vinati Organics","ZUARI.NS":"Zuari Agro Chemicals","CHAMBLFERT.NS":"Chambal Fertilizers","DEEPAKFERT.NS":"Deepak Fertilizers",
        "FACT.NS":"FACT","NFL.NS":"National Fertilizers","RCF.NS":"Rashtriya Chemicals","AVANTIFEED.NS":"Avanti Feeds",
        "BBTC.NS":"Bombay Burmah","CENTURYTEXT.NS":"Century Textiles","HINDOILEXP.NS":"Hindustan Oil","JUBLCHEM.NS":"Jubilant Ingrevia",
        "KRBL.NS":"KRBL","TATACOFFEE.NS":"Tata Coffee","VENKEYS.NS":"Venky's","ALKYLAMINE.NS":"Alkyl Amines"
    },
    "Specialty Emerging 1": {
        "AEGISCHEM.NS":"Aegis Logistics","ALLCARGO.NS":"Allcargo Logistics","BLUEDART.NS":"Blue Dart Express","CONCOR.NS":"Container Corporation",
        "GATI.NS":"Gati","MAHLOG.NS":"Mahindra Logistics","TCI.NS":"Transport Corporation","TCIEXP.NS":"TCI Express",
        "VRL.NS":"VRL Logistics","APTECH.NS":"Aptech","CAREEREDGE.NS":"Career Point","NAVNETEDUL.NS":"Navneet Education",
        "TREEHOUSE.NS":"Tree House Education","ZEE.NS":"Zee Learn","CHALET.NS":"Chalet Hotels","EIH.NS":"EIH",
        "INDHOTEL.NS":"Indian Hotels","LEMONTREE.NS":"Lemon Tree Hotels","MAHINDCIE.NS":"Mahindra Holidays","TAJGVK.NS":"Taj GVK Hotels"
    },
    "Specialty Emerging 2": {
        "COX&KINGS.NS":"Cox & Kings","EASEMYTRIP.NS":"EaseMyTrip","IRCTC.NS":"IRCTC","SPICEJET.NS":"SpiceJet",
        "TBO.NS":"TBO Tek","THOMASCOOK.NS":"Thomas Cook","CMSINFO.NS":"CMS Info Systems","SIS.NS":"SIS Limited",
        "UNOMINDA.NS":"Uno Minda","EMAMIPAP.NS":"Emami Paper","JKPAPER.NS":"JK Paper","SESAGOA.NS":"Sesa Goa",
        "TNIDETF.NS":"TNPL","WESTPAPER.NS":"West Coast Paper","BDL.NS":"Bharat Dynamics","BEL.NS":"Bharat Electronics",
        "GRSE.NS":"Garden Reach Shipbuilders","HAL.NS":"Hindustan Aeronautics","MAZDOCK.NS":"Mazagon Dock","MIDHANI.NS":"Mishra Dhatu Nigam"
    },
    "Textiles Apparels": {
        "AARVEEDEN.NS":"Aarvee Denims","ALOKTEXT.NS":"Alok Textile","ARSS.NS":"ARSS Infrastructure","BANSWRAS.NS":"Banswara Syntex",
        "CENTURYTEX.NS":"Century Textiles","DOLLAR.NS":"Dollar Industries","GOKEX.NS":"Gokaldas Exports","KPR.NS":"KPR Mill",
        "NAHARINDUS.NS":"Nahar Industrial","NITIN.NS":"Nitin Spinners","RAYMOND.NS":"Raymond","RSWM.NS":"RSWM",
        "SPENTEX.NS":"Spentex Industries","SUTLEJTEX.NS":"Sutlej Textiles","TRIDENT.NS":"Trident","VARDHACRLC.NS":"Vardhman Textiles",
        "WELSPUNIND.NS":"Welspun India","ABFRL.NS":"Aditya Birla Fashion","ARVINDFASN.NS":"Arvind Fashions","CANTABIL.NS":"Cantabil Retail"
    },
    "Diversified 1": {
        "ASAHIINDIA.NS":"Asahi India Glass","CERA.NS":"Cera Sanitaryware","HGINFRA.NS":"HG Infra","HLEGLAS.NS":"HLE Glascoat",
        "KAJARIACER.NS":"Kajaria Ceramics","ORIENT.NS":"Orient Cement","PRISM.NS":"Prism Johnson","SOMANY.NS":"Somany Ceramics",
        "APLAPOLLO.NS":"APL Apollo Tubes","APOLLOPIPE.NS":"Apollo Pipes","ASTRAL.NS":"Astral Poly","FINOLEX.NS":"Finolex Industries",
        "NAGREEKEXP.NS":"Nagreeka Exports","PRINCEPIPE.NS":"Prince Pipes","SUPREME.NS":"Supreme Industries","VALIANTORG.NS":"Valiant Organics",
        "FAG.NS":"Schaeffler India","NBC.NS":"National Bearings","NRB.NS":"NRB Bearings","SCHAEFFLER.NS":"Schaeffler India"
    },
    "Diversified 2": {
        "SKFINDIA.NS":"SKF India","TIMKEN.NS":"Timken India","FINCABLES.NS":"Finolex Cables","GALAXYSURF.NS":"Galaxy Surfactants",
        "KEI.NS":"KEI Industries","ORIENTELEC.NS":"Orient Electric","POLYCAB.NS":"Polycab India","VGUARD.NS":"V-Guard Industries",
        "CESC.NS":"CESC","CROMPTON.NS":"Crompton Greaves","HAVELLS.NS":"Havells India","KIRLOSENG.NS":"Kirloskar Oil",
        "KIRLFER.NS":"Kirloskar Ferrous","KSB.NS":"KSB Pumps","ORIENTELEC.NS":"Orient Electric","SHAKTICP.NS":"Shakti Corporation",
        "3MINDIA.NS":"3M India","AARTIDRUGS.NS":"Aarti Drugs","ACCELYA.NS":"Accelya Kale","ACI.NS":"Archean Chemical"
    }
}

INDUSTRY_BENCHMARKS = {
    'Technology': {'pe': 28, 'ev_ebitda': 16},'Financial Services': {'pe': 20, 'ev_ebitda': 14},'Consumer Cyclical': {'pe': 32, 'ev_ebitda': 16},
    'Consumer Defensive': {'pe': 38, 'ev_ebitda': 18},'Healthcare': {'pe': 30, 'ev_ebitda': 16},'Industrials': {'pe': 25, 'ev_ebitda': 14},
    'Energy': {'pe': 18, 'ev_ebitda': 10},'Basic Materials': {'pe': 20, 'ev_ebitda': 12},'Real Estate': {'pe': 28, 'ev_ebitda': 20},'Default': {'pe': 22, 'ev_ebitda': 14}
}

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
        
        benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
        industry_pe = benchmark['pe']
        industry_ev_ebitda = benchmark['ev_ebitda']
        
        historical_pe = trailing_pe * 0.9 if trailing_pe and trailing_pe > 0 else industry_pe
        blended_pe = (industry_pe + historical_pe) / 2
        fair_value_pe = trailing_eps * blended_pe if trailing_eps else None
        upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
        
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
        
        return {
            'price': price, 'trailing_pe': trailing_pe, 'forward_pe': forward_pe,'trailing_eps': trailing_eps, 'industry_pe': industry_pe,
            'fair_value_pe': fair_value_pe, 'upside_pe': upside_pe,'enterprise_value': enterprise_value, 'ebitda': ebitda,
            'market_cap': market_cap, 'current_ev_ebitda': current_ev_ebitda,'industry_ev_ebitda': industry_ev_ebitda,
            'fair_value_ev': fair_value_ev, 'upside_ev': upside_ev
        }
    except:
        return None

def create_gauge_chart(upside_pe, upside_ev):
    fig = make_subplots(rows=1, cols=2,specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],subplot_titles=("PE Multiple", "EV/EBITDA"))
    
    fig.add_trace(go.Indicator(mode="gauge+number",value=upside_pe,number={'suffix': "%", 'font': {'size': 40}},
        gauge={'axis': {'range': [-50, 50]},'bar': {'color': "#667eea"},'steps': [{'range': [-50, 0], 'color': '#ffebee'},{'range': [0, 50], 'color': '#e8f5e9'}],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 0}}), row=1, col=1)
    
    fig.add_trace(go.Indicator(mode="gauge+number",value=upside_ev,number={'suffix': "%", 'font': {'size': 40}},
        gauge={'axis': {'range': [-50, 50]},'bar': {'color': "#f093fb"},'steps': [{'range': [-50, 0], 'color': '#ffebee'},{'range': [0, 50], 'color': '#e8f5e9'}],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': 0}}), row=1, col=2)
    
    fig.update_layout(height=400)
    return fig

def create_bar_chart(vals):
    categories, current, fair, colors_fair = [], [], [], []
    if vals['fair_value_pe']:
        categories.append('PE Multiple')
        current.append(vals['price'])
        fair.append(vals['fair_value_pe'])
        colors_fair.append('#00C853' if vals['fair_value_pe'] > vals['price'] else '#e74c3c')
    if vals['fair_value_ev']:
        categories.append('EV/EBITDA')
        current.append(vals['price'])
        fair.append(vals['fair_value_ev'])
        colors_fair.append('#00C853' if vals['fair_value_ev'] > vals['price'] else '#e74c3c')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Current', x=categories, y=current, marker_color='#3498db',text=[f'Rs {p:.2f}' for p in current], textposition='outside'))
    fig.add_trace(go.Bar(name='Fair Value', x=categories, y=fair, marker_color=colors_fair,text=[f'Rs {p:.2f}' for p in fair], textposition='outside'))
    fig.update_layout(barmode='group', height=500, template='plotly_white')
    return fig

def create_pdf_report(company, ticker, sector, vals):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#667eea'), alignment=TA_CENTER)
    story = []
    story.append(Paragraph("NYZTrade Valuation Report", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>{company}</b>", styles['Heading2']))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    fair_data = [['Metric', 'Value'],['Fair Value', f"Rs {avg_fair:.2f}"],['Current Price', f"Rs {vals['price']:.2f}"],['Upside', f"{avg_up:+.2f}%"]]
    fair_table = Table(fair_data, colWidths=[3*inch, 2*inch])
    fair_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(fair_table)
    story.append(Spacer(1, 20))
    
    metrics_data = [['Metric', 'Value'],['Current Price', f"Rs {vals['price']:.2f}"],['PE Ratio', f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A'],
        ['EPS', f"Rs {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A'],['Market Cap', f"Rs {vals['market_cap']/10000000:.2f} Cr"]]
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("DISCLAIMER: Educational content only, not financial advice.", styles['Normal']))
    doc.build(story)
    buffer.seek(0)
    return buffer

st.markdown('<div class="main-header"><h1>MIDCAP VALUATION</h1><p>800+ Stocks | Professional Analysis</p></div>', unsafe_allow_html=True)

if st.sidebar.button("Logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.header("Stock Selection")

all_stocks = {}
for cat, stocks in MIDCAP_STOCKS.items():
    all_stocks.update(stocks)

st.sidebar.success(f"Total: {len(all_stocks)} stocks")

category = st.sidebar.selectbox("Category", ["All Stocks"] + list(MIDCAP_STOCKS.keys()))
search = st.sidebar.text_input("Search", placeholder="Company or ticker")

if search:
    filtered = {t: n for t, n in all_stocks.items() if search.upper() in t or search.upper() in n.upper()}
elif category == "All Stocks":
    filtered = all_stocks
else:
    filtered = MIDCAP_STOCKS[category]

if filtered:
    options = [f"{n} ({t})" for t, n in filtered.items()]
    selected = st.sidebar.selectbox("Select Stock", options)
    ticker = selected.split("(")[1].strip(")")
else:
    ticker = None
    st.sidebar.warning("No stocks found")

custom = st.sidebar.text_input("Custom Ticker", placeholder="e.g., DIXON.NS")

if st.sidebar.button("ANALYZE", use_container_width=True):
    st.session_state.analyze = custom.upper() if custom else ticker

if 'analyze' in st.session_state:
    t = st.session_state.analyze
    
    with st.spinner(f"Analyzing {t}..."):
        info, error = fetch_stock_data(t)
    
    if error or not info:
        st.error(f"Error: {error if error else 'Failed'}")
        st.stop()
    
    vals = calculate_valuations(info)
    if not vals:
        st.error("Valuation failed")
        st.stop()
    
    company = info.get('longName', t)
    sector = info.get('sector', 'N/A')
    
    st.markdown(f"## {company}")
    st.markdown(f"**Sector:** {sector} | **Ticker:** {t}")
    
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    fair_html = f'<div class="fair-value-box"><h2>FAIR VALUE</h2><h1>Rs {avg_fair:.2f}</h1><p>Current: Rs {vals["price"]:.2f}</p><h3>Upside: {avg_up:+.2f}%</h3></div>'
    st.markdown(fair_html, unsafe_allow_html=True)
    
    pdf = create_pdf_report(company, t, sector, vals)
    st.download_button("Download PDF", data=pdf, file_name=f"NYZTrade_{t}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Price", f"Rs {vals['price']:.2f}")
    with col2:
        st.metric("PE", f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else "N/A")
    with col3:
        st.metric("EPS", f"Rs {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else "N/A")
    with col4:
        st.metric("MCap", f"Rs {vals['market_cap']/10000000:.0f} Cr")
    
    if avg_up > 25:
        rec_class, rec_text = "rec-strong-buy", "STRONG BUY"
    elif avg_up > 15:
        rec_class, rec_text = "rec-buy", "BUY"
    elif avg_up > 0:
        rec_class, rec_text = "rec-buy", "ACCUMULATE"
    elif avg_up > -10:
        rec_class, rec_text = "rec-hold", "HOLD"
    else:
        rec_class, rec_text = "rec-avoid", "AVOID"
    
    rec_html = f'<div class="{rec_class}">{rec_text}<br>Return: {avg_up:+.2f}%</div>'
    st.markdown(rec_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if vals['upside_pe'] and vals['upside_ev']:
        st.subheader("Valuation Analysis")
        fig1 = create_gauge_chart(vals['upside_pe'], vals['upside_ev'])
        st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = create_bar_chart(vals)
    st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Financial Metrics")
    df = pd.DataFrame({
        'Metric': ['Current Price','PE Ratio','Industry PE','EPS','Market Cap','Enterprise Value','EBITDA','EV/EBITDA'],
        'Value': [f"Rs {vals['price']:.2f}",f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A',f"{vals['industry_pe']:.2f}x",
            f"Rs {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A',f"Rs {vals['market_cap']/10000000:.0f} Cr",
            f"Rs {vals['enterprise_value']/10000000:.0f} Cr",f"Rs {vals['ebitda']/10000000:.0f} Cr" if vals['ebitda'] else 'N/A',
            f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else 'N/A']
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("Select a stock and click ANALYZE")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>NYZTrade Platform | Educational Tool</div>", unsafe_allow_html=True)


