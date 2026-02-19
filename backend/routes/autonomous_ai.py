"""
Autonomous AI Control Routes
Central control interface for entire autonomous ML lifecycle
"""

import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any

from ai_engine.retraining_engine import RetrainingEngine
from services.data_drift_monitor import DataDriftMonitor
from services.benchmark_service import BenchmarkService
from ai_engine.rl_engine import RLEngine
from ml_pipeline.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/autonomous-ai", tags=["Autonomous AI"])

# Services
retraining_engine = RetrainingEngine()
drift_monitor = DataDriftMonitor()
benchmark_service = BenchmarkService()
rl_engine = RLEngine()
model_registry = ModelRegistry()

# ---------------------------------------------------------
# AI SYSTEM STATUS
# ---------------------------------------------------------
@router.get("/status")
async def ai_system_status() -> Dict[str, Any]:
    """
    Returns complete autonomous AI health and status
    """

    try:
        return {
            "timestamp": datetime.utcnow(),
            "components": {
                "retraining_engine": retraining_engine.pipeline_status(),
                "drift_monitor": drift_monitor.health_status(),
                "benchmark_service": benchmark_service.health_status(),
                "rl_engine": rl_engine.health_status(),
                "model_registry": model_registry.health_status()
            }
        }

    except Exception as e:
        logger.exception("AI status failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# TRIGGER FULL AUTONOMOUS LEARNING CYCLE
# ---------------------------------------------------------
@router.post("/run-full-cycle")
async def run_full_cycle():
    """
    Runs complete AI learning pipeline
    """

    try:
        drift_result = drift_monitor.run_drift_check()

        retrain_result = retraining_engine.run_retraining_pipeline()

        benchmark_result = benchmark_service.run_benchmark()

        deployment = False
        if benchmark_result.get("deployment_recommended"):
            model_registry.promote_candidate_to_production()
            deployment = True

        rl_result = rl_engine.train_step()

        return {
            "drift_check": drift_result,
            "retraining": retrain_result,
            "benchmark": benchmark_result,
            "rl_training": rl_result,
            "deployment_performed": deployment,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.exception("Full cycle execution failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# MANUAL RETRAINING
# ---------------------------------------------------------
@router.post("/retrain")
async def manual_retraining():
    """
    Manually trigger model retraining
    """

    try:
        result = retraining_engine.run_retraining_pipeline()
        return {"status": "completed", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# MANUAL DRIFT CHECK
# ---------------------------------------------------------
@router.post("/drift-check")
async def manual_drift_check():
    """
    Runs drift detection manually
    """

    try:
        result = drift_monitor.run_drift_check()
        return {"status": "completed", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# BENCHMARK MODELS
# ---------------------------------------------------------
@router.post("/benchmark")
async def benchmark_models():
    """
    Runs candidate vs production benchmarking
    """

    try:
        result = benchmark_service.run_benchmark()
        return {"status": "completed", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# RL TRAIN STEP
# ---------------------------------------------------------
@router.post("/rl-train")
async def rl_train_step():
    """
    Runs one reinforcement learning training step
    """

    try:
        result = rl_engine.train_step()
        return {"status": "completed", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# DEPLOY CANDIDATE MODEL
# ---------------------------------------------------------
@router.post("/deploy-candidate")
async def deploy_candidate_model():
    """
    Promote candidate model to production manually
    """

    try:
        model_registry.promote_candidate_to_production()
        return {"status": "candidate model deployed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
