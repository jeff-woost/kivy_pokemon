"""
xVA Market Data Analyzer
Main application entry point for analyzing funding, credit, and IR curves
"""

import sys
import json
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("xVA Market Data Analyzer")
    app.setOrganizationName("Product Control")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()