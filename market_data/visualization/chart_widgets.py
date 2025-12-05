"""
Chart widgets for visualizing curve data using matplotlib and PyQt
"""

import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from config.theme import ThemeConfig

class ChartWidget(QWidget):
    """Base widget for matplotlib charts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = ThemeConfig()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        self.figure = Figure(figsize=(10, 6), facecolor=self.theme.PRIMARY_DARK)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def clear(self):
        """Clear the current chart"""
        self.figure.clear()
        self.canvas.draw()

class CurveLineChart(ChartWidget):
    """Line chart for displaying curve data"""
    
    def plot_curves(self, df: pd.DataFrame, curve_ids: List[str] = None, 
                   title: str = "Yield Curves"):
        """
        Plot multiple curves on the same chart
        
        Args:
            df: DataFrame containing curve data
            curve_ids: List of curve IDs to plot (None = all)
            title: Chart title
        """
        self.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.theme.PRIMARY_LIGHT)
        
        if curve_ids is None:
            curve_ids = df['curve_id'].unique() if 'curve_id' in df.columns else []
        
        for i, curve_id in enumerate(curve_ids):
            curve_data = df[df['curve_id'] == curve_id].sort_values('tenor_days')
            if not curve_data.empty:
                color = self.theme.CHART_COLORS[i % len(self.theme.CHART_COLORS)]
                ax.plot(curve_data['tenor_days'], curve_data['rate'] * 10000, 
                       label=curve_id[:30], color=color, linewidth=2, marker='o', markersize=4)
        
        ax.set_xlabel('Tenor (Days)', color=self.theme.TEXT_PRIMARY)
        ax.set_ylabel('Rate (bps)', color=self.theme.TEXT_PRIMARY)
        ax.set_title(title, color=self.theme.TEXT_PRIMARY, fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Style the axes
        ax.tick_params(colors=self.theme.TEXT_SECONDARY)
        ax.spines['bottom'].set_color(self.theme.TEXT_MUTED)
        ax.spines['top'].set_color(self.theme.TEXT_MUTED)
        ax.spines['right'].set_color(self.theme.TEXT_MUTED)
        ax.spines['left'].set_color(self.theme.TEXT_MUTED)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_curve_comparison(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                            curve_id: str, labels: Tuple[str, str] = ('Day 1', 'Day 2')):
        """
        Plot comparison of the same curve across two days
        
        Args:
            df1: DataFrame for day 1
            df2: DataFrame for day 2
            curve_id: ID of curve to compare
            labels: Labels for the two days
        """
        self.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.theme.PRIMARY_LIGHT)
        
        # Plot day 1
        curve1 = df1[df1['curve_id'] == curve_id].sort_values('tenor_days')
        if not curve1.empty:
            ax.plot(curve1['tenor_days'], curve1['rate'] * 10000, 
                   label=labels[0], color=self.theme.ACCENT_BLUE, 
                   linewidth=2, marker='o', markersize=4)
        
        # Plot day 2
        curve2 = df2[df2['curve_id'] == curve_id].sort_values('tenor_days')
        if not curve2.empty:
            ax.plot(curve2['tenor_days'], curve2['rate'] * 10000, 
                   label=labels[1], color=self.theme.ACCENT_GREEN, 
                   linewidth=2, marker='s', markersize=4)
        
        ax.set_xlabel('Tenor (Days)', color=self.theme.TEXT_PRIMARY)
        ax.set_ylabel('Rate (bps)', color=self.theme.TEXT_PRIMARY)
        ax.set_title(f'Curve Comparison: {curve_id[:50]}', 
                    color=self.theme.TEXT_PRIMARY, fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Style the axes
        ax.tick_params(colors=self.theme.TEXT_SECONDARY)
        for spine in ax.spines.values():
            spine.set_color(self.theme.TEXT_MUTED)
        
        self.figure.tight_layout()
        self.canvas.draw()

class BasisPointMoveChart(ChartWidget):
    """Chart for displaying basis point movements"""
    
    def plot_bp_moves(self, df: pd.DataFrame, curve_id: str = None):
        """
        Plot basis point moves as a bar chart
        
        Args:
            df: DataFrame with basis point moves
            curve_id: Optional specific curve ID to plot
        """
        self.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.theme.PRIMARY_LIGHT)
        
        if curve_id:
            plot_data = df[df['curve_id'] == curve_id].sort_values('tenor_days')
            title = f'Basis Point Moves: {curve_id[:50]}'
        else:
            plot_data = df.sort_values('tenor_days')
            title = 'Basis Point Moves by Tenor'
        
        if plot_data.empty:
            return
        
        # Create bar chart
        x_pos = np.arange(len(plot_data))
        colors = [self.theme.ACCENT_GREEN if bp >= 0 else self.theme.ACCENT_RED 
                 for bp in plot_data['bp_move']]
        
        bars = ax.bar(x_pos, plot_data['bp_move'], color=colors, alpha=0.8)
        
        # Add value labels on bars
        for bar, value in zip(bars, plot_data['bp_move']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}', ha='center', va='bottom' if height >= 0 else 'top',
                   color=self.theme.TEXT_SECONDARY, fontsize=9)
        
        ax.set_xlabel('Tenor', color=self.theme.TEXT_PRIMARY)
        ax.set_ylabel('Basis Points Move', color=self.theme.TEXT_PRIMARY)
        ax.set_title(title, color=self.theme.TEXT_PRIMARY, fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels([f'{int(t)}d' for t in plot_data['tenor_days']], rotation=45)
        ax.axhline(y=0, color=self.theme.TEXT_MUTED, linestyle='-', linewidth=0.5)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Style the axes
        ax.tick_params(colors=self.theme.TEXT_SECONDARY)
        for spine in ax.spines.values():
            spine.set_color(self.theme.TEXT_MUTED)
        
        self.figure.tight_layout()
        self.canvas.draw()

class HeatmapChart(ChartWidget):
    """Heatmap chart for visualizing curve movements across tenors and curves"""
    
    def plot_movement_heatmap(self, df: pd.DataFrame):
        """
        Plot a heatmap of curve movements
        
        Args:
            df: DataFrame with basis point moves
        """
        self.clear()
        ax = self.figure.add_subplot(111)
        
        # Pivot data for heatmap
        if 'curve_id' in df.columns and 'tenor_days' in df.columns and 'bp_move' in df.columns:
            pivot_data = df.pivot_table(values='bp_move', 
                                       index='curve_id', 
                                       columns='tenor_days', 
                                       aggfunc='mean')
            
            if not pivot_data.empty:
                # Create heatmap
                im = ax.imshow(pivot_data.values, cmap='RdYlGn', aspect='auto', 
                             vmin=-50, vmax=50)
                
                # Set ticks and labels
                ax.set_xticks(np.arange(len(pivot_data.columns)))
                ax.set_yticks(np.arange(len(pivot_data.index)))
                ax.set_xticklabels([f'{int(t)}d' for t in pivot_data.columns], rotation=45)
                ax.set_yticklabels([str(idx)[:30] for idx in pivot_data.index])
                
                # Add colorbar
                cbar = self.figure.colorbar(im, ax=ax)
                cbar.set_label('Basis Points Move', color=self.theme.TEXT_PRIMARY)
                cbar.ax.tick_params(colors=self.theme.TEXT_SECONDARY)
                
                ax.set_xlabel('Tenor (Days)', color=self.theme.TEXT_PRIMARY)
                ax.set_ylabel('Curve ID', color=self.theme.TEXT_PRIMARY)
                ax.set_title('Curve Movement Heatmap', 
                           color=self.theme.TEXT_PRIMARY, fontsize=14, fontweight='bold')
                
                # Style the axes
                ax.tick_params(colors=self.theme.TEXT_SECONDARY)
                
        self.figure.tight_layout()
        self.canvas.draw()

class HistoricalTrendChart(ChartWidget):
    """Chart for displaying historical trends"""
    
    def plot_rate_distribution(self, df: pd.DataFrame, curve_id: str = None):
        """
        Plot distribution of rates or rate changes
        
        Args:
            df: DataFrame containing rate data
            curve_id: Optional specific curve ID
        """
        self.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.theme.PRIMARY_LIGHT)
        
        if curve_id and 'curve_id' in df.columns:
            plot_data = df[df['curve_id'] == curve_id]['rate']
            title = f'Rate Distribution: {curve_id[:50]}'
        else:
            plot_data = df['rate'] if 'rate' in df.columns else pd.Series()
            title = 'Rate Distribution'
        
        if not plot_data.empty:
            # Convert to basis points
            plot_data = plot_data * 10000
            
            # Create histogram
            n, bins, patches = ax.hist(plot_data, bins=30, 
                                      color=self.theme.ACCENT_BLUE, 
                                      alpha=0.7, edgecolor='black')
            
            # Add statistics
            mean = plot_data.mean()
            std = plot_data.std()
            ax.axvline(mean, color=self.theme.ACCENT_GREEN, linestyle='--', 
                      linewidth=2, label=f'Mean: {mean:.2f} bps')
            ax.axvline(mean + std, color=self.theme.ACCENT_YELLOW, linestyle=':', 
                      linewidth=1, label=f'±1 Std: {std:.2f} bps')
            ax.axvline(mean - std, color=self.theme.ACCENT_YELLOW, linestyle=':', 
                      linewidth=1)
            
            ax.set_xlabel('Rate (bps)', color=self.theme.TEXT_PRIMARY)
            ax.set_ylabel('Frequency', color=self.theme.TEXT_PRIMARY)
            ax.set_title(title, color=self.theme.TEXT_PRIMARY, fontsize=14, fontweight='bold')
            ax.legend(loc='best', framealpha=0.9)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Style the axes
            ax.tick_params(colors=self.theme.TEXT_SECONDARY)
            for spine in ax.spines.values():
                spine.set_color(self.theme.TEXT_MUTED)
        
        self.figure.tight_layout()
        self.canvas.draw()