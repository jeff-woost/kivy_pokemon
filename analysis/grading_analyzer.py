"""
PSA 10 grading multiplier analyzer
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging


class GradingAnalyzer:
    """Analyzer for PSA 10 grading opportunities"""
    
    # Typical grading costs
    GRADING_COSTS = {
        'PSA': {'economy': 20, 'regular': 35, 'express': 75},
        'BGS': {'economy': 25, 'regular': 40, 'express': 80},
        'CGC': {'economy': 18, 'regular': 30, 'express': 65},
    }
    
    # Minimum thresholds for recommendations
    MIN_NET_PROFIT_GOOD = 50.0  # Minimum profit for GOOD recommendation
    MIN_NET_PROFIT_MARGINAL = 25.0  # Minimum profit for MARGINAL recommendation
    
    def __init__(self, default_grading_cost: float = 35.0):
        """
        Initialize grading analyzer
        
        Args:
            default_grading_cost: Default cost for grading (in dollars)
        """
        self.default_grading_cost = default_grading_cost
        self.logger = logging.getLogger(__name__)
        
    def analyze_grading_opportunity(self, price_history: List[Dict]) -> Dict:
        """
        Analyze if a card is worth grading
        
        Args:
            price_history: List of price data including graded and ungraded
            
        Returns:
            Dictionary with grading analysis
        """
        if not price_history:
            return self._get_empty_results()
            
        df = pd.DataFrame(price_history)
        
        # Separate graded and ungraded prices
        graded_df = df[df['graded'] == True]
        ungraded_df = df[df['graded'] == False]
        
        if graded_df.empty or ungraded_df.empty:
            self.logger.warning("Insufficient graded or ungraded price data")
            return self._get_empty_results()
            
        # Calculate statistics
        avg_ungraded = ungraded_df['price'].mean()
        avg_graded = graded_df['price'].mean()
        
        # Filter for PSA 10 specifically if available
        psa10_df = graded_df[
            (graded_df['grade_value'] == 10) & 
            (graded_df['grade_company'] == 'PSA')
        ]
        
        if not psa10_df.empty:
            avg_psa10 = psa10_df['price'].mean()
            psa10_count = len(psa10_df)
        else:
            # Estimate PSA 10 as 120% of average graded
            avg_psa10 = avg_graded * 1.2
            psa10_count = 0
            
        # Calculate multiplier
        if avg_ungraded > 0:
            multiplier = avg_psa10 / avg_ungraded
        else:
            multiplier = 0.0
            
        # Calculate profit potential
        grading_cost = self.default_grading_cost
        gross_profit = avg_psa10 - avg_ungraded
        net_profit = gross_profit - grading_cost
        roi = (net_profit / (avg_ungraded + grading_cost)) * 100 if (avg_ungraded + grading_cost) > 0 else 0
        
        # Determine recommendation
        recommendation = self._get_grading_recommendation(
            multiplier, net_profit, avg_ungraded
        )
        
        return {
            'ungraded_avg_price': float(avg_ungraded),
            'ungraded_data_points': len(ungraded_df),
            'graded_avg_price': float(avg_graded),
            'graded_data_points': len(graded_df),
            'psa10_avg_price': float(avg_psa10),
            'psa10_data_points': psa10_count,
            'multiplier': float(multiplier),
            'grading_cost': grading_cost,
            'gross_profit': float(gross_profit),
            'net_profit': float(net_profit),
            'roi_percentage': float(roi),
            'recommendation': recommendation,
            'worth_grading': multiplier >= 3.0 and net_profit > 50,
            
            # Additional statistics
            'ungraded_min': float(ungraded_df['price'].min()),
            'ungraded_max': float(ungraded_df['price'].max()),
            'psa10_min': float(psa10_df['price'].min()) if not psa10_df.empty else 0.0,
            'psa10_max': float(psa10_df['price'].max()) if not psa10_df.empty else 0.0,
        }
        
    def find_cards_with_high_multiplier(
        self, 
        all_cards_data: List[Dict], 
        min_multiplier: float = 3.0,
        min_net_profit: float = None
    ) -> List[Dict]:
        """
        Find cards with high grading multipliers
        
        Args:
            all_cards_data: List of card data dictionaries
            min_multiplier: Minimum graded/ungraded multiplier
            min_net_profit: Minimum net profit after grading costs (default: MIN_NET_PROFIT_GOOD)
            
        Returns:
            List of cards sorted by profitability
        """
        if min_net_profit is None:
            min_net_profit = self.MIN_NET_PROFIT_GOOD
            
        opportunities = []
        
        for card_data in all_cards_data:
            analysis = self.analyze_grading_opportunity(card_data['prices'])
            
            if (analysis['multiplier'] >= min_multiplier and 
                analysis['net_profit'] >= min_net_profit):
                
                opportunities.append({
                    'card_name': card_data['card_name'],
                    **analysis
                })
                
        # Sort by ROI percentage
        opportunities.sort(key=lambda x: x['roi_percentage'], reverse=True)
        
        return opportunities
        
    def calculate_grading_break_even(self, ungraded_price: float, grading_cost: float = None) -> float:
        """
        Calculate break-even PSA 10 price
        
        Args:
            ungraded_price: Current ungraded price
            grading_cost: Cost to grade (uses default if None)
            
        Returns:
            Break-even PSA 10 price
        """
        cost = grading_cost or self.default_grading_cost
        return ungraded_price + cost
        
    def estimate_grading_success_rate(self, price_history: List[Dict]) -> Dict:
        """
        Estimate probability of getting PSA 10 based on historical data
        
        Args:
            price_history: Historical price data
            
        Returns:
            Dictionary with success rate estimates
        """
        df = pd.DataFrame(price_history)
        graded_df = df[df['graded'] == True]
        
        if graded_df.empty:
            return {'psa10_rate': 0.15, 'confidence': 'low', 'data_points': 0}
            
        # Count PSA 10s
        psa10_count = len(graded_df[
            (graded_df['grade_value'] == 10) & 
            (graded_df['grade_company'] == 'PSA')
        ])
        
        total_graded = len(graded_df)
        
        # Calculate rate
        psa10_rate = psa10_count / total_graded if total_graded > 0 else 0.15
        
        # Determine confidence based on sample size
        if total_graded < 5:
            confidence = 'very_low'
        elif total_graded < 20:
            confidence = 'low'
        elif total_graded < 50:
            confidence = 'medium'
        else:
            confidence = 'high'
            
        return {
            'psa10_rate': psa10_rate,
            'psa10_count': psa10_count,
            'total_graded': total_graded,
            'confidence': confidence,
            'data_points': total_graded
        }
        
    def _get_grading_recommendation(
        self, 
        multiplier: float, 
        net_profit: float,
        ungraded_price: float
    ) -> str:
        """
        Generate grading recommendation
        
        Args:
            multiplier: Graded/ungraded price multiplier
            net_profit: Expected net profit
            ungraded_price: Current ungraded price
            
        Returns:
            Recommendation string
        """
        if multiplier >= 5.0 and net_profit >= 200:
            return "EXCELLENT - High priority grading candidate"
        elif multiplier >= 4.0 and net_profit >= 100:
            return "VERY GOOD - Strong grading opportunity"
        elif multiplier >= 3.0 and net_profit >= self.MIN_NET_PROFIT_GOOD:
            return "GOOD - Worth considering for grading"
        elif multiplier >= 2.0 and net_profit >= self.MIN_NET_PROFIT_MARGINAL:
            return "MARGINAL - Only if card condition is pristine"
        else:
            return "NOT RECOMMENDED - Grading costs outweigh benefits"
            
    def calculate_portfolio_grading_value(self, portfolio: List[Dict]) -> Dict:
        """
        Calculate total potential value from grading a portfolio
        
        Args:
            portfolio: List of cards in portfolio with quantities
            
        Returns:
            Portfolio grading analysis
        """
        total_investment = 0
        total_potential_value = 0
        total_net_profit = 0
        cards_worth_grading = 0
        
        analyses = []
        
        for card in portfolio:
            quantity = card.get('quantity', 1)
            analysis = self.analyze_grading_opportunity(card['prices'])
            
            if analysis['worth_grading']:
                cards_worth_grading += quantity
                total_investment += (analysis['ungraded_avg_price'] + analysis['grading_cost']) * quantity
                total_potential_value += analysis['psa10_avg_price'] * quantity
                total_net_profit += analysis['net_profit'] * quantity
                
                analyses.append({
                    'card_name': card['card_name'],
                    'quantity': quantity,
                    **analysis
                })
                
        return {
            'total_cards': len(portfolio),
            'cards_worth_grading': cards_worth_grading,
            'total_investment': total_investment,
            'total_potential_value': total_potential_value,
            'total_net_profit': total_net_profit,
            'roi_percentage': (total_net_profit / total_investment * 100) if total_investment > 0 else 0,
            'detailed_analyses': analyses
        }
        
    def _get_empty_results(self) -> Dict:
        """Return empty results structure"""
        return {
            'ungraded_avg_price': 0.0,
            'ungraded_data_points': 0,
            'graded_avg_price': 0.0,
            'graded_data_points': 0,
            'psa10_avg_price': 0.0,
            'psa10_data_points': 0,
            'multiplier': 0.0,
            'grading_cost': self.default_grading_cost,
            'gross_profit': 0.0,
            'net_profit': 0.0,
            'roi_percentage': 0.0,
            'recommendation': 'INSUFFICIENT DATA',
            'worth_grading': False,
            'ungraded_min': 0.0,
            'ungraded_max': 0.0,
            'psa10_min': 0.0,
            'psa10_max': 0.0,
        }
