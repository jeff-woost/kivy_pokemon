"""
Curve analysis module for calculating basis point moves and curve metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CurveAnalyzer:
    """Analyzes curve movements and calculates key metrics"""
    
    def __init__(self):
        self.bp_multiplier = 10000  # Basis points multiplier
        
    def calculate_bp_move(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                         merge_keys: List[str] = None) -> pd.DataFrame:
        """
        Calculate basis point moves between two days of curve data
        
        Args:
            df1: DataFrame for day 1
            df2: DataFrame for day 2
            merge_keys: List of columns to merge on
            
        Returns:
            DataFrame with basis point movements
        """
        if merge_keys is None:
            merge_keys = ['curve_id', 'tenor_days', 'currency']
        
        # Ensure merge keys exist in both dataframes
        merge_keys = [k for k in merge_keys if k in df1.columns and k in df2.columns]
        
        # Merge dataframes
        merged = pd.merge(
            df1[merge_keys + ['rate']],
            df2[merge_keys + ['rate']],
            on=merge_keys,
            suffixes=('_day1', '_day2'),
            how='outer'
        )
        
        # Calculate basis point move
        merged['bp_move'] = (merged['rate_day2'] - merged['rate_day1']) * self.bp_multiplier
        merged['rate_change_pct'] = ((merged['rate_day2'] - merged['rate_day1']) / 
                                     merged['rate_day1'].abs()) * 100
        
        # Add absolute move for sorting
        merged['abs_bp_move'] = merged['bp_move'].abs()
        
        return merged
    
    def analyze_curve_shape(self, df: pd.DataFrame, curve_id: str) -> Dict:
        """
        Analyze the shape and characteristics of a curve
        
        Args:
            df: DataFrame containing curve data
            curve_id: ID of the curve to analyze
            
        Returns:
            Dictionary with curve shape metrics
        """
        curve_data = df[df['curve_id'] == curve_id].sort_values('tenor_days')
        
        if curve_data.empty:
            return {}
        
        metrics = {
            'curve_id': curve_id,
            'num_points': len(curve_data),
            'min_tenor': curve_data['tenor_days'].min(),
            'max_tenor': curve_data['tenor_days'].max(),
            'min_rate': curve_data['rate'].min(),
            'max_rate': curve_data['rate'].max(),
            'avg_rate': curve_data['rate'].mean(),
            'std_rate': curve_data['rate'].std(),
            'curve_type': curve_data['curve_type'].iloc[0] if 'curve_type' in curve_data.columns else 'unknown'
        }
        
        # Calculate slope metrics
        if len(curve_data) > 1:
            # Short end slope (first two points)
            short_end = curve_data.head(2)
            if len(short_end) == 2:
                metrics['short_end_slope'] = (short_end.iloc[1]['rate'] - short_end.iloc[0]['rate']) / \
                                            (short_end.iloc[1]['tenor_days'] - short_end.iloc[0]['tenor_days'])
            
            # Long end slope (last two points)
            long_end = curve_data.tail(2)
            if len(long_end) == 2:
                metrics['long_end_slope'] = (long_end.iloc[1]['rate'] - long_end.iloc[0]['rate']) / \
                                           (long_end.iloc[1]['tenor_days'] - long_end.iloc[0]['tenor_days'])
            
            # Overall slope
            metrics['overall_slope'] = (curve_data.iloc[-1]['rate'] - curve_data.iloc[0]['rate']) / \
                                      (curve_data.iloc[-1]['tenor_days'] - curve_data.iloc[0]['tenor_days'])
            
            # Curvature (2nd derivative approximation)
            if len(curve_data) >= 3:
                mid_idx = len(curve_data) // 2
                if mid_idx > 0 and mid_idx < len(curve_data) - 1:
                    h1 = curve_data.iloc[mid_idx]['tenor_days'] - curve_data.iloc[mid_idx-1]['tenor_days']
                    h2 = curve_data.iloc[mid_idx+1]['tenor_days'] - curve_data.iloc[mid_idx]['tenor_days']
                    if h1 > 0 and h2 > 0:
                        metrics['curvature'] = 2 * (
                            (curve_data.iloc[mid_idx+1]['rate'] - curve_data.iloc[mid_idx]['rate']) / h2 -
                            (curve_data.iloc[mid_idx]['rate'] - curve_data.iloc[mid_idx-1]['rate']) / h1
                        ) / (h1 + h2)
        
        return metrics
    
    def identify_outliers(self, df: pd.DataFrame, threshold_bp: float = 50) -> pd.DataFrame:
        """
        Identify outlier moves in the curve data
        
        Args:
            df: DataFrame with basis point moves
            threshold_bp: Threshold for outlier detection in basis points
            
        Returns:
            DataFrame containing outlier moves
        """
        if 'bp_move' not in df.columns:
            return pd.DataFrame()
        
        outliers = df[df['abs_bp_move'] > threshold_bp].copy()
        outliers = outliers.sort_values('abs_bp_move', ascending=False)
        
        return outliers
    
    def calculate_parallel_shift(self, df: pd.DataFrame, curve_id: str) -> float:
        """
        Calculate the average parallel shift for a curve
        
        Args:
            df: DataFrame with basis point moves
            curve_id: ID of the curve
            
        Returns:
            Average parallel shift in basis points
        """
        curve_moves = df[df['curve_id'] == curve_id]['bp_move']
        if curve_moves.empty:
            return 0.0
        
        return curve_moves.mean()
    
    def calculate_curve_steepening(self, df: pd.DataFrame, curve_id: str,
                                  short_tenor: int = 360, long_tenor: int = 3600) -> float:
        """
        Calculate curve steepening/flattening
        
        Args:
            df: DataFrame with basis point moves
            curve_id: ID of the curve
            short_tenor: Short end tenor in days
            long_tenor: Long end tenor in days
            
        Returns:
            Steepening in basis points (positive = steepening, negative = flattening)
        """
        curve_data = df[df['curve_id'] == curve_id]
        
        short_move = curve_data[curve_data['tenor_days'] == short_tenor]['bp_move'].values
        long_move = curve_data[curve_data['tenor_days'] == long_tenor]['bp_move'].values
        
        if len(short_move) > 0 and len(long_move) > 0:
            return long_move[0] - short_move[0]
        
        return 0.0
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics for curve movements
        
        Args:
            df: DataFrame with basis point moves
            
        Returns:
            Dictionary with summary statistics
        """
        if 'bp_move' not in df.columns:
            return {}
        
        return {
            'total_curves': df['curve_id'].nunique() if 'curve_id' in df.columns else 0,
            'total_points': len(df),
            'avg_bp_move': df['bp_move'].mean(),
            'std_bp_move': df['bp_move'].std(),
            'max_bp_move': df['bp_move'].max(),
            'min_bp_move': df['bp_move'].min(),
            'max_abs_move': df['abs_bp_move'].max() if 'abs_bp_move' in df.columns else 0,
            'widening_count': (df['bp_move'] > 0).sum(),
            'tightening_count': (df['bp_move'] < 0).sum(),
            'unchanged_count': (df['bp_move'] == 0).sum()
        }