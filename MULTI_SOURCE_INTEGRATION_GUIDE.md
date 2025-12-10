# Multi-Source Data Integration & Grade to Flip Feature Guide

## Overview
This guide documents the new multi-source data integration system and the "Grade to Flip" feature that helps identify profitable grading opportunities using data from 4 different sources.

## New Features

### 1. Multi-Source Data Collection

The system now collects and aggregates data from **4 independent sources**:

#### Data Sources:
1. **eBay** (`scrapers/ebay_scraper.py`)
   - Real sold listings
   - Historical transaction data
   - Grading information (PSA/BGS/CGC/SGC)
   - Sold dates and conditions

2. **PriceCharting** (`scrapers/pricecharting_scraper.py`)
   - Historical price data
   - Current market prices
   - Graded vs ungraded pricing
   - Chart data extraction

3. **PokeData.io** (`scrapers/pokedata_scraper.py`) - NEW
   - Set-level price trends
   - Individual card market data
   - Price history and trends
   - Popularity metrics
   - Sales volume data

4. **TCGPlayer** (`scrapers/tcgplayer_scraper.py`) - NEW
   - Comprehensive pricing (market, low, mid, high)
   - Sales velocity data
   - Listing counts
   - Price guide data

### 2. ScraperManager Enhancements

**File**: `scrapers/scraper_manager.py`

#### New Methods:

##### `get_aggregated_trend_data(card_name: str) -> Dict`
Aggregates and normalizes data from all 4 sources:
- Normalizes prices across different sources
- Calculates aggregate statistics
- Assesses data quality and confidence
- Detects price divergence for arbitrage opportunities

**Returns**:
```python
{
    'card_name': str,
    'sources': List[str],  # ['eBay', 'PriceCharting', 'PokeData.io', 'TCGPlayer']
    'total_data_points': int,
    'date_range': {'start': datetime, 'end': datetime},
    'price_by_source': Dict,  # Average prices per source
    'graded_vs_ungraded': Dict,  # Multiplier calculation
    'normalized_data': Dict,  # Normalized price data
    'trend_indicators': Dict,  # Price velocity, momentum
    'data_quality': Dict  # Confidence score, quality rating
}
```

### 3. Trend Detection Algorithm

**File**: `analysis/trend_detector.py`

The `TrendDetector` class analyzes trends across multiple sources using:

#### Trend Score Calculation (0-100)
Factors weighted by importance:
- **Price Velocity (40%)**: Rate of price change over time
- **Volume/Sales Momentum (20%)**: Data point count indicating market interest
- **Cross-Source Agreement (20%)**: How well sources agree on pricing
- **Historical Pattern (20%)**: Trend direction and volatility

#### Key Features:
1. **Cross-Source Price Analysis**
   - Aggregates data from multiple sources
   - Identifies pricing consensus
   - Detects outliers

2. **Price Velocity Calculation**
   - Measures rate of change
   - Compares recent vs historical prices
   - Indicates momentum direction

3. **Volume/Sales Momentum Detection**
   - Tracks listing counts
   - Monitors sales velocity
   - Identifies trending cards

4. **Price Divergence Detection**
   - Finds arbitrage opportunities
   - Identifies source discrepancies
   - Calculates potential profit from divergence

5. **Trend Prediction**
   - Predicts future price direction
   - Provides confidence levels
   - Generates BUY/SELL/HOLD recommendations

#### Example Usage:
```python
from analysis import TrendDetector
from scrapers import ScraperManager

detector = TrendDetector()
scraper_manager = ScraperManager()

# Get aggregated data
aggregated = scraper_manager.get_aggregated_trend_data("Charizard Base Set")

# Analyze trends
analysis = detector.analyze_multi_source_trends(aggregated)

print(f"Trend Score: {analysis['trend_score']:.1f}/100")
print(f"Recommendation: {analysis['prediction']['recommendation']}")
print(f"Confidence: {analysis['confidence_level']}")
```

### 4. Grade to Flip Feature

**File**: `ui/grade_to_flip_tab.py`

A dedicated tab for finding profitable grading opportunities using the **3x multiplier rule**.

#### The 3x Multiplier Rule

A card is worth grading if:
```
PSA 10 Price ≥ 3 × (Ungraded Price + $15)
```

Or equivalently, the **Grade to Flip Multiplier** must be ≥ 3.0:
```
Multiplier = PSA 10 Price / (Ungraded Price + Grading Cost)
```

**Where**:
- **$15** = Standard grading cost (PSA economy service)
- **3x** = Minimum multiplier ensuring meaningful profit margin

#### Why 3x?
- Accounts for grading cost ($15)
- Provides buffer for market fluctuations
- Ensures meaningful ROI
- Reduces risk of loss if card grades below PSA 10

#### UI Features:

1. **Filter Controls**
   - Minimum multiplier (default 3.0x)
   - Maximum ungraded price filter
   - Real-time filtering

