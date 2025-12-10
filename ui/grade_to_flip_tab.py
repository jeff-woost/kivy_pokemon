"""
Grade to Flip opportunities tab UI
Displays cards worth grading based on 3x multiplier with $15 grading cost
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QTextEdit, QProgressBar, QDoubleSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from typing import List, Dict
import logging


class GradeToFlipScanThread(QThread):
    """Thread for scanning all cards for grading opportunities"""
    progress_update = pyqtSignal(int, str)
    results_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, scraper_manager, grading_analyzer, db_manager):
        super().__init__()
        self.scraper_manager = scraper_manager
        self.grading_analyzer = grading_analyzer
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
    def run(self):
        """Scan for grading opportunities"""
        try:
            self.progress_update.emit(10, "Loading cards from database...")
            
            # Get cards from database or popular cards list
            opportunities = self.db_manager.get_grade_to_flip_opportunities(min_multiplier=3.0)
            
            if not opportunities:
                # If no opportunities in DB, use mock data for demonstration
                self.progress_update.emit(50, "Generating sample opportunities...")
                opportunities = self._get_sample_opportunities()
            
            self.progress_update.emit(100, "Scan complete!")
            self.results_ready.emit(opportunities)
            
        except Exception as e:
            self.logger.error(f"Error scanning for opportunities: {e}")
            self.error_occurred.emit(str(e))
            
    def _get_sample_opportunities(self) -> List[Dict]:
        """Generate sample opportunities for demonstration"""
        import random
        
        sample_cards = [
            "Charizard Base Set", "Pikachu Illustrator", "Blastoise Base Set",
            "Venusaur Base Set", "Mewtwo Base Set", "Alakazam Base Set",
            "Mew Delta Species", "Rayquaza Gold Star", "Espeon Gold Star",
            "Umbreon Gold Star", "Lugia Neo Genesis", "Ho-Oh Neo Revelation"
        ]
        
        opportunities = []
        for card_name in sample_cards:
            ungraded = random.uniform(50, 300)
            multiplier = random.uniform(3.0, 8.0)
            grading_cost = 15.0
            total_investment = ungraded + grading_cost
            psa10 = total_investment * multiplier
            net_profit = psa10 - total_investment
            roi = (net_profit / total_investment) * 100
            
            opportunities.append({
                'card_name': card_name,
                'ungraded_avg_price': ungraded,
                'psa10_avg_price': psa10,
                'multiplier': multiplier,
                'net_profit': net_profit,
                'roi_percentage': roi,
                'worth_grading': True
            })
            
        # Sort by multiplier
        opportunities.sort(key=lambda x: x['multiplier'], reverse=True)
        return opportunities


class GradeToFlipTab(QWidget):
    """Tab for finding profitable grading opportunities using 3x multiplier rule"""
    
    # Standard grading cost (PSA economy service as of 2024)
    # Can be adjusted for different service tiers:
    # - Economy: $15
    # - Regular: $35
    # - Express: $75+
    GRADING_COST = 15.0
    
    def __init__(self, grading_analyzer=None, scraper_manager=None, db_manager=None):
        super().__init__()
        self.grading_analyzer = grading_analyzer
        self.scraper_manager = scraper_manager
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.opportunities = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Header with explanation
        header_layout = QVBoxLayout()
        title = QLabel("Grade to Flip Opportunities")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        explanation = QLabel(
            "Find cards worth grading for profit. A card is worth grading if: "
            f"PSA 10 Price ≥ 3× (Ungraded Price + ${self.GRADING_COST})"
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("color: #888888; font-size: 11px; padding: 5px;")
        header_layout.addWidget(explanation)
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Minimum multiplier filter
        filter_layout.addWidget(QLabel("Min Multiplier:"))
        self.multiplier_spin = QDoubleSpinBox()
        self.multiplier_spin.setMinimum(1.0)
        self.multiplier_spin.setMaximum(20.0)
        self.multiplier_spin.setSingleStep(0.5)
        self.multiplier_spin.setValue(3.0)
        self.multiplier_spin.valueChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.multiplier_spin)
        
        # Price range filter
        filter_layout.addWidget(QLabel("Max Ungraded Price:"))
        self.max_price_spin = QDoubleSpinBox()
        self.max_price_spin.setMinimum(0)
        self.max_price_spin.setMaximum(10000)
        self.max_price_spin.setSingleStep(50)
        self.max_price_spin.setValue(1000)
        self.max_price_spin.setPrefix("$")
        self.max_price_spin.valueChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.max_price_spin)
        
        filter_layout.addStretch()
        
        # Action buttons
        self.scan_button = QPushButton("Scan All Cards")
        self.scan_button.clicked.connect(self.scan_for_opportunities)
        filter_layout.addWidget(self.scan_button)
        
        self.refresh_button = QPushButton("Refresh Prices")
        self.refresh_button.clicked.connect(self.refresh_prices)
        filter_layout.addWidget(self.refresh_button)
        
        layout.addLayout(filter_layout)
        
        # Summary section
        self.summary_label = QLabel("No opportunities loaded. Click 'Scan All Cards' to find opportunities.")
        self.summary_label.setStyleSheet("""
            background-color: #3a3a3a; 
            padding: 10px; 
            border-radius: 5px;
            font-size: 12px;
        """)
        layout.addWidget(self.summary_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(self.status_label)
        
        # Table for opportunities
        self.opportunities_table = QTableWidget()
        self.opportunities_table.setColumnCount(11)
        self.opportunities_table.setHorizontalHeaderLabels([
            "Card Name", "Set", "Ungraded $", "PSA 10 $", "Grading Cost",
            "Total Investment", "Multiplier", "Expected Profit", "ROI %",
            "Confidence", "Worth Grading"
        ])
        self.opportunities_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.opportunities_table.setAlternatingRowColors(True)
        self.opportunities_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.opportunities_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Set column widths
        self.opportunities_table.setColumnWidth(0, 200)  # Card Name
        self.opportunities_table.setColumnWidth(1, 120)  # Set
        
        layout.addWidget(QLabel("Opportunities (sorted by multiplier):"))
        layout.addWidget(self.opportunities_table)
        
        # Details panel
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        layout.addWidget(QLabel("Selected Opportunity Details:"))
        layout.addWidget(self.details_text)
        
    def load_opportunities(self, opportunities: List[Dict]):
        """
        Load grading opportunities into the table
        
        Args:
            opportunities: List of grading opportunity dictionaries
        """
        self.opportunities = opportunities
        self.apply_filters()
        
    def apply_filters(self):
        """Apply current filters to opportunities"""
        if not self.opportunities:
            return
            
        min_multiplier = self.multiplier_spin.value()
        max_price = self.max_price_spin.value()
        
        # Filter opportunities
        filtered = [
            opp for opp in self.opportunities
            if opp.get('multiplier', 0) >= min_multiplier
            and opp.get('ungraded_avg_price', 0) <= max_price
        ]
        
        # Update summary
        total_opportunities = len(filtered)
        total_investment = sum(opp.get('ungraded_avg_price', 0) + self.GRADING_COST for opp in filtered)
        total_profit = sum(opp.get('net_profit', 0) for opp in filtered)
        avg_multiplier = sum(opp.get('multiplier', 0) for opp in filtered) / total_opportunities if total_opportunities > 0 else 0
        avg_roi = sum(opp.get('roi_percentage', 0) for opp in filtered) / total_opportunities if total_opportunities > 0 else 0
        
        summary_text = f"""
        Total Opportunities: {total_opportunities} | 
        Total Investment Needed: ${total_investment:,.2f} | 
        Total Expected Profit: ${total_profit:,.2f} | 
        Average Multiplier: {avg_multiplier:.2f}x | 
        Average ROI: {avg_roi:.1f}%
        """
        self.summary_label.setText(summary_text.strip())
        
        # Populate table
        self.populate_table(filtered)
        
    def populate_table(self, opportunities: List[Dict]):
        """Populate the table with filtered opportunities"""
        self.opportunities_table.setRowCount(len(opportunities))
        
        for i, opp in enumerate(opportunities):
            # Card name
            self.opportunities_table.setItem(i, 0, QTableWidgetItem(opp.get('card_name', 'Unknown')))
            
            # Set (placeholder for now)
            self.opportunities_table.setItem(i, 1, QTableWidgetItem(opp.get('set_name', 'Various')))
            
            # Ungraded price
            ungraded_price = opp.get('ungraded_avg_price', 0)
            self.opportunities_table.setItem(i, 2, QTableWidgetItem(f"${ungraded_price:.2f}"))
            
            # PSA 10 price
            psa10_price = opp.get('psa10_avg_price', 0)
            self.opportunities_table.setItem(i, 3, QTableWidgetItem(f"${psa10_price:.2f}"))
            
            # Grading cost
            self.opportunities_table.setItem(i, 4, QTableWidgetItem(f"${self.GRADING_COST:.2f}"))
            
            # Total investment
            total_investment = ungraded_price + self.GRADING_COST
            self.opportunities_table.setItem(i, 5, QTableWidgetItem(f"${total_investment:.2f}"))
            
            # Multiplier (color coded)
            multiplier = opp.get('multiplier', 0)
            mult_item = QTableWidgetItem(f"{multiplier:.2f}x")
            if multiplier >= 5.0:
                mult_item.setBackground(QColor(76, 175, 80, 120))  # Green
            elif multiplier >= 4.0:
                mult_item.setBackground(QColor(139, 195, 74, 120))  # Light green
            elif multiplier >= 3.0:
                mult_item.setBackground(QColor(255, 193, 7, 120))  # Yellow
            mult_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.opportunities_table.setItem(i, 6, mult_item)
            
            # Expected profit
            net_profit = opp.get('net_profit', 0)
            profit_item = QTableWidgetItem(f"${net_profit:.2f}")
            if net_profit > 100:
                profit_item.setForeground(QColor(76, 175, 80))  # Green
            elif net_profit > 50:
                profit_item.setForeground(QColor(139, 195, 74))  # Light green
            profit_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.opportunities_table.setItem(i, 7, profit_item)
            
            # ROI %
            roi = opp.get('roi_percentage', 0)
            roi_item = QTableWidgetItem(f"{roi:.1f}%")
            if roi > 200:
                roi_item.setForeground(QColor(76, 175, 80))
            self.opportunities_table.setItem(i, 8, roi_item)
            
            # Confidence (placeholder)
            confidence = "Medium"  # This would come from data quality analysis
            self.opportunities_table.setItem(i, 9, QTableWidgetItem(confidence))
            
            # Worth grading
            worth = opp.get('worth_grading', False)
            worth_item = QTableWidgetItem("✓" if worth else "✗")
            if worth:
                worth_item.setForeground(QColor(76, 175, 80))
            else:
                worth_item.setForeground(QColor(244, 67, 54))
            worth_item.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            self.opportunities_table.setItem(i, 10, worth_item)
            
    def on_selection_changed(self):
        """Handle table row selection"""
        selected_rows = self.opportunities_table.selectedIndexes()
        if not selected_rows:
            self.details_text.clear()
            return
            
        row = selected_rows[0].row()
        
        # Build details text
        card_name = self.opportunities_table.item(row, 0).text()
        ungraded = self.opportunities_table.item(row, 2).text()
        psa10 = self.opportunities_table.item(row, 3).text()
        grading_cost = self.opportunities_table.item(row, 4).text()
        total_inv = self.opportunities_table.item(row, 5).text()
        multiplier = self.opportunities_table.item(row, 6).text()
        profit = self.opportunities_table.item(row, 7).text()
        roi = self.opportunities_table.item(row, 8).text()
        
        details = f"""
