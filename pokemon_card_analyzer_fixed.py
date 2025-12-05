import sys
import json
import time
import random
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
from urllib.parse import quote
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from pathlib import Path

# Fix PyQt conflicts by ensuring we only use PyQt6
import sys
if 'PyQt5' in sys.modules:
    del sys.modules['PyQt5']

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QLineEdit, QPushButton,
                            QTableWidget, QTableWidgetItem, QTabWidget,
                            QTextEdit, QComboBox, QSpinBox, QCheckBox,
                            QProgressBar, QSplitter, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Import our enhanced database manager
from enhanced_database import EnhancedDatabaseManager

# Data structures
@dataclass
class CardPrice:
    date: datetime
    price: float
    source: str
    condition: str
    graded: bool
    grade_value: Optional[float] = None
    grade_company: Optional[str] = None

@dataclass
class CardData:
    name: str
    set_name: str
    number: str
    rarity: str
    prices: List[CardPrice]
    current_market_price: float
    trend: str
    confidence_score: float

# Web Scraping Classes with improved error handling
class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            time.sleep(random.uniform(1, 3))  # Rate limiting
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

class TCGPlayerScraper(BaseScraper):
    def search_card(self, card_name: str) -> List[Dict]:
        """Search for card prices on TCGPlayer"""
        results = []
        try:
            # Mock data for demonstration - replace with actual scraping logic
            mock_prices = [
                {'price': random.uniform(50, 500), 'condition': 'Near Mint', 'date': datetime.now() - timedelta(days=i)}
                for i in range(30)
            ]
            for item in mock_prices:
                results.append({
                    'price': item['price'],
                    'condition': item['condition'],
                    'date': item['date'],
                    'source': 'TCGPlayer',
                    'graded': False
                })
        except Exception as e:
            print(f"TCGPlayer scraping error: {e}")

        return results

class EbayScraper(BaseScraper):
    def get_sold_listings(self, card_name: str) -> List[Dict]:
        """Get sold listings from eBay"""
        results = []
        try:
            # Mock data for demonstration
            mock_prices = [
                {'price': random.uniform(40, 450), 'condition': 'Used', 'date': datetime.now() - timedelta(days=i)}
                for i in range(20)
            ]
            for item in mock_prices:
                results.append({
                    'price': item['price'],
                    'condition': item['condition'],
                    'date': item['date'],
                    'source': 'eBay',
                    'graded': random.choice([True, False])
                })
        except Exception as e:
            print(f"eBay scraping error: {e}")

        return results

class PriceChartingScraper(BaseScraper):
    def get_price_history(self, card_name: str) -> List[Dict]:
        """Get price history from PriceCharting"""
        results = []
        try:
            # Mock data for demonstration
            mock_prices = [
                {'price': random.uniform(45, 480), 'condition': 'Complete', 'date': datetime.now() - timedelta(days=i*7)}
                for i in range(52)  # Weekly data for a year
            ]
            for item in mock_prices:
                results.append({
                    'price': item['price'],
                    'condition': item['condition'],
                    'date': item['date'],
                    'source': 'PriceCharting',
                    'graded': False
                })
        except Exception as e:
            print(f"PriceCharting scraping error: {e}")

        return results

class CollectrScraper(BaseScraper):
    def get_card_prices(self, card_name: str) -> List[Dict]:
        """Get prices from Collectr"""
        results = []
        try:
            # Mock data for demonstration
            mock_prices = [
                {'price': random.uniform(55, 520), 'condition': 'Mint', 'date': datetime.now() - timedelta(days=i*2)}
                for i in range(60)
            ]
            for item in mock_prices:
                results.append({
                    'price': item['price'],
                    'condition': item['condition'],
                    'date': item['date'],
                    'source': 'Collectr',
                    'graded': random.choice([True, False])
                })
        except Exception as e:
            print(f"Collectr scraping error: {e}")

        return results

