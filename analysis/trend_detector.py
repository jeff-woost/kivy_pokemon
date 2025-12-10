"""
Trend detection algorithm for cross-source price analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging


class TrendDetector:
    """Detects price trends across multiple data sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_multi_source_trends(self, aggregated_data: Dict) -> Dict:
        """
        Analyze trends across multiple data sources
        
        Args:
            aggregated_data: Aggregated data from ScraperManager
            
        Returns:
            Comprehensive trend analysis
        """
        try:
            if aggregated_data['total_data_points'] == 0:
                return self._get_empty_analysis()
                
            # Calculate trend score
            trend_score = self._calculate_trend_score(aggregated_data)
            
            # Detect price divergence
            divergence = self._detect_price_divergence(aggregated_data)
            
            # Calculate momentum indicators
            momentum = self._calculate_momentum(aggregated_data)
            
            # Generate predictions
            prediction = self._predict_trend(aggregated_data, trend_score, momentum)
            
            return {
                'card_name': aggregated_data['card_name'],
                'trend_score': trend_score,
                'divergence_analysis': divergence,
                'momentum_indicators': momentum,
                'prediction': prediction,
                'confidence_level': self._calculate_confidence(aggregated_data),
                'data_quality': aggregated_data['data_quality'],
                'analysis_date': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return self._get_empty_analysis()
            
    def _calculate_trend_score(self, data: Dict) -> float:
        """
        Calculate trend score (0-100) based on multiple factors
        
        Factors:
        - Price velocity (40%)
        - Volume/sales momentum (20%)
        - Cross-source agreement (20%)
        - Historical pattern (20%)
        """
        try:
            trend_indicators = data.get('trend_indicators', {})
            price_by_source = data.get('price_by_source', {})
            data_quality = data.get('data_quality', {})
            
            # Factor 1: Price velocity (40 points max)
            # Formula: Maps price velocity to score
            # -10% velocity = 0 points, 0% = 20 points, +10% = 40 points
            # velocity_score = min(40, max(0, (velocity + 10) * 2))
            velocity = trend_indicators.get('price_velocity_pct', 0)
            velocity_score = min(40, max(0, (velocity + 10) * 2))  # Map -10% to +10% to 0-40
            
            # Factor 2: Volume momentum (20 points max)
            # Higher data points from recent sources indicate strong interest
            total_points = data_quality.get('total_data_points', 0)
            volume_score = min(20, total_points / 5)  # 100 data points = 20 points
            
            # Factor 3: Cross-source agreement (20 points max)
            agreement_score = self._calculate_source_agreement(price_by_source)
            
            # Factor 4: Historical pattern (20 points max)
            pattern_score = self._calculate_pattern_score(trend_indicators)
            
            # Combine scores
            total_score = velocity_score + volume_score + agreement_score + pattern_score
            
            # Normalize to 0-100
            return min(100, max(0, total_score))
            
        except Exception as e:
            self.logger.warning(f"Error calculating trend score: {e}")
            return 50.0  # Neutral score
            
    def _calculate_source_agreement(self, price_by_source: Dict) -> float:
        """Calculate how well sources agree on pricing (0-20 points)"""
        try:
            if len(price_by_source) < 2:
                return 10.0  # Neutral if only one source
                
            # Get mean prices from each source
            means = [data['mean'] for data in price_by_source.values() if data['mean'] > 0]
            
            if not means:
                return 10.0
                
            # Calculate coefficient of variation
            mean_of_means = np.mean(means)
            std_of_means = np.std(means)
            
            if mean_of_means == 0:
                return 10.0
                
            cv = std_of_means / mean_of_means
            
            # Lower CV = higher agreement
            # CV < 0.1 = excellent (20 points)
            # CV > 0.5 = poor (0 points)
            agreement_score = max(0, 20 * (1 - cv * 2))
            
            return min(20, agreement_score)
            
        except Exception as e:
            self.logger.warning(f"Error calculating source agreement: {e}")
            return 10.0
            
    def _calculate_pattern_score(self, trend_indicators: Dict) -> float:
        """Calculate historical pattern score (0-20 points)"""
        try:
            trend_direction = trend_indicators.get('trend_direction', 'stable')
            volatility = trend_indicators.get('volatility', 50)
            
            # Base score on trend direction
            if trend_direction == 'upward':
                base_score = 15
            elif trend_direction == 'stable':
                base_score = 10
            else:  # downward
                base_score = 5
                
            # Adjust for volatility (lower volatility = more reliable pattern)
            # Volatility < 20% = +5 points
            # Volatility > 50% = -5 points
            volatility_adjustment = max(-5, min(5, (30 - volatility) / 10))
            
            return max(0, min(20, base_score + volatility_adjustment))
            
        except Exception as e:
            self.logger.warning(f"Error calculating pattern score: {e}")
            return 10.0
            
    def _detect_price_divergence(self, data: Dict) -> Dict:
        """
        Detect price divergence between sources (potential arbitrage)
        """
        try:
            price_by_source = data.get('price_by_source', {})
            
            if len(price_by_source) < 2:
                return {'has_divergence': False, 'opportunities': []}
                
            # Find min and max prices across sources
            sources_with_prices = [(source, info['mean']) for source, info in price_by_source.items()]
            sources_with_prices.sort(key=lambda x: x[1])
            
            min_source, min_price = sources_with_prices[0]
            max_source, max_price = sources_with_prices[-1]
            
            # Calculate divergence percentage
            divergence_pct = ((max_price - min_price) / min_price * 100) if min_price > 0 else 0
            
            # Significant divergence if > 10%
            has_divergence = divergence_pct > 10
            
            opportunities = []
            if has_divergence:
                opportunities.append({
                    'type': 'arbitrage',
                    'buy_source': min_source,
                    'sell_source': max_source,
                    'buy_price': min_price,
                    'sell_price': max_price,
                    'potential_profit_pct': divergence_pct,
                    'confidence': 'high' if divergence_pct > 20 else 'medium'
                })
                
            return {
                'has_divergence': has_divergence,
                'divergence_pct': divergence_pct,
                'opportunities': opportunities,
                'price_range': {
                    'min': min_price,
                    'max': max_price,
                    'min_source': min_source,
                    'max_source': max_source
                }
            }
            
        except Exception as e:
            self.logger.warning(f"Error detecting divergence: {e}")
            return {'has_divergence': False, 'opportunities': []}
            
    def _calculate_momentum(self, data: Dict) -> Dict:
        """
        Calculate volume and sales momentum indicators
        """
        try:
            trend_indicators = data.get('trend_indicators', {})
            data_quality = data.get('data_quality', {})
            
            # Price velocity as momentum indicator
            price_velocity = trend_indicators.get('price_velocity_pct', 0)
            
            # Data point growth as volume momentum
            total_points = data_quality.get('total_data_points', 0)
            
            # Calculate momentum strength
            if price_velocity > 15:
                momentum_strength = 'strong_upward'
            elif price_velocity > 5:
                momentum_strength = 'moderate_upward'
            elif price_velocity > -5:
                momentum_strength = 'neutral'
            elif price_velocity > -15:
                momentum_strength = 'moderate_downward'
            else:
                momentum_strength = 'strong_downward'
                
            return {
                'price_momentum': price_velocity,
                'volume_indicator': total_points,
                'momentum_strength': momentum_strength,
                'buy_pressure': max(0, min(100, 50 + price_velocity * 2))  # 0-100 scale
            }
            
        except Exception as e:
            self.logger.warning(f"Error calculating momentum: {e}")
            return {'momentum_strength': 'neutral', 'buy_pressure': 50}
            
    def _predict_trend(self, data: Dict, trend_score: float, momentum: Dict) -> Dict:
        """
        Predict future trend based on historical patterns
        """
        try:
            trend_indicators = data.get('trend_indicators', {})
            graded_comparison = data.get('graded_vs_ungraded', {})
            
            # Determine prediction direction
            if trend_score > 70:
                direction = 'strong_upward'
                recommendation = 'BUY'
            elif trend_score > 55:
                direction = 'upward'
                recommendation = 'BUY'
            elif trend_score > 45:
                direction = 'stable'
                recommendation = 'HOLD'
            elif trend_score > 30:
                direction = 'downward'
                recommendation = 'SELL'
            else:
                direction = 'strong_downward'
                recommendation = 'SELL'
                
            # Calculate confidence in prediction
            data_quality = data.get('data_quality', {})
            base_confidence = data_quality.get('confidence_score', 50)
            
            # Adjust confidence based on momentum agreement
            momentum_strength = momentum.get('momentum_strength', 'neutral')
            if ('upward' in direction and 'upward' in momentum_strength) or \
               ('downward' in direction and 'downward' in momentum_strength):
                confidence_adjustment = 10
            else:
                confidence_adjustment = -10
                
            prediction_confidence = min(100, max(0, base_confidence + confidence_adjustment))
            
            return {
                'direction': direction,
                'recommendation': recommendation,
                'confidence': prediction_confidence,
                'timeframe': '30-90 days',
                'key_factors': self._identify_key_factors(data, trend_score, momentum)
            }
            
        except Exception as e:
            self.logger.warning(f"Error predicting trend: {e}")
            return {
                'direction': 'unknown',
                'recommendation': 'HOLD',
                'confidence': 0,
                'timeframe': 'unknown'
            }
            
    def _identify_key_factors(self, data: Dict, trend_score: float, momentum: Dict) -> List[str]:
        """Identify key factors driving the trend"""
        factors = []
        
        try:
            trend_indicators = data.get('trend_indicators', {})
            
            # Price velocity
            velocity = trend_indicators.get('price_velocity_pct', 0)
            if abs(velocity) > 10:
                factors.append(f"{'Strong' if abs(velocity) > 20 else 'Moderate'} price {'increase' if velocity > 0 else 'decrease'} ({velocity:.1f}%)")
                
            # Multi-source data
            sources_count = data.get('data_quality', {}).get('sources_count', 0)
            if sources_count >= 3:
                factors.append(f"Data confirmed across {sources_count} sources")
                
            # Grading multiplier
            graded_comparison = data.get('graded_vs_ungraded', {})
            multiplier = graded_comparison.get('multiplier')
            if multiplier and multiplier >= 3.0:
                factors.append(f"High grading multiplier ({multiplier:.1f}x)")
                
            # Momentum
            momentum_strength = momentum.get('momentum_strength', '')
            if 'strong' in momentum_strength:
                factors.append(f"Strong market momentum")
                
        except Exception as e:
            self.logger.warning(f"Error identifying key factors: {e}")
            
        return factors if factors else ['Insufficient data for detailed analysis']
        
    def _calculate_confidence(self, data: Dict) -> str:
        """
        Calculate confidence level based on data quality and sample size
        
        Returns:
            'very_high', 'high', 'medium', 'low', 'very_low'
        """
        try:
            data_quality = data.get('data_quality', {})
            confidence_score = data_quality.get('confidence_score', 0)
            
            if confidence_score >= 80:
                return 'very_high'
            elif confidence_score >= 60:
                return 'high'
            elif confidence_score >= 40:
                return 'medium'
            elif confidence_score >= 20:
                return 'low'
            else:
                return 'very_low'
                
        except Exception as e:
            self.logger.warning(f"Error calculating confidence: {e}")
            return 'low'
            
    def _get_empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'card_name': 'Unknown',
            'trend_score': 0,
            'divergence_analysis': {'has_divergence': False},
            'momentum_indicators': {'momentum_strength': 'neutral'},
            'prediction': {
                'direction': 'unknown',
                'recommendation': 'HOLD',
                'confidence': 0
            },
            'confidence_level': 'very_low',
            'data_quality': {'confidence_score': 0},
            'analysis_date': datetime.now()
        }
        
    def batch_analyze_cards(self, cards_data: List[Dict]) -> List[Dict]:
        """
        Analyze trends for multiple cards in batch
        
        Args:
            cards_data: List of aggregated data for multiple cards
            
        Returns:
            List of trend analyses sorted by trend score
        """
        analyses = []
        
        for card_data in cards_data:
            try:
                analysis = self.analyze_multi_source_trends(card_data)
                analyses.append(analysis)
            except Exception as e:
                self.logger.error(f"Error analyzing card {card_data.get('card_name', 'Unknown')}: {e}")
                continue
                
        # Sort by trend score (highest first)
        analyses.sort(key=lambda x: x['trend_score'], reverse=True)
        
        return analyses
