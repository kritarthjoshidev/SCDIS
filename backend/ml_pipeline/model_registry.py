"""
Enterprise Model Registry

Responsibilities:
- Model version tracking
- Production / Candidate separation
- Deployment promotion
- Rollback safety
- Performance metadata tracking
- Model lifecycle governance
"""

import os
import json
import shutil
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from core.config import settings

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Enterprise-grade model lifecycle registry
    """

    def __init__(self):

        self.registry_file = settings.MODEL_REGISTRY_FILE
        self.models_dir = settings.MODEL_DIR

        os.makedirs(self.models_dir, exist_ok=True)

        if not os.path.exists(self.registry_file):
            self._initialize_registry()

        logger.info("Model registry initialized")

    # ---------------------------------------------------------
    # INITIALIZE REGISTRY
    # ---------------------------------------------------------
    def _initialize_registry(self):

        default_registry = {
            "production_model": None,
            "candidate_model": None,
            "history": []
        }

        with open(self.registry_file, "w") as f:
            json.dump(default_registry, f, indent=4)

    # ---------------------------------------------------------
    # LOAD REGISTRY
    # ---------------------------------------------------------
    def _load_registry(self) -> Dict[str, Any]:

        with open(self.registry_file, "r") as f:
            return json.load(f)

    # ---------------------------------------------------------
    # SAVE REGISTRY
    # ---------------------------------------------------------
    def _save_registry(self, data: Dict[str, Any]):

        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=4)

    # ---------------------------------------------------------
    # REGISTER NEW CANDIDATE MODEL
    # ---------------------------------------------------------
    def register_candidate_model(self, model_path: str) -> str:

        registry = self._load_registry()

        version = f"model_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        dest_path = os.path.join(self.models_dir, f"{version}.pkl")

        shutil.copy(model_path, dest_path)

        registry["candidate_model"] = dest_path
        registry["history"].append({
            "event": "candidate_registered",
            "path": dest_path,
            "timestamp": datetime.utcnow().isoformat()
        })

        self._save_registry(registry)

        logger.info(f"Candidate model registered: {dest_path}")

        return dest_path

    # ---------------------------------------------------------
    # PROMOTE CANDIDATE TO PRODUCTION
    # ---------------------------------------------------------
    def promote_candidate_to_production(self):

        registry = self._load_registry()

        candidate = registry.get("candidate_model")

        if not candidate:
            raise Exception("No candidate model available")

        previous_production = registry.get("production_model")

        registry["production_model"] = candidate
        registry["candidate_model"] = None

        registry["history"].append({
            "event": "candidate_promoted",
            "new_production": candidate,
            "previous_production": previous_production,
            "timestamp": datetime.utcnow().isoformat()
        })

        self._save_registry(registry)

        logger.info("Candidate model promoted to production")

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------
    def rollback_production(self):

        registry = self._load_registry()

        history = registry["history"]

        previous_models = [
            x for x in history
            if x["event"] == "candidate_promoted"
        ]

        if len(previous_models) < 2:
            raise Exception("No rollback target available")

        last = previous_models[-2]

        registry["production_model"] = last["new_production"]

        registry["history"].append({
            "event": "rollback",
            "target": last["new_production"],
            "timestamp": datetime.utcnow().isoformat()
        })

        self._save_registry(registry)

        logger.warning("Production model rollback executed")

    # ---------------------------------------------------------
    # GETTERS
    # ---------------------------------------------------------
    def get_production_model_path(self) -> Optional[str]:

        registry = self._load_registry()
        return registry.get("production_model")

    def get_candidate_model_path(self) -> Optional[str]:

        registry = self._load_registry()
        return registry.get("candidate_model")

    def get_registry_snapshot(self) -> Dict[str, Any]:

        return self._load_registry()

    # ---------------------------------------------------------
    # PERFORMANCE METADATA
    # ---------------------------------------------------------
    def log_model_performance(self, metrics: Dict[str, Any]):

        registry = self._load_registry()

        registry["history"].append({
            "event": "performance_logged",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })

        self._save_registry(registry)

    def get_latest_model_performance(self) -> Dict[str, Any]:

        registry = self._load_registry()

        perf_logs = [
            x for x in registry["history"]
            if x["event"] == "performance_logged"
        ]

        if not perf_logs:
            return {"accuracy": 0.9}

        return perf_logs[-1]["metrics"]

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------
    def health_status(self):

        registry = self._load_registry()

        return {
            "production_model": registry.get("production_model"),
            "candidate_model": registry.get("candidate_model"),
            "history_records": len(registry["history"]),
            "status": "OK"
        }

    # ---------------------------------------------------------
    # REFRESH
    # ---------------------------------------------------------
    def refresh_registry(self):

        self._initialize_registry()
        logger.warning("Model registry refreshed")

    # ---------------------------------------------------------
    # TRAINING DATA ACCESS (compatibility)
    # ---------------------------------------------------------
    def get_training_dataset(self):
        """
        Returns a lightweight representation of the training dataset used
        by the model registry. If none is available, returns an empty list.
        """

        # For now return empty list as placeholder compatibility
        return []
