# ============================================================================
# NYZTrade Professional Historical GEX/DEX Backtesting Dashboard
# Real-time Historical Options Greeks Analysis with Advanced Backtesting
# ============================================================================

import streamlit as st
import sys
import importlib.util
pip install streamlit pandas numpy plotly scipy requests sqlalchemy python-dateutil pytz

# ============================================================================
# CHECK DEPENDENCIES
# ============================================================================

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'plotly': 'plotly',
        'scipy': 'scipy',
        'requests': 'requests',
        'sqlalchemy': 'sqlalchemy'
    }
    
    missing_packages = []
    for package_name, import_name in required_packages.items():
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            missing_packages.append(package_name)
    
    if missing_packages:
        st.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        st.code(f"pip install {' '.join(missing_packages)}", language="bash")
        st.info("💡 Or install all at once:")
        st.code("pip install streamlit pandas numpy plotly scipy requests sqlalchemy python-dateutil pytz", language="bash")
        st.stop()

# Run dependency check
check_dependencies()

# Now import everything else
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Optional

# Import custom modules with error handling
try:
    from config import (
        DhanConfig, SYMBOL_CONFIG, DHAN_SECURITY_IDS, PROFESSIONAL_CSS,
        BACKTEST_CONFIG, HISTORICAL_CONFIG
    )
    from data_fetcher import HistoricalDataFetcher
    from backtest_engine import BacktestEngine
    from database import HistoricalDatabase
    from visualization import ChartGenerator
    from utils import (
        split_date_range, format_currency, format_percentage,
        generate_trade_summary, calculate_risk_metrics,
        calculate_strategy_performance, create_backtest_report_text,
        validate_date_range
    )
except ImportError as e:
    st.error(f"❌ Error importing custom modules: {str(e)}")
    st.info("💡 Make sure all files are in the same directory")
    st.code("""
Required files:
- config.py
- data_fetcher.py
- backtest_engine.py
- database.py
- visualization.py
- utils.py
- greeks_calculator.py
    """)
    st.stop()

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="NYZTrade Historical GEX/DEX Backtesting",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply professional CSS
st.markdown(PROFESSIONAL_CSS, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None

if 'historical_data' not in st.session_state:
    st.session_state.historical_data = None

if 'backtest_running' not in st.session_state:
    st.session_state.backtest_running = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=3600)
def fetch_historical_data_cached(symbol: str, start_date: str, end_date: str, 
                                strike_range: list, interval: str):
    """Cached function to fetch historical data"""
    try:
        fetcher = HistoricalDataFetcher()
        return fetcher.fetch_multiple_strikes_historical(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strike_range=strike_range,
            interval=interval
        )
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def run_backtest_analysis(df: pd.DataFrame, symbol: str, config: dict) -> dict:
    """Run backtest with given configuration"""
    try:
        # Aggregate data for backtesting
        fetcher = HistoricalDataFetcher()
        agg_df = fetcher.aggregate_gex_dex_by_timestamp(df)
        
        # Initialize backtest engine
        engine = BacktestEngine(
            initial_capital=config['initial_capital'],
            max_position_size=config['max_position_size'],
            commission_per_lot=config['commission_per_lot'],
            slippage=config['slippage']
        )
        
        # Run backtest
        results = engine.run_backtest(agg_df, symbol)
        
        return results
    except Exception as e:
        st.error(f"Error running backtest: {str(e)}")
        raise

