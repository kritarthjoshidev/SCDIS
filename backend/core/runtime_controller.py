"""
Enterprise Runtime Controller
Autonomous orchestration layer for the entire ML intelligence platform

Responsibilities:
- Periodic drift monitoring
- Automated retraining triggers
- Benchmark evaluation
- Candidate deployment / rollback
- Reinforcement learning training cycles
- System health supervision
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any

from core.config import settings
from services.data_drift_monitor import DataDriftMonitor
from ai_engine.retraining_engine import RetrainingEngine
from services.benchmark_service import BenchmarkService
from ai_engine.rl_engine import RLEngine
from ml_pipeline.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class RuntimeController:
    """
    Enterprise autonomous AI runtime controller
    """

    def __init__(self):
        self.drift_monitor = DataDriftMonitor()
        self.retraining_engine = RetrainingEngine()
        self.benchmark_service = BenchmarkService()
        self.rl_engine = RLEngine()
        self.model_registry = ModelRegistry()

        self.running = False
        self.last_cycle_time = None

        logger.info("Runtime Controller initialized")

    # ---------------------------------------------------------
    # MAIN AUTONOMOUS LOOP
    # ---------------------------------------------------------
    def start(self):
        """
        Starts autonomous orchestration threads
        """

        if self.running:
            return

        self.running = True

        threading.Thread(target=self.lifecycle_loop, daemon=True).start()
        threading.Thread(target=self.rl_training_loop, daemon=True).start()
        threading.Thread(target=self.health_supervision_loop, daemon=True).start()

        logger.info("Runtime Controller started")

    # ---------------------------------------------------------
    # FULL LIFECYCLE LOOP
    # ---------------------------------------------------------
    def lifecycle_loop(self):
        """
        Complete ML lifecycle automation
        """

        while self.running:
            try:
                logger.info("Runtime lifecycle cycle started")

                drift_result = self.drift_monitor.run_drift_check()

                retraining_result = None
                if drift_result.get("retraining_triggered"):
                    retraining_result = self.retraining_engine.run_retraining_pipeline()

                    benchmark_result = self.benchmark_service.run_benchmark()

                    if benchmark_result.get("deployment_recommended"):
                        logger.info("Promoting candidate model to production")
                        self.model_registry.promote_candidate_to_production()

                self.last_cycle_time = datetime.utcnow()

            except Exception:
                logger.exception("Runtime lifecycle iteration failed")

            time.sleep(settings.RUNTIME_LIFECYCLE_INTERVAL)

    # ---------------------------------------------------------
    # RL TRAINING LOOP
    # ---------------------------------------------------------
    def rl_training_loop(self):
        """
        Continuous reinforcement learning updates
        """

        while self.running:
            try:
                self.rl_engine.train_step()
            except Exception:
                logger.exception("RL training loop failed")

            time.sleep(settings.RL_TRAINING_INTERVAL)

    # ---------------------------------------------------------
    # HEALTH SUPERVISION LOOP
    # ---------------------------------------------------------
    def health_supervision_loop(self):
        """
        Monitors system health and performs automatic corrective actions
        """

        while self.running:
            try:
                health = self.system_health_snapshot()

                if health["model_registry"]["status"] != "OK":
                    logger.warning("Model registry health issue detected")
                    self.model_registry.refresh_registry()

            except Exception:
                logger.exception("Health supervision loop failed")

            time.sleep(settings.RUNTIME_HEALTH_INTERVAL)

    # ---------------------------------------------------------
    # STATUS SNAPSHOT
    # ---------------------------------------------------------
    def system_health_snapshot(self) -> Dict[str, Any]:
        """
        Returns full runtime health snapshot
        """

        return {
            "runtime_status": "running" if self.running else "stopped",
            "last_cycle_time": self.last_cycle_time,
            "model_registry": self.model_registry.health_status(),
            "rl_engine": self.rl_engine.health_status(),
            "timestamp": datetime.utcnow().isoformat()
        }

    # ---------------------------------------------------------
    # HEALTH STATUS
    # ---------------------------------------------------------
    def health_status(self) -> Dict[str, Any]:
        """
        Returns runtime controller health status
        """
        return {
            "status": "running" if self.running else "stopped",
            "timestamp": datetime.utcnow().isoformat()
        }

    # ---------------------------------------------------------
    # STOP CONTROLLER
    # ---------------------------------------------------------
    def stop(self):
        """
        Stops runtime controller
        """

        self.running = False
        logger.info("Runtime Controller stopped")

# IMPORTANT — GLOBAL INSTANCE (REQUIRED BY IMPORTS)
runtime_controller = RuntimeController()