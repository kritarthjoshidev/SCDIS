"""
Autonomous Control Routes
Controls AI-driven execution of decisions
with safety checks, simulation, and learning feedback.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

from ai_engine.orchestrator import AIOrchestrator
from ai_engine.self_learning_loop import SelfLearningLoop
from services.telemetry_service import TelemetryService
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# core engines
orchestrator = AIOrchestrator()
learning_loop = SelfLearningLoop()
telemetry_service = TelemetryService()


# ==========================================================
# SYSTEM STATE SNAPSHOT
# ==========================================================
def get_current_state():

    telemetry = telemetry_service.get_latest_telemetry()

    state = {
        "energy_load": telemetry.get("energy_load", 0),
        "temperature": telemetry.get("temperature", 25),
        "occupancy": telemetry.get("occupancy", 0),
        "timestamp": datetime.utcnow().isoformat()
    }

    return state


# ==========================================================
# SAFETY VALIDATION
# ==========================================================
def safety_check(decision: Dict[str, Any]):

    if decision.get("load_reduction_percent", 0) > settings.MAX_REDUCTION_PERCENT:
        raise HTTPException(status_code=400, detail="Unsafe reduction percentage")

    if decision.get("temperature_target", 25) < settings.MIN_TEMP_LIMIT:
        raise HTTPException(status_code=400, detail="Temperature below safety limit")

    return True


# ==========================================================
# SIMULATION ENGINE
# ==========================================================
def simulate_decision(decision: Dict[str, Any], state: Dict[str, Any]):

    simulated_state = state.copy()

    reduction = decision.get("load_reduction_percent", 0)

    simulated_state["energy_load"] = state["energy_load"] * (1 - reduction / 100)

    simulated_state["simulation_score"] = (
        state["energy_load"] - simulated_state["energy_load"]
    )

    return simulated_state


# ==========================================================
# EXECUTE AUTONOMOUS DECISION
# ==========================================================
@router.post("/autonomous/execute")
def execute_autonomous_decision():

    try:

        # 1. get current state
        state = get_current_state()

        # 2. AI decision
        decision = orchestrator.generate_decision(state)

        # 3. safety check
        safety_check(decision)

        # 4. simulate decision
        simulation = simulate_decision(decision, state)

        # 5. confidence validation
        if decision.get("confidence", 0) < settings.MIN_DECISION_CONFIDENCE:
            raise HTTPException(status_code=400, detail="Low confidence decision")

        # 6. execution (virtual execution for now)
        execution_status = {
            "executed": True,
            "execution_time": datetime.utcnow().isoformat()
        }

        # 7. learning feedback
        learning_loop.record_decision(decision, state)

        logger.info("Autonomous decision executed")

        return {
            "decision": decision,
            "simulation": simulation,
            "execution": execution_status
        }

    except Exception as e:
        logger.error(f"Execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# SAFE MODE EXECUTION
# ==========================================================
@router.post("/autonomous/safe_execute")
def safe_execute():

    state = get_current_state()
    decision = orchestrator.generate_safe_decision(state)

    safety_check(decision)
    simulation = simulate_decision(decision, state)

    learning_loop.record_decision(decision, state)

    return {
        "mode": "safe",
        "decision": decision,
        "simulation": simulation
    }


# ==========================================================
# EMERGENCY OVERRIDE
# ==========================================================
@router.post("/autonomous/emergency_override")
def emergency_override():

    logger.warning("Emergency override activated")

    return {
        "status": "override_activated",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==========================================================
# SYSTEM AUTONOMY STATUS
# ==========================================================
@router.get("/autonomous/status")
def autonomy_status():

    return {
        "autonomous_mode": True,
        "learning_active": True,
        "policy_version": "v2.1",
        "timestamp": datetime.utcnow().isoformat()
    }
