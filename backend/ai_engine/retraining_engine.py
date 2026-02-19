import os
import logging
import pandas as pd
import joblib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from sklearn.ensemble import RandomForestRegressor, IsolationForest

from core.config import settings
from utils.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class RetrainingEngine:
    """
    Handles periodic retraining of AI models using newly collected telemetry data
    """

    def __init__(self):
        self.data_path = Path(settings.DATA_DIR) / "training_dataset.csv"
        self.last_run_started: Optional[str] = None
        self.last_run_completed: Optional[str] = None
        self.last_run_result: Dict[str, Any] = {"status": "idle"}
        self.last_run_status = "idle"

    def _load_training_data(self):
        if not os.path.exists(self.data_path):
            logger.warning("Training dataset not found")
            return None
        df = pd.read_csv(self.data_path)
        if df.empty:
            logger.warning("Training dataset is empty")
            return None
        return df

    def _train_forecast_model(self, df):

        X = df[[
            "building_id",
            "temperature",
            "humidity",
            "occupancy",
            "day_of_week",
            "hour"
        ]]

        y = df["energy_usage_kwh"]

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        joblib.dump(model, settings.FORECAST_MODEL_PATH)
        logger.info("Forecast model retrained")

    def _train_anomaly_model(self, df):

        model = IsolationForest(contamination=0.02)
        model.fit(df[["energy_usage_kwh"]])

        joblib.dump(model, settings.ANOMALY_MODEL_PATH)
        logger.info("Anomaly model retrained")

    def retrain_models(self):
        """
        Full retraining pipeline
        """
        return self.run_retraining_pipeline()

    def run_retraining_pipeline(self) -> Dict[str, Any]:
        """
        Compatibility entrypoint used by routes/runtime services.
        Always returns a structured status payload.
        """

        logger.info("Retraining pipeline started")
        started_at = datetime.utcnow().isoformat()
        self.last_run_started = started_at
        self.last_run_status = "running"

        try:
            df = self._load_training_data()

            if df is None:
                completed_at = datetime.utcnow().isoformat()
                result = {
                    "status": "skipped",
                    "reason": "dataset_not_available",
                    "rows_used": 0,
                    "data_path": str(self.data_path),
                    "started_at": started_at,
                    "completed_at": completed_at,
                }
                self.last_run_status = "skipped"
                self.last_run_completed = completed_at
                self.last_run_result = result
                logger.warning("Skipping retraining: dataset unavailable")
                return result

            self._train_forecast_model(df)
            self._train_anomaly_model(df)

            reload_result = ModelLoader.reload_models()
            completed_at = datetime.utcnow().isoformat()
            result = {
                "status": "completed",
                "rows_used": int(len(df)),
                "data_path": str(self.data_path),
                "models_reloaded": reload_result,
                "started_at": started_at,
                "completed_at": completed_at,
            }
            self.last_run_status = "completed"
            self.last_run_completed = completed_at
            self.last_run_result = result
            logger.info("Retraining pipeline completed successfully")
            return result

        except Exception as exc:
            logger.exception("Retraining pipeline failed")
            completed_at = datetime.utcnow().isoformat()
            result = {
                "status": "failed",
                "error": str(exc),
                "data_path": str(self.data_path),
                "started_at": started_at,
                "completed_at": completed_at,
            }
            self.last_run_status = "failed"
            self.last_run_completed = completed_at
            self.last_run_result = result
            return result

    def pipeline_status(self):
        """
        Compatibility method for tests to report retraining engine status.
        """

        return {
            "status": self.last_run_status,
            "data_path": str(self.data_path),
            "last_run_started": self.last_run_started,
            "last_run_completed": self.last_run_completed,
            "last_result": self.last_run_result,
        }
