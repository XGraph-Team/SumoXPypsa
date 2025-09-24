"""
Manhattan Power Grid - Professional Configuration System
This is what Con Edison and NYC DOT would actually use
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class SimulationMode(str, Enum):
    REALTIME = "realtime"
    ACCELERATED = "accelerated"
    HISTORICAL = "historical"
    PREDICTIVE = "predictive"

class PowerGridSettings(BaseSettings):
    """
    Professional configuration management using Pydantic
    Type-safe, validated, and environment-aware
    """
    
    # Project Info
    project_name: str = Field("Manhattan Integrated Power Grid", description="System name")
    version: str = Field("2.0.0", description="System version")
    environment: Environment = Field(Environment.DEVELOPMENT, description="Deployment environment")
    debug: bool = Field(False, description="Debug mode")
    
    # Additional fields from .env
    prometheus_port: int = Field(9090, description="Prometheus port")
    grafana_port: int = Field(3000, description="Grafana port")
    simulation_speed: float = Field(1.0, description="Simulation speed factor")
    auto_save_interval: int = Field(60, description="Auto-save interval in seconds")
    
    # API Keys (from environment)
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    mapbox_token: Optional[str] = Field(None, env="MAPBOX_TOKEN")
    weather_api_key: Optional[str] = Field(None, env="WEATHER_API_KEY")
    con_edison_api: Optional[str] = Field(None, env="CON_EDISON_API")
    
    # Database Configuration
    database_url: str = Field(
        "postgresql://postgres:password@localhost/manhattan_grid",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(20, description="Connection pool size")
    database_max_overflow: int = Field(40, description="Max overflow connections")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    
    # Power System Configuration
    pypsa_config: Dict[str, Any] = Field(default_factory=lambda: {
        "solver": "gurobi",  # Professional solver
        "solver_options": {
            "threads": 4,
            "method": 2,  # Barrier method for large networks
            "crossover": 0
        },
        "snapshots": 96,  # 15-minute intervals for 24 hours
        "contingency_analysis": True,
        "n_minus_1": True,  # N-1 contingency analysis
        "optimal_power_flow": True
    })
    
    # Grid Network Parameters
    grid_config: Dict[str, Any] = Field(default_factory=lambda: {
        "voltage_levels": [138, 27, 13.8, 4.16, 0.48, 0.208],  # kV
        "frequency": 60,  # Hz
        "base_mva": 100,
        "power_factor_limits": [0.85, 1.0],
        "voltage_tolerance": 0.05,  # ±5%
        "emergency_limit_factor": 1.15,
        "substations": {
            "Hell's Kitchen": {"lat": 40.7614, "lon": -73.9919, "capacity_mva": 750},
            "Times Square": {"lat": 40.7589, "lon": -73.9851, "capacity_mva": 850},
            "Penn Station": {"lat": 40.7505, "lon": -73.9934, "capacity_mva": 900},
            "Grand Central": {"lat": 40.7527, "lon": -73.9772, "capacity_mva": 1000},
            "Murray Hill": {"lat": 40.7489, "lon": -73.9765, "capacity_mva": 650},
            "Turtle Bay": {"lat": 40.7532, "lon": -73.9681, "capacity_mva": 700},
            "Chelsea": {"lat": 40.7465, "lon": -73.9980, "capacity_mva": 600},
            "Midtown East": {"lat": 40.7550, "lon": -73.9700, "capacity_mva": 800}
        }
    })
    
    # Traffic System Configuration
    sumo_config: Dict[str, Any] = Field(default_factory=lambda: {
        "network_file": "manhattan.net.xml",
        "route_file": "manhattan.rou.xml",
        "additional_files": ["traffic_lights.add.xml", "detectors.add.xml"],
        "step_length": 0.1,  # 100ms time steps
        "collision_action": "warn",
        "emergency_decel": 9.0,
        "max_num_vehicles": 10000,
        "parking_search": True,
        "device.rerouting.probability": 0.8,
        "device.battery.probability": 0.3  # 30% EVs
    })
    
    # EV and Charging Configuration
    ev_config: Dict[str, Any] = Field(default_factory=lambda: {
        "penetration_rate": 0.3,  # 30% of vehicles are EVs
        "battery_capacities": {  # kWh
            "small": 40,
            "medium": 75,
            "large": 100,
            "bus": 200
        },
        "charging_powers": {  # kW
            "level1": 1.4,
            "level2": 7.2,
            "level3_50": 50,
            "level3_150": 150,
            "level3_350": 350
        },
        "v2g_enabled": True,  # Vehicle-to-Grid
        "smart_charging": True
    })
    
    # AI/ML Configuration
    ml_config: Dict[str, Any] = Field(default_factory=lambda: {
        "models": {
            "load_forecast": "prophet",  # Facebook Prophet for time series
            "failure_prediction": "xgboost",
            "traffic_prediction": "lstm",
            "optimization": "reinforcement_learning"
        },
        "training_schedule": "0 2 * * *",  # Daily at 2 AM
        "prediction_horizon": 24,  # hours
        "confidence_interval": 0.95,
        "anomaly_detection": True,
        "use_openai": True,  # Use GPT for intelligent analysis
        "openai_model": "gpt-4-turbo-preview"
    })
    
    # Simulation Parameters
    simulation_config: Dict[str, Any] = Field(default_factory=lambda: {
        "mode": SimulationMode.REALTIME,
        "speed_factor": 1.0,  # 1.0 = realtime, >1 = faster
        "auto_save_interval": 300,  # seconds
        "checkpoint_interval": 3600,  # seconds
        "enable_replay": True,
        "record_metrics": True,
        "physics_engine": "high_fidelity",  # vs "simplified"
        "weather_effects": True,
        "seasonal_patterns": True
    })
    
    # Monitoring and Alerting
    monitoring_config: Dict[str, Any] = Field(default_factory=lambda: {
        "prometheus_port": 9090,
        "grafana_port": 3000,
        "metrics_interval": 10,  # seconds
        "alert_channels": ["email", "sms", "slack", "teams"],
        "critical_alerts": {
            "voltage_deviation": 0.1,  # 10%
            "overload_threshold": 0.9,  # 90% capacity
            "cascade_risk": 0.7,
            "traffic_congestion": 0.8
        },
        "sentry_dsn": None,  # Error tracking
        "log_level": "INFO"
    })
    
    # Security Configuration
    security_config: Dict[str, Any] = Field(default_factory=lambda: {
        "enable_auth": True,
        "jwt_secret": None,  # Generated on first run
        "jwt_algorithm": "HS256",
        "access_token_expire": 30,  # minutes
        "refresh_token_expire": 7,  # days
        "allowed_origins": ["http://localhost:3000"],
        "rate_limiting": {
            "requests_per_minute": 60,
            "burst_size": 100
        },
        "audit_logging": True,
        "encryption": "AES256"
    })
    
    # File Paths
    base_dir: Path = Field(default_factory=Path.cwd)
    data_dir: Path = Field(default_factory=lambda: Path.cwd() / "data")
    cache_dir: Path = Field(default_factory=lambda: Path.cwd() / "data" / "cache")
    model_dir: Path = Field(default_factory=lambda: Path.cwd() / "data" / "models")
    log_dir: Path = Field(default_factory=lambda: Path.cwd() / "logs")
    
    # Performance Tuning
    performance_config: Dict[str, Any] = Field(default_factory=lambda: {
        "use_multiprocessing": True,
        "num_workers": os.cpu_count() or 4,
        "chunk_size": 1000,
        "cache_ttl": 3600,  # seconds
        "enable_profiling": False,
        "memory_limit_gb": 16,
        "enable_gpu": torch.cuda.is_available() if 'torch' in globals() else False
    })
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "protected_namespaces": ('settings_',),  # Fix the model_dir warning
        "extra": "allow"  # Allow extra fields from .env
    }
        
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Ensure production has proper configuration"""
        if v == Environment.PRODUCTION:
            # Add production checks here
            pass
        return v
    
    @field_validator("base_dir", "data_dir", "cache_dir", "model_dir", "log_dir")
    @classmethod
    def create_directories(cls, v):
        """Ensure all directories exist"""
        v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    def get_database_url(self, async_mode: bool = False) -> str:
        """Get database URL for sync or async operations"""
        if async_mode:
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url
    
    def get_redis_url(self, db: int = 0) -> str:
        """Get Redis URL with specific database"""
        base = self.redis_url.rsplit("/", 1)[0]
        return f"{base}/{db}"

# Global settings instance
settings = PowerGridSettings()

# Export for easy access
__all__ = ["settings", "PowerGridSettings", "Environment", "SimulationMode"]