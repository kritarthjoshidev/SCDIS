"""
Scheduler Intelligence Loop
Runs autonomous self-learning controller continuously
Responsible for continuous evolution of the AI system
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any

from ai_engine.self_learning_controller import SelfLearningController
from core.config import settings

logger = logging.getLogger(__name__)


class SchedulerIntelligenceLoop:
    """
    Autonomous scheduler running AI intelligence cycles
    """

    def __init__(self):

        self.controller = SelfLearningController()

        self.running = False
        self.last_cycle_time = None
        self.cycle_count = 0
        self.last_cycle_result: Dict[str, Any] = {}

        logger.info("Scheduler Intelligence Loop initialized")

    # ---------------------------------------------------------
    # START LOOP
    # ---------------------------------------------------------
    def start(self):
        """
        Starts autonomous intelligence loop in background thread
        """

        if self.running:
            logger.warning("Scheduler loop already running")
            return

        self.running = True

        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

        logger.info("Autonomous intelligence loop started")

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    def _loop(self):

        logger.info("Entering intelligence loop")

        while self.running:

            try:
                logger.info("Running autonomous learning cycle")

                result = self.controller.autonomous_learning_cycle()

                self.last_cycle_result = result
                self.last_cycle_time = datetime.utcnow()
                self.cycle_count += 1

                logger.info(f"Cycle {self.cycle_count} completed")

                # Adaptive policy adjustment
                performance = result.get("benchmark_result", {})
                accuracy = 0.9

                if isinstance(performance, dict):
                    accuracy = performance.get("candidate_accuracy", 0.9)

                self.controller.adapt_learning_policy(accuracy)

                # Safety check
                self.controller.safety_check()

            except Exception:
                logger.exception("Autonomous cycle failed")

            time.sleep(settings.INTELLIGENCE_LOOP_INTERVAL)

    # ---------------------------------------------------------
    # STOP LOOP
    # ---------------------------------------------------------
    def stop(self):
        """
        Stops intelligence loop
        """

        self.running = False
        logger.info("Autonomous intelligence loop stopped")

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        """
        Returns scheduler status
        """

        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "last_cycle_time": self.last_cycle_time,
            "last_cycle_result": self.last_cycle_result
        }


# Global scheduler instance
intelligence_scheduler = SchedulerIntelligenceLoop()
