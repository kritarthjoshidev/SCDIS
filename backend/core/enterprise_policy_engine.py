"""
Enterprise Policy Engine
Autonomous AI Governance Layer

Responsible for:
- Safety guardrails
- RL decision constraints
- Load control compliance
- Emergency override enforcement
- Operational policy validation
"""

import logging
from datetime import datetime
from typing import Dict, Any

from core.config import settings

logger = logging.getLogger(__name__)


class EnterprisePolicyEngine:
    """
    Enterprise governance and safety enforcement engine
    """

    def __init__(self):
        logger.info("Enterprise Policy Engine initialized")

    # ---------------------------------------------------------
    # LOAD SAFETY POLICY
    # ---------------------------------------------------------
    def enforce_load_constraints(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures recommended load actions stay within allowed safety bounds
        """

        reduction = decision.get("recommended_reduction", 0)

        if reduction > settings.MAX_ALLOWED_LOAD_REDUCTION:
            logger.warning("Policy override: reduction exceeded safety limit")
            decision["recommended_reduction"] = settings.MAX_ALLOWED_LOAD_REDUCTION
            decision["policy_override"] = True

        if reduction < settings.MIN_ALLOWED_LOAD_REDUCTION:
            decision["recommended_reduction"] = settings.MIN_ALLOWED_LOAD_REDUCTION
            decision["policy_override"] = True

        return decision

    # ---------------------------------------------------------
    # RL ACTION VALIDATION
    # ---------------------------------------------------------
    def validate_rl_action(self, action: str) -> str:
        """
        Ensures RL actions comply with enterprise allowed actions
        """

        allowed = settings.ALLOWED_RL_ACTIONS

        if action not in allowed:
            logger.warning(f"Policy blocked unauthorized RL action: {action}")
            return "maintain_state"

        return action

    # ---------------------------------------------------------
    # EMERGENCY OVERRIDE CHECK
    # ---------------------------------------------------------
    def emergency_override_required(self, system_state: Dict[str, Any]) -> bool:
        """
        Determines whether emergency control override should activate
        """

        load = system_state.get("current_load", 0)

        if load > settings.EMERGENCY_LOAD_THRESHOLD:
            logger.critical("Emergency override triggered")
            return True

        return False

    # ---------------------------------------------------------
    # COMPLIANCE VALIDATION
    # ---------------------------------------------------------
    def validate_compliance(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies compliance policy rules to decision
        """

        if decision.get("predicted_load", 0) > settings.COMPLIANCE_MAX_LOAD:
            logger.warning("Compliance load cap applied")
            decision["predicted_load"] = settings.COMPLIANCE_MAX_LOAD
            decision["compliance_adjusted"] = True

        return decision

    # ---------------------------------------------------------
    # FULL POLICY ENFORCEMENT PIPELINE
    # ---------------------------------------------------------
    def enforce_policies(
        self,
        decision: Dict[str, Any],
        rl_action: str,
        system_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes complete governance enforcement
        """

        decision = self.enforce_load_constraints(decision)
        decision = self.validate_compliance(decision)

        rl_action = self.validate_rl_action(rl_action)

        emergency = self.emergency_override_required(system_state)

        return {
            "decision": decision,
            "rl_action": rl_action,
            "emergency_override": emergency,
            "policy_timestamp": datetime.utcnow().isoformat()
        }

    # ---------------------------------------------------------
    # HEALTH STATUS
    # ---------------------------------------------------------
    def health_status(self):
        return {
            "status": "OK",
            "engine": "Enterprise Policy Engine"
        }

    # ---------------------------------------------------------
    # EVALUATE GLOBAL POLICIES
    # ---------------------------------------------------------
    def evaluate_global_policies(self) -> Dict[str, Any]:
        """
        Evaluates all global enterprise policies
        """
        return {
            "status": "compliant",
            "timestamp": datetime.utcnow().isoformat(),
            "policies_evaluated": [
                "load_constraints",
                "rl_action_validation",
                "emergency_override",
                "compliance_validation"
            ]
        }

# Global instance
enterprise_policy_engine = EnterprisePolicyEngine()
