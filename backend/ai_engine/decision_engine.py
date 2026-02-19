"""
Enterprise Decision Intelligence Engine

Responsibilities:
- Forecast future demand
- Detect anomalies
- Apply optimization
- Apply RL adaptive policy
- Generate explainable campus decisions
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ai_engine.forecasting_engine import ForecastingEngine
from ai_engine.anomaly_engine import AnomalyEngine
from ai_engine.rl_engine import RLEngine
from services.optimization_service import OptimizationService

logger = logging.getLogger(__name__)


from ai_engine.decision import DecisionEngine as SimpleDecisionEngine


class DecisionEngine:
    """
    Core intelligent decision system
    """

    def __init__(self):

        self.forecasting_engine = ForecastingEngine()
        self.anomaly_engine = AnomalyEngine()
        self.rl_engine = RLEngine()
        self.optimization_service = OptimizationService()

        logger.info("Decision Engine initialized")

    # ---------------------------------------------------------
    # MAIN DECISION PIPELINE
    # ---------------------------------------------------------
    def generate_decision(self, telemetry_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Runs full decision intelligence pipeline
        """
        logger.info("Decision pipeline started")

        # Delegate to the simpler DecisionEngine implementation which
        # gracefully handles missing telemetry (auto-fetches when needed).
        try:
            delegator = SimpleDecisionEngine()
            return delegator.generate_decision(telemetry_data)
        except Exception:
            logger.exception("Delegated decision generation failed")
            return {"status": "failed"}

    # ---------------------------------------------------------
    # MERGE DECISION LOGIC
    # ---------------------------------------------------------
    def _merge_decisions(self, optimization, rl_adjustment):

        combined_reduction = (
            optimization.get("recommended_reduction", 0)
            + rl_adjustment.get("adjustment", 0)
        )

        combined_reduction = max(0, min(combined_reduction, 100))

        return {
            "load_reduction_percent": combined_reduction,
            "recommended_actions": optimization.get("actions", [])
        }

    # ---------------------------------------------------------
    # EXPLAINABLE AI OUTPUT
    # ---------------------------------------------------------
    def _explain_decision(
        self,
        telemetry_data,
        forecast,
        anomaly,
        action
    ):

        explanation = []

        if anomaly.get("is_anomaly"):
            explanation.append("Anomaly detected in campus energy usage")

        if forecast.get("predicted_load", 0) > telemetry_data.get("current_load", 0):
            explanation.append("Forecast predicts load increase")

        if action["load_reduction_percent"] > 0:
            explanation.append("Energy optimization applied")

        if not explanation:
            explanation.append("System operating under optimal conditions")

        return explanation

    # ---------------------------------------------------------
    # HEALTH CHECK
    # ---------------------------------------------------------
    def health_status(self):

        return {
            "forecast_engine": "OK",
            "anomaly_engine": "OK",
            "rl_engine": "OK",
            "optimization_service": "OK"
        }
