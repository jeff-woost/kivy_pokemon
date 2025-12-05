"""
Backtesting results tab UI
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QTextEdit, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import Dict, List
import logging


class BacktestingTab(QWidget):
    """Tab for displaying backtesting results"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Inception-to-Date Backtesting")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Time period selector
        period_label = QLabel("Analysis Period:")
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "All Time (Inception to Date)",
            "Last 5 Years",
            "Last 3 Years",
            "Last Year",
            "Last 6 Months"
        ])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        
        header_layout.addWidget(period_label)
        header_layout.addWidget(self.period_combo)
        
        layout.addLayout(header_layout)
        
        # Performance Summary Cards
        summary_layout = QHBoxLayout()
        
        self.inception_card = self.create_summary_card("Inception Date", "N/A")
        self.total_return_card = self.create_summary_card("Total Return", "0%")
        self.annual_return_card = self.create_summary_card("Annualized Return", "0%")
        self.sharpe_card = self.create_summary_card("Sharpe Ratio", "0.00")
        
        summary_layout.addWidget(self.inception_card)
        summary_layout.addWidget(self.total_return_card)
        summary_layout.addWidget(self.annual_return_card)
        summary_layout.addWidget(self.sharpe_card)
        
        layout.addLayout(summary_layout)
        
        # Metrics Table
        metrics_label = QLabel("Historical Performance Metrics:")
        metrics_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(metrics_label)
        
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.metrics_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.metrics_table.setMaximumHeight(300)
        layout.addWidget(self.metrics_table)
        
        # Signal History Table
        signals_label = QLabel("Historical BUY/SELL/HOLD Signals:")
        signals_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(signals_label)
        
        self.signals_table = QTableWidget()
        self.signals_table.setColumnCount(5)
        self.signals_table.setHorizontalHeaderLabels([
            "Date", "Price", "Signal", "Confidence %", "Reason"
        ])
        self.signals_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.signals_table.setAlternatingRowColors(True)
        layout.addWidget(self.signals_table)
        
        # Trading Strategy Results
        strategy_label = QLabel("Backtested Trading Strategy:")
        strategy_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(strategy_label)
        
        self.strategy_text = QTextEdit()
        self.strategy_text.setReadOnly(True)
        self.strategy_text.setMaximumHeight(150)
        layout.addWidget(self.strategy_text)
        
    def create_summary_card(self, title: str, value: str) -> QWidget:
        """Create a summary card widget"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #3a3a3a;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: #888888;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        value_label.setObjectName(f"{title}_value")
        layout.addWidget(value_label)
        
        return widget
        
    def load_backtesting_results(self, metrics: Dict, signals: List[Dict], strategy_results: Dict = None):
        """
        Load backtesting results into the UI
        
        Args:
            metrics: Backtesting metrics dictionary
            signals: List of historical signals
            strategy_results: Trading strategy backtest results
        """
        # Update summary cards
        self.update_summary_card(self.inception_card, 
                                str(metrics.get('inception_date', 'N/A'))[:10])
        
        total_return = metrics.get('total_return_pct', 0)
        self.update_summary_card(self.total_return_card, 
                                f"{total_return:+.1f}%",
                                total_return > 0)
        
        annual_return = metrics.get('annualized_return_pct', 0)
        self.update_summary_card(self.annual_return_card, 
                                f"{annual_return:+.1f}%",
                                annual_return > 0)
        
        sharpe = metrics.get('sharpe_ratio', 0)
        self.update_summary_card(self.sharpe_card, f"{sharpe:.2f}")
        
        # Populate metrics table
        metrics_data = [
            ("Current Price", f"${metrics.get('current_price', 0):.2f}"),
            ("Mean Price (All Time)", f"${metrics.get('mean_price', 0):.2f}"),
            ("Median Price", f"${metrics.get('median_price', 0):.2f}"),
            ("Standard Deviation", f"${metrics.get('std_dev', 0):.2f}"),
            ("Min Price", f"${metrics.get('min_price', 0):.2f}"),
            ("Max Price", f"${metrics.get('max_price', 0):.2f}"),
            ("Price Volatility", f"{metrics.get('volatility', 0):.1f}%"),
            ("Momentum (30-day)", f"{metrics.get('momentum', 0):+.1f}%"),
            ("Trend", metrics.get('trend', 'N/A').replace('_', ' ').title()),
            ("Support Level", f"${metrics.get('support_level', 0):.2f}"),
            ("Resistance Level", f"${metrics.get('resistance_level', 0):.2f}"),
            ("Days Tracked", str(metrics.get('days_tracked', 0))),
        ]
        
        self.metrics_table.setRowCount(len(metrics_data))
        for i, (metric, value) in enumerate(metrics_data):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(metric))
            value_item = QTableWidgetItem(value)
            
            # Color code some values
            if "%" in value and value.startswith("+"):
                value_item.setForeground(QColor(76, 175, 80))
            elif "%" in value and value.startswith("-"):
                value_item.setForeground(QColor(244, 67, 54))
                
            self.metrics_table.setItem(i, 1, value_item)
            
        # Populate signals table (show last 50 signals)
        recent_signals = signals[-50:] if len(signals) > 50 else signals
        self.signals_table.setRowCount(len(recent_signals))
        
        for i, signal in enumerate(recent_signals):
            # Date
            date_str = str(signal.get('date', 'N/A'))[:10]
            self.signals_table.setItem(i, 0, QTableWidgetItem(date_str))
            
            # Price
            price = signal.get('price', 0)
            self.signals_table.setItem(i, 1, QTableWidgetItem(f"${price:.2f}"))
            
            # Signal
            signal_type = signal.get('signal', 'HOLD')
            signal_item = QTableWidgetItem(signal_type)
            
            if signal_type == 'BUY':
                signal_item.setBackground(QColor(76, 175, 80, 100))
            elif signal_type == 'SELL':
                signal_item.setBackground(QColor(244, 67, 54, 100))
            else:  # HOLD
                signal_item.setBackground(QColor(255, 193, 7, 100))
                
            self.signals_table.setItem(i, 2, signal_item)
            
            # Confidence
            confidence = signal.get('confidence', 0)
            self.signals_table.setItem(i, 3, QTableWidgetItem(f"{confidence:.1f}%"))
            
            # Reason (truncated)
            reason = signal.get('reason', 'N/A')
            if len(reason) > 50:
                reason = reason[:47] + "..."
            self.signals_table.setItem(i, 4, QTableWidgetItem(reason))
            
        # Update strategy results
        if strategy_results and strategy_results.get('success'):
            strategy_text = f"""
