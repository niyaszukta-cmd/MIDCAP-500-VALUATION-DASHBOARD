# ============================================================================
# NYZTrade Historical Dashboard - Visualization
# ============================================================================

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict
from config import CHART_COLORS

class ChartGenerator:
    """Generate professional charts for backtesting dashboard"""
    
    @staticmethod
    def create_equity_curve(daily_metrics: List[Dict]) -> go.Figure:
        """Create portfolio equity curve"""
        df = pd.DataFrame(daily_metrics)
        
        fig = go.Figure()
        
        # Equity curve
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['portfolio_value'],
            name='Portfolio Value',
            line=dict(color=CHART_COLORS['cyan'], width=3),
            fill='tozeroy',
            fillcolor='rgba(6, 182, 212, 0.1)'
        ))
        
        # Mark trades
        trade_dates = df[df['trades_count'] > df['trades_count'].shift(1)]['date']
        trade_values = df[df['trades_count'] > df['trades_count'].shift(1)]['portfolio_value']
        
        fig.add_trace(go.Scatter(
            x=trade_dates,
            y=trade_values,
            mode='markers',
            name='Trade Entry',
            marker=dict(size=10, color=CHART_COLORS['positive'], symbol='triangle-up')
        ))
        
        fig.update_layout(
            title=dict(text="<b>Portfolio Equity Curve</b>", font=dict(size=16, color='white')),
            xaxis_title="Date",
            yaxis_title="Portfolio Value (₹)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(26,35,50,0.8)',
            height=450,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_drawdown_chart(daily_metrics: List[Dict]) -> go.Figure:
        """Create drawdown chart"""
        df = pd.DataFrame(daily_metrics)
        
        # Calculate drawdown
        rolling_max = df['portfolio_value'].expanding().max()
        drawdown = (df['portfolio_value'] - rolling_max) / rolling_max * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=drawdown,
            name='Drawdown',
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.3)',
            line=dict(color=CHART_COLORS['negative'], width=2)
        ))
        
        fig.update_layout(
            title=dict(text="<b>Portfolio Drawdown</b>", font=dict(size=16, color='white')),
            xaxis_title="Date",
            yaxis_title="Drawdown (%)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(26,35,50,0.8)',
            height=350
        )
        
        return fig
    
    @staticmethod
    def create_gex_dex_time_series(daily_metrics: List[Dict]) -> go.Figure:
        """Create GEX/DEX time series"""
        df = pd.DataFrame(daily_metrics)
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Total GEX Over Time", "Total DEX Over Time"),
            vertical_spacing=0.15
        )
        
        # GEX
        colors_gex = [CHART_COLORS['positive'] if x > 0 else CHART_COLORS['negative'] 
                     for x in df['total_gex']]
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['total_gex'],
            name='Total GEX',
            marker_color=colors_gex
        ), row=1, col=1)
        
        # DEX
        colors_dex = [CHART_COLORS['positive'] if x > 0 else CHART_COLORS['negative'] 
                     for x in df['total_dex']]
        
        fig.add_trace(go.Bar(
            x=df['date'],
            y=df['total_dex'],
            name='Total DEX',
            marker_color=colors_dex
        ), row=2, col=1)
        
        fig.update_layout(
            title=dict(text="<b>GEX/DEX Historical Trends</b>", font=dict(size=16, color='white')),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(26,35,50,0.8)',
            height=600,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_trade_analysis(trades: List[Dict]) -> go.Figure:
        """Create trade analysis chart"""
        df = pd.DataFrame(trades)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("P&L per Trade", "Strategy Distribution", 
                          "Win/Loss Distribution", "Entry Reasons"),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # P&L per trade
        colors_pnl = [CHART_COLORS['positive'] if x > 0 else CHART_COLORS['negative'] 
                     for x in df['pnl']]
        
        fig.add_trace(go.Bar(
            x=df['trade_number'],
            y=df['pnl'],
            name='P&L',
            marker_color=colors_pnl
        ), row=1, col=1)
        
        # Strategy distribution
        strategy_counts = df['strategy'].value_counts()
        fig.add_trace(go.Pie(
            labels=strategy_counts.index,
            values=strategy_counts.values,
            name='Strategies'
        ), row=1, col=2)
        
        # Win/Loss distribution
        win_loss = df['pnl'].apply(lambda x: 'Win' if x > 0 else 'Loss').value_counts()
        fig.add_trace(go.Bar(
            x=win_loss.index,
            y=win_loss.values,
            marker_color=[CHART_COLORS['positive'], CHART_COLORS['negative']],
            name='Win/Loss'
        ), row=2, col=1)
        
        # Entry reasons (top 5)
        entry_reasons = df['entry_reason'].value_counts().head(5)
        fig.add_trace(go.Bar(
            x=entry_reasons.values,
            y=entry_reasons.index,
            orientation='h',
            marker_color=CHART_COLORS['blue'],
            name='Entry Reasons'
        ), row=2, col=2)
        
        fig.update_layout(
            title=dict(text="<b>Trade Analysis</b>", font=dict(size=16, color='white')),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(26,35,50,0.8)',
            height=700,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_monthly_returns_heatmap(daily_metrics: List[Dict]) -> go.Figure:
        """Create monthly returns heatmap"""
        df = pd.DataFrame(daily_metrics)
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        
        # Calculate monthly returns
        df['returns'] = df['portfolio_value'].pct_change() * 100
        monthly_returns = df.groupby(['year', 'month'])['returns'].sum().reset_index()
        
        # Pivot for heatmap
        pivot = monthly_returns.pivot(index='month', columns='year', values='returns')
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            colorscale='RdYlGn',
            text=pivot.values,
            texttemplate='%{text:.1f}%',
            textfont={"size": 10},
            colorbar=dict(title="Return %")
        ))
        
        fig.update_layout(
            title=dict(text="<b>Monthly Returns Heatmap</b>", font=dict(size=16, color='white')),
            xaxis_title="Year",
            yaxis_title="Month",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(26,35,50,0.8)',
            height=450
        )
        
        return fig
    
    @staticmethod
    def create_pcr_vs_returns(daily_metrics: List[Dict]) -> go.Figure:
        """Create PCR vs Returns scatter plot"""
        df = pd.DataFrame(daily_metrics)
        df['returns'] = df['portfolio_value'].pct_change() * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['pcr'],
            y=df['returns'],
            mode='markers',
            marker=dict(
                size=8,
                color=df['total_gex'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="GEX")
            ),
            text=df['date'],
            hovertemplate='PCR: %{x:.2f}<br>Return: %{y:.2f}%<br>Date: %{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text="<b>PCR vs Daily Returns</b>", font=dict(size=16, color='white')),
            xaxis_title="Put-Call Ratio",
            yaxis_title="Daily Return (%)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(26,35,50,0.8)',
            height=450
        )
        
        return fig
    
    @staticmethod
    def create_performance_metrics_gauge(results: Dict) -> go.Figure:
        """Create performance metrics gauge chart"""
        
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'indicator'}, {'type': 'indicator'}]],
            vertical_spacing=0.25
        )
        
        # Total Return
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=results['total_return_pct'],
            title={'text': "Total Return %", 'font': {'size': 14, 'color': 'white'}},
            delta={'reference': 0, 'increasing': {'color': CHART_COLORS['positive']}},
            gauge={
                'axis': {'range': [-100, 100]},
                'bar': {'color': CHART_COLORS['cyan']},
                'steps': [
                    {'range': [-100, 0], 'color': 'rgba(239, 68, 68, 0.3)'},
                    {'range': [0, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
                ]
            }
        ), row=1, col=1)
        
        # Win Rate
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=results['win_rate'],
            title={'text': "Win Rate %", 'font': {'size': 14, 'color': 'white'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': CHART_COLORS['positive']},
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.3)'},
                    {'range': [50, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
                ]
            }
        ), row=1, col=2)
        
        # Sharpe Ratio
        sharpe = results.get('sharpe_ratio', 0)
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=sharpe,
            title={'text': "Sharpe Ratio", 'font': {'size': 14, 'color': 'white'}},
            gauge={
                'axis': {'range': [-3, 3]},
                'bar': {'color': CHART_COLORS['purple']},
                'steps': [
                    {'range': [-3, 0], 'color': 'rgba(239, 68, 68, 0.3)'},
                    {'range': [0, 1], 'color': 'rgba(245, 158, 11, 0.3)'},
                    {'range': [1, 3], 'color': 'rgba(16, 185, 129, 0.3)'}
                ]
            }
        ), row=2, col=1)
        
        # Max Drawdown
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=results['max_drawdown'],
            title={'text': "Max Drawdown %", 'font': {'size': 14, 'color': 'white'}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': CHART_COLORS['negative']},
                'steps': [
                    {'range': [0, 20], 'color': 'rgba(16, 185, 129, 0.3)'},
                    {'range': [20, 50], 'color': 'rgba(245, 158, 11, 0.3)'},
                    {'range': [50, 100], 'color': 'rgba(239, 68, 68, 0.3)'}
                ]
            }
        ), row=2, col=2)
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': "white"},
            height=600
        )
        
        return fig
    
    @staticmethod
    def create_cumulative_pnl_by_strategy(trades: List[Dict]) -> go.Figure:
        """Create cumulative P&L by strategy"""
        df = pd.DataFrame(trades)
        
        fig = go.Figure()
        
        for strategy in df['strategy'].unique():
            strategy_trades = df[df['strategy'] == strategy].copy()
            strategy_trades['cumulative_pnl'] = strategy_trades['pnl'].cumsum()
            
            fig.add_trace(go.Scatter(
                x=strategy_trades['entry_date'],
                y=strategy_trades['cumulative_pnl'],
                name=strategy,
                mode='lines+markers',
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title=dict(text="<b>Cumulative P&L by Strategy</b>", font=dict(size=16, color='white')),
            xaxis_title="Date",
            yaxis_title="Cumulative P&L (₹)",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(26,35,50,0.8)',
            height=450,
            hovermode='x unified'
        )
        
        return fig
