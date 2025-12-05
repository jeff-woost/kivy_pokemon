"""
Enhanced Pokemon Card Investment Analyzer
Integrates real scraping, backtesting, and grading analysis
"""
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
    QComboBox, QCheckBox, QProgressBar, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

# Import our modules
from enhanced_database import EnhancedDatabaseManager
from scrapers import ScraperManager
from analysis import BacktestingEngine, GradingAnalyzer, SignalGenerator
from ui import GradingOpportunitiesTab, BacktestingTab, PriceChartWidget


class DataAnalysisThread(QThread):
    """Thread for running comprehensive data analysis"""
    progress_update = pyqtSignal(int, str)
    analysis_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, card_name: str, scraper_manager, backtesting_engine, 
                 grading_analyzer, signal_generator):
        super().__init__()
        self.card_name = card_name
        self.scraper_manager = scraper_manager
        self.backtesting_engine = backtesting_engine
        self.grading_analyzer = grading_analyzer
        self.signal_generator = signal_generator
        self.logger = logging.getLogger(__name__)
        
    def run(self):
        """Run comprehensive analysis"""
        try:
            # Step 1: Scrape data from all sources
            self.progress_update.emit(10, "Scraping data from eBay and PriceCharting...")
            inception_data = self.scraper_manager.get_inception_data(self.card_name)
            
            if not inception_data['price_history']:
                self.error_occurred.emit("No price data found for this card")
                return
                
            self.progress_update.emit(30, "Data collection complete")
            
            # Step 2: Run backtesting analysis
            self.progress_update.emit(40, "Running inception-to-date backtesting...")
            backtest_metrics = self.backtesting_engine.analyze_inception_to_date(
                inception_data['price_history']
            )
            
            signals = self.backtesting_engine.generate_historical_signals(
                inception_data['price_history']
            )
            
            self.progress_update.emit(60, "Backtesting complete")
            
            # Step 3: Analyze grading opportunities
            self.progress_update.emit(70, "Analyzing PSA 10 grading opportunities...")
            grading_analysis = self.grading_analyzer.analyze_grading_opportunity(
                inception_data['price_history']
            )
            
            self.progress_update.emit(80, "Grading analysis complete")
            
            # Step 4: Generate current trading signal
            self.progress_update.emit(90, "Generating trading signals...")
            current_signal = self.signal_generator.generate_signal(
                backtest_metrics['current_price'],
                backtest_metrics['mean_price'],
                backtest_metrics['std_dev'],
                backtest_metrics['trend']
            )
            
            # Generate signals at various price points
            price_point_signals = self.signal_generator.generate_signals_at_price_points(
                backtest_metrics['mean_price'],
                backtest_metrics['std_dev'],
                backtest_metrics['trend']
            )
            
            # Backtest trading strategy
            strategy_results = self.signal_generator.analyze_entry_exit_points(
                inception_data['price_history']
            )
            
            self.progress_update.emit(100, "Analysis complete!")
            
            # Compile results
            results = {
                'card_name': self.card_name,
                'inception_data': inception_data,
                'backtest_metrics': backtest_metrics,
                'signals': signals,
                'grading_analysis': grading_analysis,
                'current_signal': current_signal,
                'price_point_signals': price_point_signals,
                'strategy_results': strategy_results
            }
            
            self.analysis_complete.emit(results)
            
        except Exception as e:
            self.logger.error(f"Error in analysis thread: {e}", exc_info=True)
            self.error_occurred.emit(str(e))


