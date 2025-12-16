# ============================================================================
# NYZTrade Historical Dashboard - Backtest Engine
# ============================================================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import BACKTEST_CONFIG, STRATEGY_THRESHOLDS

class BacktestEngine:
    """Backtest trading strategies using historical GEX/DEX data"""
    
    def __init__(self, 
                 initial_capital: float = None,
                 max_position_size: float = None,
                 commission_per_lot: float = None,
                 slippage: float = None):
        
        self.initial_capital = initial_capital or BACKTEST_CONFIG['initial_capital']
        self.max_position_size = max_position_size or BACKTEST_CONFIG['max_position_size']
        self.commission_per_lot = commission_per_lot or BACKTEST_CONFIG['commission_per_lot']
        self.slippage = slippage or BACKTEST_CONFIG['slippage']
        
        self.reset()
    
    def reset(self):
        """Reset backtest state"""
        self.capital = self.initial_capital
        self.trades = []
        self.daily_metrics = []
        self.positions = []
        self.trade_counter = 0
        self.daily_pnl = []
        self.peak_capital = self.initial_capital
        self.max_drawdown = 0
    
    def generate_signal(self, gex: float, dex: float, pcr: float) -> Dict:
        """
        Generate trading signal based on GEX/DEX metrics
        
        Returns:
            Dict with strategy, direction, and confidence
        """
        signal = {
            'strategy': 'NONE',
            'direction': 'NEUTRAL',
            'confidence': 0,
            'entry_reason': ''
        }
        
        # Strong Suppression (GEX > 50)
        if gex > STRATEGY_THRESHOLDS['strong_suppression']['gex_threshold']:
            signal['strategy'] = 'IRON_CONDOR'
            signal['direction'] = 'NEUTRAL'
            signal['confidence'] = min(abs(gex) / 100, 1.0)
            signal['entry_reason'] = f'Strong GEX Suppression ({gex:.2f})'
        
        # High Amplification (GEX < -50)
        elif gex < -STRATEGY_THRESHOLDS['high_amplification']['gex_threshold']:
            if dex > STRATEGY_THRESHOLDS['bullish_dex']['dex_threshold']:
                signal['strategy'] = 'BULL_CALL_SPREAD'
                signal['direction'] = 'BULLISH'
                signal['confidence'] = min(abs(dex) / 100, 1.0)
                signal['entry_reason'] = f'High Vol + Bullish DEX (GEX:{gex:.2f}, DEX:{dex:.2f})'
            elif dex < STRATEGY_THRESHOLDS['bearish_dex']['dex_threshold']:
                signal['strategy'] = 'BEAR_PUT_SPREAD'
                signal['direction'] = 'BEARISH'
                signal['confidence'] = min(abs(dex) / 100, 1.0)
                signal['entry_reason'] = f'High Vol + Bearish DEX (GEX:{gex:.2f}, DEX:{dex:.2f})'
            else:
                signal['strategy'] = 'LONG_STRADDLE'
                signal['direction'] = 'VOLATILE'
                signal['confidence'] = min(abs(gex) / 100, 1.0)
                signal['entry_reason'] = f'High GEX Amplification ({gex:.2f})'
        
        # Suppression (0 < GEX < 50)
        elif 0 < gex < STRATEGY_THRESHOLDS['strong_suppression']['gex_threshold']:
            signal['strategy'] = 'SHORT_STRADDLE'
            signal['direction'] = 'NEUTRAL'
            signal['confidence'] = min(abs(gex) / 50, 1.0)
            signal['entry_reason'] = f'GEX Suppression ({gex:.2f})'
        
        # Amplification (-50 < GEX < 0)
        elif -STRATEGY_THRESHOLDS['high_amplification']['gex_threshold'] < gex < 0:
            if dex > 20:
                signal['strategy'] = 'LONG_CALL'
                signal['direction'] = 'BULLISH'
                signal['confidence'] = min(abs(dex) / 50, 1.0)
                signal['entry_reason'] = f'Moderate Vol + Bullish DEX (DEX:{dex:.2f})'
            elif dex < -20:
                signal['strategy'] = 'LONG_PUT'
                signal['direction'] = 'BEARISH'
                signal['confidence'] = min(abs(dex) / 50, 1.0)
                signal['entry_reason'] = f'Moderate Vol + Bearish DEX (DEX:{dex:.2f})'
        
        return signal
    
    def calculate_position_size(self, price: float, confidence: float) -> int:
        """Calculate position size based on capital and confidence"""
        max_investment = self.capital * self.max_position_size * confidence
        lots = int(max_investment / price)
        return max(1, lots)
    
    def enter_trade(self, 
                   signal: Dict,
                   entry_price: float,
                   entry_date: str,
                   spot_price: float,
                   gex: float,
                   dex: float,
                   pcr: float) -> Optional[Dict]:
        """Enter a new trade"""
        
        if signal['strategy'] == 'NONE':
            return None
        
        quantity = self.calculate_position_size(entry_price, signal['confidence'])
        
        # Calculate costs
        total_cost = (entry_price * quantity) + (self.commission_per_lot * quantity)
        
        if total_cost > self.capital * self.max_position_size:
            return None  # Not enough capital
        
        self.trade_counter += 1
        
        # Set stop loss and target based on strategy
        if 'SPREAD' in signal['strategy'] or 'CONDOR' in signal['strategy']:
            stop_loss_pct = 0.5  # 50% stop loss for credit spreads
            target_pct = 0.3     # 30% of max profit
        elif 'STRADDLE' in signal['strategy']:
            stop_loss_pct = 0.5
            target_pct = 1.0
        else:
            stop_loss_pct = 0.3
            target_pct = 1.0
        
        trade = {
            'trade_number': self.trade_counter,
            'entry_date': entry_date,
            'strategy': signal['strategy'],
            'direction': signal['direction'],
            'entry_price': entry_price,
            'quantity': quantity,
            'total_cost': total_cost,
            'status': 'OPEN',
            'entry_gex': gex,
            'entry_dex': dex,
            'entry_pcr': pcr,
            'entry_spot': spot_price,
            'stop_loss': entry_price * (1 - stop_loss_pct),
            'target': entry_price * (1 + target_pct),
            'entry_reason': signal['entry_reason'],
            'exit_date': None,
            'exit_price': None,
            'pnl': 0,
            'pnl_pct': 0
        }
        
        self.positions.append(trade)
        self.capital -= total_cost
        
        return trade
    
    def exit_trade(self, 
                  trade: Dict,
                  exit_price: float,
                  exit_date: str,
                  exit_reason: str = 'Target/SL'):
        """Exit an existing trade"""
        
        # Calculate P&L
        exit_value = exit_price * trade['quantity']
        exit_cost = self.commission_per_lot * trade['quantity']
        
        pnl = exit_value - trade['total_cost'] - exit_cost
        pnl_pct = (pnl / trade['total_cost']) * 100
        
        trade['exit_date'] = exit_date
        trade['exit_price'] = exit_price
        trade['pnl'] = pnl
        trade['pnl_pct'] = pnl_pct
        trade['status'] = 'CLOSED'
        trade['exit_reason'] = exit_reason
        
        self.capital += exit_value - exit_cost
        self.trades.append(trade.copy())
        
        # Update drawdown
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital
        
        drawdown = (self.peak_capital - self.capital) / self.peak_capital
        self.max_drawdown = max(self.max_drawdown, drawdown)
        
        return trade
    
    def check_exit_conditions(self, trade: Dict, current_price: float, current_date: str) -> Tuple[bool, str]:
        """Check if trade should be exited"""
        
        # Check stop loss
        if current_price <= trade['stop_loss']:
            return True, 'Stop Loss'
        
        # Check target
        if current_price >= trade['target']:
            return True, 'Target'
        
        # Check time-based exit (e.g., hold for max 5 days)
        try:
            entry_dt = datetime.strptime(trade['entry_date'], '%Y-%m-%d')
            current_dt = datetime.strptime(current_date, '%Y-%m-%d')
            days_held = (current_dt - entry_dt).days
            
            if days_held >= 5:
                return True, 'Time Exit'
        except:
            pass
        
        return False, ''
    
    def run_backtest(self, df: pd.DataFrame, symbol: str) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            df: DataFrame with aggregated GEX/DEX data (from aggregate_gex_dex_by_timestamp)
            symbol: Trading symbol
        
        Returns:
            Dict with backtest results
        """
        self.reset()
        
        for idx, row in df.iterrows():
            date = row['date']
            spot_price = row['spot_price']
            gex = row['total_gex']
            dex = row['total_dex']
            pcr = row.get('pcr', 1.0)
            
            # Check existing positions for exit
            for position in self.positions[:]:
                should_exit, exit_reason = self.check_exit_conditions(
                    position, spot_price, date
                )
                
                if should_exit:
                    self.exit_trade(position, spot_price, date, exit_reason)
                    self.positions.remove(position)
            
            # Generate new signal if no open positions
            if len(self.positions) == 0:
                signal = self.generate_signal(gex, dex, pcr)
                
                if signal['strategy'] != 'NONE' and signal['confidence'] > 0.3:
                    # Use spot price as proxy for option premium
                    # In real scenario, you'd use actual option prices
                    entry_price = spot_price * 0.02  # Assume 2% of spot as premium
                    
                    trade = self.enter_trade(
                        signal, entry_price, date, spot_price, gex, dex, pcr
                    )
            
            # Record daily metrics
            daily_metric = {
                'date': date,
                'symbol': symbol,
                'spot_price': spot_price,
                'total_gex': gex,
                'total_dex': dex,
                'pcr': pcr,
                'portfolio_value': self.capital,
                'trades_count': len(self.trades),
                'open_positions': len(self.positions)
            }
            
            self.daily_metrics.append(daily_metric)
        
        # Close any remaining open positions
        for position in self.positions:
            self.exit_trade(position, position['entry_price'], df.iloc[-1]['date'], 'End of Period')
        
        # Calculate final statistics
        results = self.calculate_statistics(symbol, df.iloc[0]['date'], df.iloc[-1]['date'])
        
        return results
    
    def calculate_statistics(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """Calculate backtest statistics"""
        
        total_trades = len(self.trades)
        
        if total_trades == 0:
            return {
                'backtest_name': f"{symbol}_Backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'strategy': 'GEX/DEX Multi-Strategy',
                'initial_capital': self.initial_capital,
                'final_capital': self.capital,
                'total_return': 0,
                'total_return_pct': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'max_drawdown': 0,
                'trades': [],
                'daily_metrics': self.daily_metrics
            }
        
        trades_df = pd.DataFrame(self.trades)
        
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_return = self.capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        max_win = trades_df['pnl'].max() if total_trades > 0 else 0
        max_loss = trades_df['pnl'].min() if total_trades > 0 else 0
        
        avg_trade_return = trades_df['pnl'].mean() if total_trades > 0 else 0
        
        # Calculate Sharpe Ratio
        if len(self.daily_metrics) > 1:
            daily_returns = [
                (self.daily_metrics[i]['portfolio_value'] - self.daily_metrics[i-1]['portfolio_value']) / 
                self.daily_metrics[i-1]['portfolio_value']
                for i in range(1, len(self.daily_metrics))
            ]
            sharpe_ratio = (np.mean(daily_returns) / np.std(daily_returns)) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'backtest_name': f"{symbol}_Backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'strategy': 'GEX/DEX Multi-Strategy',
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'max_drawdown': self.max_drawdown * 100,
            'sharpe_ratio': sharpe_ratio,
            'avg_trade_return': avg_trade_return,
            'max_win': max_win,
            'max_loss': max_loss,
            'profit_factor': profit_factor,
            'trades': self.trades,
            'daily_metrics': self.daily_metrics,
            'config': {
                'initial_capital': self.initial_capital,
                'max_position_size': self.max_position_size,
                'commission_per_lot': self.commission_per_lot,
                'slippage': self.slippage
            }
        }
