"""
Digital Twin Service
Creates a virtual replica of the campus infrastructure
to simulate AI decisions before applying them in reality.
"""

import logging
from datetime import datetime
from typing import Dict, Any
import random

from services.telemetry_service import TelemetryService
from core.config import settings

logger = logging.getLogger(__name__)


class DigitalTwinService:
    """
    Digital twin simulation environment that mirrors
    real campus operational state.
    """

    def __init__(self):

        self.telemetry_service = TelemetryService()

        # virtual environment state
        self.virtual_state = {}

        logger.info("Digital Twin Service initialized")

    # ==========================================================
    # STATE SYNC
    # ==========================================================
    def sync_state(self):

        telemetry = self.telemetry_service.get_latest_telemetry()

        self.virtual_state = telemetry

        logger.info("Digital twin synchronized with real telemetry")

        return self.virtual_state

    # ==========================================================
    # APPLY DECISION IN VIRTUAL ENVIRONMENT
    # ==========================================================
    def apply_virtual_decision(self, decision: Dict[str, Any]):

        if not self.virtual_state:
            self.sync_state()

        simulated_state = self.virtual_state.copy()

        # Example impact simulation
        load_reduction = decision.get("load_reduction", 0)
        cooling_adjustment = decision.get("cooling_adjustment", 0)

        simulated_state["energy_load"] = max(
            0,
            simulated_state.get("energy_load", 1000) * (1 - load_reduction)
        )

        simulated_state["temperature"] = (
            simulated_state.get("temperature", 25)
            + cooling_adjustment
        )

        logger.info("Virtual decision applied")

        return simulated_state

    # ==========================================================
    # SAVINGS ESTIMATION
    # ==========================================================
    def estimate_savings(self, simulated_state: Dict[str, Any]):

        baseline_load = self.virtual_state.get("energy_load", 1000)
        new_load = simulated_state.get("energy_load", baseline_load)

        savings = baseline_load - new_load

        return {
            "estimated_energy_saved": savings,
            "estimated_cost_saved": savings * settings.ENERGY_COST_PER_UNIT
        }

    # ==========================================================
    # RISK ANALYSIS
    # ==========================================================
    def risk_analysis(self, simulated_state: Dict[str, Any]):

        risk_score = 0

        if simulated_state.get("temperature", 25) > settings.MAX_SAFE_TEMP:
            risk_score += 40

        if simulated_state.get("energy_load", 1000) > settings.MAX_ALLOWED_LOAD:
            risk_score += 40

        # randomness to simulate environmental uncertainty
        risk_score += random.randint(0, 10)

        return {
            "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score > 50 else "LOW"
        }

    # ==========================================================
    # FULL SIMULATION PIPELINE
    # ==========================================================
    def simulate_decision(self, decision: Dict[str, Any]):

        self.sync_state()

        simulated_state = self.apply_virtual_decision(decision)

        savings = self.estimate_savings(simulated_state)

        risk = self.risk_analysis(simulated_state)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "simulated_state": simulated_state,
            "savings_estimation": savings,
            "risk_analysis": risk
        }

    # ==========================================================
    # MULTI-SCENARIO TESTING
    # ==========================================================
    def scenario_testing(self, decision: Dict[str, Any], scenarios: int = 5):

        results = []

        for _ in range(scenarios):

            simulation = self.simulate_decision(decision)
            results.append(simulation)

        avg_savings = sum(r["savings_estimation"]["estimated_energy_saved"]
                          for r in results) / scenarios

        avg_risk = sum(r["risk_analysis"]["risk_score"]
                       for r in results) / scenarios

        return {
            "scenarios_tested": scenarios,
            "average_savings": avg_savings,
            "average_risk": avg_risk,
            "details": results
        }
