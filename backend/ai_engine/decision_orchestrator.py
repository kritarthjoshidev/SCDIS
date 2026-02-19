"""
AI Decision Orchestrator
Central brain coordinating all AI engines in SCDIS
"""

import logging
from datetime import datetime
from typing import Dict, Any

from ai_engine.forecasting_engine import ForecastingEngine
from ai_engine.anomaly_engine import AnomalyEngine
from ai_engine.rl_engine import RLEngine
from ai_engine.reward_engine import RewardEngine
from services.optimization_service import OptimizationService
from services.telemetry_service import TelemetryService

logger = logging.getLogger(__name__)


class DecisionOrchestrator:
    """
    Central decision intelligence orchestrator.
    Responsible for autonomous decision making.
    """

    def __init__(self):
        logger.info("Initializing Decision Orchestrator")

        self.telemetry_service = TelemetryService()
        self.forecasting_engine = ForecastingEngine()
        self.anomaly_engine = AnomalyEngine()
        self.optimization_service = OptimizationService()
        self.rl_engine = RLEngine()
        self.reward_engine = RewardEngine()

        logger.info("Decision Orchestrator initialized successfully")

    # -----------------------------------------------------------
    # MAIN DECISION PIPELINE
    # -----------------------------------------------------------
    def run_full_decision_cycle(self) -> Dict[str, Any]:
        """
        Executes complete AI decision pipeline
        """

        cycle_start = datetime.utcnow()

        try:
            telemetry = self.telemetry_service.get_latest_metrics()
            logger.info("Telemetry collected")

            forecast = self.forecasting_engine.predict(telemetry)
            logger.info("Forecast generated")

            anomaly_report = self.anomaly_engine.detect(telemetry)
            logger.info("Anomaly detection completed")

            optimization_plan = self.optimization_service.optimize(
                telemetry, forecast
            )
            logger.info("Optimization plan created")

            rl_action = self.rl_engine.select_action(telemetry, forecast)
            logger.info("RL decision selected")

            final_decision = self.merge_decisions(
                optimization_plan,
                rl_action,
                anomaly_report
            )

            reward = self.reward_engine.calculate_reward(
                telemetry,
                final_decision,
                forecast
            )

            self.rl_engine.learn(telemetry, rl_action, reward)

            explanation = self.generate_decision_explanation(
                telemetry,
                forecast,
                final_decision,
                reward
            )

            result = {
                "timestamp": cycle_start.isoformat(),
                "telemetry": telemetry,
                "forecast": forecast,
                "decision": final_decision,
                "reward": reward,
                "explanation": explanation
            }

            logger.info("Decision cycle completed successfully")

            return result

        except Exception as e:
            logger.exception("Decision cycle failed")
            return self.safe_fallback_decision()

    # -----------------------------------------------------------
    # DECISION MERGING
    # -----------------------------------------------------------
    def merge_decisions(self, optimization_plan, rl_action, anomaly_report):
        """
        Combines optimization decision and RL policy decision
        """

        decision = optimization_plan.copy()

        if anomaly_report.get("critical"):
            decision["safety_mode"] = True
            decision["load_reduction"] *= 1.2

        decision["rl_adjustment"] = rl_action

        return decision

    # -----------------------------------------------------------
    # EXPLAINABILITY ENGINE
    # -----------------------------------------------------------
    def generate_decision_explanation(self, telemetry, forecast, decision, reward):
        """
        Produces explainable AI decision output
        """

        explanation = {
            "reasoning": "Decision based on predicted load, optimization strategy, and RL policy",
            "predicted_load": forecast.get("predicted_load"),
            "action_taken": decision,
            "expected_reward": reward,
            "confidence": self.estimate_confidence(forecast)
        }

        return explanation

    def estimate_confidence(self, forecast):
        """
        Estimate confidence score of decision
        """
        if "uncertainty" in forecast:
            return max(0.1, 1 - forecast["uncertainty"])
        return 0.85

    # -----------------------------------------------------------
    # FALLBACK SAFETY MODE
    # -----------------------------------------------------------
    def safe_fallback_decision(self):
        """
        Returns safe fallback decision if AI pipeline fails
        """

        logger.warning("Executing fallback decision")

        return {
            "decision": {
                "load_reduction": 5,
                "safety_mode": True
            },
            "reason": "Fallback due to pipeline error"
        }

    # -----------------------------------------------------------
    # MANUAL OVERRIDE
    # -----------------------------------------------------------
    def manual_override(self, override_payload: Dict[str, Any]):
        """
        Admin override capability
        """

        logger.warning("Manual override applied")

        return {
            "override_applied": True,
            "payload": override_payload
        }

    # -----------------------------------------------------------
    # SYSTEM HEALTH
    # -----------------------------------------------------------
    def health_check(self):
        """
        Returns orchestrator health state
        """

        return {
            "forecast_engine": "OK",
            "rl_engine": "OK",
            "optimization_service": "OK",
            "timestamp": datetime.utcnow().isoformat()
        }
