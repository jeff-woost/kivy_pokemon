"""
Inception-to-date backtesting engine for Pokemon cards
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging


class BacktestingEngine:
    """Engine for backtesting Pokemon card investments from inception to date"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_inception_to_date(self, price_history: List[Dict]) -> Dict:
        """
        Analyze card performance from inception to current date
        
        Args:
            price_history: List of price data points sorted by date
            
        Returns:
            Dictionary with backtesting metrics
        """
        if not price_history:
            return self._get_empty_results()
            
        # Convert to DataFrame
        df = pd.DataFrame(price_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate metrics
        metrics = {
            'inception_date': df['date'].min(),
            'current_date': df['date'].max(),
            'days_tracked': (df['date'].max() - df['date'].min()).days,
            
            # Price statistics
            'mean_price': float(df['price'].mean()),
            'median_price': float(df['price'].median()),
            'std_dev': float(df['price'].std()),
            'min_price': float(df['price'].min()),
            'max_price': float(df['price'].max()),
            'current_price': float(df['price'].iloc[-1]),
            
            # Performance metrics
            'total_return_pct': self._calculate_total_return(df),
            'annualized_return_pct': self._calculate_annualized_return(df),
            'volatility': self._calculate_volatility(df),
            'sharpe_ratio': self._calculate_sharpe_ratio(df),
            
            # Trend analysis
            'trend': self._analyze_trend(df),
            'momentum': self._calculate_momentum(df),
            
            # Price levels
            'support_level': self._find_support_level(df),
            'resistance_level': self._find_resistance_level(df),
            
            # Statistical bands
            'upper_band': float(df['price'].mean() + df['price'].std()),
            'lower_band': float(df['price'].mean() - df['price'].std()),
        }
        
        # Add confidence intervals
        metrics['confidence_95'] = self._calculate_confidence_interval(df, 0.95)
        
        return metrics
        
    def _calculate_total_return(self, df: pd.DataFrame) -> float:
        """Calculate total return percentage"""
        if len(df) < 2:
            return 0.0
        first_price = df['price'].iloc[0]
        last_price = df['price'].iloc[-1]
        return ((last_price - first_price) / first_price) * 100
        
    def _calculate_annualized_return(self, df: pd.DataFrame) -> float:
        """Calculate annualized return percentage"""
        if len(df) < 2:
            return 0.0
            
        days = (df['date'].max() - df['date'].min()).days
        if days == 0:
            return 0.0
            
        years = days / 365.25
        total_return = self._calculate_total_return(df) / 100
        
        if years > 0:
            annualized = (1 + total_return) ** (1 / years) - 1
            return annualized * 100
        return 0.0
        
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate price volatility (coefficient of variation)"""
        mean = df['price'].mean()
        std = df['price'].std()
        if mean > 0:
            return (std / mean) * 100
        return 0.0
        
    def _calculate_sharpe_ratio(self, df: pd.DataFrame, risk_free_rate: float = 0.03) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            df: Price DataFrame
            risk_free_rate: Annual risk-free rate (default 3%)
        """
        if len(df) < 2:
            return 0.0
            
        # Calculate returns
        returns = df['price'].pct_change().dropna()
        
        if len(returns) == 0:
            return 0.0
            
        # Annualize metrics
        mean_return = returns.mean() * 252  # Assuming daily-like data
        std_return = returns.std() * np.sqrt(252)
        
        if std_return > 0:
            return (mean_return - risk_free_rate) / std_return
        return 0.0
        
    def _analyze_trend(self, df: pd.DataFrame) -> str:
        """Analyze overall price trend"""
        if len(df) < 10:
            return 'insufficient_data'
            
        # Use linear regression on recent data
        recent_df = df.tail(30)
        X = np.arange(len(recent_df)).reshape(-1, 1)
        y = recent_df['price'].values
        
        # Calculate slope
        slope = np.polyfit(X.flatten(), y, 1)[0]
        
        # Normalize slope by average price
        avg_price = df['price'].mean()
        normalized_slope = (slope / avg_price) * 100 if avg_price > 0 else 0
        
        if normalized_slope > 2:
            return 'strong_upward'
        elif normalized_slope > 0.5:
            return 'upward'
        elif normalized_slope > -0.5:
            return 'stable'
        elif normalized_slope > -2:
            return 'downward'
        else:
            return 'strong_downward'
            
    def _calculate_momentum(self, df: pd.DataFrame) -> float:
        """Calculate price momentum (30-day rate of change)"""
        if len(df) < 30:
            return 0.0
            
        recent_price = df['price'].iloc[-1]
        old_price = df['price'].iloc[-30]
        
        return ((recent_price - old_price) / old_price) * 100 if old_price > 0 else 0.0
        
    def _find_support_level(self, df: pd.DataFrame) -> float:
        """Find support price level (25th percentile)"""
        return float(df['price'].quantile(0.25))
        
    def _find_resistance_level(self, df: pd.DataFrame) -> float:
        """Find resistance price level (75th percentile)"""
        return float(df['price'].quantile(0.75))
        
    def _calculate_confidence_interval(self, df: pd.DataFrame, confidence: float) -> Tuple[float, float]:
        """Calculate confidence interval for price"""
        mean = df['price'].mean()
        std = df['price'].std()
        
        # Z-score for 95% confidence
        z = 1.96 if confidence == 0.95 else 2.58
        
        margin = z * std
        return (float(mean - margin), float(mean + margin))
        
    def generate_historical_signals(self, price_history: List[Dict]) -> List[Dict]:
        """
        Generate BUY/SELL/HOLD signals for historical prices
        
        Args:
            price_history: List of price data points
            
        Returns:
            List of signals with dates and recommendations
        """
        if not price_history:
            return []
            
        df = pd.DataFrame(price_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        signals = []
        
        # Calculate rolling statistics
        df['ma_30'] = df['price'].rolling(window=30, min_periods=1).mean()
        df['std_30'] = df['price'].rolling(window=30, min_periods=1).std()
        
        for idx, row in df.iterrows():
            if idx < 30:  # Need enough data
                continue
                
            price = row['price']
            mean = row['ma_30']
            std = row['std_30']
            
            # Generate signal based on standard deviations from mean
            if price < mean - std:
                signal = 'BUY'
                confidence = min(((mean - price) / std) * 100, 100)
            elif price > mean + std:
                signal = 'SELL'
                confidence = min(((price - mean) / std) * 100, 100)
            else:
                signal = 'HOLD'
                confidence = 50 + abs(price - mean) / std * 25
                
            signals.append({
                'date': row['date'],
                'price': price,
                'signal': signal,
                'confidence': confidence,
                'mean_price': mean,
                'std_dev': std
            })
            
        return signals
        
    def _get_empty_results(self) -> Dict:
        """Return empty results structure"""
        return {
            'inception_date': None,
            'current_date': None,
            'days_tracked': 0,
            'mean_price': 0.0,
            'median_price': 0.0,
            'std_dev': 0.0,
            'min_price': 0.0,
            'max_price': 0.0,
            'current_price': 0.0,
            'total_return_pct': 0.0,
            'annualized_return_pct': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'trend': 'no_data',
            'momentum': 0.0,
            'support_level': 0.0,
            'resistance_level': 0.0,
            'upper_band': 0.0,
            'lower_band': 0.0,
            'confidence_95': (0.0, 0.0)
        }