class PokemonCardAnalyzerEnhanced(QMainWindow):
    """Enhanced Pokemon Card Analyzer with all new features"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.init_managers()
        self.init_ui()
        self.apply_dark_theme()
        
        # Current analysis results
        self.current_results = None
        
    def init_managers(self):
        """Initialize all manager objects"""
        try:
            # Try PostgreSQL first, fallback to SQLite
            self.db_manager = EnhancedDatabaseManager(use_postgres=True)
        except Exception as e:
            self.logger.warning(f"PostgreSQL not available, using SQLite: {e}")
            self.db_manager = EnhancedDatabaseManager(use_postgres=False)
            
        self.scraper_manager = ScraperManager()
        self.backtesting_engine = BacktestingEngine()
        self.grading_analyzer = GradingAnalyzer()
        self.signal_generator = SignalGenerator()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Pokemon Card Investment Analyzer - Enhanced Edition")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addLayout(header)
        
        # Search section
        search = self.create_search_section()
        main_layout.addLayout(search)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        main_layout.addWidget(self.status_label)
        
        # Main tabs
        self.tab_widget = QTabWidget()
        
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "Overview & Signals")
        
        # Backtesting tab
        self.backtesting_tab = BacktestingTab()
        self.tab_widget.addTab(self.backtesting_tab, "Backtesting")
        
        # Grading opportunities tab
        self.grading_tab = GradingOpportunitiesTab(self.grading_analyzer)
        self.tab_widget.addTab(self.grading_tab, "Grading Opportunities")
        
        # Price chart tab
        self.chart_tab = self.create_chart_tab()
        self.tab_widget.addTab(self.chart_tab, "Price Charts")
        
        main_layout.addWidget(self.tab_widget)
        
    def create_header(self):
        """Create header section"""
        layout = QHBoxLayout()
        
        title = QLabel("🎴 Pokemon Card Investment Analyzer")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Real-time Scraping | Backtesting | PSA 10 Analysis")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #888888;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        return layout
        
    def create_search_section(self):
        """Create search section"""
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Card Name:"))
        
        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("Enter Pokemon card name (e.g., 'Charizard Base Set')")
        self.card_input.setFont(QFont("Arial", 11))
        self.card_input.returnPressed.connect(self.start_analysis)
        layout.addWidget(self.card_input)
        
        self.analyze_button = QPushButton("Analyze Card")
        self.analyze_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.analyze_button.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_button)
        
        self.discover_button = QPushButton("Discover 3x+ Opportunities")
        self.discover_button.setFont(QFont("Arial", 11))
        self.discover_button.clicked.connect(self.discover_opportunities)
        layout.addWidget(self.discover_button)
        
        return layout
        
    def create_overview_tab(self):
        """Create overview tab with signals"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Current signal display
        signal_header = QLabel("Current Trading Signal")
        signal_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(signal_header)
        
        self.current_signal_widget = QWidget()
        self.current_signal_widget.setStyleSheet("""
            QWidget {
                background-color: #3a3a3a;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        signal_layout = QVBoxLayout(self.current_signal_widget)
        
        self.signal_label = QLabel("No analysis yet")
        self.signal_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.signal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signal_layout.addWidget(self.signal_label)
        
        self.signal_details = QLabel("")
        self.signal_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signal_layout.addWidget(self.signal_details)
        
        layout.addWidget(self.current_signal_widget)
        
        # Price point signals table
        layout.addWidget(QLabel("BUY/SELL/HOLD Signals at Different Price Points:"))
        
        self.price_signals_table = QTableWidget()
        self.price_signals_table.setColumnCount(5)
        self.price_signals_table.setHorizontalHeaderLabels([
            "Price Point", "Signal", "Confidence %", "Z-Score", "Reason"
        ])
        self.price_signals_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.price_signals_table.setAlternatingRowColors(True)
        self.price_signals_table.setMaximumHeight(300)
        layout.addWidget(self.price_signals_table)
        
        # Key metrics
        layout.addWidget(QLabel("Key Investment Metrics:"))
        
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setMaximumHeight(200)
        layout.addWidget(self.metrics_text)
        
        layout.addStretch()
        return widget
        
    def create_chart_tab(self):
        """Create chart tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Chart selector
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Chart Type:"))
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Price History with Bands",
            "Graded vs Ungraded Comparison",
            "Signals Overlay"
        ])
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        controls.addWidget(self.chart_type_combo)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Chart widget
        self.price_chart = PriceChartWidget()
        layout.addWidget(self.price_chart)
        
        return widget
        
    def start_analysis(self):
        """Start comprehensive card analysis"""
        card_name = self.card_input.text().strip()
        if not card_name:
            QMessageBox.warning(self, "Input Required", "Please enter a card name")
            return
            
        # Disable UI during analysis
        self.analyze_button.setEnabled(False)
        self.discover_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start analysis thread
        self.analysis_thread = DataAnalysisThread(
            card_name,
            self.scraper_manager,
            self.backtesting_engine,
            self.grading_analyzer,
            self.signal_generator
        )
        
        self.analysis_thread.progress_update.connect(self.update_progress)
        self.analysis_thread.analysis_complete.connect(self.display_results)
        self.analysis_thread.error_occurred.connect(self.handle_error)
        
        self.analysis_thread.start()
        
    def update_progress(self, value: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
    def display_results(self, results: Dict):
        """Display comprehensive analysis results"""
        self.current_results = results
        
        # Update overview tab
        self.update_overview_tab(results)
        
        # Update backtesting tab
        self.backtesting_tab.load_backtesting_results(
            results['backtest_metrics'],
            results['signals'],
            results['strategy_results']
        )
        
        # Update grading tab
        grading_opps = [{
            'card_name': results['card_name'],
            **results['grading_analysis']
        }]
        self.grading_tab.load_opportunities(grading_opps)
        
        # Update charts
        self.update_chart()
        
        # Save to database
        self.save_results_to_database(results)
        
        # Re-enable UI
        self.analyze_button.setEnabled(True)
        self.discover_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Analysis complete!")
        
    def update_overview_tab(self, results: Dict):
        """Update overview tab with results"""
        signal = results['current_signal']
        
        # Update signal display
        signal_text = f"{signal['signal']}"
        self.signal_label.setText(signal_text)
        
        # Color code signal
        if signal['signal'] == 'BUY':
            self.current_signal_widget.setStyleSheet("""
                QWidget {
                    background-color: #1b5e20;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
        elif signal['signal'] == 'SELL':
            self.current_signal_widget.setStyleSheet("""
                QWidget {
                    background-color: #b71c1c;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
        else:  # HOLD
            self.current_signal_widget.setStyleSheet("""
                QWidget {
                    background-color: #5d4037;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
        details = f"""
        Current Price: ${signal['current_price']:.2f}
        Mean Price: ${signal['mean_price']:.2f}
        Confidence: {signal['confidence']:.1f}%
        {signal['reason']}
        """
        self.signal_details.setText(details.strip())
        
        # Update price point signals table
        signals_at_points = results['price_point_signals']
        self.price_signals_table.setRowCount(len(signals_at_points))
        
        for i, sig in enumerate(signals_at_points):
            self.price_signals_table.setItem(i, 0, QTableWidgetItem(f"${sig['price_point']:.2f}"))
            
            signal_item = QTableWidgetItem(sig['signal'])
            if sig['signal'] == 'BUY':
                signal_item.setBackground(QColor(76, 175, 80, 100))
            elif sig['signal'] == 'SELL':
                signal_item.setBackground(QColor(244, 67, 54, 100))
            else:
                signal_item.setBackground(QColor(255, 193, 7, 100))
            self.price_signals_table.setItem(i, 1, signal_item)
            
            self.price_signals_table.setItem(i, 2, QTableWidgetItem(f"{sig['confidence']:.1f}%"))
            self.price_signals_table.setItem(i, 3, QTableWidgetItem(f"{sig['z_score']:.2f}"))
            self.price_signals_table.setItem(i, 4, QTableWidgetItem(sig['reason'][:50]))
            
        # Update metrics
        metrics = results['backtest_metrics']
        grading = results['grading_analysis']
        
        metrics_text = f"""
Card: {results['card_name']}

Price Metrics:
  • Current Price: ${metrics['current_price']:.2f}
  • Mean Price (All Time): ${metrics['mean_price']:.2f}
  • Std Deviation: ${metrics['std_dev']:.2f}
  • Volatility: {metrics['volatility']:.1f}%

Performance:
  • Total Return: {metrics['total_return_pct']:+.1f}%
  • Annualized Return: {metrics['annualized_return_pct']:+.1f}%
  • Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
  • Trend: {metrics['trend'].replace('_', ' ').title()}

Grading Opportunity:
  • PSA 10 Multiplier: {grading['multiplier']:.2f}x
  • Net Profit Potential: ${grading['net_profit']:.2f}
  • ROI if Graded: {grading['roi_percentage']:.1f}%
  • Worth Grading: {'YES ✓' if grading['worth_grading'] else 'NO ✗'}
        """
        
        self.metrics_text.setText(metrics_text.strip())
        
    def update_chart(self):
        """Update the selected chart"""
        if not self.current_results:
            return
            
        chart_type = self.chart_type_combo.currentText()
        price_history = self.current_results['inception_data']['price_history']
        card_name = self.current_results['card_name']
        metrics = self.current_results['backtest_metrics']
        
        if chart_type == "Price History with Bands":
            self.price_chart.plot_price_history_with_bands(
                price_history,
                metrics['mean_price'],
                metrics['std_dev'],
                card_name
            )
        elif chart_type == "Graded vs Ungraded Comparison":
            self.price_chart.plot_graded_vs_ungraded_comparison(
                price_history,
                card_name
            )
        elif chart_type == "Signals Overlay":
            self.price_chart.plot_signals_overlay(
                price_history,
                self.current_results['signals'],
                card_name
            )
            
    def discover_opportunities(self):
        """Discover cards with 3x+ grading multiplier"""
        self.status_label.setText("Discovering grading opportunities...")
        # This would scan PriceCharting for opportunities
        # For now, show a message
        QMessageBox.information(
            self,
            "Feature Info",
            "Grading opportunity discovery scans PriceCharting for cards with 3x+ multipliers.\n\n"
            "This feature requires extended scraping and will be implemented in a future update.\n\n"
            "For now, analyze individual cards to see their grading potential."
        )
        
    def save_results_to_database(self, results: Dict):
        """Save analysis results to database"""
        try:
            card_name = results['card_name']
            
            # Save backtesting results
            self.db_manager.save_backtesting_results(card_name, results['backtest_metrics'])
            
            # Save grading analysis
            self.db_manager.save_grading_analysis(card_name, results['grading_analysis'])
            
            # Save current signal
            self.db_manager.save_trading_signal(card_name, results['current_signal'])
            
            # Save price data
            from common import CardPrice
            price_data_list = [
                CardPrice(
                    date=p['date'],
                    price=p['price'],
                    source=p['source'],
                    condition=p.get('condition', 'Unknown'),
                    graded=p.get('graded', False),
                    grade_value=p.get('grade_value'),
                    grade_company=p.get('grade_company')
                )
                for p in results['inception_data']['price_history']
            ]
            self.db_manager.save_price_data_batch_vectorized(card_name, price_data_list)
            
            self.logger.info(f"Saved results for {card_name} to database")
            
        except Exception as e:
            self.logger.error(f"Error saving results to database: {e}")
            
    def handle_error(self, error_message: str):
        """Handle analysis error"""
        self.analyze_button.setEnabled(True)
        self.discover_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Analysis Error", f"An error occurred:\n\n{error_message}")
        
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(60, 60, 60))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        self.setPalette(dark_palette)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5d61;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #999999;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #3a3a3a;
            }
            QTableWidget {
                gridline-color: #555555;
                background-color: #3a3a3a;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                padding: 8px;
                border: 1px solid #555555;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3a3a3a;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: white;
                padding: 10px 20px;
                margin: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0d7377;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                text-align: center;
                background-color: #3a3a3a;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
                border-radius: 3px;
            }
        """)
        
    def closeEvent(self, event):
        """Handle application close"""
        self.db_manager.close()
        event.accept()
