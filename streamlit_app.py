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

# PAGE CONFIG
st.set_page_config(
    page_title="NYZTrade Midcap Valuation",
    page_icon="📊",
    layout="wide"
)

# AUTHENTICATION
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
        st.markdown("<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 3rem; border-radius: 20px; text-align: center;'><h1 style='color: white;'>NYZTrade Pro Login</h1></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.button("Login", on_click=password_entered, use_container_width=True)
            st.info("Demo: demo/demo123 | Premium: premium/premium123")
        return False
    
    elif not st.session_state["password_correct"]:
        st.error("Incorrect credentials")
        return False
    
    return True

if not check_password():
    st.stop()

# CUSTOM CSS
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
</style>
""", unsafe_allow_html=True)

# STOCK DATABASE
MIDCAP_STOCKS = {
    "Banking & Finance": {
        "ANGELONE.NS": "Angel One", "CDSL.NS": "CDSL", "HDFCAMC.NS": "HDFC AMC",
        "IIFL.NS": "IIFL Finance", "IRFC.NS": "IRFC", "MOTILALOFS.NS": "Motilal Oswal",
        "RBL.NS": "RBL Bank", "FEDERALBNK.NS": "Federal Bank", "AUBANK.NS": "AU Small Finance",
        "BANDHANBNK.NS": "Bandhan Bank", "IDFCFIRSTB.NS": "IDFC First", "ICICIGI.NS": "ICICI Lombard",
        "SUNDARMFIN.NS": "Sundaram Finance", "CHOLAFIN.NS": "Cholamandalam Investment"
    },
    "IT & Technology": {
        "COFORGE.NS": "Coforge", "HAPPSTMNDS.NS": "Happiest Minds", "KPITTECH.NS": "KPIT Technologies",
        "PERSISTENT.NS": "Persistent Systems", "ZOMATO.NS": "Zomato", "NYKAA.NS": "Nykaa",
        "DIXON.NS": "Dixon Technologies", "VOLTAS.NS": "Voltas", "HAVELLS.NS": "Havells",
        "LTIM.NS": "LTIMindtree", "TECHM.NS": "Tech Mahindra"
    },
    "Pharma & Healthcare": {
        "AJANTPHARM.NS": "Ajanta Pharma", "BIOCON.NS": "Biocon", "ALKEM.NS": "Alkem Labs",
        "APOLLOHOSP.NS": "Apollo Hospitals", "MAXHEALTH.NS": "Max Healthcare", "FORTIS.NS": "Fortis Healthcare",
        "LALPATHLAB.NS": "Dr Lal PathLabs", "METROPOLIS.NS": "Metropolis Healthcare"
    },
    "Auto & Components": {
        "ASHOKLEY.NS": "Ashok Leyland", "ESCORTS.NS": "Escorts Kubota", "MOTHERSON.NS": "Motherson Sumi",
        "APOLLOTYRE.NS": "Apollo Tyres", "EXIDEIND.NS": "Exide Industries", "BHARATFORG.NS": "Bharat Forge"
    },
    "FMCG & Consumer": {
        "JUBLFOOD.NS": "Jubilant FoodWorks", "TRENT.NS": "Trent", "BATAINDIA.NS": "Bata India",
        "ABFRL.NS": "Aditya Birla Fashion", "PAGEIND.NS": "Page Industries", "RELAXO.NS": "Relaxo Footwears"
    },
    "Industrial": {
        "ASTRAL.NS": "Astral Poly", "CERA.NS": "Cera Sanitaryware", "KEI.NS": "KEI Industries",
        "SRF.NS": "SRF", "UPL.NS": "UPL", "HAL.NS": "HAL", "APLAPOLLO.NS": "APL Apollo"
    },
    "Energy & Power": {
        "ADANIGREEN.NS": "Adani Green", "JSWENERGY.NS": "JSW Energy", "NHPC.NS": "NHPC",
        "POWERGRID.NS": "Power Grid", "TATAPOWER.NS": "Tata Power", "ADANIGAS.NS": "Adani Gas"
    },
    "Real Estate": {
        "DLF.NS": "DLF", "GODREJPROP.NS": "Godrej Properties", "OBEROIRLTY.NS": "Oberoi Realty",
        "PRESTIGE.NS": "Prestige Estates", "PHOENIXLTD.NS": "Phoenix Mills", "BRIGADE.NS": "Brigade Enterprises"
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
    'Real Estate': {'pe': 28, 'ev_ebitda': 20},
    'Default': {'pe': 22, 'ev_ebitda': 14}
}

# DATA FUNCTIONS
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
            return None, "Rate limit reached. Wait 3-5 minutes."
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

# CHART FUNCTIONS
def create_gauge_chart(upside_pe, upside_ev):
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
        subplot_titles=("PE Multiple Method", "EV/EBITDA Method")
    )
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=upside_pe,
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [-50, 50]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [-50, -10], 'color': '#ffebee'},
                {'range': [-10, 0], 'color': '#fff3e0'},
                {'range': [0, 15], 'color': '#e8f5e9'},
                {'range': [15, 50], 'color': '#c8e6c9'}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': 0}
        }
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=upside_ev,
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [-50, 50]},
            'bar': {'color': "#f093fb"},
            'steps': [
                {'range': [-50, -10], 'color': '#ffebee'},
                {'range': [-10, 0], 'color': '#fff3e0'},
                {'range': [0, 15], 'color': '#e8f5e9'},
                {'range': [15, 50], 'color': '#c8e6c9'}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': 0}
        }
    ), row=1, col=2)
    
    fig.update_layout(height=400, font={'family': 'Arial', 'size': 14})
    return fig

def create_bar_chart(valuations):
    categories = []
    current = []
    fair = []
    colors_fair = []
    
    if valuations['fair_value_pe']:
        categories.append('PE Multiple')
        current.append(valuations['price'])
        fair.append(valuations['fair_value_pe'])
        colors_fair.append('#00C853' if valuations['fair_value_pe'] > valuations['price'] else '#e74c3c')
    
    if valuations['fair_value_ev']:
        categories.append('EV/EBITDA')
        current.append(valuations['price'])
        fair.append(valuations['fair_value_ev'])
        colors_fair.append('#00C853' if valuations['fair_value_ev'] > valuations['price'] else '#e74c3c')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Current Price',
        x=categories,
        y=current,
        marker_color='#3498db',
        text=[f'Rs {p:.2f}' for p in current],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair,
        marker_color=colors_fair,
        text=[f'Rs {p:.2f}' for p in fair],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Current Price vs Fair Value",
        barmode='group',
        height=500,
        template='plotly_white',
        xaxis={'title': 'Valuation Method'},
        yaxis={'title': 'Price (Rs)'}
    )
    
    return fig

# PDF GENERATION
def create_pdf_report(company_name, ticker, sector, valuations):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        alignment=TA_CENTER
    )
    
    story = []
    
    story.append(Paragraph("NYZTrade Stock Valuation Report", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>{company_name}</b>", styles['Heading2']))
    story.append(Paragraph(f"Ticker: {ticker} | Sector: {sector}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Fair Value Summary
    upside_values = [v for v in [valuations['upside_pe'], valuations['upside_ev']] if v is not None]
    avg_upside = np.mean(upside_values) if upside_values else 0
    fair_values = [v for v in [valuations['fair_value_pe'], valuations['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fair_values) if fair_values else valuations['price']
    
    fair_data = [
        ['Metric', 'Value'],
        ['Fair Value Estimate', f"Rs {avg_fair:.2f}"],
        ['Current Price', f"Rs {valuations['price']:.2f}"],
        ['Upside Potential', f"{avg_upside:+.2f}%"]
    ]
    
    fair_table = Table(fair_data, colWidths=[3*inch, 2*inch])
    fair_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(fair_table)
    story.append(Spacer(1, 30))
    
    # Financial Metrics
    story.append(Paragraph("<b>Key Financial Metrics</b>", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    metrics_data = [
        ['Metric', 'Value'],
        ['Current Price', f"Rs {valuations['price']:.2f}"],
        ['PE Ratio', f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else 'N/A'],
        ['Industry PE', f"{valuations['industry_pe']:.2f}x"],
        ['EPS (TTM)', f"Rs {valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else 'N/A'],
        ['Market Cap', f"Rs {valuations['market_cap']/10000000:.2f} Crores"],
        ['Enterprise Value', f"Rs {valuations['enterprise_value']/10000000:.2f} Crores"],
        ['EBITDA', f"Rs {valuations['ebitda']/10000000:.2f} Crores" if valuations['ebitda'] else 'N/A']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 30))
    
    # Disclaimer
    disclaimer = "DISCLAIMER: This report is for educational purposes only and should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions."
    story.append(Paragraph(disclaimer, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# MAIN APP
st.markdown('<div class="main-header"><h1>MIDCAP VALUATION PLATFORM</h1><p>Professional Analysis with PDF Reports</p></div>', unsafe_allow_html=True)

# Sidebar
if st.sidebar.button("Logout", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.header("Stock Selection")

# Flatten stocks
all_stocks = {}
for cat, stocks in MIDCAP_STOCKS.items():
    all_stocks.update(stocks)

st.sidebar.success(f"Total: {len(all_stocks)} stocks")

# Category and search
category = st.sidebar.selectbox("Category", ["All Stocks"] + list(MIDCAP_STOCKS.keys()))
search = st.sidebar.text_input("Search", placeholder="Company or ticker...")

# Filter
if search:
    filtered = {t: n for t, n in all_stocks.items() if search.upper() in t or search.upper() in n.upper()}
elif category == "All Stocks":
    filtered = all_stocks
else:
    filtered = MIDCAP_STOCKS[category]

# Stock selection
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

# Analysis
if 'analyze' in st.session_state:
    t = st.session_state.analyze
    
    with st.spinner(f"Analyzing {t}..."):
        info, error = fetch_stock_data(t)
    
    if error or not info:
        st.error(f"Error: {error if error else 'Failed to fetch data'}")
        st.stop()
    
    vals = calculate_valuations(info)
    if not vals:
        st.error("Valuation calculation failed")
        st.stop()
    
    company = info.get('longName', t)
    sector = info.get('sector', 'N/A')
    
    st.markdown(f"## {company}")
    st.markdown(f"**Sector:** {sector} | **Ticker:** {t}")
    
    # Fair Value Box
    ups = [v for v in [vals['upside_pe'], vals['upside_ev']] if v is not None]
    avg_up = np.mean(ups) if ups else 0
    fairs = [v for v in [vals['fair_value_pe'], vals['fair_value_ev']] if v is not None]
    avg_fair = np.mean(fairs) if fairs else vals['price']
    
    fair_html = f'<div class="fair-value-box"><h2>FAIR VALUE ESTIMATE</h2><h1>Rs {avg_fair:.2f}</h1><p>Current: Rs {vals["price"]:.2f}</p><h3>Upside: {avg_up:+.2f}%</h3></div>'
    st.markdown(fair_html, unsafe_allow_html=True)
    
    # PDF Download
    pdf = create_pdf_report(company, t, sector, vals)
    st.download_button(
        label="Download PDF Report",
        data=pdf,
        file_name=f"NYZTrade_{t}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"Rs {vals['price']:.2f}")
    with col2:
        st.metric("PE Ratio", f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else "N/A")
    with col3:
        st.metric("EPS", f"Rs {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else "N/A")
    with col4:
        st.metric("Market Cap", f"Rs {vals['market_cap']/10000000:.0f} Cr")
    
    # Recommendation
    if avg_up > 25:
        rec_class = "rec-strong-buy"
        rec_text = "STRONG BUY"
    elif avg_up > 15:
        rec_class = "rec-buy"
        rec_text = "BUY"
    elif avg_up > 0:
        rec_class = "rec-buy"
        rec_text = "ACCUMULATE"
    elif avg_up > -10:
        rec_class = "rec-hold"
        rec_text = "HOLD"
    else:
        rec_class = "rec-avoid"
        rec_text = "AVOID"
    
    rec_html = f'<div class="{rec_class}">{rec_text}<br>Potential Return: {avg_up:+.2f}%</div>'
    st.markdown(rec_html, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    if vals['upside_pe'] and vals['upside_ev']:
        st.subheader("Valuation Analysis")
        fig1 = create_gauge_chart(vals['upside_pe'], vals['upside_ev'])
        st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = create_bar_chart(vals)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Metrics Table
    st.subheader("Financial Metrics")
    df = pd.DataFrame({
        'Metric': [
            'Current Price',
            'PE Ratio',
            'Industry PE',
            'Forward PE',
            'EPS (TTM)',
            'Market Cap',
            'Enterprise Value',
            'EBITDA',
            'EV/EBITDA',
            'Industry EV/EBITDA'
        ],
        'Value': [
            f"Rs {vals['price']:.2f}",
            f"{vals['trailing_pe']:.2f}x" if vals['trailing_pe'] else 'N/A',
            f"{vals['industry_pe']:.2f}x",
            f"{vals['forward_pe']:.2f}x" if vals['forward_pe'] else 'N/A',
            f"Rs {vals['trailing_eps']:.2f}" if vals['trailing_eps'] else 'N/A',
            f"Rs {vals['market_cap']/10000000:.0f} Crores",
            f"Rs {vals['enterprise_value']/10000000:.0f} Crores",
            f"Rs {vals['ebitda']/10000000:.0f} Crores" if vals['ebitda'] else 'N/A',
            f"{vals['current_ev_ebitda']:.2f}x" if vals['current_ev_ebitda'] else 'N/A',
            f"{vals['industry_ev_ebitda']:.2f}x"
        ]
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.info("Select a stock from the sidebar and click ANALYZE to begin")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("**Features:** Real-time analysis, Professional charts, PDF reports, Fair value estimation")
    with col2:
        st.warning("**Tip:** Data is cached for 2 hours. Re-analyzing same stock within 2 hours is instant!")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>NYZTrade Professional Platform | Educational Tool | Not Financial Advice</div>", unsafe_allow_html=True)
```

---

