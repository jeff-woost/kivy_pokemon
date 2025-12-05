#!/usr/bin/env python3
"""
Pokemon Card Investment Analyzer - Main Application
Enhanced with real scraping, backtesting, and grading analysis
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Import our main window
from pokemon_card_analyzer_enhanced import PokemonCardAnalyzerEnhanced

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pokemon_analyzer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("Pokemon Card Investment Analyzer")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create and show main window
    window = PokemonCardAnalyzerEnhanced()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
