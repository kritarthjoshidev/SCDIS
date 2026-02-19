"""
Enterprise Data Drift Monitoring Service
Detects feature drift, performance drift, triggers controlled retraining
"""

import logging
import numpy as np
import time
from datetime import datetime
from typing import Dict, Any, List

from core.config import settings
from services.telemetry_service import TelemetryService
from ml_pipeline.model_registry import ModelRegistry
from ai_engine.retraining_engine import RetrainingEngine

logger = logging.getLogger(__name__)


class DataDriftMonitor:

    def __init__(self):
        self.telemetry_service = TelemetryService()
        self.model_registry = ModelRegistry()
        self.retraining_engine = RetrainingEngine()

        self.last_drift_score = 0.0
        self.last_check_time = None
        self.last_retrain_time = None
        self.drift_history: List[Dict] = []

        logger.info("Enterprise Data Drift Monitor initialized")

    # ---------------------------------------------------------
    # MAIN DRIFT CHECK
    # ---------------------------------------------------------
    def run_drift_check(self) -> Dict[str, Any]:

        current_data = self.telemetry_service.get_recent_dataset()
        reference_data = self.model_registry.get_training_dataset()

        drift_score = self.calculate_multi_feature_shift(current_data, reference_data)
        performance_drift = self.evaluate_model_performance()

        retrain_required = self.should_trigger_retraining(drift_score, performance_drift)

        if retrain_required:
            if self.retraining_cooldown_passed():
                logger.warning("Retraining triggered due to drift")
                self.retraining_engine.run_retraining_pipeline()
                self.last_retrain_time = datetime.utcnow()

        self.last_drift_score = drift_score
        self.last_check_time = datetime.utcnow()

        record = {
            "timestamp": self.last_check_time.isoformat(),
            "drift_score": drift_score,
            "performance_drift": performance_drift
        }

        self.drift_history.append(record)
        self.drift_history = self.drift_history[-200:]

        return {
            "drift_score": drift_score,
            "severity": self.classify_drift(drift_score),
            "performance_drift": performance_drift,
            "retraining_triggered": retrain_required,
            "timestamp": record["timestamp"]
        }

    # ---------------------------------------------------------
    # MULTI FEATURE DRIFT
    # ---------------------------------------------------------
    def calculate_multi_feature_shift(self, current_data: List[Dict], reference_data: List[Dict]) -> float:

        try:
            features = ["energy_usage", "temperature", "occupancy"]

            scores = []

            for f in features:
                current = np.array([x.get(f, 0) for x in current_data])
                reference = np.array([x.get(f, 0) for x in reference_data])

                if len(current) == 0 or len(reference) == 0:
                    continue

                score = abs(current.mean() - reference.mean()) / (reference.std() + 1e-6)
                scores.append(score)

            if not scores:
                return 0.0

            return float(min(np.mean(scores), 10.0))

        except Exception:
            logger.exception("Multi feature drift calculation failed")
            return 0.0

    # ---------------------------------------------------------
    # MODEL PERFORMANCE DRIFT
    # ---------------------------------------------------------
    def evaluate_model_performance(self) -> float:

        try:
            performance = self.model_registry.get_latest_model_performance()
            return max(0.0, 1.0 - performance.get("accuracy", 0.9))
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # RETRAINING LOGIC
    # ---------------------------------------------------------
    def should_trigger_retraining(self, drift_score, performance_drift):

        if drift_score > settings.DRIFT_THRESHOLD:
            return True

        if performance_drift > settings.PERFORMANCE_DRIFT_THRESHOLD:
            return True

        return False

    def retraining_cooldown_passed(self):

        if not self.last_retrain_time:
            return True

        delta = (datetime.utcnow() - self.last_retrain_time).total_seconds()
        return delta > settings.RETRAIN_COOLDOWN_SECONDS

    # ---------------------------------------------------------
    # DRIFT CLASSIFICATION
    # ---------------------------------------------------------
    def classify_drift(self, drift_score):

        if drift_score < 0.5:
            return "LOW"
        elif drift_score < 1.5:
            return "MEDIUM"
        else:
            return "HIGH"

    # ---------------------------------------------------------
    # MONITOR LOOP
    # ---------------------------------------------------------
    def monitoring_loop(self):

        logger.info("Drift monitoring loop started")

        while True:
            try:
                self.run_drift_check()
            except Exception:
                logger.exception("Drift monitoring failed")

            time.sleep(settings.DRIFT_MONITOR_INTERVAL)

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------
    def health_status(self):

        return {
            "status": "OK",
            "last_check_time": self.last_check_time,
            "last_drift_score": self.last_drift_score,
            "history_records": len(self.drift_history)
        }