class MavinScraper(BaseScraper):
    def get_card_values(self, card_name: str) -> List[Dict]:
        """Get values from Mavin.io"""
        results = []
        try:
            # Mock data for demonstration
            mock_prices = [
                {'price': random.uniform(60, 550), 'condition': 'Excellent', 'date': datetime.now() - timedelta(days=i*3)}
                for i in range(40)
            ]
            for item in mock_prices:
                results.append({
                    'price': item['price'],
                    'condition': item['condition'],
                    'date': item['date'],
                    'source': 'Mavin',
                    'graded': random.choice([True, False])
                })
        except Exception as e:
            print(f"Mavin scraping error: {e}")

        return results

# Analysis Engine with vectorized operations
class PriceAnalyzer:
    def __init__(self):
        self.models = {}

    def prepare_data_vectorized(self, prices: List[Dict]) -> pd.DataFrame:
        """Vectorized data preparation using pandas operations"""
        df = pd.DataFrame(prices)
        if df.empty:
            return df

        # Vectorized datetime conversion
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # Vectorized feature engineering
        df['days_from_start'] = (df['date'] - df['date'].min()).dt.days

        # Vectorized rolling calculations
        df['price_ma7'] = df['price'].rolling(window=7, min_periods=1).mean()
        df['price_ma30'] = df['price'].rolling(window=30, min_periods=1).mean()
        df['volatility'] = df['price'].rolling(window=7, min_periods=1).std()

        # Vectorized price change calculations
        df['price_change_1d'] = df['price'].pct_change()
        df['price_change_7d'] = df['price'].pct_change(periods=7)

        return df

    def calculate_trend_vectorized(self, df: pd.DataFrame) -> Dict:
        """Vectorized trend calculation"""
        if len(df) < 2:
            return {'trend': 'insufficient_data', 'slope': 0, 'r2': 0}

        # Vectorized linear regression using numpy
        X = df['days_from_start'].values
        y = df['price'].values

        # Calculate slope and intercept using vectorized operations
        n = len(X)
        sum_x = np.sum(X)
        sum_y = np.sum(y)
        sum_xy = np.sum(X * y)
        sum_x2 = np.sum(X * X)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared
        y_pred = slope * X + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        if slope > 0.5:
            trend = 'strong_upward'
        elif slope > 0:
            trend = 'upward'
        elif slope > -0.5:
            trend = 'stable'
        else:
            trend = 'downward'

        return {'trend': trend, 'slope': slope, 'r2': r2}

    def predict_future_price_vectorized(self, df: pd.DataFrame, days_ahead: int = 30) -> Tuple[float, Tuple[float, float]]:
        """Vectorized price prediction"""
        if len(df) < 10:
            return 0, (0, 0)

        # Prepare features using vectorized operations
        feature_cols = ['days_from_start', 'price_ma7', 'price_ma30', 'volatility']
        X = df[feature_cols].fillna(method='ffill').fillna(0).values
        y = df['price'].values

        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)

        # Predict future using vectorized operations
        last_row = df.iloc[-1]
        future_days = last_row['days_from_start'] + days_ahead
        future_features = np.array([[future_days, last_row['price_ma7'], last_row['price_ma30'], last_row['volatility']]])

        predicted_price = model.predict(future_features)[0]

        # Vectorized confidence interval calculation
        predictions = model.predict(X_test)
        errors = y_test - predictions
        std_error = np.std(errors)

        # 95% confidence interval
        confidence_interval = (
            predicted_price - 1.96 * std_error,
            predicted_price + 1.96 * std_error
        )

        return predicted_price, confidence_interval

    def calculate_investment_score(self, df: pd.DataFrame, predicted_price: float,
                                  confidence_interval: Tuple[float, float]) -> Dict:
        """Calculate investment score and recommendation"""
        current_price = df['price'].iloc[-1]
        roi = ((predicted_price - current_price) / current_price) * 100

        # Calculate confidence score based on multiple factors
        trend_info = self.calculate_trend_vectorized(df)
        volatility = df['volatility'].mean()
        price_stability = 1 / (1 + volatility / current_price)

        confidence_score = (
            trend_info['r2'] * 0.3 +  # Model fit quality
            price_stability * 0.3 +    # Price stability
            min(roi / 100, 1) * 0.4    # ROI potential
        ) * 100

        # Generate recommendation
        if roi > 20 and confidence_interval[0] > current_price * 1.1:
            recommendation = "STRONG BUY"
        elif roi > 10 and confidence_interval[0] > current_price:
            recommendation = "BUY"
        elif roi > 5:
            recommendation = "HOLD"
        else:
            recommendation = "AVOID"

        return {
            'current_price': current_price,
            'predicted_price': predicted_price,
            'confidence_interval': confidence_interval,
            'roi': roi,
            'confidence_score': min(confidence_score, 100),
            'recommendation': recommendation,
            'trend': trend_info['trend']
        }

