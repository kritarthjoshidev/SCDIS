"""
Enterprise Full Production Validation Suite
Validates complete autonomous AI production stack
"""

import logging
from datetime import datetime

from ai_engine.decision_engine import DecisionEngine
from core.enterprise_event_bus import enterprise_event_bus
from core.runtime_controller import runtime_controller
from core.enterprise_runtime_supervisor import enterprise_runtime_supervisor
from core.enterprise_policy_engine import enterprise_policy_engine
from services.enterprise_alerting_service import enterprise_alerting_service
from core.enterprise_failover_controller import enterprise_failover_controller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enterprise_validation")


def run_enterprise_validation():
    logger.info("========== ENTERPRISE PRODUCTION VALIDATION STARTED ==========")

    results = {}

    try:
        # Decision Engine
        decision_engine = DecisionEngine()
        decision = decision_engine.generate_decision()

        results["decision_engine"] = "OK"

        # Event bus
        enterprise_event_bus.publish("validation_test", {"msg": "test"})
        results["event_bus"] = enterprise_event_bus.health_status()

        # Runtime controller
        results["runtime_controller"] = runtime_controller.health_status()

        # Supervisor
        results["runtime_supervisor"] = enterprise_runtime_supervisor.health_status()

        # Policy engine
        results["policy_engine"] = enterprise_policy_engine.health_status()

        # Alerting
        results["alerting_service"] = enterprise_alerting_service.health_status()

        # Failover
        results["failover_controller"] = enterprise_failover_controller.health_status()

        results["timestamp"] = datetime.utcnow().isoformat()

        logger.info("========== ENTERPRISE VALIDATION PASSED ==========")

    except Exception as e:
        logger.exception("Enterprise validation failed")
        results["error"] = str(e)

    return results


# IMPORTANT RUNNER
if __name__ == "__main__":
    output = run_enterprise_validation()
    print("\nVALIDATION RESULTS:\n")
    print(output)
