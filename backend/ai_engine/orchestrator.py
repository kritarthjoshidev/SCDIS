"""
AI Orchestrator
Central intelligence controller coordinating:
- Forecasting
- Optimization
- Reinforcement Learning
- Reward evaluation
- Autonomous decision pipeline
"""

import logging
from datetime import datetime
from typing import Dict, Any

from ai_engine.forecasting_engine import ForecastingEngine
from ai_engine.rl_engine import RLEngine
from services.optimization_service import OptimizationService
from ai_engine.reward_engine import RewardEngine
from core.config import settings

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Master AI coordination layer
    """

    def __init__(self):

        self.forecasting_engine = ForecastingEngine()
        self.rl_engine = RLEngine()
        self.optimization_service = OptimizationService()
        self.reward_engine = RewardEngine()

        self.last_decision_time = None
        self.last_decision_output = None

        logger.info("AI Orchestrator initialized")

    # ---------------------------------------------------------
    # MAIN DECISION PIPELINE
    # ---------------------------------------------------------
    def run_decision_pipeline(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes full AI decision lifecycle
        """

        logger.info("Starting decision pipeline")

        try:

            # STEP 1 — Forecast future load
            forecast = self.forecasting_engine.predict(telemetry_data)

            # STEP 2 — Optimization recommendation
            optimization = self.optimization_service.optimize_load(
                telemetry_data,
                forecast
            )

            # STEP 3 — RL policy action
            rl_action = self.rl_engine.select_action(telemetry_data)

            # STEP 4 — Merge intelligent decision
            final_decision = self.merge_decisions(
                forecast,
                optimization,
                rl_action
            )

            # STEP 5 — Reward evaluation
            reward = self.reward_engine.evaluate_reward(
                telemetry_data,
                final_decision
            )

            # STEP 6 — RL training update
            self.rl_engine.learn(telemetry_data, rl_action, reward)

            self.last_decision_time = datetime.utcnow()
            self.last_decision_output = final_decision

            return {
                "forecast": forecast,
                "optimization": optimization,
                "rl_action": rl_action,
                "final_decision": final_decision,
                "reward": reward,
                "timestamp": self.last_decision_time.isoformat()
            }

        except Exception as e:
            logger.exception("Decision pipeline failed")
            raise

    # ---------------------------------------------------------
    # DECISION MERGING
    # ---------------------------------------------------------
    def merge_decisions(self, forecast, optimization, rl_action):

        """
        Combines outputs of multiple intelligence engines
        """

        decision = {
            "recommended_reduction": max(
                optimization.get("recommended_reduction", 0),
                rl_action.get("reduction", 0)
            ),
            "predicted_load": forecast.get("predicted_load"),
            "confidence_score": (
                forecast.get("confidence", 0.8)
                + rl_action.get("confidence", 0.8)
            ) / 2,
            "control_strategy": rl_action.get("strategy", "balanced")
        }

        return decision

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------
    def health_status(self):

        return {
            "forecast_engine": "OK",
            "rl_engine": "OK",
            "optimization_service": "OK",
            "reward_engine": "OK",
            "last_decision_time": self.last_decision_time,
            "status": "healthy"
        }

    # ---------------------------------------------------------
    # PIPELINE SIMULATION
    # ---------------------------------------------------------
    def simulate_decision(self, telemetry_sample: Dict[str, Any]):

        """
        Runs decision pipeline without RL learning update
        """

        forecast = self.forecasting_engine.predict(telemetry_sample)

        optimization = self.optimization_service.optimize_load(
            telemetry_sample,
            forecast
        )

        rl_action = self.rl_engine.select_action(telemetry_sample)

        final_decision = self.merge_decisions(
            forecast,
            optimization,
            rl_action
        )

        return {
            "forecast": forecast,
            "optimization": optimization,
            "rl_action": rl_action,
            "final_decision": final_decision
        }

    # ---------------------------------------------------------
    # AUTONOMOUS LOOP
    # ---------------------------------------------------------
    def autonomous_loop(self, telemetry_provider):

        """
        Continuous autonomous decision engine
        """

        import time

        logger.info("Autonomous decision loop started")

        while True:

            try:
                telemetry_data = telemetry_provider.get_latest_data()
                result = self.run_decision_pipeline(telemetry_data)
                logger.info(f"Autonomous decision executed: {result}")

            except Exception:
                logger.exception("Autonomous decision loop error")

            time.sleep(settings.DECISION_INTERVAL_SECONDS)
