"""
Optimization Service
Industrial-grade load optimization engine

Responsible for:
- Load reduction optimization
- Constraint-aware control
- Cost optimization
- Multi-objective decision support
- Safe campus power control policies
"""

import logging
from typing import Dict, Any
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)


class OptimizationService:
    """
    Energy optimization intelligence layer
    """

    def __init__(self):

        self.default_reduction = settings.DEFAULT_REDUCTION_PERCENT
        self.max_load = settings.MAX_ALLOWED_LOAD
        self.min_load = settings.MIN_ALLOWED_LOAD
        self.cost_weight = settings.COST_WEIGHT
        self.energy_weight = settings.ENERGY_WEIGHT
        self.stability_weight = settings.STABILITY_WEIGHT

        self.last_optimization_time = None
        self.last_result = None

        logger.info("Optimization Service initialized")

    # ---------------------------------------------------------
    # MAIN OPTIMIZATION ENTRYPOINT
    # ---------------------------------------------------------
    def optimize_load(self, telemetry: Dict[str, Any], forecast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core optimization decision
        """

        try:

            current_load = telemetry.get("current_load", 0)
            predicted_load = forecast.get("predicted_load", current_load)

            reduction_needed = self._compute_required_reduction(predicted_load)

            constrained_reduction = self._apply_constraints(
                current_load,
                reduction_needed
            )

            cost_impact = self._estimate_cost_saving(
                constrained_reduction,
                current_load
            )

            stability_score = self._calculate_stability_score(
                current_load,
                constrained_reduction
            )

            result = {
                "recommended_reduction": constrained_reduction,
                "predicted_load": predicted_load,
                "cost_saving_estimate": cost_impact,
                "stability_score": stability_score,
                "optimization_timestamp": datetime.utcnow().isoformat()
            }

            self.last_optimization_time = datetime.utcnow()
            self.last_result = result

            return result

        except Exception:
            logger.exception("Optimization failed")
            return {
                "recommended_reduction": 0,
                "status": "failed"
            }

    # ---------------------------------------------------------
    # REQUIRED REDUCTION CALCULATION
    # ---------------------------------------------------------
    def _compute_required_reduction(self, predicted_load):

        if predicted_load > self.max_load:
            overload = predicted_load - self.max_load
            percent = (overload / predicted_load) * 100
            return max(percent, self.default_reduction)

        return self.default_reduction * 0.3

    # ---------------------------------------------------------
    # CONSTRAINT HANDLING
    # ---------------------------------------------------------
    def _apply_constraints(self, current_load, reduction):

        # guard against zero current_load
        if not current_load:
            return 0

        reduced_load = current_load * (1 - reduction / 100)

        if reduced_load < self.min_load:
            safe_reduction = ((current_load - self.min_load) / current_load) * 100
            return max(safe_reduction, 0)

        return min(reduction, 50)

    # ---------------------------------------------------------
    # COST SAVING ESTIMATION
    # ---------------------------------------------------------
    def _estimate_cost_saving(self, reduction, current_load):

        energy_saved = current_load * (reduction / 100)
        cost_per_unit = settings.ENERGY_COST_PER_UNIT

        return energy_saved * cost_per_unit

    # ---------------------------------------------------------
    # STABILITY SCORE
    # ---------------------------------------------------------
    def _calculate_stability_score(self, current_load, reduction):

        if reduction < 10:
            return 0.95
        if reduction < 25:
            return 0.85
        return 0.7

    # ---------------------------------------------------------
    # MULTI-OBJECTIVE SCORE
    # ---------------------------------------------------------
    def compute_multi_objective_score(self, cost_saving, stability_score):

        return (
            cost_saving * self.cost_weight
            + stability_score * self.stability_weight
        )

    # ---------------------------------------------------------
    # HEALTH
    # ---------------------------------------------------------
    def health_status(self):

        return {
            "last_optimization_time": self.last_optimization_time,
            "status": "OK"
        }

    # compatibility wrapper for older callsites
    def optimize_energy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lightweight compatibility method used by tests and legacy code.
        Calculates a simple saving estimate based on configured default reduction.
        """

        try:
            energy_usage = payload.get("energy_usage", 0)
            reduction = self.default_reduction
            energy_saved = energy_usage * (reduction / 100.0)
            cost_saved = energy_saved * settings.ENERGY_COST_PER_UNIT

            return {
                "recommended_reduction": reduction,
                "energy_saved": energy_saved,
                "cost_saved": cost_saved,
                "status": "ok"
            }

        except Exception:
            logger.exception("optimize_energy failed")
            return {"status": "failed"}

    # compatibility wrapper for newer callsites
    def optimize(self, telemetry_data: Dict[str, Any], forecast: Dict[str, Any], rl_action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unified optimize entry used by the decision engine. Delegates
        to optimize_load and formats inputs compatibly.
        """

        try:
            # telemetry_data may contain different keys; normalize expected ones
            telemetry = telemetry_data or {}
            return self.optimize_load(telemetry, forecast)

        except Exception:
            logger.exception("optimize failed")
            return {"recommended_reduction": 0, "status": "failed"}
