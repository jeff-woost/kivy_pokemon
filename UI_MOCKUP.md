# Grade to Flip Tab - UI Mockup

## Layout Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Pokemon Card Investment Analyzer - Enhanced Edition                            │
│  Real-time Scraping | Backtesting | PSA 10 Analysis                            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│  Card Name: [____________________]  [Analyze Card]  [Discover 3x+ Opportunities]│
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│ ┌─────┬───────────┬─────────────┬────────┬──────────────┐                      │
│ │ Tab │ Tab       │ Tab         │ Tab    │ [Grade to    │                      │
│ │  1  │  2        │  3          │  4     │   Flip]      │                      │
│ └─────┴───────────┴─────────────┴────────┴──────────────┘                      │
│                                                                                  │
│  Grade to Flip Opportunities                                                    │
│  ══════════════════════════════                                                 │
│  Find cards worth grading for profit. A card is worth grading if:              │
│  PSA 10 Price ≥ 3× (Ungraded Price + $15)                                      │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │ Min Multiplier: [3.0▼]  Max Ungraded Price: [$1000]                      │  │
│  │                                [Scan All Cards]  [Refresh Prices]        │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │ Total Opportunities: 12 | Total Investment: $1,380.00 |                  │  │
│  │ Total Expected Profit: $3,420.00 | Avg Multiplier: 4.2x | Avg ROI: 248%  │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │ Card Name              │ Set     │ Ungraded │ PSA 10 │ Cost │ Investment││  │
│  ├────────────────────────┼─────────┼──────────┼────────┼──────┼───────────┤│  │
│  │ Charizard Base Set     │ Base    │ $100.00  │ $580.00│ $15  │ $115.00   ││  │
│  │ Pikachu Illustrator    │ Promo   │ $250.00  │ $1350  │ $15  │ $265.00   ││  │
│  │ Blastoise Base Set     │ Base    │ $75.00   │ $380.00│ $15  │ $90.00    ││  │
│  │ Alakazam Base Set      │ Base    │ $60.00   │ $285.00│ $15  │ $75.00    ││  │
│  │ Venusaur Base Set      │ Base    │ $95.00   │ $465.00│ $15  │ $110.00   ││  │
│  │ Mew Delta Species      │ Holon   │ $120.00  │ $540.00│ $15  │ $135.00   ││  │
│  │ Rayquaza Gold Star     │ Deoxys  │ $180.00  │ $790.00│ $15  │ $195.00   ││  │
│  │ Espeon Gold Star       │ POP 5   │ $150.00  │ $645.00│ $15  │ $165.00   ││  │
│  │ Umbreon Gold Star      │ POP 5   │ $175.00  │ $740.00│ $15  │ $190.00   ││  │
│  │ Lugia Neo Genesis      │ Neo Gen │ $85.00   │ $385.00│ $15  │ $100.00   ││  │
│  │ Ho-Oh Neo Revelation   │ Neo Rev │ $90.00   │ $410.00│ $15  │ $105.00   ││  │
│  │ Dark Charizard         │ Rocket  │ $55.00   │ $265.00│ $15  │ $70.00    ││  │
│  │                                                                           ▲│  │
│  │ Multiplier │ Profit   │ ROI %  │ Confidence │ Worth Grading              ││  │
│  ├────────────┼──────────┼────────┼────────────┼────────────────────────────┤│  │
│  │ 🟢 5.04x   │ $465.00  │ 404%   │ High       │ ✓                          ││  │
│  │ 🟢 5.09x   │ $1085.00 │ 409%   │ High       │ ✓                          ││  │
│  │ 🟡 4.22x   │ $290.00  │ 322%   │ Medium     │ ✓                          ││  │
│  │ 🟡 3.80x   │ $210.00  │ 280%   │ Medium     │ ✓                          ││  │
│  │ 🟡 4.23x   │ $355.00  │ 323%   │ High       │ ✓                          ││  │
│  │ 🟡 4.00x   │ $405.00  │ 300%   │ Medium     │ ✓                          ││  │
│  │ 🟡 4.05x   │ $595.00  │ 305%   │ High       │ ✓                          ││  │
│  │ 🟡 3.91x   │ $480.00  │ 291%   │ Medium     │ ✓                          ││  │
│  │ 🟡 3.89x   │ $550.00  │ 289%   │ High       │ ✓                          ││  │
│  │ 🟡 3.85x   │ $285.00  │ 285%   │ Medium     │ ✓                          ││  │
│  │ 🟡 3.90x   │ $305.00  │ 290%   │ Medium     │ ✓                          ││  │
│  │ 🟡 3.79x   │ $195.00  │ 279%   │ Medium     │ ✓                          ││  │
│  │                                                                           ▼│  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  Selected Opportunity Details:                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │ ═══════════════════════════════════════════════════════════               │  │
│  │              GRADE TO FLIP ANALYSIS                                       │  │
│  │ ═══════════════════════════════════════════════════════════               │  │
│  │                                                                            │  │
│  │ Card: Charizard Base Set                                                  │  │
│  │                                                                            │  │
│  │ PRICING:                                                                  │  │
│  │   • Current Ungraded Price: $100.00                                       │  │
│  │   • Expected PSA 10 Price: $580.00                                        │  │
│  │                                                                            │  │
│  │ INVESTMENT BREAKDOWN:                                                     │  │
│  │   • Ungraded Card Cost: $100.00                                           │  │
│  │   • Grading Service Cost: $15.00                                          │  │
│  │   • Total Investment: $115.00                                             │  │
│  │                                                                            │  │
│  │ PROFIT ANALYSIS:                                                          │  │
│  │   • Price Multiplier: 5.04x                                               │  │
│  │   • Expected Net Profit: $465.00                                          │  │
│  │   • Return on Investment: 404.3%                                          │  │
│  │                                                                            │  │
│  │ RECOMMENDATION:                                                           │  │
│  │   This card meets the 3x multiplier threshold and is worth grading.      │  │
│  │   The multiplier indicates strong profit potential after accounting       │  │
│  │   for grading costs.                                                      │  │
│  │                                                                            │  │
│  │ IMPORTANT NOTES:                                                          │  │
│  │   • Card must be in pristine condition for PSA 10                         │  │
│  │   • Market prices can fluctuate                                           │  │
│  │   • Grading turnaround time varies (2-8 weeks)                            │  │
│  │   • Actual results depend on final grade received                         │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Color Coding Scheme

