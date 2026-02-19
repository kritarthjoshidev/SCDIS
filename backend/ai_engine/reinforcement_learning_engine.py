"""
Reinforcement Learning Engine
Self-learning decision optimization for Smart Campus Decision Intelligence System
"""

import numpy as np
import logging
import os
import joblib
from datetime import datetime
from core.config import settings

logger = logging.getLogger(__name__)


class ReinforcementLearningEngine:
    """
    Q-Learning based adaptive optimization engine.
    Learns optimal reduction decisions based on system load + outcomes.
    """

    def __init__(self):

        self.model_path = settings.RL_MODEL_PATH

        self.state_bins = 10
        self.action_space = np.linspace(
            settings.MIN_REDUCTION_PERCENT,
            settings.MAX_REDUCTION_PERCENT,
            10
        )

        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_rate = 0.1

        self.q_table = self._load_or_initialize()

    # =========================================================
    # MODEL LOAD
    # =========================================================
    def _load_or_initialize(self):

        if os.path.exists(self.model_path):
            logger.info("RL model loaded")
            return joblib.load(self.model_path)

        logger.warning("RL model not found — creating new Q-table")
        q_table = np.zeros((self.state_bins, len(self.action_space)))
        joblib.dump(q_table, self.model_path)
        return q_table

    # =========================================================
    # STATE DISCRETIZATION
    # =========================================================
    def _get_state(self, load_value: float) -> int:

        state = int(load_value * self.state_bins)
        state = max(0, min(self.state_bins - 1, state))
        return state

    # =========================================================
    # ACTION SELECTION
    # =========================================================
    def choose_action(self, load_value: float):

        state = self._get_state(load_value)

        if np.random.rand() < self.exploration_rate:
            action_idx = np.random.randint(len(self.action_space))
        else:
            action_idx = np.argmax(self.q_table[state])

        return action_idx, self.action_space[action_idx]

    # =========================================================
    # LEARNING UPDATE
    # =========================================================
    def update(self, prev_load, action_idx, reward, new_load):

        state = self._get_state(prev_load)
        new_state = self._get_state(new_load)

        best_future = np.max(self.q_table[new_state])

        self.q_table[state, action_idx] += self.learning_rate * (
            reward + self.discount_factor * best_future -
            self.q_table[state, action_idx]
        )

        self._save()

    # =========================================================
    # SAVE MODEL
    # =========================================================
    def _save(self):
        joblib.dump(self.q_table, self.model_path)

    # =========================================================
    # REWARD FUNCTION
    # =========================================================
    def compute_reward(self, energy_before, energy_after):

        reduction = energy_before - energy_after

        if reduction > 0:
            return reduction
        return -abs(reduction)

    # =========================================================
    # FULL DECISION PIPELINE
    # =========================================================
    def recommend(self, current_load):

        action_idx, reduction = self.choose_action(current_load)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_reduction_percent": float(reduction),
            "action_index": int(action_idx)
        }


# global singleton
rl_engine = ReinforcementLearningEngine()
