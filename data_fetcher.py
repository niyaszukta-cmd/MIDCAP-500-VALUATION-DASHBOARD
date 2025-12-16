# ============================================================================
# NYZTrade Historical Dashboard - Data Fetcher
# ============================================================================

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import time
from config import (
    DhanConfig, DHAN_SECURITY_IDS, EXCHANGE_SEGMENTS, SYMBOL_CONFIG,
    HISTORICAL_CONFIG, BACKTEST_CONFIG
)
from greeks_calculator import BlackScholesCalculator

class HistoricalDataFetcher:
    """Fetch historical options data from Dhan API"""
    
    def __init__(self, config: DhanConfig = None):
        self.config = config or DhanConfig()
        self.headers = {
            'access-token': self.config.access_token,
            'client-id': self.config.client_id,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.base_url = self.config.base_url
        self.bs_calc = BlackScholesCalculator()
        self.risk_free_rate = BACKTEST_CONFIG['risk_free_rate']
    
    def fetch_rolling_option_data(self, 
                                   symbol: str,
                                   start_date: str,
                                   end_date: str,
                                   interval: str = "1",
                                   expiry_flag: str = "MONTH",
                                   expiry_code: int = 1,
                                   strike_offset: str = "ATM") -> Optional[Dict]:
        """
        Fetch historical rolling options data from Dhan API
        
        Args:
            symbol: Index symbol (NIFTY, BANKNIFTY, etc.)
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Time interval (1, 5, 15, 25, 60 minutes)
            expiry_flag: WEEK or MONTH
            expiry_code: 1 for nearest, 2 for next, etc.
            strike_offset: ATM, ATM+1, ATM-1, etc.
        
        Returns:
            Dictionary containing CE and PE data
        """
        try:
            security_id = DHAN_SECURITY_IDS.get(symbol)
            segment = EXCHANGE_SEGMENTS.get(symbol)
            config = SYMBOL_CONFIG.get(symbol)
            
            if not all([security_id, segment, config]):
                print(f"Invalid symbol: {symbol}")
                return None
            
            # Prepare payload for rolling options API
            payload = {
                "exchangeSegment": segment,
                "interval": interval,
                "securityId": security_id,
                "instrument": config['instrument'],
                "expiryFlag": expiry_flag,
                "expiryCode": expiry_code,
                "strike": strike_offset,
                "drvOptionType": "CALL",  # We'll fetch both CE and PE
                "requiredData": HISTORICAL_CONFIG['required_data_fields'],
                "fromDate": start_date,
                "toDate": end_date
            }
            
            # Fetch Call Options data
            response_ce = requests.post(
                f"{self.base_url}/charts/rollingoption",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Fetch Put Options data
            payload["drvOptionType"] = "PUT"
            response_pe = requests.post(
                f"{self.base_url}/charts/rollingoption",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response_ce.status_code != 200 or response_pe.status_code != 200:
                print(f"API Error: CE={response_ce.status_code}, PE={response_pe.status_code}")
                return None
            
            data_ce = response_ce.json()
            data_pe = response_pe.json()
            
            if 'data' not in data_ce or 'data' not in data_pe:
                print("No data in API response")
                return None
            
            return {
                'ce': data_ce['data'].get('ce', {}),
                'pe': data_pe['data'].get('pe', {}),
                'symbol': symbol,
                'strike_offset': strike_offset,
                'expiry_code': expiry_code,
                'expiry_flag': expiry_flag
            }
            
        except Exception as e:
            print(f"Error fetching rolling option data: {e}")
            return None
    
    def process_rolling_data_to_dataframe(self, 
                                         raw_data: Dict,
                                         contract_size: int) -> Optional[pd.DataFrame]:
        """
        Process raw rolling options data into a structured DataFrame
        
        Args:
            raw_data: Raw data from fetch_rolling_option_data
            contract_size: Contract size for the symbol
        
        Returns:
            DataFrame with processed options data
        """
        try:
            ce_data = raw_data.get('ce', {})
            pe_data = raw_data.get('pe', {})
            
            if not ce_data or not pe_data:
                return None
            
            # Get timestamps (should be same for CE and PE)
            timestamps = ce_data.get('timestamp', [])
            if not timestamps:
                return None
            
            rows = []
            
            for i, ts in enumerate(timestamps):
                try:
                    # Convert epoch to datetime
                    dt = datetime.fromtimestamp(ts)
                    date_str = dt.strftime('%Y-%m-%d')
                    time_str = dt.strftime('%H:%M:%S')
                    
                    # Get spot price
                    spot = ce_data.get('spot', [None])[i] if i < len(ce_data.get('spot', [])) else None
                    if not spot:
                        continue
                    
                    # Process Call Option
                    if 'strike' in ce_data and i < len(ce_data['strike']):
                        strike_ce = ce_data['strike'][i]
                        
                        row_ce = {
                            'timestamp': ts,
                            'date': date_str,
                            'time': time_str,
                            'datetime': dt,
                            'strike': strike_ce,
                            'option_type': 'CE',
                            'spot_price': spot,
                            'open': ce_data.get('open', [None])[i] if i < len(ce_data.get('open', [])) else None,
                            'high': ce_data.get('high', [None])[i] if i < len(ce_data.get('high', [])) else None,
                            'low': ce_data.get('low', [None])[i] if i < len(ce_data.get('low', [])) else None,
                            'close': ce_data.get('close', [None])[i] if i < len(ce_data.get('close', [])) else None,
                            'volume': ce_data.get('volume', [0])[i] if i < len(ce_data.get('volume', [])) else 0,
                            'oi': ce_data.get('oi', [0])[i] if i < len(ce_data.get('oi', [])) else 0,
                            'iv': ce_data.get('iv', [0])[i] if i < len(ce_data.get('iv', [])) else 0,
                        }
                        rows.append(row_ce)
                    
                    # Process Put Option
                    if 'strike' in pe_data and i < len(pe_data['strike']):
                        strike_pe = pe_data['strike'][i]
                        
                        row_pe = {
                            'timestamp': ts,
                            'date': date_str,
                            'time': time_str,
                            'datetime': dt,
                            'strike': strike_pe,
                            'option_type': 'PE',
                            'spot_price': spot,
                            'open': pe_data.get('open', [None])[i] if i < len(pe_data.get('open', [])) else None,
                            'high': pe_data.get('high', [None])[i] if i < len(pe_data.get('high', [])) else None,
                            'low': pe_data.get('low', [None])[i] if i < len(pe_data.get('low', [])) else None,
                            'close': pe_data.get('close', [None])[i] if i < len(pe_data.get('close', [])) else None,
                            'volume': pe_data.get('volume', [0])[i] if i < len(pe_data.get('volume', [])) else 0,
                            'oi': pe_data.get('oi', [0])[i] if i < len(pe_data.get('oi', [])) else 0,
                            'iv': pe_data.get('iv', [0])[i] if i < len(pe_data.get('iv', [])) else 0,
                        }
                        rows.append(row_pe)
                
                except Exception as e:
                    print(f"Error processing row {i}: {e}")
                    continue
            
            if not rows:
                return None
            
            df = pd.DataFrame(rows)
            
            # Calculate Greeks
            df = self.calculate_greeks_for_dataframe(df, contract_size)
            
            return df
            
        except Exception as e:
            print(f"Error processing rolling data: {e}")
            return None
    
    def calculate_greeks_for_dataframe(self, df: pd.DataFrame, contract_size: int) -> pd.DataFrame:
        """Calculate Greeks for all options in dataframe"""
        
        def calc_time_to_expiry(row):
            # Estimate days to expiry (assuming weekly = 7 days, monthly = 30 days)
            # In real scenario, you'd need actual expiry date
            return 7 / 365  # Default to 1 week
        
        df['time_to_expiry'] = df.apply(calc_time_to_expiry, axis=1)
        
        # Calculate Greeks
        greeks_list = []
        
        for idx, row in df.iterrows():
            try:
                S = row['spot_price']
                K = row['strike']
                T = row['time_to_expiry']
                iv = row['iv'] / 100 if row['iv'] > 1 else row['iv']  # Convert to decimal
                iv = max(iv, 0.01)  # Minimum IV
                
                option_type = 'call' if row['option_type'] == 'CE' else 'put'
                greeks = self.bs_calc.calculate_all_greeks(S, K, T, self.risk_free_rate, iv, option_type)
                
                # Calculate exposure
                oi = row['oi']
                gex = (oi * greeks['gamma'] * S**2 * contract_size) / 1e9
                dex = (oi * greeks['delta'] * S * contract_size) / 1e9
                
                # For puts, GEX is negative
                if option_type == 'put':
                    gex = -gex
                
                greeks_list.append({
                    'delta': greeks['delta'],
                    'gamma': greeks['gamma'],
                    'vega': greeks['vega'],
                    'theta': greeks['theta'],
                    'vanna': greeks['vanna'],
                    'charm': greeks['charm'],
                    'gex': gex,
                    'dex': dex
                })
            except:
                greeks_list.append({
                    'delta': 0, 'gamma': 0, 'vega': 0, 'theta': 0,
                    'vanna': 0, 'charm': 0, 'gex': 0, 'dex': 0
                })
        
        greeks_df = pd.DataFrame(greeks_list)
        df = pd.concat([df, greeks_df], axis=1)
        
        return df
    
    def fetch_multiple_strikes_historical(self,
                                         symbol: str,
                                         start_date: str,
                                         end_date: str,
                                         strike_range: List[str] = None,
                                         interval: str = "1",
                                         expiry_flag: str = "MONTH",
                                         expiry_code: int = 1,
                                         delay_seconds: float = 1.0) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for multiple strikes
        
        Args:
            symbol: Index symbol
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            strike_range: List of strike offsets like ['ATM', 'ATM+1', 'ATM-1']
            interval: Time interval
            expiry_flag: WEEK or MONTH
            expiry_code: Expiry code
            delay_seconds: Delay between API calls
        
        Returns:
            Combined DataFrame for all strikes
        """
        if strike_range is None:
            strike_range = ['ATM', 'ATM+1', 'ATM-1', 'ATM+2', 'ATM-2']
        
        config = SYMBOL_CONFIG.get(symbol)
        if not config:
            return None
        
        contract_size = config['contract_size']
        all_dfs = []
        
        for strike_offset in strike_range:
            print(f"Fetching {symbol} {strike_offset} from {start_date} to {end_date}...")
            
            raw_data = self.fetch_rolling_option_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                expiry_flag=expiry_flag,
                expiry_code=expiry_code,
                strike_offset=strike_offset
            )
            
            if raw_data:
                df = self.process_rolling_data_to_dataframe(raw_data, contract_size)
                if df is not None and not df.empty:
                    df['strike_offset'] = strike_offset
                    df['expiry_code'] = expiry_code
                    df['expiry_flag'] = expiry_flag
                    all_dfs.append(df)
            
            # Delay to avoid rate limiting
            time.sleep(delay_seconds)
        
        if not all_dfs:
            return None
        
        # Combine all dataframes
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df = combined_df.sort_values(['datetime', 'strike']).reset_index(drop=True)
        
        return combined_df
    
    def aggregate_gex_dex_by_timestamp(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate GEX and DEX by timestamp for analysis
        
        Returns:
            DataFrame with aggregated metrics per timestamp
        """
        agg_df = df.groupby(['timestamp', 'datetime', 'date', 'time', 'spot_price']).agg({
            'gex': 'sum',
            'dex': 'sum',
            'oi': 'sum',
            'volume': 'sum',
            'iv': 'mean'
        }).reset_index()
        
        agg_df.columns = ['timestamp', 'datetime', 'date', 'time', 'spot_price',
                         'total_gex', 'total_dex', 'total_oi', 'total_volume', 'avg_iv']
        
        # Calculate PCR (Put-Call Ratio)
        ce_oi = df[df['option_type'] == 'CE'].groupby('timestamp')['oi'].sum()
        pe_oi = df[df['option_type'] == 'PE'].groupby('timestamp')['oi'].sum()
        
        pcr_df = pd.DataFrame({
            'timestamp': ce_oi.index,
            'pcr': pe_oi.values / ce_oi.values
        })
        
        agg_df = agg_df.merge(pcr_df, on='timestamp', how='left')
        
        return agg_df
