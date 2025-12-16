# ============================================================================
# NYZTrade Historical Dashboard - Utility Functions
# ============================================================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple

def split_date_range(start_date: str, end_date: str, max_days: int = 30) -> List[Tuple[str, str]]:
    """
    Split a date range into smaller chunks for API requests
    
    Args:
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        max_days: Maximum days per chunk
    
    Returns:
        List of (start_date, end_date) tuples
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    date_ranges = []
    current_start = start
    
    while current_start < end:
        current_end = min(current_start + timedelta(days=max_days), end)
        date_ranges.append((
            current_start.strftime('%Y-%m-%d'),
            current_end.strftime('%Y-%m-%d')
        ))
        current_start = current_end
    
    return date_ranges

def calculate_returns_distribution(trades_df: pd.DataFrame) -> dict:
    """Calculate returns distribution statistics"""
    if trades_df.empty:
        return {}
    
    pnl = trades_df['pnl']
    
    return {
        'mean': pnl.mean(),
        'median': pnl.median(),
        'std': pnl.std(),
        'skewness': pnl.skew(),
        'kurtosis': pnl.kurtosis(),
        'min': pnl.min(),
        'max': pnl.max(),
        'percentile_25': pnl.quantile(0.25),
        'percentile_75': pnl.quantile(0.75)
    }

def format_currency(value: float) -> str:
    """Format value as Indian currency"""
    if abs(value) >= 10000000:  # 1 Crore
        return f"₹{value/10000000:.2f}Cr"
    elif abs(value) >= 100000:  # 1 Lakh
        return f"₹{value/100000:.2f}L"
    else:
        return f"₹{value:,.2f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage"""
    return f"{value:.{decimals}f}%"

def calculate_max_consecutive_wins_losses(trades_df: pd.DataFrame) -> dict:
    """Calculate maximum consecutive wins and losses"""
    if trades_df.empty:
        return {'max_consecutive_wins': 0, 'max_consecutive_losses': 0}
    
    wins = (trades_df['pnl'] > 0).astype(int)
    
    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_wins = 0
    current_losses = 0
    
    for win in wins:
        if win:
            current_wins += 1
            current_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
        else:
            current_losses += 1
            current_wins = 0
            max_consecutive_losses = max(max_consecutive_losses, current_losses)
    
    return {
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses
    }

def calculate_risk_metrics(daily_metrics: List[dict], risk_free_rate: float = 0.07) -> dict:
    """Calculate advanced risk metrics"""
    df = pd.DataFrame(daily_metrics)
    
    if len(df) < 2:
        return {}
    
    # Calculate returns
    df['returns'] = df['portfolio_value'].pct_change()
    
    # Sharpe Ratio
    excess_returns = df['returns'].mean() - (risk_free_rate / 252)
    sharpe_ratio = (excess_returns / df['returns'].std()) * np.sqrt(252) if df['returns'].std() > 0 else 0
    
    # Sortino Ratio (only downside deviation)
    downside_returns = df[df['returns'] < 0]['returns']
    downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
    sortino_ratio = (excess_returns / downside_std) * np.sqrt(252) if downside_std > 0 else 0
    
    # Calmar Ratio
    rolling_max = df['portfolio_value'].expanding().max()
    drawdown = (df['portfolio_value'] - rolling_max) / rolling_max
    max_drawdown = abs(drawdown.min())
    
    total_return = (df['portfolio_value'].iloc[-1] / df['portfolio_value'].iloc[0]) - 1
    calmar_ratio = total_return / max_drawdown if max_drawdown > 0 else 0
    
    # Value at Risk (VaR) - 95% confidence
    var_95 = df['returns'].quantile(0.05)
    
    # Conditional Value at Risk (CVaR)
    cvar_95 = df[df['returns'] <= var_95]['returns'].mean()
    
    return {
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'calmar_ratio': calmar_ratio,
        'var_95': var_95 * 100,
        'cvar_95': cvar_95 * 100,
        'max_drawdown': max_drawdown * 100,
        'volatility_annual': df['returns'].std() * np.sqrt(252) * 100
    }

