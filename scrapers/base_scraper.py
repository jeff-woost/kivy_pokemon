"""
Base scraper class with rate limiting and error handling
"""
import time
import random
import requests
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from datetime import datetime


class BaseScraper:
    """Base class for all scrapers with common functionality"""
    
    def __init__(self, rate_limit_delay: tuple = (1, 3)):
        """
        Initialize base scraper
        
        Args:
            rate_limit_delay: Tuple of (min, max) seconds to wait between requests
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.rate_limit_delay = rate_limit_delay
        self.logger = logging.getLogger(self.__class__.__name__)
        self.last_request_time = 0
        
    def rate_limit(self):
        """Apply rate limiting between requests"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        min_delay, max_delay = self.rate_limit_delay
        
        delay = random.uniform(min_delay, max_delay)
        if elapsed < delay:
            time.sleep(delay - elapsed)
            
        self.last_request_time = time.time()
        
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page with retries
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
            
        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(retries):
            try:
                self.rate_limit()
                self.logger.info(f"Fetching {url} (attempt {attempt + 1}/{retries})")
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                return BeautifulSoup(response.content, 'html.parser')
                
            except requests.RequestException as e:
                self.logger.warning(f"Error fetching {url}: {e}")
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 2
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Failed to fetch {url} after {retries} attempts")
                    
        return None
        
    def parse_price(self, price_str: str) -> Optional[float]:
        """
        Parse price string to float
        
        Args:
            price_str: Price string (e.g., '$123.45', '123.45', '$1,234.56')
            
        Returns:
            Float price or None if parsing failed
        """
        try:
            # Remove currency symbols and commas
            clean_price = price_str.replace('$', '').replace(',', '').strip()
            return float(clean_price)
        except (ValueError, AttributeError):
            self.logger.warning(f"Failed to parse price: {price_str}")
            return None
            
    def extract_date(self, date_str: str) -> Optional[datetime]:
        """
        Extract datetime from various date string formats
        
        Args:
            date_str: Date string
            
        Returns:
            datetime object or None if parsing failed
        """
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%b %d, %Y',
            '%B %d, %Y',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except (ValueError, AttributeError):
                continue
                
        self.logger.warning(f"Failed to parse date: {date_str}")
        return None
