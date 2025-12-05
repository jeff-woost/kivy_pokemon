"""
Data validation module for ensuring data quality
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates and cleans market data"""
    
    REQUIRED_FIELDS = [
        'currency', 'curve_id', 'rate', 'tenor_days', 'valuation_date'
    ]
    
    OPTIONAL_FIELDS = [
        'batch_reference', 'compounding_frequency', 'day_count',
        'extrapolation', 'interpolation'
    ]
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate a DataFrame for required fields and data types
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check for required columns
        missing_cols = [col for col in self.REQUIRED_FIELDS 
                       if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        
        # Check for empty DataFrame
        if df.empty:
            errors.append("DataFrame is empty")
            return False, errors
        
        # Validate data types
        if 'rate' in df.columns:
            non_numeric = df[~pd.to_numeric(df['rate'], errors='coerce').notna()]
            if not non_numeric.empty:
                errors.append(f"Non-numeric rates found: {len(non_numeric)} rows")
        
        if 'tenor_days' in df.columns:
            non_numeric = df[~pd.to_numeric(df['tenor_days'], errors='coerce').notna()]
            if not non_numeric.empty:
                errors.append(f"Non-numeric tenor_days found: {len(non_numeric)} rows")
        
        # Check for negative rates (warning only)
        if 'rate' in df.columns:
            negative_rates = df[df['rate'] < 0]
            if not negative_rates.empty:
                logger.warning(f"Negative rates found: {len(negative_rates)} rows")
        
        # Check for duplicate entries
        if all(col in df.columns for col in ['curve_id', 'tenor_days', 'valuation_date']):
            duplicates = df.duplicated(subset=['curve_id', 'tenor_days', 'valuation_date'])
            if duplicates.any():
                errors.append(f"Duplicate entries found: {duplicates.sum()} rows")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize data
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Convert numeric columns
        if 'rate' in df_clean.columns:
            df_clean['rate'] = pd.to_numeric(df_clean['rate'], errors='coerce')
        
        if 'tenor_days' in df_clean.columns:
            df_clean['tenor_days'] = pd.to_numeric(df_clean['tenor_days'], errors='coerce')
        
        # Standardize date format
        if 'valuation_date' in df_clean.columns:
            df_clean['valuation_date'] = pd.to_datetime(
                df_clean['valuation_date'], 
                errors='coerce',
                infer_datetime_format=True
            )
        
        # Remove rows with critical missing data
        critical_cols = ['rate', 'tenor_days', 'curve_id']
        existing_critical = [col for col in critical_cols if col in df_clean.columns]
        df_clean = df_clean.dropna(subset=existing_critical)
        
        # Sort by curve_id and tenor_days
        if all(col in df_clean.columns for col in ['curve_id', 'tenor_days']):
            df_clean = df_clean.sort_values(['curve_id', 'tenor_days'])
        
        # Remove duplicates
        if all(col in df_clean.columns for col in ['curve_id', 'tenor_days', 'valuation_date']):
            df_clean = df_clean.drop_duplicates(
                subset=['curve_id', 'tenor_days', 'valuation_date'],
                keep='last'
            )
        
        return df_clean
    
    def validate_curve_data(self, df: pd.DataFrame, curve_id: str) -> Dict[str, any]:
        """
        Validate data for a specific curve
        
        Args:
            df: DataFrame containing curve data
            curve_id: ID of curve to validate
            
        Returns:
            Dictionary with validation results
        """
        curve_data = df[df['curve_id'] == curve_id] if 'curve_id' in df.columns else pd.DataFrame()
        
        validation_results = {
            'curve_id': curve_id,
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        if curve_data.empty:
            validation_results['is_valid'] = False
            validation_results['errors'].append("No data found for curve")
            return validation_results
        
        # Check for minimum number of points
        if len(curve_data) < 2:
            validation_results['warnings'].append("Less than 2 data points")
        
        # Check for tenor gaps
        if 'tenor_days' in curve_data.columns:
            tenors = sorted(curve_data['tenor_days'].unique())
            if len(tenors) > 1:
                gaps = np.diff(tenors)
                max_gap = gaps.max()
                if max_gap > 1000:  # More than 1000 days gap
                    validation_results['warnings'].append(f"Large tenor gap detected: {max_gap} days")
        
        # Check for rate consistency
        if 'rate' in curve_data.columns:
            rate_std = curve_data['rate'].std()
            rate_mean = curve_data['rate'].mean()
            if rate_mean != 0:
                cv = rate_std / abs(rate_mean)
                if cv > 2:  # Coefficient of variation > 2
                    validation_results['warnings'].append(f"High rate variability: CV={cv:.2f}")
        
        return validation_results
    
    def check_data_consistency(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, any]:
        """
        Check consistency between two DataFrames (e.g., two days of data)
        
        Args:
            df1: First DataFrame
            df2: Second DataFrame
            
        Returns:
            Dictionary with consistency check results
        """
        results = {
            'is_consistent': True,
            'issues': []
        }
        
        # Check for same curve IDs
        if 'curve_id' in df1.columns and 'curve_id' in df2.columns:
            curves1 = set(df1['curve_id'].unique())
            curves2 = set(df2['curve_id'].unique())
            
            missing_in_2 = curves1 - curves2
            missing_in_1 = curves2 - curves1
            
            if missing_in_2:
                results['issues'].append(f"Curves in day 1 but not day 2: {missing_in_2}")
            if missing_in_1:
                results['issues'].append(f"Curves in day 2 but not day 1: {missing_in_1}")
        
        # Check for same tenors per curve
        common_curves = set(df1['curve_id'].unique()) & set(df2['curve_id'].unique())
        for curve_id in common_curves:
            tenors1 = set(df1[df1['curve_id'] == curve_id]['tenor_days'])
            tenors2 = set(df2[df2['curve_id'] == curve_id]['tenor_days'])
            
            if tenors1 != tenors2:
                results['issues'].append(f"Different tenors for {curve_id}")
        
        if results['issues']:
            results['is_consistent'] = False
        
        return results