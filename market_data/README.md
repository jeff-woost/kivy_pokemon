# xVA Market Data Analyzer

A comprehensive PyQt-based application for analyzing xVA (Credit Valuation Adjustment) market data, focusing on funding curves, credit curves, and IR rate curves. This tool helps product control functions understand underlying movement of xVA PnL through visual analytics.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Data Format](#data-format)
- [Key Metrics](#key-metrics)
- [API Integration](#api-integration)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Multi-Source Data Loading**: Support for both REST API endpoints and local JSON/CSV files
- **Day-over-Day Analysis**: Calculate basis point movements between two trading days
- **Real-time Processing**: Asynchronous data loading with progress indicators
- **Curve Type Detection**: Automatic classification of funding, credit, and IR curves

### Visualization Capabilities
- **Line Charts**: Compare curves across different dates with overlay capabilities
- **Bar Charts**: Visualize basis point movements by tenor
- **Heatmaps**: Cross-sectional view of movements across curves and tenors
- **Distribution Plots**: Analyze rate distributions and identify outliers
- **Interactive Charts**: Zoom, pan, and export chart images

### Analysis Tools
- **Outlier Detection**: Configurable threshold-based identification of significant moves
- **Curve Shape Analysis**: Calculate slope, curvature, and steepening/flattening
- **Summary Statistics**: Comprehensive metrics for each curve and overall portfolio
- **Parallel Shift Analysis**: Identify systematic movements across tenors

### User Interface
- **Dark Theme**: Professional dark theme optimized for extended use
- **Tabbed Interface**: Organized views for different analysis perspectives
- **Responsive Design**: Scales appropriately for different screen sizes
- **Data Export**: Export analyzed data to CSV for further analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Windows/macOS/Linux operating system

### Step-by-Step Installation

1. **Clone the repository:**
```bash
git clone https://github.com/jeff-woost/xva-market-analyzer.git
cd xva-market-analyzer
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install required packages:**
```bash
pip install -r requirements.txt
```

4. **Verify installation:**
```bash
python -c "import PyQt5; import pandas; import matplotlib; print('All packages installed successfully')"
```

## Quick Start

1. **Launch the application:**
```bash
python main.py
```

2. **Load sample data:**
   - Select "Load from File" option
   - Use the provided sample data in `sample_data/` directory
   - Click "Load Data"

3. **View analysis:**
   - Navigate through tabs to see different visualizations
   - Adjust outlier threshold to highlight significant moves

## Usage Guide

### Loading Data

#### From API
1. Select "Load from API" checkbox
2. Enter API endpoints for two consecutive trading days:
   - Day 1: `https://api.example.com/market-data/2025-10-14`
   - Day 2: `https://api.example.com/market-data/2025-10-15`
3. Click "Load Data"

#### From Files
1. Select "Load from File" checkbox
2. Click "Browse" buttons to select JSON files
3. Supported formats: JSON, CSV
4. Click "Load Data"

### Analyzing Curves

#### Overview Tab
- View summary statistics for all curves
- Identify outliers exceeding threshold
- Quick assessment of market movements

#### Curve Analysis Tab
- Select specific curve from dropdown
- Compare curve shape between two days
- Visualize term structure changes

#### Movement Analysis Tab
- Bar chart of basis point movements
- Distribution analysis of rate changes
- Identify widening/tightening patterns

#### Heatmap Tab
- Cross-sectional view of all curves
- Identify correlated movements
- Spot patterns across curve families

### Exporting Results
1. Navigate to "Raw Data" tab
2. Click "Export to CSV"
3. Choose destination and filename
4. Data includes all calculated metrics

## Data Format

### Expected JSON Structure

```json
{
  "data": [
    {
      "batchReference": "122afbf-961a-462f-8c34-e8a852068ac0",
      "compoundingFrequency": "CONTINUOUS",
      "currency": "USD",
      "curveId": "SINGLENAME_BSPREAD_CP_TDBK_USSO_FVA_A",
      "dayCount": "ACT360",
      "extrapolation": "NEAR",
      "interpolation": "MONOTON-CONVEX",
      "rate": 0.001132,
      "tenorDays": 180,
      "valuationDate": "10/14/25"
    }
  ]
}
```

### CSV Format
The application also accepts CSV files with the following columns:
- `batchReference`: Unique identifier for the batch
- `compoundingFrequency`: Frequency of compounding (e.g., CONTINUOUS)
- `currency`: Currency code (e.g., USD, EUR)
- `curveId`: Unique identifier for the curve
- `dayCount`: Day count convention (e.g., ACT360)
- `extrapolation`: Extrapolation method
- `interpolation`: Interpolation method
- `rate`: Interest rate value
- `tenorDays`: Tenor in days
- `valuationDate`: Date of valuation

## Key Metrics

### Basis Point Calculations
- **BP Move**: `(Rate_Day2 - Rate_Day1) × 10,000`
- **Percentage Change**: `((Rate_Day2 - Rate_Day1) / Rate_Day1) × 100`

### Curve Metrics
- **Parallel Shift**: Average BP move across all tenors
- **Steepening**: `Long_End_Move - Short_End_Move`
- **Curvature**: Second derivative approximation at mid-point

### Statistical Measures
- **Mean**: Average rate or movement
- **Standard Deviation**: Volatility measure
- **Min/Max**: Range of movements
- **Outliers**: Moves exceeding threshold (default 50 bps)

## API Integration

### Supported Endpoints

```python
# Example API configuration
API_CONFIG = {
    "base_url": "https://api.marketdata.com",
    "endpoints": {
        "funding_curves": "/curves/funding/{date}",
        "credit_curves": "/curves/credit/{date}",
        "ir_curves": "/curves/ir/{date}"
    },
    "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN",
        "Content-Type": "application/json"
    }
}
```

### Authentication
The application supports:
- Bearer token authentication
- API key authentication
- Basic authentication

Configure in `config/api_config.py` (create if needed).

## Architecture

### Project Structure
```
xva-market-analyzer/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Documentation
├── PROJECT_STRUCTURE.md   # Detailed project structure
├── config/
│   └── theme.py          # UI theme configuration
├── data/
│   └── data_loader.py    # Data loading and parsing
├── analysis/
│   └── curve_analyzer.py # Curve analysis algorithms
├── visualization/
│   └── chart_widgets.py  # Chart components
├── gui/
│   └── main_window.py    # Main application window
└── sample_data/
    ├── day1_sample.json  # Sample data for testing
    └── day2_sample.json  # Sample data for testing
```

## Configuration

### Theme Customization
Edit `config/theme.py` to customize colors:

```python
PRIMARY_DARK = "#1e1e2e"    # Background color
ACCENT_BLUE = "#4a90e2"     # Primary accent
ACCENT_GREEN = "#5cb85c"    # Positive moves
ACCENT_RED = "#d9534f"      # Negative moves
```

### Analysis Parameters
Adjust in the application UI:
- **Outlier Threshold**: 1-500 basis points
- **Curve Selection**: Filter specific curves
- **Date Range**: Select analysis period

## Troubleshooting

### Common Issues

#### Application Won't Start
- Ensure Python 3.8+ is installed
- Verify all packages are installed: `pip install -r requirements.txt`
- Check for error messages in console

#### Data Loading Fails
- Verify JSON/CSV format matches expected structure
- Check API endpoint accessibility
- Ensure date format is MM/DD/YY or adjust in `data_loader.py`

#### Charts Not Displaying
- Update matplotlib: `pip install --upgrade matplotlib`
- Check PyQt5 backend: `python -c "import matplotlib; matplotlib.use('Qt5Agg')"`

#### Memory Issues with Large Datasets
- Process data in chunks
- Increase Python heap size
- Filter unnecessary curves before loading

### Error Logs
Application logs are written to console. For file logging, run:
```bash
python main.py > app.log 2>&1
```

## Performance Optimization

### Large Dataset Handling
- The application can handle datasets with 10,000+ data points
- For optimal performance, limit to 5,000 points per curve
- Use date filtering to reduce data volume

### Memory Management
- Data is cached for quick tab switching
- Clear cache by reloading data
- Monitor memory usage in Task Manager/Activity Monitor

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes and commit:**
   ```bash
   git commit -m "Add your feature description"
   ```
4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Check code style
flake8 .

# Format code
black .
```

### Code Style Guidelines
- Follow PEP 8 conventions
- Use type hints for function parameters
- Add docstrings to all classes and functions
- Keep line length under 100 characters

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Manual Testing Checklist
- [ ] Load data from API
- [ ] Load data from file
- [ ] Verify all chart types render
- [ ] Test outlier detection
- [ ] Export data to CSV
- [ ] Switch between tabs
- [ ] Test with different curve types

## Roadmap

### Version 1.1 (Q1 2026)
- [ ] Real-time data streaming
- [ ] Historical data analysis (>2 days)
- [ ] Portfolio-level analytics
- [ ] Risk metrics calculation

### Version 1.2 (Q2 2026)
- [ ] Machine learning predictions
- [ ] Automated anomaly detection
- [ ] Custom alert configuration
- [ ] Email notifications

### Version 2.0 (Q3 2026)
- [ ] Web-based interface
- [ ] Multi-user support
- [ ] Database integration
- [ ] Advanced reporting

## Support

For issues and questions:
- **GitHub Issues**: [https://github.com/jeff-woost/xva-market-analyzer/issues](https://github.com/jeff-woost/xva-market-analyzer/issues)
- **Email**: jeff.woost@example.com
- **Documentation**: [https://docs.xva-analyzer.com](https://docs.xva-analyzer.com)

## License

MIT License

Copyright (c) 2025 Jeff Woost

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

- PyQt5 team for the excellent GUI framework
- Matplotlib developers for visualization tools
- Pandas contributors for data manipulation capabilities
- The open-source community for continuous support

---

**Last Updated**: October 15, 2025
**Version**: 1.0.0
**Author**: Jeff Woost