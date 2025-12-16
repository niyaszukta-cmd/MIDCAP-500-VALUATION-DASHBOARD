# ============================================================================
# NYZTrade Historical Dashboard - Greeks Calculator
# ============================================================================

import numpy as np
from scipy.stats import norm
from typing import Dict, Optional

class BlackScholesCalculator:
    """Calculate option Greeks using Black-Scholes model"""
    
    @staticmethod
    def calculate_d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate d1 parameter"""
        if T <= 0 or sigma <= 0:
            return 0
        try:
            return (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * np.sqrt(T))
        except:
            return 0
    
    @staticmethod
    def calculate_d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate d2 parameter"""
        if T <= 0 or sigma <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return d1 - sigma * np.sqrt(T)
        except:
            return 0
    
    @staticmethod
    def calculate_gamma(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Gamma"""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            n_prime_d1 = norm.pdf(d1)
            return n_prime_d1 / (S * sigma * np.sqrt(T))
        except:
            return 0
    
    @staticmethod
    def calculate_call_delta(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Call Delta"""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return norm.cdf(d1)
        except:
            return 0
    
    @staticmethod
    def calculate_put_delta(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Put Delta"""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return norm.cdf(d1) - 1
        except:
            return 0
    
    @staticmethod
    def calculate_vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Vega (per 1% change in IV)"""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            return S * norm.pdf(d1) * np.sqrt(T) / 100
        except:
            return 0
    
    @staticmethod
    def calculate_theta_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Call Theta (per day)"""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            d2 = BlackScholesCalculator.calculate_d2(S, K, T, r, sigma)
            term1 = -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            term2 = -r * K * np.exp(-r * T) * norm.cdf(d2)
            return (term1 + term2) / 365
        except:
            return 0
    
    @staticmethod
    def calculate_theta_put(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Put Theta (per day)"""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            d2 = BlackScholesCalculator.calculate_d2(S, K, T, r, sigma)
            term1 = -S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
            return (term1 + term2) / 365
        except:
            return 0
    
    @staticmethod
    def calculate_vanna(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Vanna (delta sensitivity to volatility)"""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            d2 = BlackScholesCalculator.calculate_d2(S, K, T, r, sigma)
            vanna = -norm.pdf(d1) * d2 / sigma
            return vanna
        except:
            return 0
    
    @staticmethod
    def calculate_charm(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate Charm (delta decay per day)"""
        if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
            return 0
        try:
            d1 = BlackScholesCalculator.calculate_d1(S, K, T, r, sigma)
            d2 = BlackScholesCalculator.calculate_d2(S, K, T, r, sigma)
            charm = -norm.pdf(d1) * (2 * r * T - d2 * sigma * np.sqrt(T)) / (2 * T * sigma * np.sqrt(T))
            return charm / 365
        except:
            return 0
    
    @staticmethod
    def calculate_all_greeks(S: float, K: float, T: float, r: float, sigma: float, 
                           option_type: str = 'call') -> Dict[str, float]:
        """Calculate all Greeks for an option"""
        if option_type.lower() == 'call':
            delta = BlackScholesCalculator.calculate_call_delta(S, K, T, r, sigma)
            theta = BlackScholesCalculator.calculate_theta_call(S, K, T, r, sigma)
        else:
            delta = BlackScholesCalculator.calculate_put_delta(S, K, T, r, sigma)
            theta = BlackScholesCalculator.calculate_theta_put(S, K, T, r, sigma)
        
        return {
            'delta': delta,
            'gamma': BlackScholesCalculator.calculate_gamma(S, K, T, r, sigma),
            'vega': BlackScholesCalculator.calculate_vega(S, K, T, r, sigma),
            'theta': theta,
            'vanna': BlackScholesCalculator.calculate_vanna(S, K, T, r, sigma),
            'charm': BlackScholesCalculator.calculate_charm(S, K, T, r, sigma)
        }
