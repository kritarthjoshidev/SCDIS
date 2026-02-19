from fastapi import APIRouter, Depends, HTTPException
import logging
from datetime import datetime

from core.security import security_manager
from ml_pipeline.pipeline_controller import PipelineController
from ml_pipeline.model_registry import ModelRegistry
from ml_pipeline.deployment_manager import DeploymentManager

router = APIRouter(prefix="/admin", tags=["Admin Control"])
logger = logging.getLogger(__name__)

pipeline_controller = PipelineController()
registry = ModelRegistry()
deployment_manager = DeploymentManager()


# ==================================================
# Run full training pipeline manually
# ==================================================
@router.post("/run-training")
def run_training(user=Depends(security_manager.verify_token)):

    try:
        result = pipeline_controller.run_training_pipeline()

        return {
            "status": "training_executed",
            "timestamp": datetime.utcnow(),
            "result": result
        }

    except Exception as e:
        logger.error(f"Manual training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# Promote model manually
# ==================================================
@router.post("/promote/{version}")
def promote_model(version: str, user=Depends(security_manager.verify_token)):

    result = deployment_manager.promote_to_production(version)

    return {
        "status": "model_promoted",
        "timestamp": datetime.utcnow(),
        "result": result
    }


# ==================================================
# Rollback model
# ==================================================
@router.post("/rollback/{version}")
def rollback_model(version: str, user=Depends(security_manager.verify_token)):

    result = deployment_manager.rollback(version)

    return {
        "status": "rollback_executed",
        "timestamp": datetime.utcnow(),
        "result": result
    }


# ==================================================
# Model registry inspection
# ==================================================
@router.get("/registry")
def registry_summary(user=Depends(security_manager.verify_token)):

    return registry.get_registry_summary()


# ==================================================
# Pipeline status
# ==================================================
@router.get("/pipeline-status")
def pipeline_status(user=Depends(security_manager.verify_token)):

    return pipeline_controller.pipeline_status()


# ==================================================
# System control — scheduler restart
# ==================================================
@router.post("/system/restart-scheduler")
def restart_scheduler(user=Depends(security_manager.verify_token)):

    return {
        "status": "scheduler_restart_requested",
        "timestamp": datetime.utcnow()
    }