Trading Strategy Backtest Results:

Initial Investment: ${strategy_results.get('initial_investment', 0):,.2f}
Final Value: ${strategy_results.get('final_value', 0):,.2f}
Total Return: {strategy_results.get('total_return_pct', 0):+.2f}%

Total Trades: {strategy_results.get('total_trades', 0)}
Profitable Trades: {strategy_results.get('profitable_trades', 0)}
Win Rate: {strategy_results.get('win_rate', 0):.1f}%

Currently Holding: {'Yes' if strategy_results.get('currently_holding') else 'No'}

Strategy: Buy when price is > 1 std dev below mean, Sell when price is > 1 std dev above mean
            """
            self.strategy_text.setText(strategy_text.strip())
        else:
            self.strategy_text.setText("No strategy results available")
            
    def update_summary_card(self, card: QWidget, value: str, positive: bool = None):
        """Update a summary card value"""
        value_label = card.findChild(QLabel, lambda w: w.font().pointSize() == 16)
        if value_label:
            value_label.setText(value)
            
            if positive is not None:
                if positive:
                    value_label.setStyleSheet("color: #4caf50;")
                else:
                    value_label.setStyleSheet("color: #f44336;")
                    
    def on_period_changed(self, period: str):
        """Handle period selection change"""
        self.logger.info(f"Period changed to: {period}")
        # This would trigger a re-analysis with filtered data
