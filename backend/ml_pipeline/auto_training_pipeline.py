"""
Autonomous Model Training Pipeline

Handles:
- New dataset detection
- Automated model training
- Model evaluation
- Candidate model registration
- Training history tracking
- Failure recovery
- Auto deployment recommendation
"""

import logging
import os
import pandas as pd
import joblib
from datetime import datetime
from typing import Dict, Any

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

from core.config import settings
from ml_pipeline.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class AutoTrainingPipeline:
    """
    Fully autonomous model training system
    """

    def __init__(self):

        self.dataset_dir = settings.DATASET_DIR
        self.candidate_model_dir = settings.CANDIDATE_MODEL_DIR
        os.makedirs(self.candidate_model_dir, exist_ok=True)

        self.model_registry = ModelRegistry()

        self.training_history = []

        logger.info("Auto Training Pipeline initialized")

    # ---------------------------------------------------------
    # MAIN TRAINING ENTRY
    # ---------------------------------------------------------
    def run_training_cycle(self) -> Dict[str, Any]:
        """
        Executes full training pipeline
        """

        logger.info("Starting autonomous training cycle")

        dataset_path = self._get_latest_dataset()

        if dataset_path is None:
            logger.warning("No dataset available for training")
            return {"status": "no_dataset"}

        df = pd.read_csv(dataset_path)

        X, y = self._prepare_features(df)

        model = self._train_model(X, y)

        metrics = self._evaluate_model(model, X, y)

        model_path = self._save_candidate_model(model)

        self.model_registry.register_candidate_model(model_path, metrics)

        training_record = {
            "timestamp": datetime.utcnow(),
            "dataset": dataset_path,
            "metrics": metrics,
            "model_path": model_path
        }

        self.training_history.append(training_record)

        logger.info("Training cycle completed successfully")

        return {
            "status": "completed",
            "metrics": metrics,
            "model_path": model_path
        }

    # ---------------------------------------------------------
    # DATASET DETECTION
    # ---------------------------------------------------------
    def _get_latest_dataset(self):

        files = [f for f in os.listdir(self.dataset_dir) if f.endswith(".csv")]

        if not files:
            return None

        files.sort(reverse=True)

        return os.path.join(self.dataset_dir, files[0])

    # ---------------------------------------------------------
    # FEATURE PREPARATION
    # ---------------------------------------------------------
    def _prepare_features(self, df):

        if "energy_usage" not in df.columns:
            raise ValueError("Dataset missing target column")

        y = df["energy_usage"]
        X = df.drop(columns=["energy_usage"], errors="ignore")

        X = X.select_dtypes(include=["float64", "int64"])

        return X, y

    # ---------------------------------------------------------
    # MODEL TRAINING
    # ---------------------------------------------------------
    def _train_model(self, X, y):

        logger.info("Training regression model")

        model = LinearRegression()
        model.fit(X, y)

        return model

    # ---------------------------------------------------------
    # MODEL EVALUATION
    # ---------------------------------------------------------
    def _evaluate_model(self, model, X, y):

        predictions = model.predict(X)

        mae = mean_absolute_error(y, predictions)
        r2 = r2_score(y, predictions)

        metrics = {
            "mae": float(mae),
            "r2_score": float(r2)
        }

        logger.info(f"Model metrics: {metrics}")

        return metrics

    # ---------------------------------------------------------
    # SAVE CANDIDATE MODEL
    # ---------------------------------------------------------
    def _save_candidate_model(self, model):

        version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_path = os.path.join(self.candidate_model_dir, f"candidate_model_{version}.pkl")

        joblib.dump(model, model_path)

        logger.info(f"Candidate model saved: {model_path}")

        return model_path

    # ---------------------------------------------------------
    # CONTINUOUS AUTO TRAIN LOOP
    # ---------------------------------------------------------
    def continuous_training_loop(self):

        import time

        logger.info("Starting continuous auto-training loop")

        while True:

            try:
                result = self.run_training_cycle()
                logger.info(f"Training cycle result: {result}")

            except Exception:
                logger.exception("Training cycle failed")

            time.sleep(settings.AUTO_TRAIN_INTERVAL)

    # ---------------------------------------------------------
    # PIPELINE HEALTH
    # ---------------------------------------------------------
    def health_status(self):

        return {
            "candidate_model_dir": self.candidate_model_dir,
            "training_runs": len(self.training_history),
            "status": "OK"
        }
