"""
Self Learning Loop
Continuously improves AI decision policy using
feedback from real-world execution.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List
import numpy as np

from ai_engine.rl_engine import RLEngine
from services.telemetry_service import TelemetryService
from core.config import settings

logger = logging.getLogger(__name__)


class SelfLearningLoop:
    """
    Autonomous feedback-driven reinforcement learning system
    """

    def __init__(self):

        self.rl_engine = RLEngine()
        self.telemetry_service = TelemetryService()

        # decision history
        self.decision_history: List[Dict[str, Any]] = []

        # performance tracking
        self.performance_log: List[Dict[str, Any]] = []

        logger.info("Self Learning Loop initialized")

    # ==========================================================
    # RECORD DECISION
    # ==========================================================
    def record_decision(self, decision: Dict[str, Any], state: Dict[str, Any]):

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "state": state,
            "decision": decision,
            "outcome": None,
            "reward": None
        }

        self.decision_history.append(record)

        logger.info("Decision recorded for learning")

    # ==========================================================
    # OBSERVE OUTCOME
    # ==========================================================
    def observe_outcome(self):

        telemetry = self.telemetry_service.get_latest_telemetry()

        if not self.decision_history:
            return

        latest_record = self.decision_history[-1]
        latest_record["outcome"] = telemetry

        logger.info("Outcome observation updated")

    # ==========================================================
    # REWARD FUNCTION
    # ==========================================================
    def compute_reward(self, outcome: Dict[str, Any]) -> float:

        reward = 0

        # energy efficiency reward
        energy_saved = outcome.get("energy_saved", 0)
        reward += energy_saved * settings.ENERGY_REWARD_WEIGHT

        # penalty for overheating
        if outcome.get("temperature", 25) > settings.MAX_SAFE_TEMP:
            reward -= settings.OVERHEAT_PENALTY

        # penalty for overload
        if outcome.get("energy_load", 0) > settings.MAX_ALLOWED_LOAD:
            reward -= settings.OVERLOAD_PENALTY

        return reward

    # ==========================================================
    # UPDATE RL MODEL
    # ==========================================================
    def update_rl_model(self):

        if not self.decision_history:
            return

        latest_record = self.decision_history[-1]

        outcome = latest_record.get("outcome")
        if outcome is None:
            return

        reward = self.compute_reward(outcome)

        latest_record["reward"] = reward

        state = latest_record["state"]
        action = latest_record["decision"]

        self.rl_engine.learn(state, action, reward)

        logger.info("RL policy updated")

    # ==========================================================
    # PERFORMANCE TRACKING
    # ==========================================================
    def log_performance(self):

        if not self.decision_history:
            return

        recent_rewards = [
            r["reward"] for r in self.decision_history[-50:]
            if r["reward"] is not None
        ]

        if not recent_rewards:
            return

        avg_reward = np.mean(recent_rewards)

        performance_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "avg_reward": float(avg_reward),
            "decisions_count": len(self.decision_history)
        }

        self.performance_log.append(performance_entry)

        logger.info(f"Performance logged: avg_reward={avg_reward}")

    # ==========================================================
    # POLICY DRIFT DETECTION
    # ==========================================================
    def detect_policy_drift(self):

        if len(self.performance_log) < 5:
            return False

        last_rewards = [p["avg_reward"] for p in self.performance_log[-5:]]

        if last_rewards[-1] < np.mean(last_rewards[:-1]) * 0.8:
            logger.warning("Policy performance drift detected")
            return True

        return False

    # ==========================================================
    # FULL LEARNING STEP
    # ==========================================================
    def learning_step(self):

        self.observe_outcome()
        self.update_rl_model()
        self.log_performance()

        if self.detect_policy_drift():
            logger.warning("Retraining recommended due to drift")

    # ==========================================================
    # CONTINUOUS LEARNING LOOP
    # ==========================================================
    def start_learning_loop(self):

        logger.info("Autonomous self-learning loop started")

        while True:

            try:
                self.learning_step()
                time.sleep(settings.SELF_LEARNING_INTERVAL)

            except Exception as e:
                logger.error(f"Learning loop error: {str(e)}")
