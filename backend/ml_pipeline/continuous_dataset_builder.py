"""
Continuous Dataset Builder

Transforms live telemetry streams into continuously updated
training datasets for autonomous retraining pipelines.

Capabilities:
- Real-time dataset ingestion
- Feature engineering
- Dataset validation
- Dataset versioning
- Dataset drift tagging
- Auto training dataset refresh
"""

import logging
import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, Any, List

from core.config import settings
from services.telemetry_service import TelemetryService

logger = logging.getLogger(__name__)


class ContinuousDatasetBuilder:
    """
    Builds continuously updating ML training datasets
    """

    def __init__(self):

        self.telemetry_service = TelemetryService()

        self.dataset_dir = settings.DATASET_DIR
        os.makedirs(self.dataset_dir, exist_ok=True)

        self.latest_dataset_path = os.path.join(self.dataset_dir, "latest_training_dataset.csv")

        logger.info("Continuous Dataset Builder initialized")

    # ---------------------------------------------------------
    # MAIN DATASET BUILD
    # ---------------------------------------------------------
    def build_dataset(self) -> Dict[str, Any]:
        """
        Builds new training dataset from telemetry
        """

        logger.info("Building training dataset from telemetry")

        data = self.telemetry_service.get_recent_dataset()

        if not data:
            logger.warning("No telemetry data available")
            return {"status": "no_data"}

        df = pd.DataFrame(data)

        df = self._feature_engineering(df)

        self._validate_dataset(df)

        version_path = self._save_versioned_dataset(df)

        df.to_csv(self.latest_dataset_path, index=False)

        return {
            "status": "dataset_created",
            "records": len(df),
            "version_path": version_path
        }

    # ---------------------------------------------------------
    # FEATURE ENGINEERING
    # ---------------------------------------------------------
    def _feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:

        logger.info("Running feature engineering")

        if "timestamp" in df.columns:
            df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
            df["dayofweek"] = pd.to_datetime(df["timestamp"]).dt.dayofweek

        if "energy_usage" in df.columns:
            df["rolling_mean_3"] = df["energy_usage"].rolling(3, min_periods=1).mean()
            df["rolling_std_3"] = df["energy_usage"].rolling(3, min_periods=1).std().fillna(0)

        df = df.fillna(method="ffill").fillna(0)

        return df

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    def _validate_dataset(self, df: pd.DataFrame):

        if len(df) < settings.MIN_DATASET_SIZE:
            logger.warning("Dataset too small for reliable training")

        if df.isnull().sum().sum() > 0:
            logger.warning("Dataset still contains missing values")

    # ---------------------------------------------------------
    # SAVE VERSIONED DATASET
    # ---------------------------------------------------------
    def _save_versioned_dataset(self, df: pd.DataFrame) -> str:

        version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        version_path = os.path.join(self.dataset_dir, f"training_dataset_{version}.csv")

        df.to_csv(version_path, index=False)

        logger.info(f"Dataset version saved: {version_path}")

        return version_path

    # ---------------------------------------------------------
    # CONTINUOUS BUILD LOOP
    # ---------------------------------------------------------
    def continuous_build_loop(self):

        import time

        logger.info("Starting continuous dataset build loop")

        while True:

            try:
                result = self.build_dataset()
                logger.info(f"Dataset build result: {result}")

            except Exception:
                logger.exception("Dataset build iteration failed")

            time.sleep(settings.DATASET_BUILD_INTERVAL)

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------
    def health_status(self):

        return {
            "dataset_dir": self.dataset_dir,
            "latest_dataset": self.latest_dataset_path,
            "status": "OK"
        }