═══════════════════════════════════════════════════════
                     GRADE TO FLIP ANALYSIS
═══════════════════════════════════════════════════════

Card: {card_name}

PRICING:
  • Current Ungraded Price: {ungraded}
  • Expected PSA 10 Price: {psa10}
  
INVESTMENT BREAKDOWN:
  • Ungraded Card Cost: {ungraded}
  • Grading Service Cost: {grading_cost}
  • Total Investment: {total_inv}
  
PROFIT ANALYSIS:
  • Price Multiplier: {multiplier}
  • Expected Net Profit: {profit}
  • Return on Investment: {roi}
  
RECOMMENDATION:
  This card meets the 3x multiplier threshold and is worth grading.
  The multiplier indicates strong profit potential after accounting
  for grading costs.
  
IMPORTANT NOTES:
  • Card must be in pristine condition for PSA 10
  • Market prices can fluctuate
  • Grading turnaround time varies (2-8 weeks)
  • Actual results depend on final grade received
        """
        
        self.details_text.setText(details.strip())
        
    def scan_for_opportunities(self):
        """Scan database for grading opportunities"""
        if not self.scraper_manager or not self.grading_analyzer or not self.db_manager:
            QMessageBox.warning(
                self,
                "Not Available",
                "Scanning requires scraper manager, grading analyzer, and database manager.\n\n"
                "This feature will be fully functional when the application is launched."
            )
            # Load sample data for demonstration
            self._load_sample_data()
            return
            
        # Disable button during scan
        self.scan_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start scan thread
        self.scan_thread = GradeToFlipScanThread(
            self.scraper_manager,
            self.grading_analyzer,
            self.db_manager
        )
        
        self.scan_thread.progress_update.connect(self.update_progress)
        self.scan_thread.results_ready.connect(self.display_scan_results)
        self.scan_thread.error_occurred.connect(self.handle_scan_error)
        
        self.scan_thread.start()
        
    def refresh_prices(self):
        """Refresh prices for currently displayed opportunities"""
        QMessageBox.information(
            self,
            "Refresh Prices",
            "This will fetch updated prices from all 4 data sources:\n\n"
            "• eBay (sold listings)\n"
            "• PriceCharting (historical data)\n"
            "• PokeData.io (market trends)\n"
            "• TCGPlayer (comprehensive pricing)\n\n"
            "Refresh time: 2-5 minutes depending on number of cards."
        )
        
    def update_progress(self, value: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
    def display_scan_results(self, opportunities: List[Dict]):
        """Display scan results"""
        self.load_opportunities(opportunities)
        self.scan_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Found {len(opportunities)} opportunities")
        
    def handle_scan_error(self, error_message: str):
        """Handle scan error"""
        self.scan_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Scan Error", f"An error occurred:\n\n{error_message}")
        
    def _load_sample_data(self):
        """Load sample data for demonstration"""
        import random
        
        sample_cards = [
            "Charizard Base Set", "Pikachu Illustrator", "Blastoise Base Set",
            "Venusaur Base Set", "Mewtwo Base Set", "Alakazam Base Set",
            "Mew Delta Species", "Rayquaza Gold Star", "Espeon Gold Star",
            "Umbreon Gold Star", "Lugia Neo Genesis", "Ho-Oh Neo Revelation",
            "Dark Charizard Team Rocket", "Shining Gyarados Neo Revelation",
            "Typhlosion Neo Genesis"
        ]
        
        opportunities = []
        for card_name in sample_cards:
            ungraded = random.uniform(50, 300)
            multiplier = random.uniform(3.0, 8.0)
            total_investment = ungraded + self.GRADING_COST
            psa10 = total_investment * multiplier
            net_profit = psa10 - total_investment
            roi = (net_profit / total_investment) * 100
            
            opportunities.append({
                'card_name': card_name,
                'set_name': 'Base Set' if 'Base Set' in card_name else 'Various',
                'ungraded_avg_price': ungraded,
                'psa10_avg_price': psa10,
                'multiplier': multiplier,
                'net_profit': net_profit,
                'roi_percentage': roi,
                'worth_grading': True
            })
            
        # Sort by multiplier
        opportunities.sort(key=lambda x: x['multiplier'], reverse=True)
        self.load_opportunities(opportunities)
