"""
Manhattan Power Grid - Enterprise Database Layer
Professional data persistence with async support, connection pooling, and monitoring
Compatible with both SQLite and PostgreSQL
"""

import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import Optional, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool

# Check database type
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///manhattan_grid.db')
IS_SQLITE = 'sqlite' in DATABASE_URL.lower()

# Import settings
from .settings import settings

# Optional imports for PostgreSQL
if not IS_SQLITE:
    from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TIMESTAMP
    from redis import asyncio as aioredis
    import redis
else:
    # SQLite fallbacks
    JSONB = Text
    ARRAY = Text
    TIMESTAMP = DateTime

# Create declarative base
Base = declarative_base()

# ==================== HELPER FUNCTIONS ====================

def get_uuid_type():
    """Get appropriate UUID column type based on database"""
    if IS_SQLITE:
        return String(36)
    else:
        return UUID(as_uuid=True)

def get_json_type():
    """Get appropriate JSON column type"""
    if IS_SQLITE:
        return Text
    else:
        return JSONB

def get_array_type(item_type):
    """Get appropriate array column type"""
    if IS_SQLITE:
        return Text  # Will serialize as JSON
    else:
        return ARRAY(item_type)

def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())

# ==================== DATA MODELS ====================

class NetworkState(Base):
    """Complete network state at a point in time"""
    __tablename__ = "network_states"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    simulation_time = Column(Integer, nullable=False)
    
    # Power System State
    power_data = Column(Text, nullable=False)  # JSON string
    total_load_mw = Column(Float, nullable=False)
    total_generation_mw = Column(Float, nullable=False)
    system_frequency = Column(Float, default=60.0)
    
    # Traffic System State  
    traffic_data = Column(Text, nullable=False)  # JSON string
    active_vehicles = Column(Integer, nullable=False)
    average_speed_mph = Column(Float)
    congestion_level = Column(Float)
    
    # System Health
    health_score = Column(Float)
    active_failures = Column(Text)  # JSON array
    warnings = Column(Text)  # JSON array
    
    # Indexes for fast queries
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_simulation_time', 'simulation_time'),
        Index('idx_health_score', 'health_score'),
    )

class Substation(Base):
    """Substation configuration and state"""
    __tablename__ = "substations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    
    # Electrical parameters
    voltage_kv = Column(Float, nullable=False)
    capacity_mva = Column(Float, nullable=False)
    current_load_mva = Column(Float, default=0)
    power_factor = Column(Float, default=0.95)
    
    # Status
    operational = Column(Boolean, default=True)
    health_status = Column(String(20), default="normal")
    last_maintenance = Column(DateTime)
    failure_probability = Column(Float, default=0.01)
    
    # Relationships
    transformers = relationship("Transformer", back_populates="substation")
    incidents = relationship("Incident", back_populates="substation")
    
    # Configuration
    config = Column(Text, default='{}')  # JSON string

class Transformer(Base):
    """Transformer configuration and state"""
    __tablename__ = "transformers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    substation_id = Column(String(36), ForeignKey("substations.id"))
    
    # Electrical parameters
    primary_voltage_kv = Column(Float, nullable=False)
    secondary_voltage_kv = Column(Float, nullable=False)
    capacity_mva = Column(Float, nullable=False)
    impedance_pu = Column(Float, default=0.1)
    
    # Real-time measurements
    temperature_c = Column(Float)
    oil_level = Column(Float)
    load_percentage = Column(Float, default=0)
    
    # Status
    operational = Column(Boolean, default=True)
    tap_position = Column(Integer, default=0)
    cooling_stage = Column(Integer, default=0)
    
    # Relationships
    substation = relationship("Substation", back_populates="transformers")

class PowerLine(Base):
    """Power line/cable configuration"""
    __tablename__ = "power_lines"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    line_type = Column(String(20))
    
    # Connectivity
    from_bus = Column(String(100), nullable=False)
    to_bus = Column(String(100), nullable=False)
    coordinates = Column(Text)  # GeoJSON LineString
    
    # Electrical parameters
    voltage_kv = Column(Float, nullable=False)
    length_km = Column(Float, nullable=False)
    resistance_ohm_per_km = Column(Float)
    reactance_ohm_per_km = Column(Float)
    capacity_mva = Column(Float)
    
    # Real-time state
    current_flow_mva = Column(Float, default=0)
    temperature_c = Column(Float)
    sag_mm = Column(Float)
    
    # Status
    operational = Column(Boolean, default=True)
    health_status = Column(String(20), default="normal")

class TrafficSignal(Base):
    """Traffic signal configuration and state"""
    __tablename__ = "traffic_signals"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    signal_id = Column(String(50), unique=True, nullable=False)
    intersection_name = Column(String(200))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    
    # Power connection
    power_source = Column(String(100))
    power_consumption_w = Column(Float, default=300)
    has_backup_power = Column(Boolean, default=False)
    battery_level = Column(Float)
    
    # Signal state
    current_phase = Column(String(20))
    phase_time_remaining = Column(Integer)
    operational = Column(Boolean, default=True)
    control_mode = Column(String(20), default="adaptive")
    
    # Traffic measurements
    vehicle_count_per_hour = Column(Integer)
    average_wait_time_s = Column(Float)
    congestion_level = Column(Float)

