"""
Grading opportunities tab UI
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QTextEdit, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict
import logging


class GradingAnalysisThread(QThread):
    """Thread for running grading analysis"""
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    results_ready = pyqtSignal(list)
    
    def __init__(self, grading_analyzer, price_history):
        super().__init__()
        self.grading_analyzer = grading_analyzer
        self.price_history = price_history
        
    def run(self):
        try:
            self.status_update.emit("Analyzing grading opportunities...")
            self.progress_update.emit(50)
            
            analysis = self.grading_analyzer.analyze_grading_opportunity(self.price_history)
            
            self.progress_update.emit(100)
            self.results_ready.emit([analysis])
        except Exception as e:
            self.status_update.emit(f"Error: {str(e)}")


class GradingOpportunitiesTab(QWidget):
    """Tab for displaying PSA 10 grading opportunities"""
    
    def __init__(self, grading_analyzer=None):
        super().__init__()
        self.grading_analyzer = grading_analyzer
        self.logger = logging.getLogger(__name__)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("PSA 10 Grading Opportunities")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Filter controls
        filter_label = QLabel("Min Multiplier:")
        self.multiplier_combo = QComboBox()
        self.multiplier_combo.addItems(["2.0x", "2.5x", "3.0x", "4.0x", "5.0x"])
        self.multiplier_combo.setCurrentText("3.0x")
        self.multiplier_combo.currentTextChanged.connect(self.apply_filter)
        
        header_layout.addWidget(filter_label)
        header_layout.addWidget(self.multiplier_combo)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Summary section
        self.summary_label = QLabel("No data loaded")
        self.summary_label.setStyleSheet("background-color: #3a3a3a; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.summary_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Table for grading opportunities
        self.opportunities_table = QTableWidget()
        self.opportunities_table.setColumnCount(10)
        self.opportunities_table.setHorizontalHeaderLabels([
            "Card Name", "Ungraded $", "PSA 10 $", "Multiplier", 
            "Grading Cost", "Net Profit", "ROI %", "Data Points",
            "Recommendation", "Worth Grading"
        ])
        self.opportunities_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.opportunities_table.setAlternatingRowColors(True)
        self.opportunities_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.opportunities_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(QLabel("Grading Opportunities:"))
        layout.addWidget(self.opportunities_table)
        
        # Details panel
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        layout.addWidget(QLabel("Selected Card Details:"))
        layout.addWidget(self.details_text)
        
    def load_opportunities(self, opportunities: List[Dict]):
        """
        Load grading opportunities into the table
        
        Args:
            opportunities: List of grading opportunity dictionaries
        """
        # Apply current filter
        min_multiplier = float(self.multiplier_combo.currentText().replace('x', ''))
        filtered = [opp for opp in opportunities if opp.get('multiplier', 0) >= min_multiplier]
        
        # Update summary
        total_net_profit = sum(opp.get('net_profit', 0) for opp in filtered)
        avg_multiplier = sum(opp.get('multiplier', 0) for opp in filtered) / len(filtered) if filtered else 0
        
        summary_text = f"""
        Total Opportunities: {len(filtered)} | 
        Total Potential Profit: ${total_net_profit:,.2f} | 
        Average Multiplier: {avg_multiplier:.2f}x
        """
        self.summary_label.setText(summary_text)
        
        # Populate table
        self.opportunities_table.setRowCount(len(filtered))
        
        for i, opp in enumerate(filtered):
            # Card name
            self.opportunities_table.setItem(i, 0, QTableWidgetItem(opp.get('card_name', 'Unknown')))
            
            # Ungraded price
            ungraded_price = opp.get('ungraded_avg_price', 0)
            self.opportunities_table.setItem(i, 1, QTableWidgetItem(f"${ungraded_price:.2f}"))
            
            # PSA 10 price
            psa10_price = opp.get('psa10_avg_price', 0)
            self.opportunities_table.setItem(i, 2, QTableWidgetItem(f"${psa10_price:.2f}"))
            
            # Multiplier
            multiplier = opp.get('multiplier', 0)
            mult_item = QTableWidgetItem(f"{multiplier:.2f}x")
            if multiplier >= 5.0:
                mult_item.setBackground(QColor(76, 175, 80, 100))  # Green
            elif multiplier >= 4.0:
                mult_item.setBackground(QColor(139, 195, 74, 100))  # Light green
            elif multiplier >= 3.0:
                mult_item.setBackground(QColor(255, 193, 7, 100))  # Yellow
            self.opportunities_table.setItem(i, 3, mult_item)
            
            # Grading cost
            grading_cost = opp.get('grading_cost', 0)
            self.opportunities_table.setItem(i, 4, QTableWidgetItem(f"${grading_cost:.2f}"))
            
            # Net profit
            net_profit = opp.get('net_profit', 0)
            profit_item = QTableWidgetItem(f"${net_profit:.2f}")
            if net_profit > 0:
                profit_item.setForeground(QColor(76, 175, 80))
            else:
                profit_item.setForeground(QColor(244, 67, 54))
            self.opportunities_table.setItem(i, 5, profit_item)
            
            # ROI %
            roi = opp.get('roi_percentage', 0)
            roi_item = QTableWidgetItem(f"{roi:.1f}%")
            if roi > 100:
                roi_item.setForeground(QColor(76, 175, 80))
            self.opportunities_table.setItem(i, 6, roi_item)
            
            # Data points
            data_points = opp.get('psa10_data_points', 0)
            self.opportunities_table.setItem(i, 7, QTableWidgetItem(str(data_points)))
            
            # Recommendation
            recommendation = opp.get('recommendation', 'N/A')
            self.opportunities_table.setItem(i, 8, QTableWidgetItem(recommendation))
            
            # Worth grading
            worth = opp.get('worth_grading', False)
            worth_item = QTableWidgetItem("✓" if worth else "✗")
            if worth:
                worth_item.setForeground(QColor(76, 175, 80))
            else:
                worth_item.setForeground(QColor(244, 67, 54))
            self.opportunities_table.setItem(i, 9, worth_item)
            
    def on_selection_changed(self):
        """Handle table row selection"""
        selected_rows = self.opportunities_table.selectedIndexes()
        if not selected_rows:
            self.details_text.clear()
            return
            
        row = selected_rows[0].row()
        
        # Build details text
        card_name = self.opportunities_table.item(row, 0).text()
        ungraded = self.opportunities_table.item(row, 1).text()
        psa10 = self.opportunities_table.item(row, 2).text()
        multiplier = self.opportunities_table.item(row, 3).text()
        net_profit = self.opportunities_table.item(row, 5).text()
        roi = self.opportunities_table.item(row, 6).text()
        recommendation = self.opportunities_table.item(row, 8).text()
        
        details = f"""
Card: {card_name}

Price Analysis:
  • Ungraded Average: {ungraded}
  • PSA 10 Average: {psa10}
  • Multiplier: {multiplier}
  
Investment Analysis:
  • Net Profit (after grading): {net_profit}
  • Return on Investment: {roi}
  
Recommendation: {recommendation}

Note: This analysis is based on historical market data. Actual results may vary based on card condition and market conditions.
        """
        
        self.details_text.setText(details.strip())
        
    def apply_filter(self):
        """Re-apply filters to current data"""
        # This would need to store the original data and re-filter
        # For now, just a placeholder
        pass
        
    def refresh_data(self):
        """Refresh grading opportunities data"""
        # Emit signal to parent to refresh data
        self.logger.info("Refresh requested")
        
    def update_progress(self, value: int):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    def show_progress(self, show: bool):
        """Show/hide progress bar"""
        self.progress_bar.setVisible(show)
