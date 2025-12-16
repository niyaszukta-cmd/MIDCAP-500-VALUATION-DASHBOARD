# ============================================================================
# NYZTrade Historical GEX/DEX Dashboard - Configuration
# ============================================================================

from dataclasses import dataclass
from typing import Dict

# ============================================================================
# DHAN API CONFIGURATION
# ============================================================================

@dataclass
class DhanConfig:
    """Dhan API Configuration"""
    client_id: str = "1100480354"
    access_token: str = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzY1OTYzMzk2LCJhcHBfaWQiOiJjOTNkM2UwOSIsImlhdCI6MTc2NTg3Njk5NiwidG9rZW5Db25zdW1lclR5cGUiOiJBUFAiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDQ4MDM1NCJ9.K93qVFYO2XrMJ-Jn4rY2autNZ444tc-AzYtaxVUsjRfsjW7NhfQom58vzuSMVI6nRMMB_sa7fCtWE5JIvk75yw"
    expiry_time: str = "2025-12-17T14:53:17"
    base_url: str = "https://api.dhan.co/v2"

# ============================================================================
# SYMBOL CONFIGURATION
# ============================================================================

DHAN_SECURITY_IDS = {
    "NIFTY": 13,
    "BANKNIFTY": 25,
    "FINNIFTY": 27,
    "MIDCPNIFTY": 442,
    "SENSEX": 51
}

EXCHANGE_SEGMENTS = {
    "NIFTY": "NSE_FNO",
    "BANKNIFTY": "NSE_FNO",
    "FINNIFTY": "NSE_FNO",
    "MIDCPNIFTY": "NSE_FNO",
    "SENSEX": "BSE_FNO"
}

SYMBOL_CONFIG = {
    "NIFTY": {
        "contract_size": 25,
        "strike_interval": 50,
        "lot_size": 25,
        "instrument": "OPTIDX"
    },
    "BANKNIFTY": {
        "contract_size": 15,
        "strike_interval": 100,
        "lot_size": 15,
        "instrument": "OPTIDX"
    },
    "FINNIFTY": {
        "contract_size": 40,
        "strike_interval": 50,
        "lot_size": 40,
        "instrument": "OPTIDX"
    },
    "MIDCPNIFTY": {
        "contract_size": 75,
        "strike_interval": 25,
        "lot_size": 75,
        "instrument": "OPTIDX"
    },
}

# ============================================================================
# BACKTESTING CONFIGURATION
# ============================================================================

BACKTEST_CONFIG = {
    "initial_capital": 100000,  # ₹1,00,000
    "max_position_size": 0.02,  # 2% of capital per trade
    "max_daily_loss": 0.05,     # 5% max daily loss
    "commission_per_lot": 20,   # ₹20 per lot
    "slippage": 0.5,           # ₹0.50 slippage per option
    "risk_free_rate": 0.07      # 7% risk-free rate
}

# ============================================================================
# TRADING STRATEGIES CONFIGURATION
# ============================================================================

STRATEGY_THRESHOLDS = {
    "strong_suppression": {
        "gex_threshold": 50,
        "strategy": "Iron Condor",
        "direction": "neutral",
        "volatility_regime": "low"
    },
    "suppression": {
        "gex_threshold": 0,
        "strategy": "Short Straddle",
        "direction": "neutral",
        "volatility_regime": "low"
    },
    "high_amplification": {
        "gex_threshold": -50,
        "strategy": "Long Straddle",
        "direction": "volatile",
        "volatility_regime": "high"
    },
    "amplification": {
        "gex_threshold": 0,
        "strategy": "Directional",
        "direction": "volatile",
        "volatility_regime": "medium"
    },
    "bullish_dex": {
        "dex_threshold": 20,
        "strategy": "Bull Call Spread",
        "direction": "bullish"
    },
    "bearish_dex": {
        "dex_threshold": -20,
        "strategy": "Bear Put Spread",
        "direction": "bearish"
    }
}

# ============================================================================
# HISTORICAL DATA CONFIGURATION
# ============================================================================

HISTORICAL_CONFIG = {
    "max_days_per_request": 30,
    "intervals": {
        "1MIN": "1",
        "5MIN": "5",
        "15MIN": "15",
        "25MIN": "25",
        "1HOUR": "60"
    },
    "strike_range": {
        "index_near_expiry": list(range(-10, 11)),  # ATM-10 to ATM+10
        "index_regular": list(range(-3, 4)),         # ATM-3 to ATM+3
        "stock": list(range(-3, 4))                  # ATM-3 to ATM+3
    },
    "expiry_types": {
        "WEEKLY": "WEEK",
        "MONTHLY": "MONTH"
    },
    "required_data_fields": [
        "open", "high", "low", "close", "volume", "iv", "oi", "strike", "spot"
    ]
}

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE_CONFIG = {
    "db_path": "historical_gex_data.db",
    "tables": {
        "historical_data": "historical_options_data",
        "backtest_results": "backtest_results",
        "trades": "trades_log",
        "daily_metrics": "daily_metrics"
    }
}

# ============================================================================
# VISUALIZATION CONFIGURATION
# ============================================================================

CHART_COLORS = {
    "positive": "#10b981",
    "negative": "#ef4444",
    "neutral": "#f59e0b",
    "blue": "#3b82f6",
    "purple": "#8b5cf6",
    "cyan": "#06b6d4",
    "pink": "#ec4899",
    "background": "#0a0e17",
    "card": "#1a2332",
    "border": "#2d3748"
}

# ============================================================================
# CSS STYLING (Same as original dashboard)
# ============================================================================

PROFESSIONAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a2332;
        --bg-card-hover: #232f42;
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-yellow: #f59e0b;
        --accent-cyan: #06b6d4;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border-color: #2d3748;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0f172a 50%, var(--bg-primary) 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    
    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .sub-title {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 8px;
    }
    
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        background: var(--bg-card-hover);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card.positive { border-left: 4px solid var(--accent-green); }
    .metric-card.negative { border-left: 4px solid var(--accent-red); }
    .metric-card.neutral { border-left: 4px solid var(--accent-yellow); }
    
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-muted);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    .metric-value.positive { color: var(--accent-green); }
    .metric-value.negative { color: var(--accent-red); }
    .metric-value.neutral { color: var(--accent-yellow); }
    
    .metric-delta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        margin-top: 8px;
        color: var(--text-secondary);
    }
    
    .backtest-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 20px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .backtest-badge.running {
        background: rgba(245, 158, 11, 0.15);
        color: var(--accent-yellow);
        border: 1px solid rgba(245, 158, 11, 0.3);
        animation: pulse-backtest 2s infinite;
    }
    
    .backtest-badge.complete {
        background: rgba(16, 185, 129, 0.15);
        color: var(--accent-green);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    @keyframes pulse-backtest {
        0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
        50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
    }
    
    .strategy-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }
    
    .strategy-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--accent-cyan);
        margin-bottom: 12px;
    }
    
    .strategy-detail {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    .trade-log-entry {
        background: var(--bg-card);
        border-left: 4px solid var(--accent-blue);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }
    
    .trade-log-entry.profit {
        border-left-color: var(--accent-green);
    }
    
    .trade-log-entry.loss {
        border-left-color: var(--accent-red);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-card);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-blue);
        color: white;
    }
    
    .progress-container {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }
    
    .progress-bar {
        height: 8px;
        background: var(--bg-secondary);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
        transition: width 0.3s ease;
    }
</style>
"""
