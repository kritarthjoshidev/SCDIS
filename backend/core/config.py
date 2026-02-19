from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    # =====================================================
    # SYSTEM
    # =====================================================
    SERVICE_NAME: str = "Smart Campus Decision Intelligence System"
    ENVIRONMENT: str = "development"
    BASE_DIR: Path = BASE_DIR

    # =====================================================
    # DIRECTORIES
    # =====================================================
    DATA_DIR: Path = BASE_DIR / "data"
    AI_MODEL_DIR: Path = BASE_DIR / "ai_models"
    MODEL_DIR: Path = AI_MODEL_DIR
    LOG_DIR: Path = BASE_DIR / "logs"
    BENCHMARK_DATASET_PATH: Path = BASE_DIR / "data" / "processed" / "benchmark_dataset.csv"

    # =====================================================
    # MODEL FILES
    # =====================================================
    FORECAST_MODEL_PATH: Path = AI_MODEL_DIR / "forecast_model.pkl"
    ANOMALY_MODEL_PATH: Path = AI_MODEL_DIR / "anomaly_model.pkl"
    RL_MODEL_PATH: Path = AI_MODEL_DIR / "rl_model.pkl"
    MODEL_REGISTRY_FILE: Path = AI_MODEL_DIR / "model_registry.json"

    # =====================================================
    # SECURITY
    # =====================================================
    SECRET_KEY: str = "SUPER_SECRET_PRODUCTION_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    TOKEN_EXPIRE_MINUTES: int = 60

    # =====================================================
    # OPTIMIZATION CONSTRAINTS
    # =====================================================
    MAX_ALLOWED_LOAD: float = 100.0
    MIN_ALLOWED_LOAD: float = 5.0
    DEFAULT_REDUCTION_PERCENT: float = 15.0

    # =====================================================
    # ADDITIONAL CONSTANTS
    # =====================================================
    HIGH_USAGE_THRESHOLD: float = 300.0
    ENERGY_COST_PER_UNIT: float = 0.15
    RETRAIN_COOLDOWN_SECONDS: int = 86400
    SIMULATION_MODE: bool = True

    # =====================================================
    # OPTIMIZATION OBJECTIVE WEIGHTS
    # =====================================================
    ENERGY_WEIGHT: float = 0.30
    COST_WEIGHT: float = 0.25
    COMFORT_WEIGHT: float = 0.15
    CARBON_WEIGHT: float = 0.10
    LOAD_WEIGHT: float = 0.10
    STABILITY_WEIGHT: float = 0.10

    # =====================================================
    # RL SETTINGS
    # =====================================================
    RL_EXPLORATION_RATE: float = 0.10
    RL_LEARNING_RATE: float = 0.001
    RL_DISCOUNT_FACTOR: float = 0.95

    # =====================================================
    # RL REWARD WEIGHTS
    # =====================================================
    REWARD_ENERGY_WEIGHT: float = 0.30
    REWARD_COST_WEIGHT: float = 0.20
    REWARD_COMFORT_WEIGHT: float = 0.15
    REWARD_CARBON_WEIGHT: float = 0.10
    REWARD_LOAD_WEIGHT: float = 0.10
    REWARD_STABILITY_WEIGHT: float = 0.15

    # =====================================================
    # DRIFT DETECTION
    # =====================================================
    DRIFT_THRESHOLD: float = 1.5
    PERFORMANCE_DRIFT_THRESHOLD: float = 0.15
    DRIFT_MONITOR_INTERVAL: int = 3600

    # =====================================================
    # SCHEDULER INTERVALS
    # =====================================================
    RETRAIN_INTERVAL_SECONDS: int = 86400
    RETRAIN_INTERVAL_HOURS: int = 24
    DATA_MONITOR_INTERVAL: int = 3600
    HEALTH_CHECK_INTERVAL: int = 600
    RUNTIME_LIFECYCLE_INTERVAL: int = 60
    RUNTIME_HEALTH_INTERVAL: int = 30
    RUNTIME_SUPERVISOR_INTERVAL: int = 45
    RL_TRAINING_INTERVAL: int = 120
    SELF_EVOLUTION_INTERVAL: int = 90
    CRITICAL_DRIFT_THRESHOLD: float = 2.0

    class Config:
        env_file = ".env"


settings = Settings()
