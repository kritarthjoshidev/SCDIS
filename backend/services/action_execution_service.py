"""
Autonomous Action Execution Service

Responsibilities:
- Convert AI decisions into operational campus actions
- Maintain execution logs
- Provide rollback safety
- Simulate actuator control for hackathon/demo mode
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

from core.config import settings

logger = logging.getLogger(__name__)


class ActionExecutionService:
    """
    Executes decisions produced by Decision Engine
    """

    def __init__(self):

        self.execution_log: List[Dict[str, Any]] = []
        self.simulation_mode = settings.SIMULATION_MODE

        logger.info("Action Execution Service initialized")

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compatibility wrapper for single-action execution used in tests.
        """

        result = self._execute_single_action(action)

        record = {
            "timestamp": datetime.utcnow(),
            "action": result,
            "mode": "simulation" if self.simulation_mode else "live"
        }

        self.execution_log.append(record)

        return result

    # ---------------------------------------------------------
    # MAIN EXECUTION ENTRY
    # ---------------------------------------------------------
    def execute_actions(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes recommended actions from Decision Engine
        """

        actions = decision.get("final_action", {}).get("recommended_actions", [])

        results = []

        for action in actions:
            result = self._execute_single_action(action)
            results.append(result)

        execution_record = {
            "timestamp": datetime.utcnow(),
            "actions": results,
            "mode": "simulation" if self.simulation_mode else "live"
        }

        self.execution_log.append(execution_record)

        return execution_record

    # ---------------------------------------------------------
    # SINGLE ACTION EXECUTION
    # ---------------------------------------------------------
    def _execute_single_action(self, action: Dict[str, Any]) -> Dict[str, Any]:

        try:

            action_type = action.get("type", "unknown")
            target = action.get("target", "unknown")

            if self.simulation_mode:
                logger.info(f"[SIMULATION] Executing {action_type} on {target}")
            else:
                logger.info(f"[LIVE] Executing {action_type} on {target}")
                # Here real actuator control APIs would be called

            return {
                "action": action_type,
                "target": target,
                "status": "executed"
            }

        except Exception as e:
            logger.exception("Action execution failed")

            return {
                "action": action.get("type"),
                "status": "failed",
                "error": str(e)
            }

    # ---------------------------------------------------------
    # EXECUTION HISTORY
    # ---------------------------------------------------------
    def get_execution_history(self):

        return self.execution_log[-100:]

    # ---------------------------------------------------------
    # ROLLBACK LAST ACTION
    # ---------------------------------------------------------
    def rollback_last(self):

        if not self.execution_log:
            return {"status": "no_actions_to_rollback"}

        last = self.execution_log[-1]

        logger.warning("Rollback executed for last action batch")

        return {
            "status": "rollback_simulated",
            "rolled_back_actions": last
        }

    # ---------------------------------------------------------
    # HEALTH CHECK
    # ---------------------------------------------------------
    def health_status(self):

        return {
            "total_executions": len(self.execution_log),
            "mode": "simulation" if self.simulation_mode else "live",
            "status": "OK"
        }
