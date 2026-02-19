"""
Enterprise Event Bus
Distributed autonomous AI messaging core
"""

import logging
import threading
import queue
import time
from datetime import datetime
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)


class EnterpriseEventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        self.events_processed = 0

    # --------------------------------------------------
    # LIFECYCLE
    # --------------------------------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(
            target=self._event_loop,
            daemon=True
        )
        self.worker_thread.start()

        logger.info("Enterprise Event Bus started")

    def stop(self):
        self.running = False
        logger.info("Enterprise Event Bus stopped")

    # --------------------------------------------------
    # SUBSCRIBE
    # --------------------------------------------------
    def subscribe(self, topic: str, handler: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []

        self.subscribers[topic].append(handler)

    # --------------------------------------------------
    # PUBLISH
    # --------------------------------------------------
    def publish(self, topic: str, payload: Dict[str, Any]):
        event = {
            "topic": topic,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.event_queue.put(event)
        logger.info(f"Publishing event: {topic}")

    # --------------------------------------------------
    # EVENT LOOP
    # --------------------------------------------------
    def _event_loop(self):
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                topic = event["topic"]

                if topic in self.subscribers:
                    for handler in self.subscribers[topic]:
                        try:
                            handler(event["payload"])
                        except Exception:
                            logger.exception("Subscriber handler failure")

                self.events_processed += 1

            except queue.Empty:
                continue
            except Exception:
                logger.exception("Event bus failure")
                time.sleep(1)

    # --------------------------------------------------
    # HEALTH
    # --------------------------------------------------
    def health_status(self):
        return {
            "status": "running" if self.running else "stopped",
            "subscriber_count": sum(len(v) for v in self.subscribers.values()),
            "events_processed": self.events_processed,
            "timestamp": datetime.utcnow().isoformat()
        }


# GLOBAL SINGLETON
enterprise_event_bus = EnterpriseEventBus()