2. **Opportunities Table**
   Columns:
   - Card Name
   - Set
   - Ungraded Price
   - PSA 10 Price
   - Grading Cost ($15)
   - Total Investment
   - **Multiplier** (color-coded)
   - Expected Profit
   - ROI %
   - Confidence Score
   - Worth Grading (✓/✗)

3. **Color Coding**
   - 🟢 Green (5x+): Excellent opportunities
   - 🟡 Yellow (3-5x): Good opportunities
   - 🔴 Red (<3x): Not recommended

4. **Action Buttons**
   - **Scan All Cards**: Discovers opportunities from database
   - **Refresh Prices**: Updates prices from all 4 sources

5. **Details Panel**
   - Investment breakdown
   - Profit analysis
   - Recommendation
   - Important notes

#### Example Calculations:

**Example 1: Profitable Card**
```
Ungraded Price: $100
Grading Cost: $15
Total Investment: $115
PSA 10 Price: $400

Multiplier = $400 / $115 = 3.48x ✓
Net Profit = $400 - $115 = $285
ROI = 247.8%
Worth Grading: YES
```

**Example 2: Not Profitable**
```
Ungraded Price: $75
Grading Cost: $15
Total Investment: $90
PSA 10 Price: $250

Multiplier = $250 / $90 = 2.78x ✗
Net Profit = $160 (but below 3x threshold)
ROI = 177.8%
Worth Grading: NO (doesn't meet 3x rule)
```

### 5. Database Updates

**File**: `enhanced_database.py`

#### New Tables:

##### `multi_source_prices`
Stores normalized prices from all sources:
```sql
CREATE TABLE multi_source_prices (
    id INTEGER PRIMARY KEY,
    card_name TEXT,
    source TEXT,  -- 'eBay', 'PriceCharting', 'PokeData.io', 'TCGPlayer'
    price REAL,
    normalized_price REAL,
    date_recorded TIMESTAMP,
    condition TEXT,
    graded BOOLEAN,
    grade_value REAL,
    data_quality_score REAL
)
```

##### `trend_analysis`
Stores trend detection results:
```sql
CREATE TABLE trend_analysis (
    id INTEGER PRIMARY KEY,
    card_name TEXT,
    trend_score REAL,  -- 0-100
    price_velocity REAL,
    momentum_strength TEXT,
    prediction_direction TEXT,
    confidence_level TEXT,
    sources_count INTEGER,
    divergence_detected BOOLEAN,
    analysis_date TIMESTAMP
)
```

#### New Methods:

- `save_multi_source_prices(prices: List[Dict])`: Save normalized multi-source data
- `save_trend_analysis(card_name: str, trend_data: Dict)`: Save trend analysis
- `get_grade_to_flip_opportunities(min_multiplier=3.0)`: Query cards meeting criteria
- `get_multi_source_data(card_name: str)`: Retrieve multi-source price data

### 6. Updated GradingAnalyzer

**File**: `analysis/grading_analyzer.py`

#### Key Changes:

1. **Updated Default Grading Cost**: $15 (from $35)
   ```python
   STANDARD_GRADING_COST = 15.0
   ```

2. **3x Multiplier Constant**:
   ```python
   MIN_MULTIPLIER = 3.0
   ```

3. **Grade to Flip Multiplier Calculation**:
   ```python
   total_investment = ungraded_price + grading_cost
   grade_to_flip_multiplier = psa10_price / total_investment
   worth_grading = grade_to_flip_multiplier >= MIN_MULTIPLIER
   ```

4. **Enhanced Return Data**:
   - Includes `total_investment`
   - Uses `grade_to_flip_multiplier` instead of simple price ratio
   - Consistent with 3x rule across all calculations

## Integration

### Main Application Updates

**File**: `pokemon_card_analyzer_enhanced.py`

1. **New Imports**:
   ```python
   from analysis import TrendDetector
   from ui import GradeToFlipTab
   ```

2. **New Component**:
   ```python
   self.trend_detector = TrendDetector()
   ```

3. **New Tab**:
   ```python
   self.grade_to_flip_tab = GradeToFlipTab(
       self.grading_analyzer,
       self.scraper_manager,
       self.db_manager
   )
   self.tab_widget.addTab(self.grade_to_flip_tab, "Grade to Flip")
   ```

## Usage Examples

### Example 1: Multi-Source Price Aggregation
```python
from scrapers import ScraperManager

manager = ScraperManager()

# Get data from all 4 sources
all_prices = manager.get_all_prices("Charizard Base Set")
print(f"Collected {len(all_prices)} prices from 4 sources")

# Get aggregated trend data
trend_data = manager.get_aggregated_trend_data("Charizard Base Set")
print(f"Data Quality: {trend_data['data_quality']['quality_rating']}")
print(f"Price Velocity: {trend_data['trend_indicators']['price_velocity_pct']:.1f}%")
```