# Data Collection Thread
class DataCollectionThread(QThread):
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    data_ready = pyqtSignal(dict)

    def __init__(self, card_name: str):
        super().__init__()
        self.card_name = card_name
        self.scrapers = {
            'TCGPlayer': TCGPlayerScraper(),
            'eBay': EbayScraper(),
            'PriceCharting': PriceChartingScraper(),
            'Collectr': CollectrScraper(),
            'Mavin': MavinScraper()
        }

    def run(self):
        all_prices = []
        total_scrapers = len(self.scrapers)

        for i, (name, scraper) in enumerate(self.scrapers.items()):
            self.status_update.emit(f"Collecting data from {name}...")

            if name == 'TCGPlayer':
                prices = scraper.search_card(self.card_name)
            elif name == 'eBay':
                prices = scraper.get_sold_listings(self.card_name)
            elif name == 'PriceCharting':
                prices = scraper.get_price_history(self.card_name)
            elif name == 'Collectr':
                prices = scraper.get_card_prices(self.card_name)
            elif name == 'Mavin':
                prices = scraper.get_card_values(self.card_name)

            all_prices.extend(prices)
            self.progress_update.emit(int((i + 1) / total_scrapers * 100))

        self.status_update.emit("Analyzing data...")
        self.data_ready.emit({'card_name': self.card_name, 'prices': all_prices})

