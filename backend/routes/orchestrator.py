"""
Orchestrator API Routes
Expose autonomous AI decision system endpoints
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from ai_engine.decision_orchestrator import DecisionOrchestrator
from core.security import security_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestrator", tags=["AI Orchestrator"])

orchestrator = DecisionOrchestrator()

# ------------------------------------------------------------
# RUN FULL DECISION PIPELINE
# ------------------------------------------------------------
@router.post("/run-decision-cycle")
async def run_decision_cycle(current_user: Dict = Depends(security_manager.get_current_user)):
    """
    Runs complete AI autonomous decision pipeline
    """

    try:
        result = orchestrator.run_full_decision_cycle()

        return {
            "status": "success",
            "timestamp": datetime.utcnow(),
            "data": result
        }

    except Exception as e:
        logger.exception("Decision cycle execution failed")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# DECISION EXPLANATION
# ------------------------------------------------------------
@router.get("/explain-last-decision")
async def explain_last_decision(current_user: Dict = Depends(security_manager.get_current_user)):
    """
    Returns explanation of last decision
    """

    try:
        result = orchestrator.run_full_decision_cycle()

        return {
            "status": "success",
            "explanation": result.get("explanation")
        }

    except Exception as e:
        logger.exception("Explainability fetch failed")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# MANUAL ADMIN OVERRIDE
# ------------------------------------------------------------
@router.post("/manual-override")
async def manual_override(payload: Dict[str, Any],
                          current_user: Dict = Depends(security_manager.get_current_admin)):
    """
    Allows admin to override AI decision
    """

    try:
        result = orchestrator.manual_override(payload)

        return {
            "status": "override_applied",
            "data": result
        }

    except Exception as e:
        logger.exception("Manual override failed")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# AI HEALTH CHECK
# ------------------------------------------------------------
@router.get("/ai-health")
async def ai_health():
    """
    Returns AI subsystem health
    """

    try:
        health = orchestrator.health_check()

        return {
            "status": "healthy",
            "services": health
        }

    except Exception as e:
        logger.exception("AI health check failed")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# RL POLICY UPDATE TRIGGER
# ------------------------------------------------------------
@router.post("/trigger-rl-training")
async def trigger_rl_training(current_user: Dict = Depends(security_manager.get_current_admin)):
    """
    Trigger reinforcement learning training manually
    """

    try:
        orchestrator.rl_engine.force_training()

        return {
            "status": "training_started"
        }

    except Exception as e:
        logger.exception("RL training trigger failed")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# DECISION SIMULATION
# ------------------------------------------------------------
@router.post("/simulate-decision")
async def simulate_decision(simulation_payload: Dict[str, Any],
                            current_user: Dict = Depends(security_manager.get_current_user)):
    """
    Simulates decision outcome for given scenario
    """

    try:
        telemetry = simulation_payload.get("telemetry")
        forecast = orchestrator.forecasting_engine.predict(telemetry)

        decision = orchestrator.merge_decisions(
            orchestrator.optimization_service.optimize(telemetry, forecast),
            orchestrator.rl_engine.select_action(telemetry, forecast),
            {}
        )

        return {
            "status": "simulation_success",
            "decision": decision,
            "forecast": forecast
        }

    except Exception as e:
        logger.exception("Decision simulation failed")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# DECISION HISTORY PLACEHOLDER
# ------------------------------------------------------------
@router.get("/decision-history")
async def decision_history():
    """
    Returns recent decisions (future DB integration)
    """

    return {
        "message": "Decision history module under development"
    }
