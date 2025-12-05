import os
import json
import sqlite3
import psycopg2
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from pathlib import Path
import pickle
import lz4.frame
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

class EnhancedDatabaseManager:
    def __init__(self, use_postgres=False, external_drive_path="/Volumes/ExternalSSD"):
        self.use_postgres = use_postgres
        self.external_drive_path = Path(external_drive_path)
        self.cache = {}
        self.setup_logging()

        # Ensure external drive directory exists
        self.ensure_external_drive()

        if use_postgres:
            try:
                self.setup_postgres()
            except Exception as e:
                self.logger.warning(f"PostgreSQL setup failed: {e}, falling back to SQLite")
                self.use_postgres = False
                self.setup_sqlite()
        else:
            self.setup_sqlite()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def ensure_external_drive(self):
        """Ensure external drive path exists, fallback to project directory"""
        try:
            if not self.external_drive_path.exists():
                # Try common external drive mount points
                possible_paths = [
                    Path("/Volumes/ExternalSSD"),
                    Path("/Volumes/External"),
                    Path("/Volumes/USB"),
                    Path(os.path.expanduser("~/Desktop/pokemon_db"))  # Desktop fallback
                ]

                for path in possible_paths:
                    if path.exists() or path.name == "pokemon_db":
                        self.external_drive_path = path
                        break

                # Create directory if it doesn't exist
                self.external_drive_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Using database path: {self.external_drive_path}")

        except Exception as e:
            self.logger.warning(f"External drive not accessible: {e}, using project directory")
            self.external_drive_path = Path(os.getcwd()) / "data"
            self.external_drive_path.mkdir(exist_ok=True)

    def setup_postgres(self):
        """Setup PostgreSQL connection with connection pooling"""
        db_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'pokemon_cards',
            'user': 'pokemon_user',
            'password': 'pokemon_pass'
        }

        connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )

        self.Session = sessionmaker(bind=self.engine)
        self.create_tables_postgres()
        self.logger.info("PostgreSQL database initialized")

    def setup_sqlite(self):
        """Setup SQLite with optimizations and external storage"""
        db_file = self.external_drive_path / "pokemon_cards_optimized.db"

        # SQLite connection string with optimizations
        connection_string = f"sqlite:///{db_file}?cache=shared&synchronous=NORMAL&journal_mode=WAL"

        self.engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=0,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                'timeout': 30,
                'check_same_thread': False
            }
        )

        # Apply SQLite optimizations
        with self.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL;"))
            conn.execute(text("PRAGMA synchronous=NORMAL;"))
            conn.execute(text("PRAGMA cache_size=10000;"))
            conn.execute(text("PRAGMA temp_store=memory;"))
            conn.execute(text("PRAGMA mmap_size=268435456;"))  # 256MB
            conn.commit()

        self.Session = sessionmaker(bind=self.engine)
        self.create_tables_sqlite()
        self.logger.info(f"SQLite database initialized at {db_file}")

    def create_tables_sqlite(self):
        """Create optimized SQLite tables with proper indexing"""
        with self.engine.connect() as conn:
            # Price data table with vectorized design
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS card_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    date_recorded TIMESTAMP NOT NULL,
                    source TEXT NOT NULL,
                    condition TEXT,
                    graded BOOLEAN DEFAULT FALSE,
                    grade_value REAL,
                    grade_company TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Analysis results table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_name TEXT NOT NULL,
                    current_price REAL,
                    predicted_price REAL,
                    roi REAL,
                    confidence_score REAL,
                    recommendation TEXT,
                    trend TEXT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Backtesting results table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS backtesting_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_name TEXT NOT NULL,
                    inception_date TIMESTAMP,
                    total_return_pct REAL,
                    annualized_return_pct REAL,
                    sharpe_ratio REAL,
                    volatility REAL,
                    mean_price REAL,
                    std_dev REAL,
                    trend TEXT,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Grading multiplier snapshots table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS grading_multipliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_name TEXT NOT NULL,
                    ungraded_avg_price REAL,
                    psa10_avg_price REAL,
                    multiplier REAL,
                    net_profit REAL,
                    roi_percentage REAL,
                    worth_grading BOOLEAN,
                    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # BUY/SELL/HOLD signals table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_name TEXT NOT NULL,
                    price REAL,
                    signal TEXT,
                    confidence REAL,
                    z_score REAL,
                    reason TEXT,
                    signal_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Card metadata table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS card_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_name TEXT NOT NULL UNIQUE,
                    inception_date TIMESTAMP,
                    set_name TEXT,
                    card_number TEXT,
                    rarity TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create optimized indexes for vectorized queries
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_card_name_date ON card_prices(card_name, date_recorded)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_source_date ON card_prices(source, date_recorded)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_price_date ON card_prices(price, date_recorded)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_graded ON card_prices(graded, grade_value)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_analysis_card ON analysis_results(card_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_backtest_card ON backtesting_results(card_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_grading_card ON grading_multipliers(card_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_signals_card ON trading_signals(card_name, signal_date)"))

            conn.commit()

    def create_tables_postgres(self):
        """Create optimized PostgreSQL tables"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS card_prices (
                    id SERIAL PRIMARY KEY,
                    card_name VARCHAR(255) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    date_recorded TIMESTAMP NOT NULL,
                    source VARCHAR(100) NOT NULL,
                    condition VARCHAR(50),
                    graded BOOLEAN DEFAULT FALSE,
                    grade_value DECIMAL(3,1),
                    grade_company VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id SERIAL PRIMARY KEY,
                    card_name VARCHAR(255) NOT NULL,
                    current_price DECIMAL(10,2),
                    predicted_price DECIMAL(10,2),
                    roi DECIMAL(8,2),
                    confidence_score DECIMAL(5,2),
                    recommendation VARCHAR(20),
                    trend VARCHAR(50),
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Backtesting results table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS backtesting_results (
                    id SERIAL PRIMARY KEY,
                    card_name VARCHAR(255) NOT NULL,
                    inception_date TIMESTAMP,
                    total_return_pct DECIMAL(8,2),
                    annualized_return_pct DECIMAL(8,2),
                    sharpe_ratio DECIMAL(6,3),
                    volatility DECIMAL(8,2),
                    mean_price DECIMAL(10,2),
                    std_dev DECIMAL(10,2),
                    trend VARCHAR(50),
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Grading multiplier snapshots table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS grading_multipliers (
                    id SERIAL PRIMARY KEY,
                    card_name VARCHAR(255) NOT NULL,
                    ungraded_avg_price DECIMAL(10,2),
                    psa10_avg_price DECIMAL(10,2),
                    multiplier DECIMAL(6,2),
                    net_profit DECIMAL(10,2),
                    roi_percentage DECIMAL(8,2),
                    worth_grading BOOLEAN,
                    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # BUY/SELL/HOLD signals table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id SERIAL PRIMARY KEY,
                    card_name VARCHAR(255) NOT NULL,
                    price DECIMAL(10,2),
                    signal VARCHAR(10),
                    confidence DECIMAL(5,2),
                    z_score DECIMAL(6,3),
                    reason TEXT,
                    signal_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Card metadata table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS card_metadata (
                    id SERIAL PRIMARY KEY,
                    card_name VARCHAR(255) NOT NULL UNIQUE,
                    inception_date TIMESTAMP,
                    set_name VARCHAR(255),
                    card_number VARCHAR(50),
                    rarity VARCHAR(50),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            # Create indexes for performance
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_card_name_date ON card_prices(card_name, date_recorded)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_source_date ON card_prices(source, date_recorded)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_graded ON card_prices(graded, grade_value)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_backtest_card ON backtesting_results(card_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_grading_card ON grading_multipliers(card_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_signals_card ON trading_signals(card_name, signal_date)"))

            conn.commit()

    def save_price_data_batch_vectorized(self, card_name: str, price_data: List, batch_size: int = 1000):
        """Vectorized batch insert for price data with compression"""
        if not price_data:
            return

        try:
            # Convert to DataFrame for vectorized operations
            data_dicts = []
            for price in price_data:
                data_dicts.append({
                    'card_name': card_name,
                    'price': float(price.price),
                    'date_recorded': price.date,
                    'source': price.source,
                    'condition': price.condition,
                    'graded': bool(price.graded),
                    'grade_value': float(price.grade_value) if price.grade_value else None,
                    'grade_company': price.grade_company
                })

            df = pd.DataFrame(data_dicts)

            # Remove duplicates using vectorized operations
            df = df.drop_duplicates(subset=['card_name', 'date_recorded', 'source', 'price'])

            # Batch insert with pandas to_sql for optimal performance
            df.to_sql('card_prices', self.engine, if_exists='append', index=False,
                     method='multi', chunksize=batch_size)

            # Cache recent data
            cache_key = f"recent_prices_{card_name}"
            compressed_data = lz4.frame.compress(pickle.dumps(df.tail(100).to_dict('records')))
            self.cache[cache_key] = compressed_data

            self.logger.info(f"Saved {len(df)} price records for {card_name}")

        except Exception as e:
            self.logger.error(f"Error saving price data: {e}")

    def get_card_prices_vectorized(self, card_name: str, days_back: int = 365) -> pd.DataFrame:
        """Vectorized retrieval of card prices with caching"""
        cache_key = f"prices_{card_name}_{days_back}"

        # Check cache first
        if cache_key in self.cache:
            try:
                cached_data = pickle.loads(lz4.frame.decompress(self.cache[cache_key]))
                return pd.DataFrame(cached_data)
            except Exception:
                pass

        try:
            cutoff_date = datetime.now() - pd.Timedelta(days=days_back)

            query = text("""
                SELECT card_name, price, date_recorded as date, source, condition, 
                       graded, grade_value, grade_company
                FROM card_prices 
                WHERE card_name = :card_name 
                AND date_recorded >= :cutoff_date 
                ORDER BY date_recorded
            """)

            df = pd.read_sql(query, self.engine, params={
                'card_name': card_name,
                'cutoff_date': cutoff_date
            })

            if not df.empty:
                # Vectorized data type conversions
                df['date'] = pd.to_datetime(df['date'])
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                df['graded'] = df['graded'].astype(bool)

                # Cache the result
                compressed_data = lz4.frame.compress(pickle.dumps(df.to_dict('records')))
                self.cache[cache_key] = compressed_data

            return df

        except Exception as e:
            self.logger.error(f"Error retrieving prices for {card_name}: {e}")
            return pd.DataFrame()

    def save_analysis_results(self, card_name: str, results: Dict[str, Any]):
        """Save analysis results with upsert logic"""
        try:
            with self.engine.connect() as conn:
                # Check if recent analysis exists
                check_query = text("""
                    SELECT id FROM analysis_results 
                    WHERE card_name = :card_name 
                    AND analysis_date > datetime('now', '-1 hour')
                """)

                existing = conn.execute(check_query, {'card_name': card_name}).fetchone()

                if existing:
                    # Update existing
                    update_query = text("""
                        UPDATE analysis_results 
                        SET current_price = :current_price,
                            predicted_price = :predicted_price,
                            roi = :roi,
                            confidence_score = :confidence_score,
                            recommendation = :recommendation,
                            trend = :trend,
                            analysis_date = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """)
                    conn.execute(update_query, {
                        'id': existing[0],
                        'current_price': results['current_price'],
                        'predicted_price': results['predicted_price'],
                        'roi': results['roi'],
                        'confidence_score': results['confidence_score'],
                        'recommendation': results['recommendation'],
                        'trend': results['trend']
                    })
                else:
                    # Insert new
                    insert_query = text("""
                        INSERT INTO analysis_results 
                        (card_name, current_price, predicted_price, roi, 
                         confidence_score, recommendation, trend)
                        VALUES (:card_name, :current_price, :predicted_price, :roi,
                                :confidence_score, :recommendation, :trend)
                    """)
                    conn.execute(insert_query, {
                        'card_name': card_name,
                        'current_price': results['current_price'],
                        'predicted_price': results['predicted_price'],
                        'roi': results['roi'],
                        'confidence_score': results['confidence_score'],
                        'recommendation': results['recommendation'],
                        'trend': results['trend']
                    })

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error saving analysis results: {e}")
    
    def save_backtesting_results(self, card_name: str, metrics: Dict[str, Any]):
        """Save backtesting results to database"""
        try:
            with self.engine.connect() as conn:
                insert_query = text("""
                    INSERT INTO backtesting_results 
                    (card_name, inception_date, total_return_pct, annualized_return_pct,
                     sharpe_ratio, volatility, mean_price, std_dev, trend)
                    VALUES (:card_name, :inception_date, :total_return_pct, :annualized_return_pct,
                            :sharpe_ratio, :volatility, :mean_price, :std_dev, :trend)
                """)
                
                conn.execute(insert_query, {
                    'card_name': card_name,
                    'inception_date': metrics.get('inception_date'),
                    'total_return_pct': metrics.get('total_return_pct'),
                    'annualized_return_pct': metrics.get('annualized_return_pct'),
                    'sharpe_ratio': metrics.get('sharpe_ratio'),
                    'volatility': metrics.get('volatility'),
                    'mean_price': metrics.get('mean_price'),
                    'std_dev': metrics.get('std_dev'),
                    'trend': metrics.get('trend')
                })
                
                conn.commit()
                self.logger.info(f"Saved backtesting results for {card_name}")
                
        except Exception as e:
            self.logger.error(f"Error saving backtesting results: {e}")
    
    def save_grading_analysis(self, card_name: str, analysis: Dict[str, Any]):
        """Save grading multiplier analysis to database"""
        try:
            with self.engine.connect() as conn:
                insert_query = text("""
                    INSERT INTO grading_multipliers 
                    (card_name, ungraded_avg_price, psa10_avg_price, multiplier,
                     net_profit, roi_percentage, worth_grading)
                    VALUES (:card_name, :ungraded_avg_price, :psa10_avg_price, :multiplier,
                            :net_profit, :roi_percentage, :worth_grading)
                """)
                
                conn.execute(insert_query, {
                    'card_name': card_name,
                    'ungraded_avg_price': analysis.get('ungraded_avg_price'),
                    'psa10_avg_price': analysis.get('psa10_avg_price'),
                    'multiplier': analysis.get('multiplier'),
                    'net_profit': analysis.get('net_profit'),
                    'roi_percentage': analysis.get('roi_percentage'),
                    'worth_grading': analysis.get('worth_grading')
                })
                
                conn.commit()
                self.logger.info(f"Saved grading analysis for {card_name}")
                
        except Exception as e:
            self.logger.error(f"Error saving grading analysis: {e}")
    
    def save_trading_signal(self, card_name: str, signal: Dict[str, Any]):
        """Save trading signal to database"""
        try:
            with self.engine.connect() as conn:
                insert_query = text("""
                    INSERT INTO trading_signals 
                    (card_name, price, signal, confidence, z_score, reason)
                    VALUES (:card_name, :price, :signal, :confidence, :z_score, :reason)
                """)
                
                conn.execute(insert_query, {
                    'card_name': card_name,
                    'price': signal.get('current_price'),
                    'signal': signal.get('signal'),
                    'confidence': signal.get('confidence'),
                    'z_score': signal.get('z_score'),
                    'reason': signal.get('reason')
                })
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error saving trading signal: {e}")

    def get_market_summary_vectorized(self) -> Dict[str, Any]:
        """Get vectorized market summary statistics"""
        try:
            with self.engine.connect() as conn:
                # Get recent market data using vectorized SQL
                query = text("""
                    SELECT 
                        card_name,
                        AVG(price) as avg_price,
                        COUNT(*) as data_points,
                        MIN(date_recorded) as first_date,
                        MAX(date_recorded) as last_date,
                        STDDEV(price) as price_volatility
                    FROM card_prices 
                    WHERE date_recorded >= datetime('now', '-30 days')
                    GROUP BY card_name
                    HAVING COUNT(*) >= 5
                    ORDER BY avg_price DESC
                    LIMIT 100
                """)

                df = pd.read_sql(query, conn)

                if df.empty:
                    return {}

                # Vectorized calculations
                summary = {
                    'total_cards': len(df),
                    'avg_market_price': float(df['avg_price'].mean()),
                    'median_market_price': float(df['avg_price'].median()),
                    'highest_avg_price': float(df['avg_price'].max()),
                    'most_volatile': df.loc[df['price_volatility'].idxmax(), 'card_name'] if 'price_volatility' in df.columns else 'N/A',
                    'most_data_points': df.loc[df['data_points'].idxmax(), 'card_name'],
                    'top_cards': df.head(10)[['card_name', 'avg_price']].to_dict('records')
                }

                return summary

        except Exception as e:
            self.logger.error(f"Error getting market summary: {e}")
            return {}

    def optimize_database(self):
        """Perform database optimization operations"""
        try:
            with self.engine.connect() as conn:
                if not self.use_postgres:
                    # SQLite optimizations
                    conn.execute(text("VACUUM;"))
                    conn.execute(text("ANALYZE;"))
                    conn.execute(text("PRAGMA optimize;"))
                else:
                    # PostgreSQL optimizations
                    conn.execute(text("VACUUM ANALYZE card_prices;"))
                    conn.execute(text("VACUUM ANALYZE analysis_results;"))

                conn.commit()

            # Clear old cache entries
            cache_keys_to_remove = [k for k in self.cache.keys() if len(self.cache) > 100]
            for key in cache_keys_to_remove[:50]:  # Remove oldest 50 entries
                del self.cache[key]

            self.logger.info("Database optimization completed")

        except Exception as e:
            self.logger.error(f"Error optimizing database: {e}")

    def close(self):
        """Clean shutdown with optimization"""
        try:
            self.optimize_database()
            if hasattr(self, 'engine'):
                self.engine.dispose()
            self.logger.info("Database connection closed")
        except Exception as e:
            self.logger.error(f"Error closing database: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.close()
        except:
            pass
