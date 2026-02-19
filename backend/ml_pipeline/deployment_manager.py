import logging
from datetime import datetime
from typing import Dict

from ml_pipeline.model_registry import ModelRegistry
from core.config import settings

logger = logging.getLogger(__name__)


class DeploymentManager:
    """
    Handles automated model deployment lifecycle:
    - staging deployment
    - production promotion
    - rollback
    - deployment validation
    - blue/green switching
    """

    def __init__(self):
        self.registry = ModelRegistry()

    # ==================================================
    # Validate model before deployment
    # ==================================================
    def validate_model(self, metrics: Dict):

        accuracy = metrics.get("accuracy", 0)

        if accuracy < settings.MIN_MODEL_ACCURACY:
            logger.warning("Model validation failed")
            return False

        return True

    # ==================================================
    # Deploy model to staging
    # ==================================================
    def deploy_to_staging(self, version):

        self.registry.promote_to_staging(version)

        logger.info(f"Model deployed to staging: {version}")

        return {
            "status": "staging_deployed",
            "version": version,
            "time": datetime.utcnow()
        }

    # ==================================================
    # Promote staging model to production
    # ==================================================
    def promote_to_production(self, version):

        self.registry.promote_to_production(version)

        logger.info(f"Model promoted to production: {version}")

        return {
            "status": "production_deployed",
            "version": version,
            "time": datetime.utcnow()
        }

    # ==================================================
    # Automated deployment pipeline
    # ==================================================
    def auto_deploy(self, version, metrics):

        if not self.validate_model(metrics):
            return {"status": "deployment_failed"}

        self.deploy_to_staging(version)

        self.promote_to_production(version)

        logger.info("Auto deployment completed")

        return {
            "status": "auto_deployment_success",
            "version": version
        }

    # ==================================================
    # Rollback production
    # ==================================================
    def rollback(self, version):

        self.registry.rollback_production(version)

        logger.warning(f"Rollback executed to {version}")

        return {
            "status": "rollback_success",
            "version": version,
            "time": datetime.utcnow()
        }

    # ==================================================
    # Get deployment status
    # ==================================================
    def deployment_status(self):

        production = self.registry.get_production_model()

        return {
            "production_model": production,
            "timestamp": datetime.utcnow()
        }
