# xVA Market Data Analyzer - Project Structure

## Overview
This document outlines the complete structure and architecture of the xVA Market Data Analyzer application, a PyQt5-based tool for analyzing funding curves, credit curves, and IR rate curves to help product control functions understand xVA PnL movements.

## Directory Structure

```
xva-market-analyzer/
│
├── main.py                     # Application entry point
├── requirements.txt            # Python package dependencies
├── requirements-dev.txt        # Development dependencies
├── README.md                   # User documentation
├── PROJECT_STRUCTURE.md        # This file - architectural documentation
├── LICENSE                     # MIT License
├── .gitignore                 # Git ignore patterns
├── setup.py                   # Package setup configuration
│
├── config/                    # Configuration modules
│   ├── __init__.py
│   ├── theme.py              # UI theme and color scheme
│   ├── api_config.py         # API configuration settings
│   └── settings.py           # Application settings
│
├── data/                      # Data handling modules
│   ├── __init__.py
│   ├── data_loader.py        # JSON/CSV data loading and parsing
│   ├── data_validator.py     # Data validation and cleaning
│   └── cache_manager.py      # Data caching functionality
│
├── analysis/                  # Analysis and calculation modules
│   ├── __init__.py
│   ├── curve_analyzer.py     # Core curve analysis algorithms
│   ├── metrics_calculator.py # Financial metrics calculations
│   └── outlier_detector.py   # Outlier detection algorithms
│
├── visualization/             # Visualization components
│   ├── __init__.py
│   ├── chart_widgets.py      # Chart widget implementations
│   ├── chart_styles.py       # Chart styling configurations
│   └── export_manager.py     # Chart export functionality
│
├── gui/                       # GUI components
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   ├── dialogs.py            # Dialog windows
│   ├── widgets.py            # Custom widget components
│   └── tabs/                 # Tab implementations
│       ├── __init__.py
│       ├── overview_tab.py
│       ├── curve_tab.py
│       ├── movement_tab.py
│       ├── heatmap_tab.py
│       └── data_tab.py
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── date_utils.py         # Date handling utilities
│   ├── file_utils.py         # File I/O utilities
│   └── math_utils.py         # Mathematical utilities
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── unit/                 # Unit tests
│   │   ├── test_data_loader.py
│   │   ├── test_analyzer.py
│   │   └── test_charts.py
│   ├── integration/          # Integration tests
│   │   └── test_workflow.py
│   └── fixtures/             # Test data fixtures
│       ├── sample_data.json
│       └── expected_results.json
│
├── sample_data/              # Sample data for testing
│   ├── funding_curve_day1.json
│   ├── funding_curve_day2.json
│   ├── credit_curve_day1.json
│   ├── credit_curve_day2.json
│   ├── ir_curve_day1.json
│   └── ir_curve_day2.json
│
├── docs/                     # Additional documentation
│   ├── api_reference.md     # API reference guide
│   ├── user_manual.md       # Detailed user manual
│   └── developer_guide.md   # Developer documentation
│
└── resources/                # Application resources
    ├── icons/               # Application icons
    ├── images/              # Images and logos
    └── styles/              # QSS stylesheets
```

## Module Descriptions

### Core Application (`main.py`)
- **Purpose**: Entry point for the application
- **Responsibilities**:
  - Initialize QApplication
  - Set up logging configuration
  - Create and display main window
  - Handle application-level exceptions

### Configuration (`config/`)

#### `theme.py`
- **Purpose**: Define UI color scheme and styling
- **Key Components**:
  - `ThemeConfig` class with color definitions
  - Chart color palettes
  - QSS stylesheet strings
  - Theme switching capability

#### `api_config.py`
- **Purpose**: Manage API endpoint configurations
- **Key Components**:
  - API base URLs
  - Authentication settings
  - Request timeout configurations
  - Rate limiting parameters

#### `settings.py`
- **Purpose**: Application-wide settings
- **Key Components**:
  - Default analysis parameters
  - File paths and directories
  - User preferences
  - Performance settings

### Data Handling (`data/`)

#### `data_loader.py`
- **Purpose**: Load and parse market data from various sources
- **Key Classes**:
  - `MarketDataLoader`: Main data loading class
- **Key Methods**:
  - `fetch_json_from_api()`: Retrieve data from API
  - `load_from_file()`: Load local JSON/CSV files
  - `parse_market_data()`: Convert to DataFrame
  - `classify_curve_type()`: Identify curve types
  - `load_two_day_comparison()`: Load comparative data

