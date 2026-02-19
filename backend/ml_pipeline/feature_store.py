import os
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List
from core.config import settings

logger = logging.getLogger(__name__)


class FeatureStore:
    """
    Centralized feature management layer.
    Provides feature ingestion, retrieval,
    versioning, and consistency enforcement.
    """

    def __init__(self):

        self.feature_dir = os.path.join(settings.DATA_DIR, "feature_store")
        os.makedirs(self.feature_dir, exist_ok=True)

        self.current_version = "v1"

    # ============================================
    # Feature validation
    # ============================================
    def _validate_features(self, features: Dict):

        required = [
            "building_id",
            "temperature",
            "humidity",
            "occupancy",
            "day_of_week",
            "hour"
        ]

        for field in required:
            if field not in features:
                raise ValueError(f"Missing feature: {field}")

        return True

    # ============================================
    # Store features
    # ============================================
    def store_features(self, features: Dict):

        self._validate_features(features)

        features["timestamp"] = datetime.utcnow()
        features["feature_version"] = self.current_version

        file_path = os.path.join(
            self.feature_dir,
            f"features_{self.current_version}.csv"
        )

        df = pd.DataFrame([features])

        if os.path.exists(file_path):
            df.to_csv(file_path, mode="a", header=False, index=False)
        else:
            df.to_csv(file_path, index=False)

        logger.info("Features stored successfully")

        return {"status": "stored", "version": self.current_version}

    # ============================================
    # Retrieve latest features
    # ============================================
    def get_latest_features(self, limit: int = 100):

        file_path = os.path.join(
            self.feature_dir,
            f"features_{self.current_version}.csv"
        )

        if not os.path.exists(file_path):
            return []

        df = pd.read_csv(file_path)

        return df.tail(limit).to_dict(orient="records")

    # ============================================
    # Historical feature retrieval
    # ============================================
    def get_features_by_time_range(
        self,
        start_time,
        end_time
    ):

        file_path = os.path.join(
            self.feature_dir,
            f"features_{self.current_version}.csv"
        )

        if not os.path.exists(file_path):
            return []

        df = pd.read_csv(file_path)

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        result = df[
            (df["timestamp"] >= start_time)
            & (df["timestamp"] <= end_time)
        ]

        return result.to_dict(orient="records")

    # ============================================
    # Feature version management
    # ============================================
    def create_new_version(self):

        version_number = int(self.current_version.replace("v", "")) + 1
        self.current_version = f"v{version_number}"

        logger.info(f"Feature store upgraded to version {self.current_version}")

        return self.current_version

    # ============================================
    # Drift monitoring helper
    # ============================================
    def compute_feature_statistics(self):

        file_path = os.path.join(
            self.feature_dir,
            f"features_{self.current_version}.csv"
        )

        if not os.path.exists(file_path):
            return {}

        df = pd.read_csv(file_path)

        stats = df.describe().to_dict()

        logger.info("Feature statistics computed")

        return stats
