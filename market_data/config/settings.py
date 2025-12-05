"""
Application settings and configuration
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import json
from pathlib import Path

@dataclass
class AppSettings:
    """Application-wide settings"""
    
    # Analysis settings
    DEFAULT_OUTLIER_THRESHOLD_BP: float = 50.0
    DEFAULT_SHORT_TENOR_DAYS: int = 360
    DEFAULT_LONG_TENOR_DAYS: int = 3600
    CURVE_INTERPOLATION_METHOD: str = 'linear'  # 'linear', 'cubic', 'akima'
    
    # Display settings
    MAX_CURVES_TO_DISPLAY: int = 10
    CHART_DPI: int = 100
    CHART_FIGSIZE: tuple = (10, 6)
    TABLE_ROW_HEIGHT: int = 25
    DECIMAL_PLACES: int = 4
    
    # Performance settings
    CACHE_ENABLED: bool = True
    CACHE_SIZE_MB: int = 100
    CACHE_TTL_SECONDS: int = 3600
    MAX_WORKERS: int = 4
    CHUNK_SIZE: int = 1000
    
    # File settings
    DEFAULT_EXPORT_PATH: Path = Path.home() / "Documents" / "xVA_Analysis"
    SUPPORTED_FILE_TYPES: List[str] = field(default_factory=lambda: ['.json', '.csv', '.xlsx'])
    MAX_FILE_SIZE_MB: int = 50
    
    # Curve type patterns
    CURVE_TYPE_PATTERNS: Dict[str, List[str]] = field(default_factory=lambda: {
        'funding': ['FVA', 'FUNDING', 'FCA', 'COLVA'],
        'credit': ['BSPREAD', 'CREDIT', 'CDS', 'CVA', 'DVA'],
        'ir': ['IR', 'SWAP', 'LIBOR', 'SOFR', 'ESTR', 'OIS']
    })
    
    # Chart colors (backup if theme not available)
    DEFAULT_COLORS: List[str] = field(default_factory=lambda: [
        '#4a90e2', '#5cb85c', '#f0ad4e', '#d9534f', 
        '#9b59b6', '#3498db', '#e67e22', '#1abc9c'
    ])
    
    def save_to_file(self, filepath: Path):
        """Save settings to JSON file"""
        settings_dict = {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith('_')
        }
        with open(filepath, 'w') as f:
            json.dump(settings_dict, f, indent=2, default=str)
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'AppSettings':
        """Load settings from JSON file"""
        if filepath.exists():
            with open(filepath, 'r') as f:
                settings_dict = json.load(f)
            return cls(**settings_dict)
        return cls()
    
    def validate(self) -> bool:
        """Validate settings values"""
        validations = [
            self.DEFAULT_OUTLIER_THRESHOLD_BP > 0,
            self.DEFAULT_SHORT_TENOR_DAYS > 0,
            self.DEFAULT_LONG_TENOR_DAYS > self.DEFAULT_SHORT_TENOR_DAYS,
            self.MAX_CURVES_TO_DISPLAY > 0,
            self.CACHE_SIZE_MB > 0,
            self.MAX_FILE_SIZE_MB > 0
        ]
        return all(validations)