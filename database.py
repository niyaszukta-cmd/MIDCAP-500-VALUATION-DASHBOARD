# ============================================================================
# NYZTrade Historical Dashboard - Database Operations
# ============================================================================

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict
import json
from config import DATABASE_CONFIG

class HistoricalDatabase:
    """Manage SQLite database for historical data and backtest results"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_CONFIG['db_path']
        self.initialize_database()
    
    def initialize_database(self):
        """Create all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Historical options data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_options_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                date TEXT NOT NULL,
                strike REAL NOT NULL,
                option_type TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                spot_price REAL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                oi INTEGER,
                iv REAL,
                delta REAL,
                gamma REAL,
                vega REAL,
                theta REAL,
                vanna REAL,
                charm REAL,
                gex REAL,
                dex REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp, strike, option_type, expiry_date)
            )
        ''')
        
        # Backtest results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backtest_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                strategy TEXT NOT NULL,
                initial_capital REAL NOT NULL,
                final_capital REAL NOT NULL,
                total_return REAL NOT NULL,
                total_return_pct REAL NOT NULL,
                total_trades INTEGER NOT NULL,
                winning_trades INTEGER NOT NULL,
                losing_trades INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                max_drawdown REAL NOT NULL,
                sharpe_ratio REAL,
                sortino_ratio REAL,
                avg_trade_return REAL,
                max_win REAL,
                max_loss REAL,
                profit_factor REAL,
                config_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Trades log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backtest_id INTEGER NOT NULL,
                trade_number INTEGER NOT NULL,
                entry_date TEXT NOT NULL,
                exit_date TEXT,
                strategy TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                quantity INTEGER NOT NULL,
                pnl REAL,
                pnl_pct REAL,
                status TEXT NOT NULL,
                entry_gex REAL,
                entry_dex REAL,
                entry_pcr REAL,
                stop_loss REAL,
                target REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (backtest_id) REFERENCES backtest_results(id)
            )
        ''')
        
        # Daily metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backtest_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                spot_price REAL NOT NULL,
                total_gex REAL,
                total_dex REAL,
                gex_near REAL,
                dex_near REAL,
                pcr REAL,
                atm_iv REAL,
                portfolio_value REAL NOT NULL,
                daily_pnl REAL,
                cumulative_pnl REAL,
                drawdown REAL,
                trades_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (backtest_id) REFERENCES backtest_results(id),
                UNIQUE(backtest_id, date)
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_historical_symbol_date 
            ON historical_options_data(symbol, date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_historical_timestamp 
            ON historical_options_data(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trades_backtest 
            ON trades_log(backtest_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_daily_backtest 
            ON daily_metrics(backtest_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_historical_data(self, df: pd.DataFrame, symbol: str):
        """Save historical options data to database"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            df_to_save = df.copy()
            df_to_save['symbol'] = symbol
            df_to_save['created_at'] = datetime.now().isoformat()
            
            df_to_save.to_sql('historical_options_data', conn, 
                            if_exists='append', index=False)
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving historical data: {e}")
            return False
        finally:
            conn.close()
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Retrieve historical data for a symbol and date range"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM historical_options_data
            WHERE symbol = ? AND date >= ? AND date <= ?
            ORDER BY timestamp, strike
        '''
        
        try:
            df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
            return df if not df.empty else None
        except Exception as e:
            print(f"Error retrieving historical data: {e}")
            return None
        finally:
            conn.close()
    
    def save_backtest_result(self, result: Dict) -> Optional[int]:
        """Save backtest result and return backtest_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO backtest_results (
                    backtest_name, symbol, start_date, end_date, strategy,
                    initial_capital, final_capital, total_return, total_return_pct,
                    total_trades, winning_trades, losing_trades, win_rate,
                    max_drawdown, sharpe_ratio, sortino_ratio, avg_trade_return,
                    max_win, max_loss, profit_factor, config_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['backtest_name'], result['symbol'], result['start_date'], result['end_date'],
                result['strategy'], result['initial_capital'], result['final_capital'],
                result['total_return'], result['total_return_pct'], result['total_trades'],
                result['winning_trades'], result['losing_trades'], result['win_rate'],
                result['max_drawdown'], result.get('sharpe_ratio'), result.get('sortino_ratio'),
                result.get('avg_trade_return'), result.get('max_win'), result.get('max_loss'),
                result.get('profit_factor'), json.dumps(result.get('config', {}))
            ))
            
            backtest_id = cursor.lastrowid
            conn.commit()
            return backtest_id
        except Exception as e:
            print(f"Error saving backtest result: {e}")
            return None
        finally:
            conn.close()
    
    def save_trade(self, backtest_id: int, trade: Dict):
        """Save individual trade to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO trades_log (
                    backtest_id, trade_number, entry_date, exit_date, strategy,
                    direction, entry_price, exit_price, quantity, pnl, pnl_pct,
                    status, entry_gex, entry_dex, entry_pcr, stop_loss, target, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                backtest_id, trade['trade_number'], trade['entry_date'], trade.get('exit_date'),
                trade['strategy'], trade['direction'], trade['entry_price'], trade.get('exit_price'),
                trade['quantity'], trade.get('pnl'), trade.get('pnl_pct'), trade['status'],
                trade.get('entry_gex'), trade.get('entry_dex'), trade.get('entry_pcr'),
                trade.get('stop_loss'), trade.get('target'), trade.get('notes')
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Error saving trade: {e}")
        finally:
            conn.close()
    
    def save_daily_metrics(self, backtest_id: int, metrics: Dict):
        """Save daily portfolio metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_metrics (
                    backtest_id, date, symbol, spot_price, total_gex, total_dex,
                    gex_near, dex_near, pcr, atm_iv, portfolio_value, daily_pnl,
                    cumulative_pnl, drawdown, trades_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                backtest_id, metrics['date'], metrics['symbol'], metrics['spot_price'],
                metrics.get('total_gex'), metrics.get('total_dex'), metrics.get('gex_near'),
                metrics.get('dex_near'), metrics.get('pcr'), metrics.get('atm_iv'),
                metrics['portfolio_value'], metrics.get('daily_pnl'), metrics.get('cumulative_pnl'),
                metrics.get('drawdown'), metrics.get('trades_count', 0)
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Error saving daily metrics: {e}")
        finally:
            conn.close()
    
    def get_backtest_results(self, limit: int = 10) -> Optional[pd.DataFrame]:
        """Get recent backtest results"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM backtest_results
            ORDER BY created_at DESC
            LIMIT ?
        '''
        
        try:
            df = pd.read_sql_query(query, conn, params=(limit,))
            return df if not df.empty else None
        except Exception as e:
            print(f"Error retrieving backtest results: {e}")
            return None
        finally:
            conn.close()
    
    def get_trades_for_backtest(self, backtest_id: int) -> Optional[pd.DataFrame]:
        """Get all trades for a specific backtest"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM trades_log
            WHERE backtest_id = ?
            ORDER BY trade_number
        '''
        
        try:
            df = pd.read_sql_query(query, conn, params=(backtest_id,))
            return df if not df.empty else None
        except Exception as e:
            print(f"Error retrieving trades: {e}")
            return None
        finally:
            conn.close()
    
    def get_daily_metrics_for_backtest(self, backtest_id: int) -> Optional[pd.DataFrame]:
        """Get daily metrics for a specific backtest"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM daily_metrics
            WHERE backtest_id = ?
            ORDER BY date
        '''
        
        try:
            df = pd.read_sql_query(query, conn, params=(backtest_id,))
            return df if not df.empty else None
        except Exception as e:
            print(f"Error retrieving daily metrics: {e}")
            return None
        finally:
            conn.close()
