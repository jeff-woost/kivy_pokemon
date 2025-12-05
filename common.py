"""
Common data structures used across the application
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class CardPrice:
    """Data structure for a card price point"""
    date: datetime
    price: float
    source: str
    condition: str
    graded: bool
    grade_value: Optional[float] = None
    grade_company: Optional[str] = None


@dataclass
class CardData:
    """Complete card data with price history"""
    name: str
    set_name: str
    number: str
    rarity: str
    prices: List[CardPrice]
    current_market_price: float
    trend: str
    confidence_score: float