# ============================================================================
# MAIN HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="main-title">📈 NYZTrade Historical GEX/DEX Backtesting</h1>
            <p class="sub-title">Professional Options Greeks Analysis | Historical Data | Advanced Backtesting Engine</p>
        </div>
        <div class="backtest-badge complete">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">READY TO BACKTEST</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Backtest Configuration")
    
    # Symbol selection
    symbol = st.selectbox(
        "📈 Select Index",
        options=list(DHAN_SECURITY_IDS.keys()),
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📅 Date Range")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=90),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    st.markdown("---")
    st.markdown("### 📊 Data Configuration")
    
    # Time interval
    interval_map = {
        "1 Minute": "1",
        "5 Minutes": "5",
        "15 Minutes": "15",
        "1 Hour": "60"
    }
    
    interval_selected = st.selectbox(
        "⏱️ Time Interval",
        options=list(interval_map.keys()),
        index=2
    )
    interval = interval_map[interval_selected]
    
    # Expiry type
    expiry_flag = st.selectbox(
        "📅 Expiry Type",
        options=["MONTH", "WEEK"],
        index=0
    )
    
    # Strike range
    strike_range_size = st.slider(
        "📏 Strike Range (±)",
        min_value=1,
        max_value=5,
        value=3
    )
    
    strike_range = ['ATM']
    for i in range(1, strike_range_size + 1):
        strike_range.extend([f'ATM+{i}', f'ATM-{i}'])
    
    st.markdown("---")
    st.markdown("### 💰 Capital Configuration")
    
    initial_capital = st.number_input(
        "Initial Capital (₹)",
        min_value=10000,
        max_value=10000000,
        value=BACKTEST_CONFIG['initial_capital'],
        step=10000
    )
    
    max_position_size = st.slider(
        "Max Position Size (%)",
        min_value=1,
        max_value=10,
        value=int(BACKTEST_CONFIG['max_position_size'] * 100)
    ) / 100
    
    commission_per_lot = st.number_input(
        "Commission per Lot (₹)",
        min_value=0,
        max_value=100,
        value=BACKTEST_CONFIG['commission_per_lot']
    )
    
    st.markdown("---")
    st.markdown("### 🔑 API Status")
    
    config = DhanConfig()
    try:
        expiry_time = datetime.strptime(config.expiry_time, "%Y-%m-%dT%H:%M:%S")
        remaining = expiry_time - datetime.now()
        if remaining.total_seconds() > 0:
            st.success(f"✅ Token Valid: {remaining.days}d {remaining.seconds//3600}h")
        else:
            st.error("❌ Token Expired - Please update")
    except:
        st.warning("⚠️ Token status unknown")

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# Create tabs
tabs = st.tabs([
    "🔄 Fetch & Backtest",
    "📊 Results",
    "📈 Charts",
    "💼 Trades",
    "📋 Raw Data",
    "📚 History"
])

# ============================================================================
# TAB 1: FETCH & BACKTEST
# ============================================================================

with tabs[0]:
    st.markdown("### 🔄 Historical Data & Backtesting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Fetch Historical Data", use_container_width=True, type="primary"):
            # Validate date range
            if not validate_date_range(start_date_str, end_date_str):
                st.error("❌ Invalid date range!")
            else:
                with st.spinner(f"🔄 Fetching historical data for {symbol}..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Fetch data
                        status_text.text(f"Fetching {symbol} data from {start_date_str} to {end_date_str}...")
                        progress_bar.progress(30)
                        
                        df = fetch_historical_data_cached(
                            symbol=symbol,
                            start_date=start_date_str,
                            end_date=end_date_str,
                            strike_range=strike_range,
                            interval=interval
                        )
                        
                        progress_bar.progress(70)
                        
                        if df is not None and not df.empty:
                            st.session_state.historical_data = df
                            progress_bar.progress(100)
                            status_text.empty()
                            st.success(f"✅ Successfully fetched {len(df)} data points!")
                            
                            # Show preview
                            st.markdown("#### 📊 Data Preview")
                            st.dataframe(df.head(20), use_container_width=True)
                            
                            # Save to database
                            try:
                                db = HistoricalDatabase()
                                db.save_historical_data(df, symbol)
                            except Exception as e:
                                st.warning(f"Could not save to database: {str(e)}")
                            
                        else:
                            progress_bar.progress(100)
                            st.error("❌ No data found for the selected period!")
                    
                    except Exception as e:
                        st.error(f"❌ Error fetching data: {str(e)}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
    
    with col2:
        if st.button("🚀 Run Backtest", use_container_width=True, type="primary",
                    disabled=st.session_state.historical_data is None):
            
            if st.session_state.historical_data is None:
                st.warning("⚠️ Please fetch historical data first!")
            else:
                with st.spinner("🔄 Running backtest..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        status_text.text("Initializing backtest engine...")
                        progress_bar.progress(10)
                        
                        # Prepare config
                        backtest_config = {
                            'initial_capital': initial_capital,
                            'max_position_size': max_position_size,
                            'commission_per_lot': commission_per_lot,
                            'slippage': BACKTEST_CONFIG['slippage']
                        }
                        
                        status_text.text("Running strategy simulations...")
                        progress_bar.progress(40)
                        
                        # Run backtest
                        results = run_backtest_analysis(
                            st.session_state.historical_data,
                            symbol,
                            backtest_config
                        )
                        
                        status_text.text("Calculating metrics...")
                        progress_bar.progress(80)
                        
                        # Save results
                        st.session_state.backtest_results = results
                        
                        # Save to database
                        try:
                            db = HistoricalDatabase()
                            backtest_id = db.save_backtest_result(results)
                            
                            if backtest_id:
                                # Save trades
                                for trade in results['trades']:
                                    db.save_trade(backtest_id, trade)
                                
                                # Save daily metrics
                                for metric in results['daily_metrics']:
                                    db.save_daily_metrics(backtest_id, metric)
                        except Exception as e:
                            st.warning(f"Could not save to database: {str(e)}")
                        
                        progress_bar.progress(100)
                        status_text.empty()
                        
                        st.success("✅ Backtest completed successfully!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error running backtest: {str(e)}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
    
    with col3:
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.historical_data = None
            st.session_state.backtest_results = None
            st.rerun()
    
    st.markdown("---")
    
    # Show current status
    if st.session_state.historical_data is not None:
        df = st.session_state.historical_data
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""<div class="metric-card neutral">
                <div class="metric-label">Data Points</div>
                <div class="metric-value">{len(df):,}</div>
            </div>""", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""<div class="metric-card neutral">
                <div class="metric-label">Date Range</div>
                <div class="metric-value" style="font-size: 1.2rem;">{df['date'].min()} to {df['date'].max()}</div>
            </div>""", unsafe_allow_html=True)
        
        with col3:
            unique_strikes = df['strike'].nunique()
            st.markdown(f"""<div class="metric-card neutral">
                <div class="metric-label">Strikes</div>
                <div class="metric-value">{unique_strikes}</div>
            </div>""", unsafe_allow_html=True)
        
        with col4:
            total_volume = df['volume'].sum()
            st.markdown(f"""<div class="metric-card neutral">
                <div class="metric-label">Total Volume</div>
                <div class="metric-value">{total_volume:,}</div>
            </div>""", unsafe_allow_html=True)

# ============================================================================
# TAB 2: RESULTS
# ============================================================================

with tabs[1]:
    if st.session_state.backtest_results is None:
        st.info("📊 Run a backtest to see results here")
    else:
        results = st.session_state.backtest_results
        
        st.markdown("### 📊 Backtest Performance Summary")
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            return_class = "positive" if results['total_return'] > 0 else "negative"
            st.markdown(f"""<div class="metric-card {return_class}">
                <div class="metric-label">Total Return</div>
                <div class="metric-value {return_class}">{format_currency(results['total_return'])}</div>
                <div class="metric-delta">{format_percentage(results['total_return_pct'])}</div>
            </div>""", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""<div class="metric-card neutral">
                <div class="metric-label">Total Trades</div>
                <div class="metric-value">{results['total_trades']}</div>
                <div class="metric-delta">Win Rate: {format_percentage(results['win_rate'])}</div>
            </div>""", unsafe_allow_html=True)
        
        with col3:
            win_class = "positive" if results['win_rate'] > 50 else "negative"
            st.markdown(f"""<div class="metric-card {win_class}">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value {win_class}">{format_percentage(results['win_rate'])}</div>
                <div class="metric-delta">{results['winning_trades']}W / {results['losing_trades']}L</div>
            </div>""", unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""<div class="metric-card negative">
                <div class="metric-label">Max Drawdown</div>
                <div class="metric-value negative">{format_percentage(results['max_drawdown'])}</div>
            </div>""", unsafe_allow_html=True)
        
        with col5:
            sharpe = results.get('sharpe_ratio', 0)
            sharpe_class = "positive" if sharpe > 1 else "neutral"
            st.markdown(f"""<div class="metric-card {sharpe_class}">
                <div class="metric-label">Sharpe Ratio</div>
                <div class="metric-value {sharpe_class}">{sharpe:.2f}</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Performance gauges
        try:
            st.markdown("### 🎯 Performance Metrics")
            chart_gen = ChartGenerator()
            st.plotly_chart(
                chart_gen.create_performance_metrics_gauge(results),
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"Could not create performance gauges: {str(e)}")
        
        st.markdown("---")
        
        # Trade summary
        st.markdown("### 💼 Trade Summary")
        
        if results['trades']:
            trade_summary = generate_trade_summary(results['trades'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📈 Profitability")
                st.markdown(f"""
                - **Average Win:** {format_currency(trade_summary['avg_win'])}
                - **Average Loss:** {format_currency(trade_summary['avg_loss'])}
                - **Largest Win:** {format_currency(trade_summary['largest_win'])}
                - **Largest Loss:** {format_currency(trade_summary['largest_loss'])}
                - **Profit Factor:** {trade_summary['profit_factor']:.2f}
                """)
            
            with col2:
                st.markdown("#### 🎯 Win Streaks")
                st.markdown(f"""
                - **Max Consecutive Wins:** {trade_summary['max_consecutive_wins']}
                - **Max Consecutive Losses:** {trade_summary['max_consecutive_losses']}
                - **Average Holding:** {trade_summary['avg_holding_period']:.1f} days
                """)
            
            with col3:
                st.markdown("#### 📊 Strategy Performance")
                strategy_perf = calculate_strategy_performance(results['trades'])
                st.dataframe(strategy_perf, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Download options
        st.markdown("### 📥 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export trades to CSV
            if results['trades']:
                trades_df = pd.DataFrame(results['trades'])
                csv = trades_df.to_csv(index=False)
                st.download_button(
                    "📥 Download Trades (CSV)",
                    data=csv,
                    file_name=f"backtest_trades_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            # Export report as text
            report_text = create_backtest_report_text(results)
            st.download_button(
                "📄 Download Report (TXT)",
                data=report_text,
                file_name=f"backtest_report_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

# ============================================================================
# TAB 3: CHARTS
# ============================================================================

with tabs[2]:
    if st.session_state.backtest_results is None:
        st.info("📈 Run a backtest to see charts here")
    else:
        results = st.session_state.backtest_results
        
        try:
            chart_gen = ChartGenerator()
            
            st.markdown("### 📈 Performance Charts")
            
            # Equity curve
            st.plotly_chart(
                chart_gen.create_equity_curve(results['daily_metrics']),
                use_container_width=True
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Drawdown chart
                st.plotly_chart(
                    chart_gen.create_drawdown_chart(results['daily_metrics']),
                    use_container_width=True
                )
            
            with col2:
                # Cumulative P&L by strategy
                if results['trades']:
                    st.plotly_chart(
                        chart_gen.create_cumulative_pnl_by_strategy(results['trades']),
                        use_container_width=True
                    )
            
            # GEX/DEX time series
            st.plotly_chart(
                chart_gen.create_gex_dex_time_series(results['daily_metrics']),
                use_container_width=True
            )
            
            # Trade analysis
            if results['trades']:
                st.plotly_chart(
                    chart_gen.create_trade_analysis(results['trades']),
                    use_container_width=True
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Monthly returns heatmap
                st.plotly_chart(
                    chart_gen.create_monthly_returns_heatmap(results['daily_metrics']),
                    use_container_width=True
                )
            
            with col2:
                # PCR vs Returns
                st.plotly_chart(
                    chart_gen.create_pcr_vs_returns(results['daily_metrics']),
                    use_container_width=True
                )
        
        except Exception as e:
            st.error(f"Error creating charts: {str(e)}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())

# ============================================================================
# TAB 4: TRADES
# ============================================================================

with tabs[3]:
    if st.session_state.backtest_results is None:
        st.info("💼 Run a backtest to see trades here")
    else:
        results = st.session_state.backtest_results
        
        if results['trades']:
            st.markdown("### 💼 Trade Log")
            
            trades_df = pd.DataFrame(results['trades'])
            
            # Display filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_strategy = st.multiselect(
                    "Filter by Strategy",
                    options=trades_df['strategy'].unique(),
                    default=trades_df['strategy'].unique()
                )
            
            with col2:
                filter_direction = st.multiselect(
                    "Filter by Direction",
                    options=trades_df['direction'].unique(),
                    default=trades_df['direction'].unique()
                )
            
            with col3:
                filter_status = st.multiselect(
                    "Filter by Status",
                    options=trades_df['status'].unique(),
                    default=trades_df['status'].unique()
                )
            
            # Apply filters
            filtered_df = trades_df[
                (trades_df['strategy'].isin(filter_strategy)) &
                (trades_df['direction'].isin(filter_direction)) &
                (trades_df['status'].isin(filter_status))
            ]
            
            # Display trades
            st.dataframe(
                filtered_df[[
                    'trade_number', 'entry_date', 'exit_date', 'strategy',
                    'direction', 'entry_price', 'exit_price', 'quantity',
                    'pnl', 'pnl_pct', 'entry_reason', 'exit_reason'
                ]],
                use_container_width=True,
                hide_index=True,
                height=600
            )
        else:
            st.info("No trades executed in this backtest")

# ============================================================================
# TAB 5: RAW DATA
# ============================================================================

with tabs[4]:
    if st.session_state.historical_data is None:
        st.info("📋 Fetch historical data to view it here")
    else:
        df = st.session_state.historical_data
        
        st.markdown("### 📋 Raw Historical Data")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_strikes = st.multiselect(
                "Filter Strikes",
                options=sorted(df['strike'].unique()),
                default=[]
            )
        
        with col2:
            filter_option_type = st.multiselect(
                "Option Type",
                options=df['option_type'].unique(),
                default=df['option_type'].unique()
            )
        
        with col3:
            show_columns = st.multiselect(
                "Show Columns",
                options=df.columns.tolist(),
                default=['date', 'time', 'strike', 'option_type', 'spot_price', 
                        'close', 'volume', 'oi', 'iv', 'gex', 'dex']
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        if filter_strikes:
            filtered_df = filtered_df[filtered_df['strike'].isin(filter_strikes)]
        
        if filter_option_type:
            filtered_df = filtered_df[filtered_df['option_type'].isin(filter_option_type)]
        
        if show_columns:
            filtered_df = filtered_df[show_columns]
        
        st.dataframe(filtered_df, use_container_width=True, height=600)
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"historical_data_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# ============================================================================
# TAB 6: HISTORY
# ============================================================================

with tabs[5]:
    st.markdown("### 📚 Backtest History")
    
    try:
        db = HistoricalDatabase()
        history_df = db.get_backtest_results(limit=20)
        
        if history_df is not None and not history_df.empty:
            # Display history
            st.dataframe(
                history_df[[
                    'id', 'backtest_name', 'symbol', 'start_date', 'end_date',
                    'total_return_pct', 'win_rate', 'max_drawdown', 'sharpe_ratio',
                    'total_trades', 'created_at'
                ]],
                use_container_width=True,
                hide_index=True
            )
            
            # Load previous backtest
            selected_id = st.selectbox(
                "Select a backtest to view details",
                options=history_df['id'].tolist(),
                format_func=lambda x: history_df[history_df['id'] == x]['backtest_name'].iloc[0]
            )
            
            if st.button("📂 Load Selected Backtest"):
                # Load trades and metrics
                trades_df = db.get_trades_for_backtest(selected_id)
                daily_df = db.get_daily_metrics_for_backtest(selected_id)
                
                if trades_df is not None:
                    st.success(f"✅ Loaded backtest with {len(trades_df)} trades")
                    
                    # Reconstruct results object
                    backtest_row = history_df[history_df['id'] == selected_id].iloc[0]
                    
                    loaded_results = {
                        'backtest_name': backtest_row['backtest_name'],
                        'symbol': backtest_row['symbol'],
                        'start_date': backtest_row['start_date'],
                        'end_date': backtest_row['end_date'],
                        'strategy': backtest_row['strategy'],
                        'initial_capital': backtest_row['initial_capital'],
                        'final_capital': backtest_row['final_capital'],
                        'total_return': backtest_row['total_return'],
                        'total_return_pct': backtest_row['total_return_pct'],
                        'total_trades': backtest_row['total_trades'],
                        'winning_trades': backtest_row['winning_trades'],
                        'losing_trades': backtest_row['losing_trades'],
                        'win_rate': backtest_row['win_rate'],
                        'max_drawdown': backtest_row['max_drawdown'],
                        'sharpe_ratio': backtest_row['sharpe_ratio'],
                        'trades': trades_df.to_dict('records') if trades_df is not None else [],
                        'daily_metrics': daily_df.to_dict('records') if daily_df is not None else []
                    }
                    
                    st.session_state.backtest_results = loaded_results
                    st.rerun()
        else:
            st.info("No backtest history found. Run your first backtest!")
    
    except Exception as e:
        st.warning(f"Could not load history: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""<div style="text-align: center; padding: 20px; color: #64748b;">
    <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
    NYZTrade Historical GEX/DEX Backtesting Dashboard | Data: Dhan API Historical Rolling Options<br>
    Advanced Backtesting Engine | Multi-Strategy Support | Professional Analytics</p>
    <p style="font-size: 0.75rem;">⚠️ Educational purposes only. Past performance does not guarantee future results.</p>
</div>""", unsafe_allow_html=True)