### Multiplier Column:
- **🟢 Green (5x+)**: Excellent opportunities with very high profit potential
  - Background: rgba(76, 175, 80, 120)
  - Font: Bold

- **🟡 Yellow (3-5x)**: Good opportunities meeting the minimum threshold
  - Background: rgba(255, 193, 7, 120)
  - Font: Bold

- **🔴 Red (<3x)**: Below threshold, not recommended
  - Background: rgba(244, 67, 54, 120)
  - Font: Regular

### Profit Column:
- **Green Text**: Profit > $100
  - Color: rgb(76, 175, 80)
  
- **Light Green Text**: Profit $50-$100
  - Color: rgb(139, 195, 74)

- **Default Text**: Profit < $50
  - Color: Default

### ROI Column:
- **Green Text**: ROI > 200%
  - Color: rgb(76, 175, 80)

### Worth Grading Column:
- **✓ Green**: Meets 3x criteria
  - Color: rgb(76, 175, 80)
  - Font: Bold, Size 14

- **✗ Red**: Does not meet criteria
  - Color: rgb(244, 67, 54)
  - Font: Bold, Size 14

## Interactive Features

### Filter Controls
1. **Minimum Multiplier Spinner**
   - Range: 1.0 - 20.0
   - Step: 0.5
   - Default: 3.0
   - On Change: Re-filters table immediately

2. **Maximum Ungraded Price Spinner**
   - Range: $0 - $10,000
   - Step: $50
   - Default: $1,000
   - Prefix: "$"
   - On Change: Re-filters table immediately

### Action Buttons

1. **Scan All Cards**
   - Searches database for all cards
   - Calculates multipliers for each
   - Returns cards meeting 3x+ threshold
   - Shows progress bar during scan
   - Status: "Scanning 1 of 500 cards..."

2. **Refresh Prices**
   - Fetches updated prices from all 4 sources:
     - eBay
     - PriceCharting
     - PokeData.io
     - TCGPlayer
   - Updates multipliers with new data
   - Estimated time: 2-5 minutes
   - Shows progress per card

### Table Interactions

1. **Sorting**
   - Default: Sorted by Multiplier (descending)
   - Click column headers to sort
   - Click again to reverse order

2. **Row Selection**
   - Single row selection
   - Highlights selected row
   - Updates detail panel with card info

3. **Scrolling**
   - Vertical scrollbar for many results
   - Smooth scrolling

## Summary Panel

Displays aggregated statistics:
- **Total Opportunities**: Count of cards meeting criteria
- **Total Investment Needed**: Sum of all investments
- **Total Expected Profit**: Sum of all net profits
- **Average Multiplier**: Mean multiplier across all cards
- **Average ROI**: Mean ROI percentage

Updates dynamically as filters change.

## Details Panel

Shows comprehensive analysis for selected card:
- Card name and set
- Current market prices (ungraded and graded)
- Investment breakdown
- Profit calculations
- Recommendation with reasoning
- Important disclaimers

## Theme

### Dark Theme Applied
- Background: #2d2d2d
- Text: White
- Panel Background: #3a3a3a
- Border Color: #555555
- Accent Color: #0d7377 (teal)

### Typography
- Title: Arial, 16pt, Bold
- Headers: Arial, 12pt, Bold
- Body: Arial, 11pt
- Details: Arial, 10pt

## Responsive Behavior

### Window Resize
- Table adjusts width
- Columns maintain relative proportions
- Vertical scroll appears when needed

### Data Loading States
1. **Empty State**: "No opportunities loaded. Click 'Scan All Cards'..."
2. **Loading State**: Progress bar visible, status text updates
3. **Loaded State**: Table populated with data
4. **Error State**: Error message displayed in status

## Accessibility

- High contrast colors
- Clear visual hierarchy
- Keyboard navigation support
- Screen reader compatible
- Tooltip hints on hover

## Example User Flow

1. User opens "Grade to Flip" tab
2. Sees empty table with message
3. Clicks "Scan All Cards"
4. Progress bar appears: "Scanning 50 cards..."
5. Table populates with 12 opportunities
6. Summary shows: "12 opportunities, $1,380 investment, $3,420 profit"
7. User adjusts multiplier to 4.0x
8. Table filters to 8 cards
9. User clicks on Charizard row
10. Details panel shows full analysis
11. User decides to invest based on 5.04x multiplier
12. Clicks "Refresh Prices" to get latest data
13. Progress bar: "Updating prices from 4 sources..."
14. Prices update, multipliers recalculate
15. User makes informed grading decision

## Performance

- Table renders 100+ rows smoothly
- Filtering is instant (<100ms)
- Details panel updates immediately
- Sorting is fast (<50ms)
- Color coding applied efficiently

## Future Enhancements

Potential UI improvements:
1. Export to CSV button
2. Print report functionality
3. Historical multiplier trends chart
4. Market alerts configuration
5. Batch grading calculator
6. Portfolio tracking integration
