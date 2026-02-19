"""
Runtime Controller Routes
Enterprise control interface for autonomous runtime orchestration
"""

import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any

from core.runtime_controller import RuntimeController

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/runtime", tags=["Runtime Control"])

runtime_controller = RuntimeController()

# ---------------------------------------------------------
# START RUNTIME CONTROLLER
# ---------------------------------------------------------
@router.post("/start")
async def start_runtime() -> Dict[str, Any]:
    """
    Starts enterprise autonomous runtime controller
    """
    try:
        runtime_controller.start()
        return {
            "status": "runtime_started",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.exception("Runtime start failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# STOP RUNTIME CONTROLLER
# ---------------------------------------------------------
@router.post("/stop")
async def stop_runtime() -> Dict[str, Any]:
    """
    Stops runtime controller
    """
    try:
        runtime_controller.stop()
        return {
            "status": "runtime_stopped",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.exception("Runtime stop failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# RUNTIME STATUS
# ---------------------------------------------------------
@router.get("/status")
async def runtime_status() -> Dict[str, Any]:
    """
    Returns runtime health snapshot
    """
    try:
        return runtime_controller.system_health_snapshot()
    except Exception as e:
        logger.exception("Runtime status failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# MANUAL LIFECYCLE EXECUTION
# ---------------------------------------------------------
@router.post("/run-cycle")
async def run_manual_cycle():
    """
    Runs one lifecycle orchestration cycle manually
    """
    try:
        result = runtime_controller.drift_monitor.run_drift_check()

        if result.get("retraining_triggered"):
            retraining = runtime_controller.retraining_engine.run_retraining_pipeline()
        else:
            retraining = {"status": "not_required"}

        return {
            "cycle_result": result,
            "retraining": retraining,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.exception("Manual cycle execution failed")
        raise HTTPException(status_code=500, detail=str(e))
