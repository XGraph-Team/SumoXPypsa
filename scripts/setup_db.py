"""
Database Setup Script
Run this to initialize the database
"""

import sys
import os

# Force SQLite for initial setup
os.environ['DATABASE_URL'] = 'sqlite:///manhattan_grid.db'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import db_manager, Base
from config.settings import settings
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def setup_database():
    """Initialize database with tables and seed data"""
    
    print("=" * 60)
    print("MANHATTAN POWER GRID - DATABASE SETUP")
    print("=" * 60)
    
    # Initialize connections
    print("\n1. Initializing database connections...")
    db_manager.initialize()
    
    # Create tables
    print("2. Creating database tables...")
    db_manager.create_tables()
    
    # Seed initial data
    print("3. Loading initial configuration...")
    seed_initial_data()
    
    print("\nSuccess Database setup complete!")
    print("=" * 60)

def seed_initial_data():
    """Load initial substations and components"""
    
    from config.database import Substation, Transformer
    
    with db_manager.get_session() as session:
        # Add substations
        for name, config in settings.grid_config['substations'].items():
            substation = Substation(
                name=name,
                lat=config['lat'],
                lon=config['lon'],
                voltage_kv=138,
                capacity_mva=config['capacity_mva'],
                operational=True,
                health_status="normal"
            )
            session.add(substation)
        
        session.commit()
        logger.info(f"Added {len(settings.grid_config['substations'])} substations")

if __name__ == "__main__":
    setup_database()