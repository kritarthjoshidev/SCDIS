import random
import time
import logging
from datetime import datetime
from typing import Dict, List

from ai_engine.orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)


class DemoModeEngine:
    """
    Generates synthetic campus telemetry and runs
    continuous AI pipeline simulation for demos.
    """

    def __init__(self):

        self.orchestrator = AIOrchestrator()
        self.running = False
        self.history: List[Dict] = []

    # =====================================================
    # Synthetic telemetry generator
    # =====================================================
    def generate_telemetry(self):

        telemetry = {
            "building_id": random.randint(1, 5),
            "temperature": round(random.uniform(22, 38), 2),
            "humidity": round(random.uniform(40, 75), 2),
            "occupancy": random.randint(20, 300),
            "day_of_week": random.randint(0, 6),
            "hour": random.randint(0, 23)
        }

        return telemetry

    # =====================================================
    # Load spike scenario
    # =====================================================
    def generate_load_spike(self):

        telemetry = self.generate_telemetry()
        telemetry["occupancy"] = random.randint(350, 600)
        telemetry["temperature"] = random.uniform(32, 40)

        return telemetry

    # =====================================================
    # Anomaly injection
    # =====================================================
    def generate_anomaly_event(self):

        telemetry = self.generate_telemetry()
        telemetry["temperature"] = random.uniform(45, 55)
        telemetry["humidity"] = random.uniform(85, 95)

        return telemetry

    # =====================================================
    # Run single simulation step
    # =====================================================
    def run_step(self, scenario="normal"):

        if scenario == "spike":
            telemetry = self.generate_load_spike()
        elif scenario == "anomaly":
            telemetry = self.generate_anomaly_event()
        else:
            telemetry = self.generate_telemetry()

        result = self.orchestrator.run_pipeline(telemetry)

        entry = {
            "timestamp": datetime.utcnow(),
            "scenario": scenario,
            "telemetry": telemetry,
            "result": result
        }

        self.history.append(entry)

        logger.info("Demo simulation step executed")

        return entry

    # =====================================================
    # Continuous demo loop
    # =====================================================
    def start_demo(self, interval_seconds=5):

        self.running = True

        logger.info("Demo mode started")

        while self.running:

            scenario_choice = random.choice(
                ["normal", "normal", "normal", "spike", "anomaly"]
            )

            self.run_step(scenario_choice)

            time.sleep(interval_seconds)

    # =====================================================
    # Stop demo
    # =====================================================
    def stop_demo(self):

        self.running = False
        logger.info("Demo mode stopped")

    # =====================================================
    # Get recent demo outputs
    # =====================================================
    def get_recent_results(self, limit=10):

        return self.history[-limit:]
