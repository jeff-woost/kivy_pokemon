"""
API configuration settings for market data endpoints
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class APIConfig:
    """Configuration for API endpoints"""
    
    # Base configuration
    BASE_URL: str = os.getenv('MARKET_DATA_API_URL', 'https://api.marketdata.com')
    API_VERSION: str = 'v1'
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    
    # Authentication
    AUTH_TYPE: str = 'bearer'  # 'bearer', 'api_key', 'basic'
    API_KEY: Optional[str] = os.getenv('MARKET_DATA_API_KEY')
    API_SECRET: Optional[str] = os.getenv('MARKET_DATA_API_SECRET')
    
    # Endpoints
    ENDPOINTS: Dict[str, str] = {
        'funding_curves': '/curves/funding/{date}',
        'credit_curves': '/curves/credit/{date}',
        'ir_curves': '/curves/ir/{date}',
        'all_curves': '/curves/all/{date}',
        'historical': '/curves/historical/{curve_id}/{start_date}/{end_date}'
    }
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.AUTH_TYPE == 'bearer' and self.API_KEY:
            headers['Authorization'] = f'Bearer {self.API_KEY}'
        elif self.AUTH_TYPE == 'api_key' and self.API_KEY:
            headers['X-API-Key'] = self.API_KEY
        
        return headers
    
    def get_endpoint_url(self, endpoint: str, **kwargs) -> str:
        """Build full URL for endpoint"""
        if endpoint not in self.ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint}")
        
        path = self.ENDPOINTS[endpoint].format(**kwargs)
        return f"{self.BASE_URL}/{self.API_VERSION}{path}"