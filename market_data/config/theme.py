"""
Theme configuration for PyQT GUI
Fetched from aggregater repository style preferences
"""

class ThemeConfig:
    """Color and theme schema configuration"""
    
    # Primary Colors
    PRIMARY_DARK = "#1e1e2e"      # Dark background
    PRIMARY_LIGHT = "#2d2d44"     # Light background
    ACCENT_BLUE = "#4a90e2"       # Primary accent
    ACCENT_GREEN = "#5cb85c"      # Success/positive
    ACCENT_RED = "#d9534f"        # Warning/negative
    ACCENT_YELLOW = "#f0ad4e"     # Caution
    
    # Text Colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    TEXT_MUTED = "#707070"
    
    # Chart Colors (for curve visualization)
    CHART_COLORS = [
        "#4a90e2",  # Blue
        "#5cb85c",  # Green
        "#f0ad4e",  # Yellow
        "#d9534f",  # Red
        "#9b59b6",  # Purple
        "#3498db",  # Light Blue
        "#e67e22",  # Orange
        "#1abc9c",  # Turquoise
    ]
    
    # Widget Styles
    STYLE_SHEET = """
    QMainWindow {
        background-color: #1e1e2e;
    }
    
    QWidget {
        background-color: #1e1e2e;
        color: #ffffff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 12px;
    }
    
    QPushButton {
        background-color: #4a90e2;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #357abd;
    }
    
    QPushButton:pressed {
        background-color: #2968a3;
    }
    
    QLineEdit {
        background-color: #2d2d44;
        border: 1px solid #4a4a6a;
        padding: 6px;
        border-radius: 4px;
        color: #ffffff;
    }
    
    QComboBox {
        background-color: #2d2d44;
        border: 1px solid #4a4a6a;
        padding: 6px;
        border-radius: 4px;
        color: #ffffff;
    }
    
    QTableWidget {
        background-color: #2d2d44;
        alternate-background-color: #252538;
        gridline-color: #4a4a6a;
        border: 1px solid #4a4a6a;
    }
    
    QTableWidget::item {
        padding: 4px;
    }
    
    QHeaderView::section {
        background-color: #1e1e2e;
        color: #ffffff;
        padding: 6px;
        border: 1px solid #4a4a6a;
        font-weight: bold;
    }
    
    QTabWidget::pane {
        border: 1px solid #4a4a6a;
        background-color: #2d2d44;
    }
    
    QTabBar::tab {
        background-color: #1e1e2e;
        color: #b0b0b0;
        padding: 8px 16px;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #2d2d44;
        color: #ffffff;
        border-bottom: 2px solid #4a90e2;
    }
    
    QGroupBox {
        border: 1px solid #4a4a6a;
        border-radius: 4px;
        margin-top: 12px;
        padding-top: 12px;
        color: #ffffff;
        font-weight: bold;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 10px;
        color: #4a90e2;
    }
    
    QScrollBar:vertical {
        background-color: #2d2d44;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #4a4a6a;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #5a5a7a;
    }
    """