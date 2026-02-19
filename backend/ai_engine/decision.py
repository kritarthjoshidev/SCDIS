"""
Decision Engine
Central intelligence layer combining forecasting, RL and optimization
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ai_engine.forecasting_engine import ForecastingEngine
from ai_engine.rl_engine import RLEngine
from services.optimization_service import OptimizationService
from services.telemetry_service import TelemetryService

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Core AI decision engine
    """

    def __init__(self):
        self.forecasting_engine = ForecastingEngine()
        self.rl_engine = RLEngine()
        self.optimization_service = OptimizationService()
        self.telemetry_service = TelemetryService()

        logger.info("Decision Engine initialized")

    # ---------------------------------------------------------
    # MAIN DECISION FUNCTION
    # ---------------------------------------------------------
    def generate_decision(self, telemetry_data: Optional[Dict] = None) -> Dict[str, Any]:

        """
        Generates optimization decision.
        If telemetry_data not provided, auto fetch latest telemetry.
        """

        try:
            # AUTO TELEMETRY LOAD (fix)
            if telemetry_data is None:
                telemetry_data = self.telemetry_service.get_latest()

            forecast = self.forecasting_engine.predict(telemetry_data)

            # RL engine expects a state string; derive from telemetry when possible
            state = "normal"
            if isinstance(telemetry_data, dict):
                state = telemetry_data.get("state", telemetry_data.get("current_state", "normal"))

            rl_action = self.rl_engine.select_action(state)

            optimized = self.optimization_service.optimize(
                telemetry_data=telemetry_data,
                forecast=forecast,
                rl_action=rl_action
            )

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "forecast": forecast,
                "rl_action": rl_action,
                "optimized_decision": optimized
            }

        except Exception:
            logger.exception("Decision generation failed")
            return {"status": "failed"}

    def health_status(self):
        return {"status": "OK"}