# Main GUI Application
class PokemonCardAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        # Use enhanced database manager with PostgreSQL if available, fallback to SQLite
        try:
            self.db_manager = EnhancedDatabaseManager(use_postgres=True)
        except Exception as e:
            print(f"PostgreSQL not available, using SQLite: {e}")
            self.db_manager = EnhancedDatabaseManager(use_postgres=False)

        self.analyzer = PriceAnalyzer()
        self.current_data = None
        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        self.setWindowTitle("Pokémon Card Investment Analyzer")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Pokémon Card Investment Analyzer")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Search Section
        search_layout = QHBoxLayout()

        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("Enter Pokémon card name (e.g., 'Charizard Base Set')")
        self.card_input.setFont(QFont("Arial", 11))
        search_layout.addWidget(self.card_input)

        self.graded_checkbox = QCheckBox("Include Graded Cards")
        self.graded_checkbox.setChecked(True)
        search_layout.addWidget(self.graded_checkbox)

        self.search_button = QPushButton("Analyze")
        self.search_button.clicked.connect(self.start_analysis)
        self.search_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        search_layout.addWidget(self.search_button)

        main_layout.addLayout(search_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 10))
        main_layout.addWidget(self.status_label)

        # Main Content Area
        self.tab_widget = QTabWidget()

        # Overview Tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "Overview")

        # Price Chart Tab
        self.chart_tab = self.create_chart_tab()
        self.tab_widget.addTab(self.chart_tab, "Price Chart")

        # Detailed Analysis Tab
        self.analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "Detailed Analysis")

        # Market Comparison Tab
        self.comparison_tab = self.create_comparison_tab()
        self.tab_widget.addTab(self.comparison_tab, "Market Comparison")

        main_layout.addWidget(self.tab_widget)

    def create_overview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Summary Cards
        cards_layout = QHBoxLayout()

        self.current_price_card = self.create_info_card("Current Market Price", "$0.00")
        cards_layout.addWidget(self.current_price_card)

        self.predicted_price_card = self.create_info_card("30-Day Prediction", "$0.00")
        cards_layout.addWidget(self.predicted_price_card)

        self.roi_card = self.create_info_card("Expected ROI", "0%")
        cards_layout.addWidget(self.roi_card)

        self.confidence_card = self.create_info_card("Confidence Score", "0%")
        cards_layout.addWidget(self.confidence_card)

        layout.addLayout(cards_layout)

        # Recommendation Section
        self.recommendation_label = QLabel("Recommendation: Awaiting Analysis")
        self.recommendation_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.recommendation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.recommendation_label)

        # Key Insights
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setMaximumHeight(200)
        layout.addWidget(QLabel("Key Insights:"))
        layout.addWidget(self.insights_text)

        layout.addStretch()
        return widget

    def create_info_card(self, title: str, value: str) -> QWidget:
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

    def create_chart_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Chart controls
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Time Range:"))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["1 Month", "3 Months", "6 Months", "1 Year", "All Time"])
        self.time_range_combo.currentTextChanged.connect(self.update_chart)
        controls_layout.addWidget(self.time_range_combo)

        controls_layout.addWidget(QLabel("Chart Type:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Line Chart", "Candlestick", "Scatter Plot"])
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        controls_layout.addWidget(self.chart_type_combo)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Chart Canvas
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        return widget

    def create_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Analysis Results Table
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(7)
        self.analysis_table.setHorizontalHeaderLabels([
            "Metric", "Value", "7-Day Change", "30-Day Change",
            "Volatility", "Trend", "Signal"
        ])
        self.analysis_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.analysis_table)

        # Statistical Summary
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        layout.addWidget(QLabel("Statistical Summary:"))
        layout.addWidget(self.stats_text)

        return widget

    def create_comparison_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Source Comparison Table
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(6)
        self.comparison_table.setHorizontalHeaderLabels([
            "Source", "Current Price", "Avg Price (30d)", "Min Price",
            "Max Price", "Data Points"
        ])
        self.comparison_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(QLabel("Price Comparison Across Sources:"))
        layout.addWidget(self.comparison_table)

        # Graded vs Ungraded Comparison
        graded_layout = QHBoxLayout()

        self.graded_stats = QTextEdit()
        self.graded_stats.setReadOnly(True)
        graded_layout.addWidget(self.graded_stats)

        self.ungraded_stats = QTextEdit()
        self.ungraded_stats.setReadOnly(True)
        graded_layout.addWidget(self.ungraded_stats)

        layout.addWidget(QLabel("Graded vs Ungraded Analysis:"))
        layout.addLayout(graded_layout)

        return widget

    def apply_dark_theme(self):
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
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        self.setPalette(dark_palette)

        # Additional styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5d61;
            }
            QLineEdit {
                padding: 8px;
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
                padding: 6px;
                border: 1px solid #555555;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3a3a3a;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                padding: 8px 16px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0d7377;
            }
        """)

    def start_analysis(self):
        card_name = self.card_input.text().strip()
        if not card_name:
            QMessageBox.warning(self, "Input Error", "Please enter a card name.")
            return

        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.data_thread = DataCollectionThread(card_name)
        self.data_thread.progress_update.connect(self.update_progress)
        self.data_thread.status_update.connect(self.update_status)
        self.data_thread.data_ready.connect(self.process_data)
        self.data_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)

    def process_data(self, data):
        self.current_data = data
        prices = data['prices']

        if not prices:
            QMessageBox.warning(self, "No Data", "No price data found for this card.")
            self.reset_ui()
            return

        # Prepare DataFrame using vectorized method
        df = self.analyzer.prepare_data_vectorized(prices)

        # Perform analysis using vectorized methods
        predicted_price, confidence_interval = self.analyzer.predict_future_price_vectorized(df)
        analysis_results = self.analyzer.calculate_investment_score(df, predicted_price, confidence_interval)

        # Update UI with results
        self.update_overview(analysis_results)
        self.update_chart_data(df)
        self.update_analysis_table(df, analysis_results)
        self.update_comparison_table(prices)

        # Save to enhanced database using vectorized batch insert
        price_data_list = [
            CardPrice(
                date=price_dict['date'],
                price=price_dict['price'],
                source=price_dict['source'],
                condition=price_dict.get('condition', 'Unknown'),
                graded=price_dict.get('graded', False)
            )
            for price_dict in prices
        ]
        self.db_manager.save_price_data_batch_vectorized(data['card_name'], price_data_list)

        # Save analysis results
        self.db_manager.save_analysis_results(data['card_name'], analysis_results)

        self.reset_ui()
        self.status_label.setText("Analysis complete!")

    def update_overview(self, results):
        # Update info cards
        current_price_label = self.current_price_card.findChild(QLabel, "Current Market Price_value")
        if current_price_label:
            current_price_label.setText(f"${results['current_price']:.2f}")

        predicted_price_label = self.predicted_price_card.findChild(QLabel, "30-Day Prediction_value")
        if predicted_price_label:
            predicted_price_label.setText(f"${results['predicted_price']:.2f}")

        roi_label = self.roi_card.findChild(QLabel, "Expected ROI_value")
        if roi_label:
            roi_label.setText(f"{results['roi']:.1f}%")
            if results['roi'] > 0:
                roi_label.setStyleSheet("color: #4caf50;")
            else:
                roi_label.setStyleSheet("color: #f44336;")

        confidence_label = self.confidence_card.findChild(QLabel, "Confidence Score_value")
        if confidence_label:
            confidence_label.setText(f"{results['confidence_score']:.1f}%")

        # Update recommendation
        self.recommendation_label.setText(f"Recommendation: {results['recommendation']}")
        if results['recommendation'] == "STRONG BUY":
            self.recommendation_label.setStyleSheet("color: #4caf50; background-color: #1b5e20; padding: 10px; border-radius: 5px;")
        elif results['recommendation'] == "BUY":
            self.recommendation_label.setStyleSheet("color: #8bc34a; background-color: #33691e; padding: 10px; border-radius: 5px;")
        elif results['recommendation'] == "HOLD":
            self.recommendation_label.setStyleSheet("color: #ffc107; background-color: #5d4037; padding: 10px; border-radius: 5px;")
        else:
            self.recommendation_label.setStyleSheet("color: #f44336; background-color: #b71c1c; padding: 10px; border-radius: 5px;")

        # Update insights
        insights = f"""
        • Current market trend: {results['trend'].replace('_', ' ').title()}
        • 95% Confidence Interval: ${results['confidence_interval'][0]:.2f} - ${results['confidence_interval'][1]:.2f}
        • This card shows {'strong potential for growth' if results['roi'] > 15 else 'moderate growth potential' if results['roi'] > 5 else 'limited growth potential'}
        • Based on historical data from multiple sources including TCGPlayer (primary authority)
        • {'Graded cards show higher returns' if results.get('graded_premium', False) else 'Consider both graded and ungraded options'}
        """
        self.insights_text.setText(insights)

    def update_chart_data(self, df):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Plot based on selected chart type
        chart_type = self.chart_type_combo.currentText()

        if chart_type == "Line Chart":
            ax.plot(df['date'], df['price'], 'b-', label='Actual Price', linewidth=2)
            if 'price_ma7' in df.columns and df['price_ma7'].notna().any():
                ax.plot(df['date'], df['price_ma7'], 'g--', label='7-Day MA', alpha=0.7)
            if 'price_ma30' in df.columns and df['price_ma30'].notna().any():
                ax.plot(df['date'], df['price_ma30'], 'r--', label='30-Day MA', alpha=0.7)
        elif chart_type == "Scatter Plot":
            ax.scatter(df['date'], df['price'], c='blue', alpha=0.6, s=30)
        else:  # Candlestick-like view
            ax.bar(df['date'], df['price'], width=0.8, alpha=0.6)

        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        ax.set_title(f'Price History - {self.current_data["card_name"]}')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Format x-axis
        self.figure.autofmt_xdate()

        self.canvas.draw()

    def update_analysis_table(self, df, results):
        metrics = [
            ("Current Price", f"${results['current_price']:.2f}", "", "", "", results['trend'], ""),
            ("Predicted Price (30d)", f"${results['predicted_price']:.2f}", "", "", "", "", ""),
            ("Expected ROI", f"{results['roi']:.1f}%", "", "", "", "", "BUY" if results['roi'] > 10 else "HOLD"),
            ("Confidence Score", f"{results['confidence_score']:.1f}%", "", "", "", "", ""),
            ("Average Daily Volume", f"${df['price'].mean():.2f}", "", "", "", "", ""),
            ("Price Volatility", f"${df['price'].std():.2f}", "", "", "", "", ""),
        ]

        self.analysis_table.setRowCount(len(metrics))
        for i, metric in enumerate(metrics):
            for j, value in enumerate(metric):
                item = QTableWidgetItem(str(value))
                self.analysis_table.setItem(i, j, item)

    def update_comparison_table(self, prices):
        # Group by source using pandas
        df = pd.DataFrame(prices)
        if df.empty:
            return

        source_stats = df.groupby('source')['price'].agg(['mean', 'min', 'max', 'count'])
        source_stats['current'] = df.groupby('source')['price'].last()

        self.comparison_table.setRowCount(len(source_stats))
        for i, (source, row) in enumerate(source_stats.iterrows()):
            self.comparison_table.setItem(i, 0, QTableWidgetItem(source))
            self.comparison_table.setItem(i, 1, QTableWidgetItem(f"${row['current']:.2f}"))
            self.comparison_table.setItem(i, 2, QTableWidgetItem(f"${row['mean']:.2f}"))
            self.comparison_table.setItem(i, 3, QTableWidgetItem(f"${row['min']:.2f}"))
            self.comparison_table.setItem(i, 4, QTableWidgetItem(f"${row['max']:.2f}"))
            self.comparison_table.setItem(i, 5, QTableWidgetItem(str(int(row['count']))))

        # Update graded vs ungraded stats
        if 'graded' in df.columns:
            graded_prices = df[df['graded'] == True]['price']
            ungraded_prices = df[df['graded'] == False]['price']

            if len(graded_prices) > 0:
                graded_text = f"""
                Graded Cards Statistics:
                • Average Price: ${graded_prices.mean():.2f}
                • Median Price: ${graded_prices.median():.2f}
                • Min/Max: ${graded_prices.min():.2f} - ${graded_prices.max():.2f}
                • Data Points: {len(graded_prices)}
                """
            else:
                graded_text = "No graded card data available"

            if len(ungraded_prices) > 0:
                ungraded_text = f"""
                Ungraded Cards Statistics:
                • Average Price: ${ungraded_prices.mean():.2f}
                • Median Price: ${ungraded_prices.median():.2f}
                • Min/Max: ${ungraded_prices.min():.2f} - ${ungraded_prices.max():.2f}
                • Data Points: {len(ungraded_prices)}
                """
            else:
                ungraded_text = "No ungraded card data available"

            self.graded_stats.setText(graded_text)
            self.ungraded_stats.setText(ungraded_text)

    def update_chart(self):
        if self.current_data:
            df = self.analyzer.prepare_data_vectorized(self.current_data['prices'])
            self.update_chart_data(df)

    def reset_ui(self):
        self.search_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    analyzer = PokemonCardAnalyzer()
    analyzer.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
