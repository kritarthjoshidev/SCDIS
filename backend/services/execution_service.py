"""
Execution Service
Responsible for executing AI decisions on real or simulated devices.
Provides safe, auditable, retry-enabled execution pipelines.
"""

import logging
import time
from typing import Dict, Any, List
from datetime import datetime

from core.config import settings
from services.telemetry_service import TelemetryService

logger = logging.getLogger(__name__)


class ExecutionService:

    def __init__(self):
        self.telemetry = TelemetryService()
        self.execution_history: List[Dict[str, Any]] = []

    # ==========================================================
    # MAIN EXECUTION PIPELINE
    # ==========================================================
    def execute(self, decision: Dict[str, Any]) -> Dict[str, Any]:

        logger.info("Execution pipeline started")

        validated = self.validate_decision(decision)

        if not validated:
            raise Exception("Decision validation failed")

        if settings.SIMULATION_MODE:
            result = self.simulate_execution(decision)
        else:
            result = self.execute_live(decision)

        self.log_execution(decision, result)

        return result

    # ==========================================================
    # VALIDATION LAYER
    # ==========================================================
    def validate_decision(self, decision: Dict[str, Any]) -> bool:

        if decision.get("confidence", 0) < settings.MIN_DECISION_CONFIDENCE:
            logger.warning("Decision rejected: low confidence")
            return False

        if decision.get("load_reduction_percent", 0) > settings.MAX_REDUCTION_PERCENT:
            logger.warning("Decision rejected: unsafe load reduction")
            return False

        return True

    # ==========================================================
    # SIMULATION EXECUTION
    # ==========================================================
    def simulate_execution(self, decision: Dict[str, Any]) -> Dict[str, Any]:

        logger.info("Simulation execution running")

        telemetry = self.telemetry.get_latest_telemetry()

        simulated_load = telemetry["energy_load"] * (
            1 - decision.get("load_reduction_percent", 0) / 100
        )

        time.sleep(0.2)

        return {
            "mode": "simulation",
            "simulated_energy_load": simulated_load,
            "executed": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    # ==========================================================
    # LIVE EXECUTION
    # ==========================================================
    def execute_live(self, decision: Dict[str, Any]) -> Dict[str, Any]:

        logger.info("Live device execution started")

        devices = self.resolve_target_devices(decision)

        results = []

        for device in devices:

            result = self.send_device_command(device, decision)
            results.append(result)

        verification = self.verify_execution()

        return {
            "mode": "live",
            "devices": results,
            "verification": verification,
            "timestamp": datetime.utcnow().isoformat()
        }

    # ==========================================================
    # DEVICE ROUTING
    # ==========================================================
    def resolve_target_devices(self, decision: Dict[str, Any]) -> List[str]:

        if decision.get("target") == "lighting":
            return ["lighting_controller"]

        if decision.get("target") == "hvac":
            return ["hvac_controller"]

        return ["main_energy_controller"]

    # ==========================================================
    # DEVICE COMMAND
    # ==========================================================
    def send_device_command(self, device: str, decision: Dict[str, Any]) -> Dict[str, Any]:

        retries = 0

        while retries < settings.EXECUTION_RETRY_LIMIT:

            try:
                # placeholder for real IoT command
                logger.info(f"Command sent to {device}")
                time.sleep(0.1)

                return {
                    "device": device,
                    "status": "success",
                    "attempt": retries + 1
                }

            except Exception as e:
                retries += 1
                logger.error(f"Retry {retries} failed for {device}")

        return {
            "device": device,
            "status": "failed"
        }

    # ==========================================================
    # EXECUTION VERIFICATION
    # ==========================================================
    def verify_execution(self) -> bool:

        telemetry = self.telemetry.get_latest_telemetry()

        if telemetry["energy_load"] <= settings.MAX_ALLOWED_LOAD:
            return True

        return False

    # ==========================================================
    # EXECUTION LOGGING
    # ==========================================================
    def log_execution(self, decision: Dict[str, Any], result: Dict[str, Any]):

        record = {
            "decision": decision,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.execution_history.append(record)

        if len(self.execution_history) > settings.MAX_EXECUTION_HISTORY:
            self.execution_history.pop(0)

        logger.info("Execution logged")

    # ==========================================================
    # ROLLBACK ENGINE
    # ==========================================================
    def rollback_last(self):

        if not self.execution_history:
            return {"status": "no_action"}

        last = self.execution_history[-1]

        logger.warning("Rollback triggered")

        # placeholder rollback logic
        return {
            "status": "rollback_executed",
            "rollback_of": last["decision"]
        }

    # ==========================================================
    # EXECUTION METRICS
    # ==========================================================
    def execution_metrics(self):

        success_count = sum(
            1 for r in self.execution_history if r["result"].get("executed", True)
        )

        return {
            "total_executions": len(self.execution_history),
            "success_rate": success_count / max(len(self.execution_history), 1)
        }
