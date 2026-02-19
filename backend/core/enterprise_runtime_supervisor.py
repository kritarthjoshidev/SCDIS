"""
Enterprise Runtime Supervisor
Top Autonomous Orchestration Brain

Responsibilities:
- Global autonomous lifecycle supervision
- Runtime controller coordination
- Policy enforcement integration
- Failover orchestration
- Alert routing and escalation
- Enterprise event flow coordination
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any

from core.enterprise_failover_controller import enterprise_failover_controller
from core.enterprise_event_bus import enterprise_event_bus
from core.enterprise_policy_engine import enterprise_policy_engine
from core.runtime_controller import runtime_controller
from services.enterprise_alerting_service import enterprise_alerting_service
from core.config import settings

logger = logging.getLogger(__name__)


class EnterpriseRuntimeSupervisor:
    """
    Enterprise autonomous supervisory intelligence layer
    """

    def __init__(self):
        self.running = False
        self.last_cycle_time = None

        logger.info("Enterprise Runtime Supervisor initialized")

    # ---------------------------------------------------------
    # SUPERVISOR START
    # ---------------------------------------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        threading.Thread(target=self.supervisor_loop, daemon=True).start()
        logger.info("Enterprise Runtime Supervisor started")

    # ---------------------------------------------------------
    # MAIN SUPERVISOR LOOP
    # ---------------------------------------------------------
    def supervisor_loop(self):
        """
        Continuous global supervision loop
        """

        while self.running:
            try:
                self.execute_supervision_cycle()
            except Exception:
                logger.exception("Supervisor cycle failed")

            time.sleep(settings.RUNTIME_SUPERVISOR_INTERVAL)

    # ---------------------------------------------------------
    # SUPERVISION CYCLE
    # ---------------------------------------------------------
    def execute_supervision_cycle(self):
        """
        Executes enterprise-level orchestration cycle
        """

        # Policy enforcement check
        policy_result = enterprise_policy_engine.evaluate_global_policies()

        if policy_result.get("violation_detected"):
            enterprise_alerting_service.raise_alert(
                "policy_violation",
                policy_result
            )

        # Runtime health check
        runtime_health = runtime_controller.health_status()

        if runtime_health.get("status") != "OK":
            enterprise_alerting_service.raise_alert(
                "runtime_health_issue",
                runtime_health
            )

        # Failover health check
        failover_health = enterprise_failover_controller.health_status()

        # Publish enterprise heartbeat
        enterprise_event_bus.publish(
            "enterprise_heartbeat",
            {
                "timestamp": datetime.utcnow().isoformat(),
                "runtime_health": runtime_health,
                "failover_health": failover_health
            }
        )

        self.last_cycle_time = datetime.utcnow()

        logger.debug("Enterprise supervision cycle completed")

    # ---------------------------------------------------------
    # MANUAL EMERGENCY HANDLER
    # ---------------------------------------------------------
    def emergency_shutdown(self) -> Dict[str, Any]:
        """
        Emergency autonomous shutdown
        """

        logger.critical("Enterprise emergency shutdown triggered")

        self.running = False

        enterprise_alerting_service.raise_alert(
            "emergency_shutdown",
            {"timestamp": datetime.utcnow().isoformat()}
        )

        return {"status": "shutdown_executed"}

    # ---------------------------------------------------------
    # HEALTH STATUS
    # ---------------------------------------------------------
    def health_status(self):
        return {
            "status": "OK",
            "running": self.running,
            "last_cycle_time": (
                self.last_cycle_time.isoformat()
                if self.last_cycle_time else None
            )
        }


# Global supervisor instance
enterprise_runtime_supervisor = EnterpriseRuntimeSupervisor()