### Example 2: Trend Detection
```python
from analysis import TrendDetector
from scrapers import ScraperManager

detector = TrendDetector()
manager = ScraperManager()

# Analyze trends
aggregated = manager.get_aggregated_trend_data("Pikachu Illustrator")
analysis = detector.analyze_multi_source_trends(aggregated)

print(f"Trend Score: {analysis['trend_score']:.1f}/100")
print(f"Momentum: {analysis['momentum_indicators']['momentum_strength']}")
print(f"Recommendation: {analysis['prediction']['recommendation']}")
print(f"Confidence: {analysis['confidence_level']}")
```

### Example 3: Grade to Flip Analysis
```python
from analysis import GradingAnalyzer

analyzer = GradingAnalyzer()  # Uses $15 grading cost by default

# Analyze opportunity
price_history = [
    {'price': 100, 'graded': False, 'date': '2024-01-01'},
    {'price': 400, 'graded': True, 'grade_value': 10, 'grade_company': 'PSA', 'date': '2024-01-02'}
]

analysis = analyzer.analyze_grading_opportunity(price_history)

print(f"Ungraded: ${analysis['ungraded_avg_price']:.2f}")
print(f"PSA 10: ${analysis['psa10_avg_price']:.2f}")
print(f"Total Investment: ${analysis['total_investment']:.2f}")
print(f"Multiplier: {analysis['multiplier']:.2f}x")
print(f"Net Profit: ${analysis['net_profit']:.2f}")
print(f"ROI: {analysis['roi_percentage']:.1f}%")
print(f"Worth Grading: {analysis['worth_grading']}")
```

### Example 4: Database Queries
```python
from enhanced_database import EnhancedDatabaseManager

db = EnhancedDatabaseManager()

# Get Grade to Flip opportunities
opportunities = db.get_grade_to_flip_opportunities(min_multiplier=3.0)
print(f"Found {len(opportunities)} opportunities")

for opp in opportunities[:5]:
    print(f"{opp['card_name']}: {opp['multiplier']:.2f}x, ${opp['net_profit']:.2f} profit")

# Save trend analysis
trend_data = {
    'trend_score': 75.5,
    'momentum_indicators': {'price_momentum': 12.5, 'momentum_strength': 'upward'},
    'prediction': {'direction': 'strong_upward', 'recommendation': 'BUY'},
    'confidence_level': 'high',
    'data_quality': {'sources_count': 4},
    'divergence_analysis': {'has_divergence': False}
}
db.save_trend_analysis("Charizard Base Set", trend_data)
```

## Best Practices

### 1. Data Collection
- Always use `get_all_prices()` to collect from all 4 sources
- Check data quality scores before making decisions
- Supplement real data with historical database records

### 2. Trend Analysis
- Require minimum 3 sources for high confidence
- Consider trend score above 60 for BUY signals
- Monitor price velocity for momentum trading

### 3. Grade to Flip Decisions
- **Always** use the 3x multiplier rule
- Account for the $15 grading cost
- Consider card condition requirements for PSA 10
- Factor in grading turnaround time (2-8 weeks)
- Be aware of market volatility

### 4. Risk Management
- Higher multipliers (5x+) = lower risk
- Verify prices across multiple sources
- Check confidence scores before investing
- Consider portfolio diversification

## Performance Considerations

### Rate Limiting
All scrapers implement rate limiting:
- Default: 2-4 seconds between requests
- Respects robots.txt
- Implements exponential backoff on errors

### Parallel Processing
- ScraperManager uses ThreadPoolExecutor
- Max 4 workers for 4 sources
- Parallel data collection reduces wait time

### Database Optimization
- Indexed queries for fast lookups
- Batch inserts for efficiency
- Cached results for repeated queries
- Vectorized operations with pandas

## Troubleshooting

### Issue: No opportunities found
**Solution**: Run "Scan All Cards" to populate the database with current market data.

### Issue: Low confidence scores
**Solution**: Ensure data is being collected from all 4 sources. Check scraper connectivity.

### Issue: Inconsistent multipliers
**Solution**: Verify that the $15 grading cost is being applied consistently. Check `GradingAnalyzer.STANDARD_GRADING_COST`.

### Issue: Missing trend data
**Solution**: Call `scraper_manager.get_aggregated_trend_data()` before running trend analysis.

## Future Enhancements

Potential improvements:
1. Real-time price alerts when cards cross 3x threshold
2. Machine learning for improved trend predictions
3. Historical accuracy tracking for recommendations
4. Integration with additional data sources
5. Automated portfolio optimization
6. Risk scoring for individual cards

## Testing

The implementation includes comprehensive logic testing:
- Grade to Flip formula validation
- Multi-source aggregation verification
- Multiplier calculation accuracy
- ROI computation correctness

Run tests:
```bash
python3 -m pytest tests/test_grade_to_flip.py
python3 -m pytest tests/test_trend_detector.py
python3 -m pytest tests/test_scrapers.py
```

## Conclusion

The multi-source data integration and Grade to Flip feature provide a comprehensive system for:
1. Collecting data from 4 independent sources
2. Analyzing trends with sophisticated algorithms
3. Identifying profitable grading opportunities
4. Making data-driven investment decisions

The 3x multiplier rule with $15 grading cost ensures that recommended cards have meaningful profit potential while accounting for all costs and risks.
