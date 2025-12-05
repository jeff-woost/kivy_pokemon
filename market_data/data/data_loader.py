"""
Data loader module for fetching and parsing JSON market data
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MarketDataLoader:
    """Handles loading and parsing of market data from JSON APIs"""
    
    def __init__(self):
        self.data_cache = {}
        self.curve_types = ['funding', 'credit', 'ir']
        
    def fetch_json_from_api(self, api_url: str) -> Dict:
        """
        Fetch JSON data from API endpoint
        
        Args:
            api_url: URL of the API endpoint
            
        Returns:
            Dictionary containing the JSON response
        """
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data from API: {e}")
            raise
    
    def load_from_file(self, filepath: Path) -> Dict:
        """
        Load JSON data from a local file
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Dictionary containing the JSON data
        """
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading file {filepath}: {e}")
            raise
    
    def parse_market_data(self, json_data: Dict) -> pd.DataFrame:
        """
        Parse JSON market data into pandas DataFrame
        
        Args:
            json_data: Dictionary containing market data
            
        Returns:
            DataFrame with parsed market data
        """
        # Handle both nested and flat JSON structures
        if 'data' in json_data:
            records = json_data['data']
        elif 'curves' in json_data:
            records = json_data['curves']
        else:
            records = json_data if isinstance(json_data, list) else [json_data]
        
        df = pd.DataFrame(records)
        
        # Standardize column names
        column_mapping = {
            'batchRefernce': 'batch_reference',
            'batchReference': 'batch_reference',
            'compoundingFrequency': 'compounding_frequency',
            'curveId': 'curve_id',
            'DayCount': 'day_count',
            'dayCount': 'day_count',
            'tenorDays': 'tenor_days',
            'valuationDate': 'valuation_date'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Convert data types
        if 'rate' in df.columns:
            df['rate'] = pd.to_numeric(df['rate'], errors='coerce')
        if 'tenor_days' in df.columns:
            df['tenor_days'] = pd.to_numeric(df['tenor_days'], errors='coerce')
        if 'valuation_date' in df.columns:
            df['valuation_date'] = pd.to_datetime(df['valuation_date'], format='%m/%d/%y', errors='coerce')
        
        return df
    
    def classify_curve_type(self, curve_id: str) -> str:
        """
        Classify the type of curve based on curve ID
        
        Args:
            curve_id: Identifier string for the curve
            
        Returns:
            Type of curve (funding, credit, or ir)
        """
        curve_id_upper = curve_id.upper()
        
        if 'FVA' in curve_id_upper or 'FUNDING' in curve_id_upper:
            return 'funding'
        elif 'BSPREAD' in curve_id_upper or 'CREDIT' in curve_id_upper or 'CDS' in curve_id_upper:
            return 'credit'
        elif 'IR' in curve_id_upper or 'SWAP' in curve_id_upper or 'LIBOR' in curve_id_upper:
            return 'ir'
        else:
            return 'unknown'
    
    def load_two_day_comparison(self, day1_source: str, day2_source: str, 
                                from_api: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load two days of market data for comparison
        
        Args:
            day1_source: API URL or file path for day 1
            day2_source: API URL or file path for day 2
            from_api: Whether to load from API (True) or file (False)
            
        Returns:
            Tuple of (day1_df, day2_df)
        """
        if from_api:
            day1_data = self.fetch_json_from_api(day1_source)
            day2_data = self.fetch_json_from_api(day2_source)
        else:
            day1_data = self.load_from_file(Path(day1_source))
            day2_data = self.load_from_file(Path(day2_source))
        
        day1_df = self.parse_market_data(day1_data)
        day2_df = self.parse_market_data(day2_data)
        
        # Add curve type classification
        if 'curve_id' in day1_df.columns:
            day1_df['curve_type'] = day1_df['curve_id'].apply(self.classify_curve_type)
        if 'curve_id' in day2_df.columns:
            day2_df['curve_type'] = day2_df['curve_id'].apply(self.classify_curve_type)
        
        return day1_df, day2_df