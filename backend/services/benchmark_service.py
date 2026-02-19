"""
Enterprise Benchmark Service

Compares:
- Candidate model
- Production model

Provides:
- Automated evaluation
- Deployment recommendation
- Historical benchmarking logs
- Rollback safety metrics
"""

import logging
import joblib
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any

from sklearn.metrics import mean_absolute_error, r2_score

from core.config import settings
from ml_pipeline.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class BenchmarkService:
    """
    Evaluates candidate vs production models
    """

    def __init__(self):

        self.model_registry = ModelRegistry()
        self.dataset_path = settings.BENCHMARK_DATASET_PATH
        self.history = []

        logger.info("Benchmark Service initialized")

    # ---------------------------------------------------------
    # MAIN BENCHMARK
    # ---------------------------------------------------------
    def run_benchmark(self) -> Dict[str, Any]:

        logger.info("Running model benchmark")

        production_model_path = self.model_registry.get_production_model_path()
        candidate_model_path = self.model_registry.get_candidate_model_path()

        if not candidate_model_path:
            return {"status": "no_candidate_model"}

        if not os.path.exists(self.dataset_path):
            return {"status": "benchmark_dataset_missing"}

        df = pd.read_csv(self.dataset_path)

        X = df.drop(columns=["energy_usage"], errors="ignore")
        y = df["energy_usage"]

        X = X.select_dtypes(include=["float64", "int64"])

        production_metrics = self._evaluate_model(production_model_path, X, y)
        candidate_metrics = self._evaluate_model(candidate_model_path, X, y)

        deployment_recommended = self._deployment_decision(
            production_metrics,
            candidate_metrics
        )

        result = {
            "timestamp": datetime.utcnow(),
            "production_metrics": production_metrics,
            "candidate_metrics": candidate_metrics,
            "deployment_recommended": deployment_recommended
        }

        self.history.append(result)

        logger.info(f"Benchmark result: {result}")

        return result

    # ---------------------------------------------------------
    # MODEL EVALUATION
    # ---------------------------------------------------------
    def _evaluate_model(self, model_path, X, y):

        try:
            model = joblib.load(model_path)
        except Exception:
            return {"mae": 999999, "r2_score": -1}

        preds = model.predict(X)

        mae = mean_absolute_error(y, preds)
        r2 = r2_score(y, preds)

        return {
            "mae": float(mae),
            "r2_score": float(r2)
        }

    # ---------------------------------------------------------
    # DEPLOYMENT DECISION
    # ---------------------------------------------------------
    def _deployment_decision(self, prod_metrics, cand_metrics):

        mae_improved = cand_metrics["mae"] < prod_metrics["mae"]
        r2_improved = cand_metrics["r2_score"] > prod_metrics["r2_score"]

        if mae_improved and r2_improved:
            return True

        if cand_metrics["r2_score"] > prod_metrics["r2_score"] * 1.02:
            return True

        return False

    # ---------------------------------------------------------
    # BENCHMARK HISTORY
    # ---------------------------------------------------------
    def get_history(self):

        return self.history[-50:]

    # ---------------------------------------------------------
    # HEALTH CHECK
    # ---------------------------------------------------------
    def health_status(self):

        return {
            "history_records": len(self.history),
            "benchmark_dataset": self.dataset_path,
            "status": "OK"
        }
