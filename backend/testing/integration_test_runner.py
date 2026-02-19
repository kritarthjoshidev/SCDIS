"""
Integration Test Runner
Runs complete end-to-end system simulation to validate autonomous pipeline
"""

import logging
import random
from datetime import datetime
from typing import Dict, Any, List

from services.telemetry_service import TelemetryService
from ai_engine.decision_engine import DecisionEngine
from services.action_execution_service import ActionExecutionService
from services.data_drift_monitor import DataDriftMonitor
from ai_engine.retraining_engine import RetrainingEngine
from ml_pipeline.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class IntegrationTestRunner:
    """
    Executes full AI lifecycle simulation
    """

    def __init__(self):
        self.telemetry_service = TelemetryService()
        self.decision_engine = DecisionEngine()
        self.action_executor = ActionExecutionService()
        self.drift_monitor = DataDriftMonitor()
        self.retraining_engine = RetrainingEngine()
        self.model_registry = ModelRegistry()

        logger.info("Integration Test Runner initialized")

    # --------------------------------------------------------
    # GENERATE TEST DATA
    # --------------------------------------------------------
    def generate_test_telemetry(self, size: int = 100) -> List[Dict[str, Any]]:
        """
        Creates synthetic telemetry dataset
        """

        dataset = []

        for _ in range(size):
            dataset.append({
                "timestamp": datetime.utcnow().isoformat(),
                "energy_usage": random.uniform(50, 200),
                "occupancy": random.randint(0, 200),
                "temperature": random.uniform(18, 35),
                "device_load": random.uniform(0.1, 0.9)
            })

        return dataset

    # --------------------------------------------------------
    # RUN FULL PIPELINE
    # --------------------------------------------------------
    def run_full_pipeline_test(self) -> Dict[str, Any]:
        """
        Executes full decision-action-learning loop
        """

        logger.info("Starting integration pipeline test")

        # Step 1 — Generate telemetry
        telemetry_data = self.generate_test_telemetry()

        # Step 2 — Push telemetry
        self.telemetry_service.ingest_bulk_data(telemetry_data)

        # Step 3 — Decision generation
        decision = self.decision_engine.generate_decision()

        # Step 4 — Execute actions
        execution_result = self.action_executor.execute_actions(decision)

        # Step 5 — Drift check
        drift_result = self.drift_monitor.run_drift_check()

        # Step 6 — Optional retraining
        retraining_result = None
        if drift_result.get("retraining_triggered"):
            retraining_result = self.retraining_engine.run_retraining_pipeline()

        # Step 7 — Model performance snapshot
        performance = self.model_registry.get_latest_model_performance()

        result = {
            "decision_generated": decision is not None,
            "execution_status": execution_result,
            "drift_result": drift_result,
            "retraining": retraining_result,
            "model_performance": performance,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"Integration test completed: {result}")

        return result

    # --------------------------------------------------------
    # STRESS TEST
    # --------------------------------------------------------
    def stress_test(self, cycles: int = 10):
        """
        Runs repeated cycles for stability testing
        """

        results = []

        for i in range(cycles):
            logger.info(f"Running test cycle {i+1}")
            results.append(self.run_full_pipeline_test())

        return {
            "cycles": cycles,
            "results": results
        }

    # --------------------------------------------------------
    # HEALTH
    # --------------------------------------------------------
    def health_status(self):
        return {
            "status": "integration_test_runner_ready"
        }
