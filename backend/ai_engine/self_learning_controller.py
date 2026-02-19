"""
Self Learning Controller
Autonomous intelligence supervisor controlling learning cycles,
policy adaptation, retraining decisions and safety checks
"""

import logging
from datetime import datetime
from typing import Dict, Any

from services.data_drift_monitor import DataDriftMonitor
from ai_engine.retraining_engine import RetrainingEngine
from ai_engine.rl_engine import RLEngine
from services.benchmark_service import BenchmarkService
from ml_pipeline.model_registry import ModelRegistry
from core.config import settings

logger = logging.getLogger(__name__)


class SelfLearningController:
    """
    Central autonomous learning decision system
    """

    def __init__(self):

        self.drift_monitor = DataDriftMonitor()
        self.retraining_engine = RetrainingEngine()
        self.rl_engine = RLEngine()
        self.benchmark_service = BenchmarkService()
        self.model_registry = ModelRegistry()

        self.last_cycle_time = None
        self.last_decision = None

        logger.info("Self Learning Controller initialized")

    # ---------------------------------------------------------
    # MAIN AUTONOMOUS DECISION LOOP
    # ---------------------------------------------------------
    def autonomous_learning_cycle(self) -> Dict[str, Any]:
        """
        Executes full autonomous decision cycle
        """

        logger.info("Autonomous learning cycle started")

        drift_result = self.drift_monitor.run_drift_check()

        retraining_triggered = False
        benchmark_result = None
        deployment = False
        rl_training = None

        # Retraining decision
        if drift_result["retraining_triggered"]:
            retraining_triggered = True
            retraining_result = self.retraining_engine.run_retraining_pipeline()

            benchmark_result = self.benchmark_service.run_benchmark()

            if benchmark_result.get("deployment_recommended"):
                self.model_registry.promote_candidate_to_production()
                deployment = True

        # RL training always continues
        rl_training = self.rl_engine.train_step()

        self.last_cycle_time = datetime.utcnow()
        self.last_decision = {
            "retraining": retraining_triggered,
            "deployment": deployment
        }

        logger.info("Autonomous learning cycle completed")

        return {
            "drift_result": drift_result,
            "retraining_triggered": retraining_triggered,
            "benchmark_result": benchmark_result,
            "deployment": deployment,
            "rl_training": rl_training,
            "timestamp": self.last_cycle_time.isoformat()
        }

    # ---------------------------------------------------------
    # SYSTEM INTELLIGENCE STATUS
    # ---------------------------------------------------------
    def intelligence_status(self) -> Dict[str, Any]:
        """
        Returns learning intelligence health
        """

        return {
            "last_cycle_time": self.last_cycle_time,
            "last_decision": self.last_decision,
            "status": "ACTIVE"
        }

    # ---------------------------------------------------------
    # POLICY ADAPTATION
    # ---------------------------------------------------------
    def adapt_learning_policy(self, performance_metric: float):
        """
        Dynamically adjusts learning intensity
        """

        if performance_metric < settings.LOW_PERFORMANCE_THRESHOLD:
            self.rl_engine.increase_learning_rate()

        elif performance_metric > settings.HIGH_PERFORMANCE_THRESHOLD:
            self.rl_engine.decrease_learning_rate()

        logger.info("Learning policy adapted")

    # ---------------------------------------------------------
    # FAILSAFE CHECK
    # ---------------------------------------------------------
    def safety_check(self):
        """
        Ensures system is not degrading
        """

        perf = self.model_registry.get_latest_model_performance()

        if perf.get("accuracy", 0.9) < settings.SAFETY_MIN_ACCURACY:
            logger.warning("Performance degraded — rolling back model")
            self.model_registry.rollback_production_model()
