"""
Reward Intelligence Engine
Calculates reward signals for RL decision system.

Reward Sources:
- Energy saving performance
- Cost reduction
- Load balance stability
- Carbon reduction
- Comfort score
- Anomaly recovery speed
"""

import logging
from typing import Dict, Any
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)


class RewardEngine:

    def __init__(self):

        self.energy_weight = settings.REWARD_ENERGY_WEIGHT
        self.cost_weight = settings.REWARD_COST_WEIGHT
        self.load_weight = settings.REWARD_LOAD_WEIGHT
        self.comfort_weight = settings.REWARD_COMFORT_WEIGHT
        self.carbon_weight = settings.REWARD_CARBON_WEIGHT
        self.stability_weight = settings.REWARD_STABILITY_WEIGHT

        logger.info("Reward Engine initialized")

    # ============================================================
    # MAIN REWARD CALCULATION
    # ============================================================
    def calculate_reward(self,
                         telemetry_before: Dict[str, Any],
                         telemetry_after: Dict[str, Any],
                         decision_meta: Dict[str, Any]) -> float:

        energy_reward = self.energy_reward(
            telemetry_before,
            telemetry_after
        )

        cost_reward = self.cost_reward(
            telemetry_before,
            telemetry_after
        )

        load_reward = self.load_stability_reward(
            telemetry_before,
            telemetry_after
        )

        comfort_reward = self.comfort_reward(
            telemetry_after
        )

        carbon_reward = self.carbon_reward(
            telemetry_before,
            telemetry_after
        )

        stability_reward = self.system_stability_reward(
            decision_meta
        )

        total_reward = (
            energy_reward * self.energy_weight +
            cost_reward * self.cost_weight +
            load_reward * self.load_weight +
            comfort_reward * self.comfort_weight +
            carbon_reward * self.carbon_weight +
            stability_reward * self.stability_weight
        )

        logger.debug("Reward calculated: %f", total_reward)

        return total_reward

    # ============================================================
    # ENERGY SAVING REWARD
    # ============================================================
    def energy_reward(self, before, after):

        try:
            saving = before["energy_usage"] - after["energy_usage"]
            return max(saving, 0)
        except:
            return 0

    # ============================================================
    # COST SAVING REWARD
    # ============================================================
    def cost_reward(self, before, after):

        try:
            saving = before["energy_cost"] - after["energy_cost"]
            return max(saving, 0)
        except:
            return 0

    # ============================================================
    # LOAD BALANCE STABILITY
    # ============================================================
    def load_stability_reward(self, before, after):

        try:
            diff = abs(after["peak_load"] - before["peak_load"])
            return -diff
        except:
            return 0

    # ============================================================
    # COMFORT SCORE
    # ============================================================
    def comfort_reward(self, after):

        try:
            return after.get("comfort_score", 0)
        except:
            return 0

    # ============================================================
    # CARBON FOOTPRINT
    # ============================================================
    def carbon_reward(self, before, after):

        try:
            saving = before["carbon_emission"] - after["carbon_emission"]
            return max(saving, 0)
        except:
            return 0

    # ============================================================
    # SYSTEM STABILITY
    # ============================================================
    def system_stability_reward(self, decision_meta):

        if decision_meta.get("caused_instability"):
            return -10

        return 5

    # ============================================================
    # REWARD EXPLAINABILITY
    # ============================================================
    def explain_reward(self,
                       telemetry_before,
                       telemetry_after,
                       decision_meta):

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "energy_component": self.energy_reward(telemetry_before, telemetry_after),
            "cost_component": self.cost_reward(telemetry_before, telemetry_after),
            "load_component": self.load_stability_reward(telemetry_before, telemetry_after),
            "comfort_component": self.comfort_reward(telemetry_after),
            "carbon_component": self.carbon_reward(telemetry_before, telemetry_after),
            "stability_component": self.system_stability_reward(decision_meta)
        }

    # Compatibility wrapper used by RL engine simulation
    def compute_reward(self, system_metrics: Dict[str, Any]) -> float:
        """
        Lightweight reward for simulated RL environment.
        Uses available metrics (comfort_score, energy_usage) to produce
        a numeric reward when the full telemetry-before/after flow
        is not available.
        """

        try:
            comfort = self.comfort_reward(system_metrics)
            energy = system_metrics.get("energy_usage", 0)

            # higher comfort increases reward; higher energy reduces it
            reward = float(comfort) - float(energy) / 100.0

            return reward
        except Exception:
            logger.exception("compute_reward failed")
            return 0.0
