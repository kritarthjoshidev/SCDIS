"""
Policy Engine
Responsible for intelligent policy scoring, risk-aware decision weighting,
multi-objective optimization, and explainable decision reasoning.
"""

import logging
import math
from typing import Dict, Any, List
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)


class PolicyEngine:

    def __init__(self):

        self.policy_weights = {
            "energy": settings.POLICY_WEIGHT_ENERGY,
            "cost": settings.POLICY_WEIGHT_COST,
            "carbon": settings.POLICY_WEIGHT_CARBON,
            "comfort": settings.POLICY_WEIGHT_COMFORT,
            "risk": settings.POLICY_WEIGHT_RISK
        }

        self.policy_history: List[Dict[str, Any]] = []

    # ==========================================================
    # MASTER POLICY EVALUATION
    # ==========================================================
    def evaluate(self,
                 forecast: Dict[str, Any],
                 anomaly_score: float,
                 optimization_plan: Dict[str, Any]) -> Dict[str, Any]:

        logger.info("Policy evaluation started")

        energy_score = self.energy_objective(forecast)
        cost_score = self.cost_objective(forecast)
        carbon_score = self.carbon_objective(forecast)
        comfort_score = self.comfort_objective(optimization_plan)
        risk_score = self.risk_objective(anomaly_score)

        final_score = self.combine_scores(
            energy_score,
            cost_score,
            carbon_score,
            comfort_score,
            risk_score
        )

        decision = self.generate_decision(optimization_plan, final_score)

        self.log_policy(decision)

        return decision

    # ==========================================================
    # OBJECTIVE FUNCTIONS
    # ==========================================================
    def energy_objective(self, forecast):

        demand = forecast.get("predicted_load", 0)
        score = 1 - min(demand / settings.MAX_ALLOWED_LOAD, 1)

        return score

    def cost_objective(self, forecast):

        cost = forecast.get("energy_cost", 1)
        score = math.exp(-cost / settings.COST_NORMALIZATION)

        return score

    def carbon_objective(self, forecast):

        carbon = forecast.get("carbon_intensity", 0.5)
        score = 1 - carbon

        return score

    def comfort_objective(self, plan):

        reduction = plan.get("load_reduction_percent", 0)
        score = max(0, 1 - reduction / settings.COMFORT_IMPACT_FACTOR)

        return score

    def risk_objective(self, anomaly_score):

        return 1 - anomaly_score

    # ==========================================================
    # SCORE COMBINATION
    # ==========================================================
    def combine_scores(self, energy, cost, carbon, comfort, risk):

        weighted_score = (
            energy * self.policy_weights["energy"]
            + cost * self.policy_weights["cost"]
            + carbon * self.policy_weights["carbon"]
            + comfort * self.policy_weights["comfort"]
            + risk * self.policy_weights["risk"]
        )

        return weighted_score

    # ==========================================================
    # DECISION GENERATOR
    # ==========================================================
    def generate_decision(self, plan, score):

        confidence = min(1.0, score)

        action_level = "normal"

        if score < settings.POLICY_LOW_THRESHOLD:
            action_level = "aggressive"

        if score > settings.POLICY_HIGH_THRESHOLD:
            action_level = "minimal"

        return {
            "decision_time": datetime.utcnow().isoformat(),
            "confidence": confidence,
            "action_level": action_level,
            "load_reduction_percent": plan.get("load_reduction_percent", 0),
            "target": plan.get("target", "main"),
            "explanation": self.explain(score)
        }

    # ==========================================================
    # EXPLAINABLE AI
    # ==========================================================
    def explain(self, score):

        if score > 0.8:
            return "System operating optimally — minimal intervention required"

        if score > 0.5:
            return "Moderate optimization applied to balance efficiency and comfort"

        return "Aggressive optimization triggered due to high risk conditions"

    # ==========================================================
    # POLICY HISTORY
    # ==========================================================
    def log_policy(self, decision):

        self.policy_history.append({
            "decision": decision,
            "timestamp": datetime.utcnow().isoformat()
        })

        if len(self.policy_history) > settings.MAX_POLICY_HISTORY:
            self.policy_history.pop(0)

    # ==========================================================
    # POLICY ADAPTATION (future RL integration)
    # ==========================================================
    def update_policy_weights(self, feedback: Dict[str, float]):

        for k in self.policy_weights:
            if k in feedback:
                self.policy_weights[k] += feedback[k]

        logger.info("Policy weights updated dynamically")

    # ==========================================================
    # POLICY METRICS
    # ==========================================================
    def policy_metrics(self):

        return {
            "total_decisions": len(self.policy_history),
            "current_weights": self.policy_weights
        }
