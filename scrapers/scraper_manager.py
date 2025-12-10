"""
Scraper manager to coordinate all data sources
"""
from typing import List, Dict
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pandas as pd
import numpy as np
from .ebay_scraper import EbayScraper
from .pricecharting_scraper import PriceChartingScraper
from .pokedata_scraper import PokeDataScraper
from .tcgplayer_scraper import TCGPlayerScraper


class ScraperManager:
    """Manages multiple scrapers and aggregates results"""
    
    def __init__(self):
        self.ebay = EbayScraper()
        self.pricecharting = PriceChartingScraper()
        self.pokedata = PokeDataScraper()
        self.tcgplayer = TCGPlayerScraper()
        self.logger = logging.getLogger(__name__)
        
    def get_all_prices(self, card_name: str, max_workers: int = 4) -> List[Dict]:
        """
        Get prices from all sources in parallel
        
        Args:
            card_name: Name of the card to search
            max_workers: Number of parallel scraping threads (default 4, one per source)
                        Note: Each scraper has its own rate limiting (2-4 sec between requests)
            
        Returns:
            Combined list of all price data
        """
        all_prices = []
        
        # Define scraping tasks for all 4 sources
        tasks = [
            ('eBay', self.ebay.get_sold_listings, card_name),
            ('PriceCharting', self.pricecharting.get_price_history, card_name),
            ('PokeData.io', self.pokedata.get_card_market_data, card_name),
            ('TCGPlayer', self.tcgplayer.get_card_prices, card_name),
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
        Get data from card inception to current date from all sources
        
        Args:
            card_name: Name of the card
            
        Returns:
            Dictionary with inception date and full history
        """
        # Get data from all sources
        all_prices = self.get_all_prices(card_name)
        
        # Sort by date
        all_prices.sort(key=lambda x: x['date'])
        
        inception_date = all_prices[0]['date'] if all_prices else None
        
        return {
            'card_name': card_name,
            'inception_date': inception_date,
            'price_history': all_prices,
            'data_points': len(all_prices)
        }
        
    def get_aggregated_trend_data(self, card_name: str) -> Dict:
        """
        Get aggregated trend data from all sources with normalization
        
        Args:
            card_name: Name of the card
            
        Returns:
            Dictionary with normalized and aggregated data
        """
        try:
            # Get data from all sources
            all_prices = self.get_all_prices(card_name)
            
            if not all_prices:
                return self._get_empty_trend_data(card_name)
                
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(all_prices)
            
            # Normalize prices by source (in case of different grading/conditions)
            normalized_data = self._normalize_multi_source_data(df)
            
            # Calculate aggregate statistics
            aggregated = {
                'card_name': card_name,
                'sources': list(df['source'].unique()),
                'total_data_points': len(df),
                'date_range': {
                    'start': df['date'].min() if not df.empty else None,
                    'end': df['date'].max() if not df.empty else None
                },
                'price_by_source': self._calculate_source_prices(df),
                'graded_vs_ungraded': self._calculate_graded_comparison(df),
                'normalized_data': normalized_data,
                'trend_indicators': self._calculate_trend_indicators(df),
                'data_quality': self._assess_data_quality(df)
            }
            
            return aggregated
            
        except Exception as e:
            self.logger.error(f"Error aggregating trend data: {e}")
            return self._get_empty_trend_data(card_name)
            
    def _normalize_multi_source_data(self, df: pd.DataFrame) -> Dict:
        """Normalize price data across different sources"""
        normalized = {}
        
        try:
            # Group by source and condition
            for source in df['source'].unique():
                source_df = df[df['source'] == source]
                
                # Separate graded and ungraded
                ungraded = source_df[~source_df['graded'].astype(bool)]
                graded = source_df[source_df['graded'].astype(bool)]
                
                normalized[source] = {
                    'ungraded_mean': float(ungraded['price'].mean()) if not ungraded.empty else None,
                    'ungraded_median': float(ungraded['price'].median()) if not ungraded.empty else None,
                    'graded_mean': float(graded['price'].mean()) if not graded.empty else None,
                    'graded_median': float(graded['price'].median()) if not graded.empty else None,
                    'data_points': len(source_df)
                }
                
        except Exception as e:
            self.logger.warning(f"Error normalizing data: {e}")
            
        return normalized
        
    def _calculate_source_prices(self, df: pd.DataFrame) -> Dict:
        """Calculate average prices by source"""
        prices_by_source = {}
        
        try:
            for source in df['source'].unique():
                source_df = df[df['source'] == source]
                prices_by_source[source] = {
                    'mean': float(source_df['price'].mean()),
                    'median': float(source_df['price'].median()),
                    'min': float(source_df['price'].min()),
                    'max': float(source_df['price'].max()),
                    'count': len(source_df)
                }
        except Exception as e:
            self.logger.warning(f"Error calculating source prices: {e}")
            
        return prices_by_source
        
    def _calculate_graded_comparison(self, df: pd.DataFrame) -> Dict:
        """Calculate comparison between graded and ungraded prices"""
        try:
            graded_df = df[df['graded'].astype(bool)]
            ungraded_df = df[~df['graded'].astype(bool)]
            
            if graded_df.empty or ungraded_df.empty:
                return {'multiplier': None, 'insufficient_data': True}
                
            graded_mean = float(graded_df['price'].mean())
            ungraded_mean = float(ungraded_df['price'].mean())
            
            return {
                'graded_mean': graded_mean,
                'ungraded_mean': ungraded_mean,
                'multiplier': graded_mean / ungraded_mean if ungraded_mean > 0 else None,
                'graded_count': len(graded_df),
                'ungraded_count': len(ungraded_df)
            }
        except Exception as e:
            self.logger.warning(f"Error calculating graded comparison: {e}")
            return {'multiplier': None, 'error': str(e)}
            
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate trend indicators from multi-source data"""
        try:
            # Sort by date
            df_sorted = df.sort_values('date')
            
            # Calculate price velocity (rate of change)
            if len(df_sorted) > 1:
                recent = df_sorted.tail(10)
                older = df_sorted.head(10)
                
                recent_avg = recent['price'].mean()
                older_avg = older['price'].mean()
                
                price_velocity = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            else:
                price_velocity = 0
                
            # Calculate volatility
            volatility = float(df['price'].std() / df['price'].mean() * 100) if df['price'].mean() > 0 else 0
            
            return {
                'price_velocity_pct': price_velocity,
                'volatility': volatility,
                'trend_direction': 'upward' if price_velocity > 5 else 'downward' if price_velocity < -5 else 'stable'
            }
        except Exception as e:
            self.logger.warning(f"Error calculating trend indicators: {e}")
            return {}
            
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict:
        """Assess the quality and reliability of collected data"""
        try:
            source_counts = df['source'].value_counts().to_dict()
            
            # Calculate confidence based on data points and source diversity
            total_points = len(df)
            source_count = len(source_counts)
            
            confidence = min(100, (total_points / 2) + (source_count * 10))
            
            return {
                'confidence_score': float(confidence),
                'total_data_points': total_points,
                'sources_count': source_count,
                'source_distribution': source_counts,
                'quality_rating': 'high' if confidence > 70 else 'medium' if confidence > 40 else 'low'
            }
        except Exception as e:
            self.logger.warning(f"Error assessing data quality: {e}")
            return {'confidence_score': 0, 'quality_rating': 'low'}
            
    def _get_empty_trend_data(self, card_name: str) -> Dict:
        """Return empty trend data structure"""
        return {
            'card_name': card_name,
            'sources': [],
            'total_data_points': 0,
            'date_range': {'start': None, 'end': None},
            'price_by_source': {},
            'graded_vs_ungraded': {'multiplier': None},
            'normalized_data': {},
            'trend_indicators': {},
            'data_quality': {'confidence_score': 0, 'quality_rating': 'none'}
        }