class EVChargingStation(Base):
    """EV charging station configuration and state"""
    __tablename__ = "ev_charging_stations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    
    # Charging infrastructure
    total_chargers = Column(Integer, nullable=False)
    level2_chargers = Column(Integer, default=0)
    level3_chargers = Column(Integer, default=0)
    
    # Power parameters
    max_power_kw = Column(Float, nullable=False)
    current_load_kw = Column(Float, default=0)
    power_source = Column(String(100))
    has_solar = Column(Boolean, default=False)
    solar_capacity_kw = Column(Float, default=0)
    has_battery = Column(Boolean, default=False)
    battery_capacity_kwh = Column(Float, default=0)
    battery_soc = Column(Float, default=50)
    
    # Usage statistics
    vehicles_charging = Column(Integer, default=0)
    vehicles_queued = Column(Integer, default=0)
    average_session_kwh = Column(Float)
    daily_energy_kwh = Column(Float)
    
    # V2G capabilities
    v2g_enabled = Column(Boolean, default=False)
    v2g_power_available_kw = Column(Float, default=0)

class Incident(Base):
    """System incidents and failures"""
    __tablename__ = "incidents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    incident_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    
    # Location
    substation_id = Column(String(36), ForeignKey("substations.id"), nullable=True)
    affected_area = Column(Text)  # GeoJSON polygon
    
    # Impact
    customers_affected = Column(Integer, default=0)
    load_lost_mw = Column(Float, default=0)
    estimated_duration_min = Column(Integer)
    
    # Response
    status = Column(String(20), default="active")
    response_team = Column(String(100))
    resolution_time = Column(DateTime)
    root_cause = Column(Text)
    
    # Relationships
    substation = relationship("Substation", back_populates="incidents")

class SimulationRun(Base):
    """Track simulation runs for replay and analysis"""
    __tablename__ = "simulation_runs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200))
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    # Configuration
    scenario = Column(String(100))
    parameters = Column(Text)  # JSON
    
    # Results
    total_energy_mwh = Column(Float)
    peak_load_mw = Column(Float)
    incidents_count = Column(Integer, default=0)
    average_frequency = Column(Float)
    
    # Metadata
    user_id = Column(String(100))
    notes = Column(Text)
    tags = Column(Text)  # JSON array

class PredictionModel(Base):
    """ML model tracking and versioning"""
    __tablename__ = "prediction_models"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_type = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Performance metrics
    accuracy = Column(Float)
    mape = Column(Float)
    training_samples = Column(Integer)
    
    # Model data
    model_path = Column(String(500))
    parameters = Column(Text)  # JSON
    feature_importance = Column(Text)  # JSON
    
    # Status
    active = Column(Boolean, default=False)
    last_prediction = Column(DateTime)

# ==================== DATABASE ENGINE ====================

class DatabaseManager:
    """Professional database management with connection pooling"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self.redis_client = None
        self.async_redis_client = None
        
    def initialize(self):
        """Initialize database connections"""
        db_url = os.environ.get('DATABASE_URL', 'sqlite:///manhattan_grid.db')
        
        if IS_SQLITE:
            # SQLite configuration
            connect_args = {"check_same_thread": False}
            self.engine = create_engine(
                db_url,
                connect_args=connect_args,
                echo=settings.debug
            )
        else:
            # PostgreSQL configuration
            self.engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                pool_pre_ping=True,
                echo=settings.debug
            )
            
            # Async engine for PostgreSQL
            self.async_engine = create_async_engine(
                settings.get_database_url(async_mode=True),
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                echo=settings.debug
            )
            
            # Initialize Redis if using PostgreSQL
            try:
                import redis
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True
                )
            except:
                print("Redis not available, continuing without caching")
        
        # Session factories
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )
        
        if not IS_SQLITE and self.async_engine:
            self.AsyncSessionLocal = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        
        print(f"Database initialized ({'SQLite' if IS_SQLITE else 'PostgreSQL'})")
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        print("Database tables created")
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session"""
        if IS_SQLITE or not self.AsyncSessionLocal:
            raise NotImplementedError("Async sessions not available with SQLite")
        
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                print(f"Async database error: {e}")
                raise
    
    def close(self):
        """Close all connections"""
        if self.SessionLocal:
            self.SessionLocal.remove()
        if self.engine:
            self.engine.dispose()
        if self.redis_client:
            self.redis_client.close()
        print("Database connections closed")
    
    async def close_async(self):
        """Close async connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if hasattr(self, 'async_redis_client') and self.async_redis_client:
            await self.async_redis_client.close()

# Global database manager
db_manager = DatabaseManager()

# Export for easy access
__all__ = [
    "Base",
    "NetworkState",
    "Substation", 
    "Transformer",
    "PowerLine",
    "TrafficSignal",
    "EVChargingStation",
    "Incident",
    "SimulationRun",
    "PredictionModel",
    "db_manager"
]