#### `data_validator.py`
- **Purpose**: Validate and clean input data
- **Key Functions**:
  - `validate_json_structure()`: Check JSON format
  - `validate_required_fields()`: Ensure required fields exist
  - `clean_data()`: Remove invalid entries
  - `standardize_dates()`: Normalize date formats

#### `cache_manager.py`
- **Purpose**: Manage data caching for performance
- **Key Classes**:
  - `CacheManager`: Handle data caching
- **Key Methods**:
  - `store_data()`: Cache processed data
  - `retrieve_data()`: Get cached data
  - `clear_cache()`: Remove cached entries
  - `is_cache_valid()`: Check cache validity

### Analysis (`analysis/`)

#### `curve_analyzer.py`
- **Purpose**: Core analysis algorithms for curve data
- **Key Classes**:
  - `CurveAnalyzer`: Main analysis class
- **Key Methods**:
  - `calculate_bp_move()`: Compute basis point movements
  - `analyze_curve_shape()`: Determine curve characteristics
  - `identify_outliers()`: Find significant moves
  - `calculate_parallel_shift()`: Measure parallel shifts
  - `calculate_curve_steepening()`: Measure steepening/flattening
  - `get_summary_statistics()`: Generate summary metrics

#### `metrics_calculator.py`
- **Purpose**: Calculate financial metrics
- **Key Functions**:
  - `calculate_dv01()`: Dollar value of 01
  - `calculate_convexity()`: Curve convexity
  - `calculate_duration()`: Modified duration
  - `calculate_spread()`: Spread calculations

#### `outlier_detector.py`
- **Purpose**: Advanced outlier detection
- **Key Functions**:
  - `detect_statistical_outliers()`: Statistical methods
  - `detect_pattern_breaks()`: Pattern recognition
  - `classify_outlier_type()`: Categorize outliers

### Visualization (`visualization/`)

#### `chart_widgets.py`
- **Purpose**: Implement chart components
- **Key Classes**:
  - `ChartWidget`: Base chart class
  - `CurveLineChart`: Line chart for curves
  - `BasisPointMoveChart`: Bar chart for BP moves
  - `HeatmapChart`: Heatmap visualization
  - `HistoricalTrendChart`: Distribution charts
- **Key Methods**:
  - `plot_curves()`: Render curve lines
  - `plot_bp_moves()`: Display BP movements
  - `plot_movement_heatmap()`: Create heatmaps
  - `plot_rate_distribution()`: Show distributions

#### `chart_styles.py`
- **Purpose**: Define chart styling parameters
- **Key Components**:
  - Color schemes for different chart types
  - Font configurations
  - Grid and axis styles
  - Legend positioning

#### `export_manager.py`
- **Purpose**: Handle chart and data exports
- **Key Functions**:
  - `export_to_image()`: Save charts as images
  - `export_to_pdf()`: Generate PDF reports
  - `export_to_excel()`: Create Excel workbooks

### GUI Components (`gui/`)

#### `main_window.py`
- **Purpose**: Main application window
- **Key Classes**:
  - `MainWindow`: Primary QMainWindow
  - `DataLoadThread`: Async data loading
- **Key Methods**:
  - `init_ui()`: Initialize interface
  - `create_header_section()`: Build header
  - `create_main_content()`: Build content area
  - `load_data()`: Initiate data loading
  - `update_all_views()`: Refresh displays

#### `dialogs.py`
- **Purpose**: Dialog windows for user interaction
- **Key Classes**:
  - `SettingsDialog`: Application settings
  - `AboutDialog`: About information
  - `ExportDialog`: Export options
  - `FilterDialog`: Data filtering

#### `widgets.py`
- **Purpose**: Custom widget components
- **Key Classes**:
  - `DateRangeSelector`: Date selection
  - `CurveSelector`: Curve filtering
  - `ThresholdSlider`: Threshold adjustment
  - `StatusIndicator`: Status display

#### `tabs/` (Individual Tab Modules)
Each tab module contains:
- Tab-specific UI layout
- Data binding logic
- Update methods
- Event handlers

### Utilities (`utils/`)

#### `date_utils.py`
- **Purpose**: Date manipulation utilities
- **Key Functions**:
  - `parse_date()`: Parse various date formats
  - `calculate_business_days()`: Business day calculations
  - `get_tenor_from_days()`: Convert days to tenor labels

