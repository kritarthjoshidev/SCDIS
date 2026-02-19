"""
Autonomous Learning Controller
Enterprise AI self-learning orchestration engine

Responsibilities:
- Continuous system intelligence evaluation
- Trigger retraining when needed
- Trigger RL policy update
- Model performance benchmarking
- Auto-deployment of best model
- Long-term learning optimization
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any

from core.config import settings
from ai_engine.retraining_engine import RetrainingEngine
from ai_engine.rl_engine import RLEngine
from ml_pipeline.model_registry import ModelRegistry
from services.data_drift_monitor import DataDriftMonitor
from services.benchmark_service import BenchmarkService

logger = logging.getLogger(__name__)


class AutonomousLearningController:
    """
    Self-improving AI controller
    """

    def __init__(self):
        self.retraining_engine = RetrainingEngine()
        self.rl_engine = RLEngine()
        self.model_registry = ModelRegistry()
        self.drift_monitor = DataDriftMonitor()
        self.benchmark_service = BenchmarkService()

        self.last_cycle_time = None
        self.learning_cycles = 0

        logger.info("Autonomous Learning Controller initialized")

    # ---------------------------------------------------------
    # MAIN AUTONOMOUS LOOP
    # ---------------------------------------------------------
    def autonomous_learning_cycle(self) -> Dict[str, Any]:
        """
        Executes one intelligent learning cycle
        """

        logger.info("Autonomous learning cycle started")

        drift_result = self.drift_monitor.run_drift_check()

        retrained = False
        rl_updated = False

        # Retraining decision
        if drift_result["retraining_triggered"]:
            logger.info("Retraining required — starting retraining pipeline")
            self.retraining_engine.run_retraining_pipeline()
            retrained = True

        # RL update decision
        rl_score = self.rl_engine.evaluate_policy()

        if rl_score < settings.RL_MIN_ACCEPTABLE_SCORE:
            logger.info("RL policy underperforming — updating policy")
            self.rl_engine.train_policy()
            rl_updated = True

        # Benchmark models
        benchmark_result = self.benchmark_service.run_benchmark()

        if benchmark_result["new_model_better"]:
            logger.info("Deploying new best model")
            self.model_registry.deploy_candidate_model()

        self.learning_cycles += 1
        self.last_cycle_time = datetime.utcnow()

        logger.info("Autonomous learning cycle completed")

        return {
            "cycle": self.learning_cycles,
            "retraining": retrained,
            "rl_updated": rl_updated,
            "benchmark": benchmark_result,
            "timestamp": self.last_cycle_time.isoformat()
        }

    # ---------------------------------------------------------
    # CONTINUOUS SELF-LEARNING LOOP
    # ---------------------------------------------------------
    def run_continuous_learning(self):
        """
        Runs continuous learning system
        """

        logger.info("Starting continuous autonomous learning loop")

        while True:
            try:
                result = self.autonomous_learning_cycle()
                logger.info(f"Learning cycle result: {result}")
            except Exception:
                logger.exception("Autonomous learning cycle failed")

            time.sleep(settings.AUTONOMOUS_LEARNING_INTERVAL)

    # ---------------------------------------------------------
    # HEALTH STATUS
    # ---------------------------------------------------------
    def health_status(self):
        """
        Returns controller health
        """

        return {
            "status": "OK",
            "learning_cycles": self.learning_cycles,
            "last_cycle_time": self.last_cycle_time
        }
