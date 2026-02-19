"""
Full System Integration Test Runner
Validates entire autonomous AI backend pipeline
"""

import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.decision_engine import DecisionEngine
from ai_engine.rl_engine import RLEngine
from ai_engine.retraining_engine import RetrainingEngine
from services.data_drift_monitor import DataDriftMonitor
from services.optimization_service import OptimizationService
from services.action_execution_service import ActionExecutionService
from ml_pipeline.model_registry import ModelRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("integration_test")


def run_full_integration_test():
    logger.info("========== FULL SYSTEM INTEGRATION TEST STARTED ==========")

    results = {}

    try:
        # --------------------------------------------------
        # MODEL REGISTRY
        # --------------------------------------------------
        registry = ModelRegistry()
        results["model_registry"] = registry.health_status()

        # --------------------------------------------------
        # DECISION ENGINE
        # --------------------------------------------------
        decision_engine = DecisionEngine()
        decision = decision_engine.generate_decision()
        results["decision_engine"] = decision

        # --------------------------------------------------
        # RL ENGINE STEP
        # --------------------------------------------------
        rl_engine = RLEngine()
        rl_result = rl_engine.train_step()
        results["rl_engine"] = rl_result

        # --------------------------------------------------
        # OPTIMIZATION SERVICE
        # --------------------------------------------------
        optimizer = OptimizationService()
        opt_result = optimizer.optimize_energy({"energy_usage": 120})
        results["optimization"] = opt_result

        # --------------------------------------------------
        # DRIFT MONITOR
        # --------------------------------------------------
        drift_monitor = DataDriftMonitor()
        drift_result = drift_monitor.run_drift_check()
        results["drift_monitor"] = drift_result

        # --------------------------------------------------
        # RETRAINING ENGINE
        # --------------------------------------------------
        retraining_engine = RetrainingEngine()
        retrain_result = retraining_engine.pipeline_status()
        results["retraining_engine"] = retrain_result

        # --------------------------------------------------
        # ACTION EXECUTION
        # --------------------------------------------------
        executor = ActionExecutionService()
        action_exec = executor.execute_action({
            "type": "load_reduction",
            "value": 5
        })
        results["action_execution"] = action_exec

        logger.info("========== FULL SYSTEM TEST PASSED ==========")

    except Exception as e:
        logger.exception("Integration test failed")
        results["error"] = str(e)

    results["timestamp"] = datetime.utcnow().isoformat()

    return results


if __name__ == "__main__":
    output = run_full_integration_test()
    print("\nTEST RESULTS:\n")
    print(output)