#### `file_utils.py`
- **Purpose**: File handling utilities
- **Key Functions**:
  - `read_json_file()`: Read JSON files
  - `read_csv_file()`: Read CSV files
  - `write_csv_file()`: Write CSV files
  - `validate_file_path()`: Path validation

#### `math_utils.py`
- **Purpose**: Mathematical utilities
- **Key Functions**:
  - `interpolate_curve()`: Curve interpolation
  - `calculate_percentile()`: Percentile calculations
  - `smooth_curve()`: Curve smoothing algorithms

## Data Flow

### 1. Data Input Flow
```
User Input (API/File) → DataLoader → Validator → Parser → DataFrame
```

### 2. Analysis Flow
```
DataFrame → CurveAnalyzer → Metrics Calculator → Results DataFrame
```

### 3. Visualization Flow
```
Results DataFrame → Chart Widgets → Matplotlib Canvas → PyQt Display
```

### 4. Export Flow
```
Analyzed Data → Export Manager → File System (CSV/PDF/Image)
```

## Key Design Patterns

### 1. Model-View Pattern
- **Model**: Data and analysis modules
- **View**: GUI and visualization components
- **Separation**: Clean separation of concerns

### 2. Observer Pattern
- Signal/slot mechanism for UI updates
- Event-driven architecture

### 3. Factory Pattern
- Chart creation based on type
- Dynamic tab generation

### 4. Singleton Pattern
- Configuration management
- Cache manager instance

## Threading Model

### Main Thread
- UI rendering and updates
- User interaction handling
- Chart rendering

### Worker Threads
- Data loading from API/files
- Heavy calculations
- Export operations

## Error Handling Strategy

### Levels of Error Handling
1. **Data Level**: Validation and cleaning
2. **Analysis Level**: Calculation exceptions
3. **UI Level**: User-friendly error messages
4. **Application Level**: Global exception handling

### Error Recovery
- Graceful degradation
- Partial data processing
- User notification system
- Automatic retry for API calls

## Performance Considerations

### Memory Management
- Lazy loading of data
- Efficient DataFrame operations
- Chart caching mechanisms
- Memory cleanup on tab switches

### Optimization Techniques
- Vectorized calculations using NumPy
- DataFrame optimizations with Pandas
- Matplotlib backend optimization
- Asynchronous data loading

## Security Considerations

### Data Security
- Secure API authentication
- Input validation
- SQL injection prevention (if database added)
- Sensitive data handling

### Application Security
- Error message sanitization
- Path traversal prevention
- Rate limiting for API calls

## Extensibility Points

### Adding New Curve Types
1. Update `classify_curve_type()` in data_loader.py
2. Add specific analysis methods
3. Create specialized visualizations

### Adding New Analysis Methods
1. Extend `CurveAnalyzer` class
2. Add new metric calculations
3. Update UI to display results

### Adding New Data Sources
1. Implement new loader in data module
2. Add validation rules
3. Update UI for source selection

## Testing Strategy

### Unit Testing
- Test individual functions
- Mock external dependencies
- Validate calculations

### Integration Testing
- Test complete workflows
- API integration tests
- File I/O tests

### UI Testing
- Manual testing checklist
- Automated UI tests (optional)
- Cross-platform testing

## Deployment Considerations

### Packaging
- PyInstaller for executable creation
- Include all dependencies
- Resource file packaging

### Distribution
- Windows: MSI installer
- macOS: DMG package
- Linux: AppImage or snap

### Updates
- Version checking mechanism
- Auto-update capability (future)
- Migration scripts for settings

## Maintenance Guidelines

### Code Maintenance
- Follow PEP 8 style guide
- Maintain comprehensive docstrings
- Regular dependency updates
- Performance profiling

### Documentation Maintenance
- Keep README current
- Update API documentation
- Maintain changelog
- User guide updates

## Future Enhancements

### Short Term (v1.1)
- Real-time data streaming
- Additional curve types
- Enhanced filtering options
- Batch processing capability

### Medium Term (v1.2)
- Machine learning integration
- Predictive analytics
- Custom alert system
- Report scheduling

### Long Term (v2.0)
- Web-based interface
- Multi-user support
- Database backend
- Cloud deployment

---

**Document Version**: 1.0.0
**Last Updated**: October 15, 2025
**Maintained By**: Jeff Woost