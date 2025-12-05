"""
BUY/SELL/HOLD signal generator
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
import logging


class SignalGenerator:
    """Generates BUY/SELL/HOLD signals based on statistical analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate_signal(
        self, 
        current_price: float, 
        mean_price: float, 
        std_dev: float,
        trend: str = 'stable'
    ) -> Dict:
        """
        Generate trading signal based on statistical analysis
        
        Args:
            current_price: Current market price
            mean_price: Historical mean price
            std_dev: Standard deviation of prices
            trend: Current trend direction
            
        Returns:
            Dictionary with signal and confidence
        """
        # Calculate z-score (how many standard deviations from mean)
        z_score = (current_price - mean_price) / std_dev if std_dev > 0 else 0
        
        # Generate signal based on z-score
        if z_score < -1.0:
            # Price is more than 1 std dev below mean - BUY
            signal = 'BUY'
            confidence = min(abs(z_score) * 50, 100)
            reason = f"Price is {abs(z_score):.2f} standard deviations below mean"
        elif z_score > 1.0:
            # Price is more than 1 std dev above mean - SELL
            signal = 'SELL'
            confidence = min(abs(z_score) * 50, 100)
            reason = f"Price is {z_score:.2f} standard deviations above mean"
        else:
            # Price is within 1 std dev of mean - HOLD
            signal = 'HOLD'
            confidence = 50 + abs(z_score) * 25
            reason = f"Price is near mean ({abs(z_score):.2f} std dev)"
            
        # Adjust based on trend
        if trend == 'strong_upward' and signal == 'BUY':
            confidence = min(confidence * 1.2, 100)
            reason += " + strong upward trend"
        elif trend == 'strong_downward' and signal == 'SELL':
            confidence = min(confidence * 1.2, 100)
            reason += " + strong downward trend"
        elif trend == 'strong_upward' and signal == 'SELL':
            confidence *= 0.8
            reason += " but strong upward trend (caution)"
        elif trend == 'strong_downward' and signal == 'BUY':
            confidence *= 0.8
            reason += " but strong downward trend (caution)"
            
        return {
            'signal': signal,
            'confidence': round(confidence, 1),
            'z_score': round(z_score, 2),
            'reason': reason,
            'current_price': current_price,
            'mean_price': mean_price,
            'std_dev': std_dev,
            'trend': trend
        }
        
    def generate_signals_at_price_points(
        self, 
        mean_price: float, 
        std_dev: float, 
        trend: str = 'stable',
        num_points: int = 10
    ) -> List[Dict]:
        """
        Generate signals at various price points around current price
        
        Args:
            mean_price: Historical mean price
            std_dev: Standard deviation
            trend: Current trend
            num_points: Number of price points to evaluate
            
        Returns:
            List of signals at different price points
        """
        signals = []
        
        # Generate price points from -2 std dev to +2 std dev
        min_price = max(mean_price - 2 * std_dev, 0)
        max_price = mean_price + 2 * std_dev
        
        price_points = np.linspace(min_price, max_price, num_points)
        
        for price in price_points:
            signal = self.generate_signal(price, mean_price, std_dev, trend)
            signal['price_point'] = round(price, 2)
            signals.append(signal)
            
        return signals
        
    def generate_alert(
        self,
        previous_signal: str,
        current_signal: str,
        card_name: str,
        current_price: float
    ) -> Dict:
        """
        Generate alert if signal has changed
        
        Args:
            previous_signal: Previous signal (BUY/SELL/HOLD)
            current_signal: Current signal
            card_name: Name of the card
            current_price: Current price
            
        Returns:
            Alert dictionary or None if no alert
        """
        if previous_signal == current_signal:
            return None
            
        # Generate alert for signal changes
        alert_priority = 'low'
        
        if previous_signal == 'HOLD' and current_signal == 'BUY':
            alert_priority = 'high'
            message = f"BUY opportunity detected for {card_name} at ${current_price:.2f}"
        elif previous_signal == 'BUY' and current_signal == 'SELL':
            alert_priority = 'high'
            message = f"Consider selling {card_name} at ${current_price:.2f}"
        elif previous_signal == 'SELL' and current_signal == 'BUY':
            alert_priority = 'medium'
            message = f"Price has dropped - BUY signal for {card_name} at ${current_price:.2f}"
        elif previous_signal == 'HOLD' and current_signal == 'SELL':
            alert_priority = 'medium'
            message = f"Price rising - consider selling {card_name} at ${current_price:.2f}"
        else:
            alert_priority = 'low'
            message = f"Signal changed from {previous_signal} to {current_signal} for {card_name}"
            
        return {
            'card_name': card_name,
            'previous_signal': previous_signal,
            'current_signal': current_signal,
            'price': current_price,
            'priority': alert_priority,
            'message': message,
            'timestamp': datetime.now()
        }
        
    def analyze_entry_exit_points(
        self, 
        price_history: List[Dict],
        investment_amount: float = 1000.0
    ) -> Dict:
        """
        Backtest entry and exit points based on signals
        
        Args:
            price_history: Historical price data
            investment_amount: Amount to invest
            
        Returns:
            Dictionary with backtesting results
        """
        if not price_history:
            return {'success': False, 'reason': 'No price history'}
            
        df = pd.DataFrame(price_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate rolling statistics
        df['ma_30'] = df['price'].rolling(window=30, min_periods=1).mean()
        df['std_30'] = df['price'].rolling(window=30, min_periods=1).std()
        
        # Track trades
        trades = []
        position = None  # Current position (buy price)
        shares = 0
        cash = investment_amount
        
        for idx, row in df.iterrows():
            if idx < 30:  # Need enough data
                continue
                
            price = row['price']
            mean = row['ma_30']
            std = row['std_30']
            
            signal = self.generate_signal(price, mean, std)
            
            # Execute trades based on signals
            if signal['signal'] == 'BUY' and position is None and cash >= price:
                # Buy
                shares = cash / price
                position = price
                cash = 0
                trades.append({
                    'date': row['date'],
                    'type': 'BUY',
                    'price': price,
                    'shares': shares,
                    'signal_confidence': signal['confidence']
                })
            elif signal['signal'] == 'SELL' and position is not None:
                # Sell
                cash = shares * price
                profit = cash - investment_amount
                trades.append({
                    'date': row['date'],
                    'type': 'SELL',
                    'price': price,
                    'shares': shares,
                    'profit': profit,
                    'return_pct': (profit / investment_amount) * 100,
                    'signal_confidence': signal['confidence']
                })
                position = None
                shares = 0
                
        # Calculate final value
        if position is not None:
            # Still holding position
            final_value = shares * df['price'].iloc[-1]
        else:
            final_value = cash
            
        total_return = ((final_value - investment_amount) / investment_amount) * 100
        
        # Count successful trades
        profitable_trades = len([t for t in trades if t.get('profit', 0) > 0])
        total_trades = len([t for t in trades if t['type'] == 'SELL'])
        
        return {
            'success': True,
            'initial_investment': investment_amount,
            'final_value': final_value,
            'total_return_pct': total_return,
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': (profitable_trades / total_trades * 100) if total_trades > 0 else 0,
            'trades': trades,
            'currently_holding': position is not None
        }