def generate_trade_summary(trades: List[dict]) -> dict:
    """Generate comprehensive trade summary"""
    if not trades:
        return {}
    
    df = pd.DataFrame(trades)
    
    winning_trades = df[df['pnl'] > 0]
    losing_trades = df[df['pnl'] < 0]
    
    avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
    avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
    
    total_wins = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
    total_losses = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
    
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    # Average holding period
    df['holding_period'] = (pd.to_datetime(df['exit_date']) - pd.to_datetime(df['entry_date'])).dt.days
    avg_holding = df['holding_period'].mean()
    
    # Best and worst trades
    best_trade = df.loc[df['pnl'].idxmax()] if len(df) > 0 else None
    worst_trade = df.loc[df['pnl'].idxmin()] if len(df) > 0 else None
    
    consecutive = calculate_max_consecutive_wins_losses(df)
    
    return {
        'total_trades': len(df),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': (len(winning_trades) / len(df)) * 100,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'largest_win': df['pnl'].max(),
        'largest_loss': df['pnl'].min(),
        'profit_factor': profit_factor,
        'avg_holding_period': avg_holding,
        'max_consecutive_wins': consecutive['max_consecutive_wins'],
        'max_consecutive_losses': consecutive['max_consecutive_losses'],
        'best_trade': best_trade.to_dict() if best_trade is not None else None,
        'worst_trade': worst_trade.to_dict() if worst_trade is not None else None
    }

def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate date range"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start >= end:
            return False
        
        if start < datetime(2020, 1, 1):
            return False
        
        if end > datetime.now():
            return False
        
        return True
    except:
        return False

def calculate_strategy_performance(trades: List[dict]) -> pd.DataFrame:
    """Calculate performance by strategy"""
    if not trades:
        return pd.DataFrame()
    
    df = pd.DataFrame(trades)
    
    strategy_perf = df.groupby('strategy').agg({
        'pnl': ['count', 'sum', 'mean', 'std'],
        'pnl_pct': 'mean'
    }).reset_index()
    
    strategy_perf.columns = ['Strategy', 'Trades', 'Total PnL', 'Avg PnL', 'Std PnL', 'Avg PnL %']
    
    # Calculate win rate per strategy
    win_rates = []
    for strategy in strategy_perf['Strategy']:
        strategy_trades = df[df['strategy'] == strategy]
        wins = len(strategy_trades[strategy_trades['pnl'] > 0])
        win_rate = (wins / len(strategy_trades)) * 100 if len(strategy_trades) > 0 else 0
        win_rates.append(win_rate)
    
    strategy_perf['Win Rate %'] = win_rates
    
    return strategy_perf

def export_to_csv(data: pd.DataFrame, filename: str) -> str:
    """Export DataFrame to CSV and return as string"""
    return data.to_csv(index=False)

def create_backtest_report_text(results: dict) -> str:
    """Create a text report of backtest results"""
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║           NYZTrade Historical Backtest Report                ║
╚══════════════════════════════════════════════════════════════╝

OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Symbol:              {results['symbol']}
Strategy:            {results['strategy']}
Period:              {results['start_date']} to {results['end_date']}

CAPITAL & RETURNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Initial Capital:     {format_currency(results['initial_capital'])}
Final Capital:       {format_currency(results['final_capital'])}
Total Return:        {format_currency(results['total_return'])}
Total Return %:      {format_percentage(results['total_return_pct'])}

TRADE STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Trades:        {results['total_trades']}
Winning Trades:      {results['winning_trades']}
Losing Trades:       {results['losing_trades']}
Win Rate:            {format_percentage(results['win_rate'])}

RISK METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Max Drawdown:        {format_percentage(results['max_drawdown'])}
Sharpe Ratio:        {results.get('sharpe_ratio', 0):.2f}
Profit Factor:       {results.get('profit_factor', 0):.2f}

TRADE PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Trade:       {format_currency(results.get('avg_trade_return', 0))}
Largest Win:         {format_currency(results.get('max_win', 0))}
Largest Loss:        {format_currency(results.get('max_loss', 0))}

═══════════════════════════════════════════════════════════════
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════
    """
    
    return report
