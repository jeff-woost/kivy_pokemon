"""
Enhanced chart widgets for price visualization
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging


class PriceChartWidget(QWidget):
    """Enhanced price chart widget with mean/std dev bands"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the chart UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 6), facecolor='#2d2d2d')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(self.canvas)
        
        # Configure matplotlib style
        plt.style.use('dark_background')
        
    def plot_price_history_with_bands(
        self, 
        price_history: List[Dict],
        mean_price: float,
        std_dev: float,
        card_name: str = "Pokemon Card"
    ):
        """
        Plot price history with mean and standard deviation bands
        
        Args:
            price_history: List of price data dictionaries
            mean_price: Mean price
            std_dev: Standard deviation
            card_name: Name of the card
        """
        if not price_history:
            self.logger.warning("No price history to plot")
            return
            
        # Convert to DataFrame
        df = pd.DataFrame(price_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Separate graded and ungraded
        graded_df = df[df['graded'] == True]
        ungraded_df = df[df['graded'] == False]
        
        # Clear previous plot
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#2d2d2d')
        
        # Plot ungraded prices
        if not ungraded_df.empty:
            ax.scatter(ungraded_df['date'], ungraded_df['price'], 
                      c='#42a5f5', alpha=0.6, s=30, label='Ungraded', zorder=3)
                      
        # Plot graded prices
        if not graded_df.empty:
            ax.scatter(graded_df['date'], graded_df['price'], 
                      c='#ffa726', alpha=0.6, s=30, label='Graded (PSA 10)', zorder=3)
        
        # Plot moving average
        if len(df) > 7:
            df_sorted = df.sort_values('date')
            ma_7 = df_sorted['price'].rolling(window=7, min_periods=1).mean()
            ax.plot(df_sorted['date'], ma_7, 'g--', linewidth=2, 
                   label='7-Day MA', alpha=0.7, zorder=2)
        
        # Plot mean price line
        ax.axhline(y=mean_price, color='#00ff00', linestyle='-', 
                  linewidth=2, label=f'Mean: ${mean_price:.2f}', zorder=1)
        
        # Plot standard deviation bands
        upper_band = mean_price + std_dev
        lower_band = mean_price - std_dev
        
        ax.axhline(y=upper_band, color='#ff5252', linestyle='--', 
                  linewidth=1.5, label=f'+1 SD: ${upper_band:.2f}', alpha=0.7, zorder=1)
        ax.axhline(y=lower_band, color='#ff5252', linestyle='--', 
                  linewidth=1.5, label=f'-1 SD: ${lower_band:.2f}', alpha=0.7, zorder=1)
        
        # Fill between std dev bands
        date_range = pd.date_range(df['date'].min(), df['date'].max(), periods=100)
        ax.fill_between(date_range, lower_band, upper_band, 
                       color='#ff5252', alpha=0.1, zorder=0)
        
        # Formatting
        ax.set_xlabel('Date', fontsize=11, color='white')
        ax.set_ylabel('Price ($)', fontsize=11, color='white')
        ax.set_title(f'Price History - {card_name}', fontsize=14, fontweight='bold', color='white')
        ax.grid(True, alpha=0.2, color='white')
        ax.legend(loc='upper left', framealpha=0.9, facecolor='#3a3a3a', edgecolor='white')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.figure.autofmt_xdate()
        
        # Style the axes
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(colors='white')
        
        self.canvas.draw()
        
    def plot_graded_vs_ungraded_comparison(
        self,
        price_history: List[Dict],
        card_name: str = "Pokemon Card"
    ):
        """
        Plot comparison between graded and ungraded prices over time
        
        Args:
            price_history: List of price data dictionaries
            card_name: Name of the card
        """
        if not price_history:
            return
            
        df = pd.DataFrame(price_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Separate graded and ungraded
        graded_df = df[df['graded'] == True].copy()
        ungraded_df = df[df['graded'] == False].copy()
        
        if graded_df.empty or ungraded_df.empty:
            self.logger.warning("Insufficient data for graded vs ungraded comparison")
            return
        
        # Clear previous plot
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#2d2d2d')
        
        # Calculate rolling averages
        window = 7
        
        if len(ungraded_df) >= window:
            ungraded_ma = ungraded_df.set_index('date')['price'].rolling(window=window).mean()
            ax.plot(ungraded_ma.index, ungraded_ma.values, 
                   color='#42a5f5', linewidth=2, label='Ungraded MA')
        
        if len(graded_df) >= window:
            graded_ma = graded_df.set_index('date')['price'].rolling(window=window).mean()
            ax.plot(graded_ma.index, graded_ma.values, 
                   color='#ffa726', linewidth=2, label='Graded (PSA 10) MA')
        
        # Calculate and display multiplier
        if not graded_df.empty and not ungraded_df.empty:
            avg_graded = graded_df['price'].mean()
            avg_ungraded = ungraded_df['price'].mean()
            multiplier = avg_graded / avg_ungraded if avg_ungraded > 0 else 0
            
            # Add text annotation
            ax.text(0.02, 0.98, f'Avg Multiplier: {multiplier:.2f}x', 
                   transform=ax.transAxes, fontsize=12, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='#3a3a3a', alpha=0.8),
                   color='white')
        
        # Formatting
        ax.set_xlabel('Date', fontsize=11, color='white')
        ax.set_ylabel('Price ($)', fontsize=11, color='white')
        ax.set_title(f'Graded vs Ungraded Price Comparison - {card_name}', 
                    fontsize=14, fontweight='bold', color='white')
        ax.grid(True, alpha=0.2, color='white')
        ax.legend(loc='upper left', framealpha=0.9, facecolor='#3a3a3a', edgecolor='white')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.figure.autofmt_xdate()
        
        # Style the axes
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(colors='white')
        
        self.canvas.draw()
        
    def plot_signals_overlay(
        self,
        price_history: List[Dict],
        signals: List[Dict],
        card_name: str = "Pokemon Card"
    ):
        """
        Plot price history with BUY/SELL/HOLD signals overlaid
        
        Args:
            price_history: List of price data dictionaries
            signals: List of signal dictionaries
            card_name: Name of the card
        """
        if not price_history or not signals:
            return
            
        # Convert to DataFrames
        df = pd.DataFrame(price_history)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        signals_df = pd.DataFrame(signals)
        signals_df['date'] = pd.to_datetime(signals_df['date'])
        
        # Clear previous plot
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#2d2d2d')
        
        # Plot price line
        ax.plot(df['date'], df['price'], 'b-', linewidth=2, label='Price', alpha=0.7)
        
        # Overlay signals
        buy_signals = signals_df[signals_df['signal'] == 'BUY']
        sell_signals = signals_df[signals_df['signal'] == 'SELL']
        hold_signals = signals_df[signals_df['signal'] == 'HOLD']
        
        if not buy_signals.empty:
            ax.scatter(buy_signals['date'], buy_signals['price'], 
                      c='green', marker='^', s=100, label='BUY', zorder=5, edgecolors='white')
        
        if not sell_signals.empty:
            ax.scatter(sell_signals['date'], sell_signals['price'], 
                      c='red', marker='v', s=100, label='SELL', zorder=5, edgecolors='white')
        
        # Formatting
        ax.set_xlabel('Date', fontsize=11, color='white')
        ax.set_ylabel('Price ($)', fontsize=11, color='white')
        ax.set_title(f'Price History with Trading Signals - {card_name}', 
                    fontsize=14, fontweight='bold', color='white')
        ax.grid(True, alpha=0.2, color='white')
        ax.legend(loc='upper left', framealpha=0.9, facecolor='#3a3a3a', edgecolor='white')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.figure.autofmt_xdate()
        
        # Style the axes
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(colors='white')
        
        self.canvas.draw()
