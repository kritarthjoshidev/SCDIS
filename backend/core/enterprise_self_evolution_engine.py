"""
Enterprise Self Evolution Engine
Autonomous architecture self-improvement layer

Capabilities:
- Detect system performance degradation
- Evaluate AI decision quality
- Identify architecture bottlenecks
- Trigger autonomous optimization or retraining
- Recommend pipeline upgrades
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any

from core.config import settings
from core.enterprise_event_bus import enterprise_event_bus
from services.data_drift_monitor import DataDriftMonitor
from ai_engine.retraining_engine import RetrainingEngine
from ml_pipeline.model_registry import ModelRegistry
from services.enterprise_alerting_service import enterprise_alerting_service

logger = logging.getLogger(__name__)


class EnterpriseSelfEvolutionEngine:
    """
    Autonomous self-improving intelligence core
    """

    def __init__(self):
        self.running = False
        self.last_evolution_cycle = None

        self.drift_monitor = DataDriftMonitor()
        self.retraining_engine = RetrainingEngine()
        self.model_registry = ModelRegistry()

        logger.info("Enterprise Self Evolution Engine initialized")

    # ---------------------------------------------------------
    # START ENGINE
    # ---------------------------------------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        threading.Thread(target=self.evolution_loop, daemon=True).start()
        logger.info("Enterprise Self Evolution Engine started")

    # ---------------------------------------------------------
    # EVOLUTION LOOP
    # ---------------------------------------------------------
    def evolution_loop(self):
        while self.running:
            try:
                self.run_evolution_cycle()
            except Exception:
                logger.exception("Self-evolution cycle failed")

            time.sleep(settings.SELF_EVOLUTION_INTERVAL)

    # ---------------------------------------------------------
    # EVOLUTION CYCLE
    # ---------------------------------------------------------
    def run_evolution_cycle(self) -> Dict[str, Any]:
        """
        Executes full autonomous evolution cycle
        """

        logger.info("Running enterprise evolution cycle")

        drift_result = self.drift_monitor.run_drift_check()

        retraining_triggered = False

        if drift_result.get("retraining_triggered"):
            retraining_result = self.retraining_engine.run_retraining_pipeline()
            retraining_triggered = True
        else:
            retraining_result = {"status": "not_required"}

        model_health = self.model_registry.health_status()

        evolution_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "drift_score": drift_result.get("drift_score"),
            "performance_drift": drift_result.get("performance_drift"),
            "retraining_triggered": retraining_triggered,
            "model_health": model_health
        }

        # Publish enterprise evolution event
        enterprise_event_bus.publish("enterprise_evolution_cycle", evolution_report)

        # Alert if severe degradation
        if drift_result.get("drift_score", 0) > settings.CRITICAL_DRIFT_THRESHOLD:
            enterprise_alerting_service.raise_alert(
                "critical_model_drift",
                evolution_report
            )

        self.last_evolution_cycle = datetime.utcnow()

        logger.info("Enterprise evolution cycle completed")

        return evolution_report

    # ---------------------------------------------------------
    # MANUAL EVOLUTION TRIGGER
    # ---------------------------------------------------------
    def trigger_manual_evolution(self):
        return self.run_evolution_cycle()

    # ---------------------------------------------------------
    # HEALTH STATUS
    # ---------------------------------------------------------
    def health_status(self):
        return {
            "status": "OK",
            "running": self.running,
            "last_cycle": (
                self.last_evolution_cycle.isoformat()
                if self.last_evolution_cycle else None
            )
        }


# Global instance
enterprise_self_evolution_engine = EnterpriseSelfEvolutionEngine()
