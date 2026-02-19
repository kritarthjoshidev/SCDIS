"""
State Builder Engine

Constructs normalized system state vectors for:
- Reinforcement Learning decision agent
- Optimization orchestration
- Scenario simulations
- Autonomous control loops

This module aggregates:
telemetry + prediction + anomaly + environment signals
and converts them into structured ML-ready state tensors.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
import numpy as np

from core.config import settings

logger = logging.getLogger(__name__)


class StateBuilder:

    def __init__(self):
        self.state_history: List[Dict[str, Any]] = []
        self.feature_schema = settings.STATE_FEATURE_SCHEMA

    # ============================================================
    # MASTER STATE CONSTRUCTION
    # ============================================================
    def build_state(
        self,
        telemetry: Dict[str, Any],
        prediction: Dict[str, Any],
        anomaly: Dict[str, Any],
        environment: Dict[str, Any]
    ) -> Dict[str, Any]:

        try:
            energy_features = self.energy_features(telemetry, prediction)
            anomaly_features = self.anomaly_features(anomaly)
            environmental_features = self.environmental_features(environment)
            operational_features = self.operational_features(telemetry)

            feature_vector = (
                energy_features
                + anomaly_features
                + environmental_features
                + operational_features
            )

            state_obj = {
                "timestamp": datetime.utcnow().isoformat(),
                "features": feature_vector,
                "vector": np.array(feature_vector, dtype=float),
                "feature_count": len(feature_vector)
            }

            self.state_history.append(state_obj)

            if len(self.state_history) > settings.STATE_HISTORY_LIMIT:
                self.state_history.pop(0)

            logger.info("State built with %d features", len(feature_vector))

            return state_obj

        except Exception as e:
            logger.error("State building failed: %s", str(e))
            raise

    # ============================================================
    # FEATURE BUILDERS
    # ============================================================
    def energy_features(self, telemetry, prediction):

        current_load = telemetry.get("current_load", 0)
        peak_load = telemetry.get("peak_load", 0)
        predicted_load = prediction.get("predicted_load", 0)

        load_ratio = current_load / max(peak_load, 1)
        forecast_ratio = predicted_load / max(peak_load, 1)

        return [
            current_load,
            peak_load,
            predicted_load,
            load_ratio,
            forecast_ratio
        ]

    def anomaly_features(self, anomaly):

        score = anomaly.get("score", 0)
        severity = anomaly.get("severity", 0)
        incidents = anomaly.get("recent_incidents", 0)

        return [score, severity, incidents]

    def environmental_features(self, env):

        temperature = env.get("temperature", 25)
        humidity = env.get("humidity", 50)
        occupancy = env.get("occupancy", 0)

        return [temperature, humidity, occupancy]

    def operational_features(self, telemetry):

        uptime = telemetry.get("system_uptime_hours", 0)
        failures = telemetry.get("recent_failures", 0)
        maintenance = telemetry.get("maintenance_due", 0)

        return [uptime, failures, maintenance]

    # ============================================================
    # STATE NORMALIZATION
    # ============================================================
    def normalize_state(self, state_vector: np.ndarray):

        normalized = (state_vector - np.mean(state_vector)) / (
            np.std(state_vector) + 1e-8
        )

        return normalized

    # ============================================================
    # TEMPORAL STATE STACK
    # ============================================================
    def temporal_stack(self, steps=5):

        history = self.state_history[-steps:]

        if not history:
            return None

        stacked = np.stack([s["vector"] for s in history])

        return stacked

    # ============================================================
    # RL READY EXPORT
    # ============================================================
    def export_rl_state(self):

        if not self.state_history:
            return None

        latest = self.state_history[-1]

        return {
            "state_vector": latest["vector"],
            "timestamp": latest["timestamp"]
        }

    # ============================================================
    # DIAGNOSTICS
    # ============================================================
    def state_metrics(self):

        if not self.state_history:
            return {"states": 0}

        return {
            "states": len(self.state_history),
            "features_per_state": len(self.state_history[-1]["features"])
        }
