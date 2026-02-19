"""
Enterprise Alerting Service
Autonomous AI Reliability Layer

Responsible for:
- Drift alerts
- Model degradation alerts
- Runtime failures
- Deployment notifications
- RL instability warnings
- System reliability escalation
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

from core.enterprise_event_bus import enterprise_event_bus

logger = logging.getLogger(__name__)


class EnterpriseAlertingService:
    """
    Enterprise autonomous reliability monitoring
    """

    def __init__(self):
        self.alert_history: List[Dict[str, Any]] = []
        self.running = False
        logger.info("Enterprise Alerting Service initialized")

    # ---------------------------------------------------------
    # START / STOP
    # ---------------------------------------------------------
    def start(self):
        """Start the alerting service"""
        if self.running:
            logger.info("Alerting Service already running")
            return
        
        self.running = True
        logger.info("Enterprise Alerting Service started")

    def stop(self):
        """Stop the alerting service"""
        self.running = False
        logger.info("Enterprise Alerting Service stopped")

    # ---------------------------------------------------------
    # RAISE ALERT
    # ---------------------------------------------------------
    def raise_alert(self, alert_type: str, context: Dict[str, Any]):
        """
        Raises an alert with the given type and context
        """
        alert = {
            "type": alert_type,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.alert_history.append(alert)
        logger.warning(f"[ALERT-{alert_type}] {context}")

    # ---------------------------------------------------------
    # ALERT CREATION
    # ---------------------------------------------------------
    def create_alert(self, level: str, category: str, message: str, metadata: Dict[str, Any] = None):
        """
        Creates and logs enterprise alert
        """

        alert = {
            "level": level,            # INFO / WARNING / CRITICAL
            "category": category,      # drift / retraining / runtime / rl / deployment
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        self.alert_history.append(alert)

        if level == "CRITICAL":
            logger.critical(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

        return alert

    # ---------------------------------------------------------
    # EVENT BUS ALERT HANDLER
    # ---------------------------------------------------------
    async def event_alert_handler(self, event: Dict[str, Any]):
        """
        Handles events from enterprise event bus
        """

        event_type = event.get("type")
        payload = event.get("payload", {})

        if event_type == "DATA_DRIFT_DETECTED":
            self.create_alert(
                "WARNING",
                "drift",
                "Data drift threshold exceeded",
                payload
            )

        elif event_type == "MODEL_DEPLOYED":
            self.create_alert(
                "INFO",
                "deployment",
                "New model promoted to production",
                payload
            )

        elif event_type == "RETRAINING_FAILED":
            self.create_alert(
                "CRITICAL",
                "training",
                "Model retraining failed",
                payload
            )

        elif event_type == "RL_INSTABILITY":
            self.create_alert(
                "WARNING",
                "rl",
                "RL agent instability detected",
                payload
            )

        elif event_type == "SYSTEM_RUNTIME_ERROR":
            self.create_alert(
                "CRITICAL",
                "runtime",
                "Runtime failure detected",
                payload
            )

    # ---------------------------------------------------------
    # SUBSCRIBE TO EVENT BUS
    # ---------------------------------------------------------
    def register_event_handlers(self):
        """
        Registers alert handlers into enterprise event bus
        """

        enterprise_event_bus.subscribe("DATA_DRIFT_DETECTED", self.event_alert_handler)
        enterprise_event_bus.subscribe("MODEL_DEPLOYED", self.event_alert_handler)
        enterprise_event_bus.subscribe("RETRAINING_FAILED", self.event_alert_handler)
        enterprise_event_bus.subscribe("RL_INSTABILITY", self.event_alert_handler)
        enterprise_event_bus.subscribe("SYSTEM_RUNTIME_ERROR", self.event_alert_handler)

        logger.info("Enterprise alerting event handlers registered")

    # ---------------------------------------------------------
    # ALERT HISTORY
    # ---------------------------------------------------------
    def get_recent_alerts(self, limit: int = 50):
        """
        Returns recent alert history
        """
        return self.alert_history[-limit:]

    # ---------------------------------------------------------
    # HEALTH STATUS
    # ---------------------------------------------------------
    def health_status(self):
        """
        Returns service health
        """
        return {
            "status": "OK",
            "total_alerts": len(self.alert_history)
        }


# Global instance
enterprise_alerting_service = EnterpriseAlertingService()
enterprise_alerting_service.register_event_handlers()
