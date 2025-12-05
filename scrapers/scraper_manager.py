"""
Scraper manager to coordinate all data sources
"""
from typing import List, Dict
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .ebay_scraper import EbayScraper
from .pricecharting_scraper import PriceChartingScraper


class ScraperManager:
    """Manages multiple scrapers and aggregates results"""
    
    def __init__(self):
        self.ebay = EbayScraper()
        self.pricecharting = PriceChartingScraper()
        self.logger = logging.getLogger(__name__)
        
    def get_all_prices(self, card_name: str, max_workers: int = 2) -> List[Dict]:
        """
        Get prices from all sources in parallel
        
        Args:
            card_name: Name of the card to search
            max_workers: Number of parallel scraping threads
            
        Returns:
            Combined list of all price data
        """
        all_prices = []
        
        # Define scraping tasks
        tasks = [
            ('eBay', self.ebay.get_sold_listings, card_name),
            ('PriceCharting', self.pricecharting.get_price_history, card_name),
        ]
        
        # Execute scrapers in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_source = {
                executor.submit(func, name): source 
                for source, func, name in tasks
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    prices = future.result()
                    all_prices.extend(prices)
                    self.logger.info(f"Got {len(prices)} prices from {source}")
                except Exception as e:
                    self.logger.error(f"Error getting prices from {source}: {e}")
                    
        self.logger.info(f"Total prices collected: {len(all_prices)}")
        return all_prices
        
    def find_grading_opportunities(self, min_multiplier: float = 3.0) -> List[Dict]:
        """
        Find cards with high grading multipliers
        
        Args:
            min_multiplier: Minimum graded/ungraded price ratio
            
        Returns:
            List of cards with grading opportunities
        """
        return self.pricecharting.search_cards_with_3x_multiplier(min_multiplier)
        
    def get_inception_data(self, card_name: str) -> Dict:
        """
        Get data from card inception to current date
        
        Args:
            card_name: Name of the card
            
        Returns:
            Dictionary with inception date and full history
        """
        # Get historical data from PriceCharting (goes back further)
        historical_prices = self.pricecharting.get_price_history(card_name, max_results=200)
        
        # Get recent sold data from eBay
        recent_prices = self.ebay.get_sold_listings(card_name, max_results=50)
        
        # Combine and sort by date
        all_prices = historical_prices + recent_prices
        all_prices.sort(key=lambda x: x['date'])
        
        inception_date = all_prices[0]['date'] if all_prices else None
        
        return {
            'card_name': card_name,
            'inception_date': inception_date,
            'price_history': all_prices,
            'data_points': len(all_prices)
        }
