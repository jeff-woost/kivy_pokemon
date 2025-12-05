# Pokemon Card Investment Analyzer - Enhanced Edition

A comprehensive Pokemon card investment analysis tool with real-time data scraping, inception-to-date backtesting, and PSA 10 grading multiplier analysis.

## Features

### 🔍 Real Data Scraping
- **eBay.com**: Scrapes actual sold listings for real transaction prices
- **PriceCharting.com**: Historical price data from card inception to current date
- Proper rate limiting and error handling
- Automatic fallback to mock data when scraping fails

### 📊 Inception-to-Date Backtesting
- Analyzes cards from first available date until now
- Calculates comprehensive historical metrics:
  - Mean and median prices over card lifetime
  - Standard deviation and volatility
  - Sharpe ratio for risk-adjusted returns
  - Total and annualized returns
  - Support and resistance levels
- Trend analysis (upward/downward/stable)
- Trading strategy backtesting with win rate calculation

### 💎 PSA 10 Grading Multiplier Analysis
- Identifies cards with 3x+ grading multipliers
- Calculates:
  - Average ungraded vs PSA 10 prices
  - Grading cost considerations ($20-50 per card)
  - Net profit potential after grading
  - ROI percentage
- Smart recommendations (EXCELLENT/VERY GOOD/GOOD/MARGINAL/NOT RECOMMENDED)
- Filters to show only profitable grading opportunities

### 📈 BUY/SELL/HOLD Signal Generation
- Statistical analysis based on:
  - Current price vs mean price
  - Standard deviation bands
  - Historical trends and momentum
- Signals generated at various price points
- Confidence scores for each signal
- Real-time alerts when signals change

### 🎨 PyQt6 User Interface
- **Overview Tab**: Current signals and key metrics at a glance
- **Backtesting Tab**: Complete historical analysis with performance metrics
- **Grading Opportunities Tab**: Cards worth grading with profit potential
- **Price Charts Tab**: 
  - Price history with mean/std dev bands
  - Graded vs ungraded price comparison
  - Trading signals overlay
- Modern dark theme throughout
- Real-time progress indicators

### 💾 Database Features
- PostgreSQL or SQLite support (automatic fallback)
- Stores:
  - Complete price history (graded and ungraded)
  - Backtesting results
  - Grading multiplier snapshots
  - Trading signals history
  - Card metadata including inception dates
- Optimized with indexes for fast queries
- LZ4 compression for caching

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, will use SQLite if not available)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Optional: PostgreSQL Setup
```bash
# Start PostgreSQL with Docker
docker-compose up -d
```

## Usage

### Run the Application
```bash
python main.py
```

### Analyze a Card
1. Enter a Pokemon card name (e.g., "Charizard Base Set")
2. Click "Analyze Card"
3. Wait for comprehensive analysis to complete
4. View results across all tabs

### Features in Action

#### Overview Tab
- See current BUY/SELL/HOLD signal
- View signals at different price points
- Check key investment metrics

#### Backtesting Tab
- Review historical performance from inception
- See total and annualized returns
- Examine trading strategy backtest results
- View historical BUY/SELL/HOLD signals

#### Grading Opportunities Tab
- Filter by minimum multiplier (2x, 3x, 4x, 5x)
- Sort by ROI or profit potential
- See which cards are worth grading

#### Price Charts Tab
- **Price History with Bands**: Shows mean price line with ±1 std dev bands
- **Graded vs Ungraded**: Compare graded and ungraded price trends
- **Signals Overlay**: See where BUY/SELL signals occurred historically

## Project Structure

