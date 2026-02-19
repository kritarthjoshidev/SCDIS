"""
Reinforcement Learning Engine
Handles autonomous decision learning and adaptive optimization
"""

import logging
import numpy as np
from datetime import datetime
from typing import Dict, Any

from core.config import settings
from ai_engine.reward_engine import RewardEngine
from simulation.environment import SimulationEnvironment

logger = logging.getLogger(__name__)


class RLEngine:
    """
    Reinforcement learning controller for autonomous optimization
    """

    def __init__(self):
        self.reward_engine = RewardEngine()
        self.environment = SimulationEnvironment()

        # simple Q-table (expandable to deep RL later)
        self.q_table = {}
        self.learning_rate = settings.RL_LEARNING_RATE
        self.discount_factor = settings.RL_DISCOUNT_FACTOR
        self.exploration_rate = settings.RL_EXPLORATION_RATE

        self.last_training_time = None

        logger.info("RL Engine initialized")

    # --------------------------------------------------
    # ACTION SELECTION
    # --------------------------------------------------
    def select_action(self, state: str):
        """
        epsilon-greedy policy
        """

        if np.random.rand() < self.exploration_rate:
            return self.environment.random_action()

        return self.q_table.get(state, {}).get("best_action",
                                              self.environment.random_action())

    # --------------------------------------------------
    # TRAIN STEP
    # --------------------------------------------------
    def train_step(self) -> Dict[str, Any]:
        """
        Executes one RL learning iteration
        """

        state = self.environment.get_state()

        action = self.select_action(state)

        next_state, system_metrics = self.environment.execute_action(action)

        reward = self.reward_engine.compute_reward(system_metrics)

        self.update_q_table(state, action, reward, next_state)

        self.last_training_time = datetime.utcnow()

        return {
            "state": state,
            "action": action,
            "reward": reward,
            "timestamp": self.last_training_time.isoformat()
        }

    # --------------------------------------------------
    # Q TABLE UPDATE
    # --------------------------------------------------
    def update_q_table(self, state, action, reward, next_state):

        if state not in self.q_table:
            self.q_table[state] = {"value": 0, "best_action": action}

        next_max = self.q_table.get(next_state, {}).get("value", 0)

        current_value = self.q_table[state]["value"]

        updated_value = current_value + self.learning_rate * (
            reward + self.discount_factor * next_max - current_value
        )

        self.q_table[state]["value"] = updated_value
        self.q_table[state]["best_action"] = action

    # --------------------------------------------------
    # HEALTH STATUS
    # --------------------------------------------------
    def health_status(self):
        return {
            "status": "OK",
            "q_table_size": len(self.q_table),
            "last_training_time": self.last_training_time
        }
