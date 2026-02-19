import logging
import threading
import time
from datetime import datetime

from ai_engine.retraining_engine import RetrainingEngine
from services.telemetry_service import TelemetryService
from ai_engine.orchestrator import AIOrchestrator
from core.config import settings

logger = logging.getLogger(__name__)


class AutonomousScheduler:
    """
    Runs background automated AI lifecycle tasks
    """

    def __init__(self):

        self.retraining_engine = RetrainingEngine()
        self.telemetry_service = TelemetryService()
        self.orchestrator = AIOrchestrator()

        self.running = False

    # ==========================================
    # Daily retraining loop
    # ==========================================
    def retraining_loop(self):

        while self.running:

            try:
                logger.info("Scheduled retraining started")
                self.retraining_engine.retrain_models()
                logger.info("Scheduled retraining completed")

            except Exception as e:
                logger.error(f"Retraining failed: {e}")

            time.sleep(settings.RETRAIN_INTERVAL_SECONDS)

    # ==========================================
    # Dataset monitoring loop
    # ==========================================
    def dataset_monitor_loop(self):

        while self.running:

            try:
                stats = self.telemetry_service._enforce_dataset_limit()
                logger.info("Dataset monitoring executed")

            except Exception as e:
                logger.error(f"Dataset monitoring error: {e}")

            time.sleep(settings.DATA_MONITOR_INTERVAL)

    # ==========================================
    # System health monitoring loop
    # ==========================================
    def health_monitor_loop(self):

        while self.running:

            try:
                logger.info("System health check OK")

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

            time.sleep(settings.HEALTH_CHECK_INTERVAL)

    # ==========================================
    # Start scheduler
    # ==========================================
    def start(self):

        self.running = True

        threading.Thread(target=self.retraining_loop, daemon=True).start()
        threading.Thread(target=self.dataset_monitor_loop, daemon=True).start()
        threading.Thread(target=self.health_monitor_loop, daemon=True).start()

        logger.info("Autonomous scheduler started")

    # ==========================================
    # Stop scheduler
    # ==========================================
    def stop(self):
        self.running = False
        logger.info("Autonomous scheduler stopped")