```
├── main.py                              # Application entry point
├── pokemon_card_analyzer_enhanced.py    # Main PyQt6 application
├── pokemon_card_analyzer_fixed.py       # Original implementation (legacy)
├── enhanced_database.py                 # Database manager
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py                  # Base scraper with rate limiting
│   ├── ebay_scraper.py                  # Real eBay scraper
│   ├── pricecharting_scraper.py         # Real PriceCharting scraper
│   └── scraper_manager.py               # Coordinates all scrapers
├── analysis/
│   ├── __init__.py
│   ├── backtesting.py                   # Inception-to-date backtesting engine
│   ├── grading_analyzer.py              # PSA 10 multiplier analysis
│   └── signals.py                       # BUY/SELL/HOLD signal generator
├── ui/
│   ├── __init__.py
│   ├── grading_tab.py                   # Grading opportunities UI
│   ├── backtesting_tab.py               # Backtesting results UI
│   └── charts.py                        # Enhanced chart widgets
├── requirements.txt                     # Python dependencies
├── docker-compose.yml                   # PostgreSQL/Redis services
└── README.md                            # This file
```

## Technical Details

### Backtesting Methodology
The backtesting engine analyzes cards from their inception date (first recorded price) to the current date:

1. **Data Collection**: Gathers all available price data
2. **Statistical Analysis**: Calculates mean, std dev, volatility
3. **Signal Generation**: Generates BUY signals when price < mean - 1σ, SELL when price > mean + 1σ
4. **Strategy Testing**: Backtests a simple mean-reversion strategy
5. **Performance Metrics**: Calculates returns, Sharpe ratio, win rate

### Grading Analysis Algorithm
```python
multiplier = avg_psa10_price / avg_ungraded_price
net_profit = avg_psa10_price - avg_ungraded_price - grading_cost
roi = (net_profit / (avg_ungraded_price + grading_cost)) * 100

if multiplier >= 5.0 and net_profit >= 200:
    recommendation = "EXCELLENT"
elif multiplier >= 4.0 and net_profit >= 100:
    recommendation = "VERY GOOD"
elif multiplier >= 3.0 and net_profit >= 50:
    recommendation = "GOOD"
else:
    recommendation = "NOT RECOMMENDED"
```

### Signal Generation
Signals are based on z-score (standard deviations from mean):
- **BUY**: z-score < -1.0 (price is more than 1 std dev below mean)
- **SELL**: z-score > 1.0 (price is more than 1 std dev above mean)
- **HOLD**: -1.0 ≤ z-score ≤ 1.0

Confidence is adjusted based on:
- Magnitude of z-score
- Current trend direction
- Historical volatility

## Data Sources

### eBay
- Sold listings with actual transaction prices
- Grading information extracted from titles
- Sold dates for historical tracking

### PriceCharting
- Long-term historical price data
- Card inception dates
- Graded vs ungraded pricing
- Market trend data

## Database Schema

### Tables
- `card_prices`: All price data (graded and ungraded)
- `analysis_results`: General analysis results
- `backtesting_results`: Inception-to-date backtesting metrics
- `grading_multipliers`: PSA 10 multiplier snapshots
- `trading_signals`: BUY/SELL/HOLD signal history
- `card_metadata`: Card information and inception dates

## Performance Optimizations

- **Vectorized Operations**: Pandas/NumPy for fast calculations
- **Database Indexes**: Optimized queries for card name, date ranges
- **LZ4 Compression**: Cached data compression
- **Parallel Scraping**: Multiple sources scraped concurrently
- **Connection Pooling**: Efficient database connections

## Troubleshooting

### PostgreSQL Connection Issues
If PostgreSQL fails to connect, the app automatically falls back to SQLite:
```
PostgreSQL not available, using SQLite
```

### No Data Found
If no price data is found:
1. Check card name spelling
2. Try a more popular card first
3. Check internet connection for scraping

### Slow Performance
- First run takes longer (scraping data)
- Subsequent runs are faster (cached data)
- Consider running PostgreSQL for better performance

## Future Enhancements

- [ ] Export analysis to CSV/Excel
- [ ] Portfolio tracking feature
- [ ] Alert system for price changes
- [ ] Card discovery mode (auto-scan for opportunities)
- [ ] Machine learning price predictions
- [ ] Multi-card batch analysis
- [ ] Price alert notifications

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is for educational purposes. Please respect the terms of service of all data sources.

## Disclaimer

This tool is for informational purposes only. Investment decisions should be made based on your own research and risk tolerance. Historical performance does not guarantee future results. Grading outcomes can vary based on card condition.