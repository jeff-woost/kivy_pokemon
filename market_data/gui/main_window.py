"""
Main window for the xVA Market Data Analyzer application
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QPushButton, QLineEdit, QLabel, 
                            QGroupBox, QTableWidget, QTableWidgetItem, 
                            QComboBox, QSpinBox, QFileDialog, QMessageBox,
                            QSplitter, QTextEdit, QProgressBar, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import pandas as pd
from typing import Optional
from datetime import datetime
import traceback
import logging

from config.theme import ThemeConfig
from data.data_loader import MarketDataLoader
from analysis.curve_analyzer import CurveAnalyzer
from visualization.chart_widgets import (CurveLineChart, BasisPointMoveChart, 
                                        HeatmapChart, HistoricalTrendChart)

logger = logging.getLogger(__name__)

class DataLoadThread(QThread):
    """Thread for loading data without blocking UI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(object, object)
    error = pyqtSignal(str)
    
    def __init__(self, source1, source2, from_api=True):
        super().__init__()
        self.source1 = source1
        self.source2 = source2
        self.from_api = from_api
        self.loader = MarketDataLoader()
        
    def run(self):
        try:
            self.progress.emit("Loading day 1 data...")
            df1, df2 = self.loader.load_two_day_comparison(
                self.source1, self.source2, self.from_api
            )
            self.progress.emit("Data loaded successfully!")
            self.finished.emit(df1, df2)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.theme = ThemeConfig()
        self.data_loader = MarketDataLoader()
        self.analyzer = CurveAnalyzer()
        self.df_day1 = None
        self.df_day2 = None
        self.df_comparison = None
        
        self.init_ui()
        self.apply_theme()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("xVA Market Data Analyzer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add header section
        main_layout.addWidget(self.create_header_section())
        
        # Add main content area
        main_layout.addWidget(self.create_main_content())
        
        # Add status bar
        self.status_bar = QProgressBar()
        self.status_bar.setTextVisible(True)
        self.status_bar.setMaximum(100)
        main_layout.addWidget(self.status_bar)
        
    def create_header_section(self) -> QWidget:
        """Create the header section with data input controls"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        # Title
        title_label = QLabel("xVA Market Data Analyzer - Curve Movement Analysis")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {self.theme.ACCENT_BLUE}; padding: 10px;")
        header_layout.addWidget(title_label)
        
        # Data source group
        source_group = QGroupBox("Data Sources")
        source_layout = QVBoxLayout()
        
        # API/File selection
        source_type_layout = QHBoxLayout()
        self.api_radio = QCheckBox("Load from API")
        self.api_radio.setChecked(True)
        self.file_radio = QCheckBox("Load from File")
        source_type_layout.addWidget(QLabel("Source Type:"))
        source_type_layout.addWidget(self.api_radio)
        source_type_layout.addWidget(self.file_radio)
        source_type_layout.addStretch()
        source_layout.addLayout(source_type_layout)
        
        # Connect radio buttons
        self.api_radio.toggled.connect(self.on_source_type_changed)
        self.file_radio.toggled.connect(self.on_source_type_changed)
        
        # Day 1 input
        day1_layout = QHBoxLayout()
        day1_layout.addWidget(QLabel("Day 1:"))
        self.day1_input = QLineEdit()
        self.day1_input.setPlaceholderText("Enter API URL or file path for Day 1")
        day1_layout.addWidget(self.day1_input)
        self.day1_browse_btn = QPushButton("Browse")
        self.day1_browse_btn.clicked.connect(lambda: self.browse_file(self.day1_input))
        self.day1_browse_btn.setEnabled(False)
        day1_layout.addWidget(self.day1_browse_btn)
        source_layout.addLayout(day1_layout)
        
        # Day 2 input
        day2_layout = QHBoxLayout()
        day2_layout.addWidget(QLabel("Day 2:"))
        self.day2_input = QLineEdit()
        self.day2_input.setPlaceholderText("Enter API URL or file path for Day 2")
        day2_layout.addWidget(self.day2_input)
        self.day2_browse_btn = QPushButton("Browse")
        self.day2_browse_btn.clicked.connect(lambda: self.browse_file(self.day2_input))
        self.day2_browse_btn.setEnabled(False)
        day2_layout.addWidget(self.day2_browse_btn)
        source_layout.addLayout(day2_layout)
        
        # Load button
        load_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load Data")
        self.load_btn.clicked.connect(self.load_data)
        load_layout.addWidget(self.load_btn)
        
        # Analysis threshold
        load_layout.addWidget(QLabel("Outlier Threshold (bps):"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(1, 500)
        self.threshold_spin.setValue(50)
        load_layout.addWidget(self.threshold_spin)
        
        load_layout.addStretch()
        source_layout.addLayout(load_layout)
        
        source_group.setLayout(source_layout)
        header_layout.addWidget(source_group)
        
        return header_widget
    
    def create_main_content(self) -> QWidget:
        """Create the main content area with tabs"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "Overview")
        
        # Curve Analysis tab
        self.curve_tab = self.create_curve_analysis_tab()
        self.tab_widget.addTab(self.curve_tab, "Curve Analysis")
        
        # Movement Analysis tab
        self.movement_tab = self.create_movement_analysis_tab()
        self.tab_widget.addTab(self.movement_tab, "Movement Analysis")
        
        # Heatmap tab
        self.heatmap_tab = self.create_heatmap_tab()
        self.tab_widget.addTab(self.heatmap_tab, "Heatmap")
        
        # Data tab
        self.data_tab = self.create_data_tab()
        self.tab_widget.addTab(self.data_tab, "Raw Data")
        
        content_layout.addWidget(self.tab_widget)
        
        return content_widget
    
    def create_overview_tab(self) -> QWidget:
        """Create the overview tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary statistics
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        layout.addWidget(QLabel("Summary Statistics"))
        layout.addWidget(self.summary_text)
        
        # Outliers table
        layout.addWidget(QLabel("Significant Moves (Outliers)"))
        self.outliers_table = QTableWidget()
        self.outliers_table.setColumnCount(5)
        self.outliers_table.setHorizontalHeaderLabels(
            ["Curve ID", "Tenor", "BP Move", "Rate Day1", "Rate Day2"]
        )
        layout.addWidget(self.outliers_table)
        
        return tab
    
    def create_curve_analysis_tab(self) -> QWidget:
        """Create the curve analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Curve selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Curve:"))
        self.curve_selector = QComboBox()
        self.curve_selector.currentTextChanged.connect(self.update_curve_charts)
        selector_layout.addWidget(self.curve_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)
        
        # Charts
        splitter = QSplitter(Qt.Vertical)
        
        self.curve_line_chart = CurveLineChart()
        splitter.addWidget(self.curve_line_chart)
        
        self.curve_comparison_chart = CurveLineChart()
        splitter.addWidget(self.curve_comparison_chart)
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_movement_analysis_tab(self) -> QWidget:
        """Create the movement analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Movement charts
        splitter = QSplitter(Qt.Vertical)
        
        self.bp_move_chart = BasisPointMoveChart()
        splitter.addWidget(self.bp_move_chart)
        
        self.distribution_chart = HistoricalTrendChart()
        splitter.addWidget(self.distribution_chart)
        
        layout.addWidget(splitter)
        
        return tab
    
    def create_heatmap_tab(self) -> QWidget:
        """Create the heatmap tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.heatmap_chart = HeatmapChart()
        layout.addWidget(self.heatmap_chart)
        
        return tab
    
    def create_data_tab(self) -> QWidget:
        """Create the raw data tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Data table
        self.data_table = QTableWidget()
        layout.addWidget(self.data_table)
        
        # Export button
        export_layout = QHBoxLayout()
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_data)
        export_layout.addWidget(export_btn)
        export_layout.addStretch()
        layout.addLayout(export_layout)
        
        return tab
    
    def apply_theme(self):
        """Apply the dark theme to the application"""
        self.setStyleSheet(self.theme.STYLE_SHEET)
    
    def on_source_type_changed(self):
        """Handle source type selection change"""
        is_file = self.file_radio.isChecked()
        self.day1_browse_btn.setEnabled(is_file)
        self.day2_browse_btn.setEnabled(is_file)
        
        if self.api_radio.isChecked():
            self.file_radio.setChecked(False)
            self.day1_input.setPlaceholderText("Enter API URL for Day 1")
            self.day2_input.setPlaceholderText("Enter API URL for Day 2")
        else:
            self.api_radio.setChecked(False)
            self.day1_input.setPlaceholderText("Select JSON file for Day 1")
            self.day2_input.setPlaceholderText("Select JSON file for Day 2")
    
    def browse_file(self, line_edit: QLineEdit):
        """Browse for a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select JSON File", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        if file_path:
            line_edit.setText(file_path)
    
    def load_data(self):
        """Load data from specified sources"""
        source1 = self.day1_input.text()
        source2 = self.day2_input.text()
        
        if not source1 or not source2:
            QMessageBox.warning(self, "Warning", "Please specify both data sources.")
            return
        
        # Disable UI during loading
        self.load_btn.setEnabled(False)
        self.status_bar.setValue(50)
        
        # Create and start loading thread
        self.load_thread = DataLoadThread(source1, source2, self.api_radio.isChecked())
        self.load_thread.progress.connect(self.update_status)
        self.load_thread.finished.connect(self.on_data_loaded)
        self.load_thread.error.connect(self.on_load_error)
        self.load_thread.start()
    
    def update_status(self, message: str):
        """Update status bar with message"""
        self.status_bar.setFormat(message)
    
    def on_data_loaded(self, df1: pd.DataFrame, df2: pd.DataFrame):
        """Handle successful data load"""
        self.df_day1 = df1
        self.df_day2 = df2
        
        # Calculate comparisons
        self.df_comparison = self.analyzer.calculate_bp_move(df1, df2)
        
        # Update UI
        self.update_all_views()
        
        self.load_btn.setEnabled(True)
        self.status_bar.setValue(100)
        self.status_bar.setFormat("Data loaded successfully!")
        
        QMessageBox.information(self, "Success", "Data loaded and analyzed successfully!")
    
    def on_load_error(self, error_msg: str):
        """Handle data loading error"""
        self.load_btn.setEnabled(True)
        self.status_bar.setValue(0)
        self.status_bar.setFormat("Error loading data")
        QMessageBox.critical(self, "Error", f"Failed to load data:\n{error_msg}")
    
    def update_all_views(self):
        """Update all views with loaded data"""
        if self.df_comparison is None:
            return
        
        # Update curve selector
        if 'curve_id' in self.df_comparison.columns:
            curve_ids = sorted(self.df_comparison['curve_id'].unique())
            self.curve_selector.clear()
            self.curve_selector.addItems(curve_ids)
        
        # Update overview
        self.update_overview()
        
        # Update charts
        self.update_curve_charts()
        self.update_movement_charts()
        self.update_heatmap()
        
        # Update data table
        self.update_data_table()
    
    def update_overview(self):
        """Update overview tab"""
        # Summary statistics
        stats = self.analyzer.get_summary_statistics(self.df_comparison)
        summary_text = "=== Summary Statistics ===\n"
        summary_text += f"Total Curves: {stats.get('total_curves', 0)}\n"
        summary_text += f"Total Data Points: {stats.get('total_points', 0)}\n"
        summary_text += f"Average BP Move: {stats.get('avg_bp_move', 0):.2f}\n"
        summary_text += f"Std Dev: {stats.get('std_bp_move', 0):.2f}\n"
        summary_text += f"Max Move: {stats.get('max_bp_move', 0):.2f} bps\n"
        summary_text += f"Min Move: {stats.get('min_bp_move', 0):.2f} bps\n"
        summary_text += f"Widening: {stats.get('widening_count', 0)} points\n"
        summary_text += f"Tightening: {stats.get('tightening_count', 0)} points\n"
        self.summary_text.setText(summary_text)
        
        # Outliers
        threshold = self.threshold_spin.value()
        outliers = self.analyzer.identify_outliers(self.df_comparison, threshold)
        self.outliers_table.setRowCount(len(outliers))
        
        for i, (_, row) in enumerate(outliers.iterrows()):
            self.outliers_table.setItem(i, 0, QTableWidgetItem(str(row.get('curve_id', ''))))
            self.outliers_table.setItem(i, 1, QTableWidgetItem(str(row.get('tenor_days', ''))))
            self.outliers_table.setItem(i, 2, QTableWidgetItem(f"{row.get('bp_move', 0):.2f}"))
            self.outliers_table.setItem(i, 3, QTableWidgetItem(f"{row.get('rate_day1', 0):.4f}"))
            self.outliers_table.setItem(i, 4, QTableWidgetItem(f"{row.get('rate_day2', 0):.4f}"))
    
    def update_curve_charts(self):
        """Update curve analysis charts"""
        curve_id = self.curve_selector.currentText()
        if not curve_id or self.df_day1 is None or self.df_day2 is None:
            return
        
        # Update comparison chart
        self.curve_comparison_chart.plot_curve_comparison(
            self.df_day1, self.df_day2, curve_id, 
            labels=('Day 1', 'Day 2')
        )
        
        # Update line chart with multiple curves
        if 'curve_id' in self.df_day1.columns:
            curve_ids = self.df_day1['curve_id'].unique()[:5]  # Show first 5 curves
            self.curve_line_chart.plot_curves(self.df_day1, curve_ids, "Day 1 Curves")
    
    def update_movement_charts(self):
        """Update movement analysis charts"""
        curve_id = self.curve_selector.currentText()
        
        if self.df_comparison is not None:
            self.bp_move_chart.plot_bp_moves(self.df_comparison, curve_id)
        
        if self.df_day1 is not None:
            self.distribution_chart.plot_rate_distribution(self.df_day1, curve_id)
    
    def update_heatmap(self):
        """Update heatmap chart"""
        if self.df_comparison is not None:
            self.heatmap_chart.plot_movement_heatmap(self.df_comparison)
    
    def update_data_table(self):
        """Update raw data table"""
        if self.df_comparison is None:
            return
        
        # Set up table
        self.data_table.setRowCount(len(self.df_comparison))
        self.data_table.setColumnCount(len(self.df_comparison.columns))
        self.data_table.setHorizontalHeaderLabels(self.df_comparison.columns.tolist())
        
        # Populate table
        for i in range(len(self.df_comparison)):
            for j, col in enumerate(self.df_comparison.columns):
                value = self.df_comparison.iloc[i, j]
                if pd.isna(value):
                    item = QTableWidgetItem("")
                elif isinstance(value, float):
                    item = QTableWidgetItem(f"{value:.4f}")
                else:
                    item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
    
    def export_data(self):
        """Export comparison data to CSV"""
        if self.df_comparison is None:
            QMessageBox.warning(self, "Warning", "No data to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                self.df_comparison.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data:\n{str(e)}")