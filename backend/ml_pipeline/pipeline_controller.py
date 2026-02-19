import logging
from datetime import datetime
from typing import Dict

from ai_engine.retraining_engine import RetrainingEngine
from ml_pipeline.model_registry import ModelRegistry
from ml_pipeline.deployment_manager import DeploymentManager
from core.config import settings

logger = logging.getLogger(__name__)


class PipelineController:
    """
    Master ML lifecycle controller.
    Handles:
    - retraining
    - evaluation
    - model registration
    - automated deployment
    - rollback support
    """

    def __init__(self):

        self.retraining_engine = RetrainingEngine()
        self.registry = ModelRegistry()
        self.deployment_manager = DeploymentManager()

    # ==================================================
    # Evaluate model performance
    # ==================================================
    def evaluate_model(self, metrics: Dict):

        accuracy = metrics.get("accuracy", 0)
        mae = metrics.get("mae", 0)

        if accuracy >= settings.MIN_MODEL_ACCURACY and mae <= settings.MAX_MODEL_MAE:
            return True

        return False

    # ==================================================
    # Full retraining lifecycle
    # ==================================================
    def run_training_pipeline(self):

        logger.info("Training pipeline started")

        # Step 1 — Retrain models
        metrics = self.retraining_engine.retrain_models()

        # Step 2 — Evaluate
        passed = self.evaluate_model(metrics)

        if not passed:
            logger.warning("Model evaluation failed")
            return {"status": "evaluation_failed"}

        # Step 3 — Register
        version = self.registry.register_model(
            settings.MODEL_NAME,
            metrics
        )

        # Step 4 — Auto deploy
        deploy_result = self.deployment_manager.auto_deploy(
            version,
            metrics
        )

        logger.info("Training pipeline completed")

        return {
            "status": "pipeline_success",
            "model_version": version,
            "deployment": deploy_result,
            "metrics": metrics,
            "timestamp": datetime.utcnow()
        }

    # ==================================================
    # Manual deployment
    # ==================================================
    def manual_deploy(self, version):

        return self.deployment_manager.promote_to_production(version)

    # ==================================================
    # Rollback pipeline
    # ==================================================
    def rollback_pipeline(self, version):

        return self.deployment_manager.rollback(version)

    # ==================================================
    # Pipeline status
    # ==================================================
    def pipeline_status(self):

        return self.deployment_manager.deployment_status()
