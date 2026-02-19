"""
Simulation Environment (Digital Twin)
Provides virtual campus energy environment for RL training
"""

import logging
import random
import numpy as np
from typing import Dict, Any

from core.config import settings

logger = logging.getLogger(__name__)


class CampusSimulationEnvironment:
    """
    Simulated environment representing campus infrastructure
    Used by RL engine for policy learning
    """

    def __init__(self):
        self.state = None
        self.step_count = 0
        self.max_steps = settings.RL_MAX_EPISODE_STEPS

        logger.info("Campus Simulation Environment initialized")

    # -------------------------------------------------------
    # RESET ENVIRONMENT
    # -------------------------------------------------------
    def reset(self) -> Dict[str, float]:
        """
        Resets environment to starting state
        """

        self.step_count = 0

        self.state = {
            "energy_usage": random.uniform(80, 150),
            "occupancy": random.uniform(50, 300),
            "temperature": random.uniform(20, 32),
            "device_load": random.uniform(0.2, 0.9)
        }

        return self.state

    # -------------------------------------------------------
    # APPLY ACTION
    # -------------------------------------------------------
    def step(self, action: Dict[str, Any]):
        """
        Applies action and moves environment forward
        """

        self.step_count += 1

        reduction = action.get("load_reduction", 0)

        # Simulated energy transition
        noise = np.random.normal(0, 2)

        self.state["energy_usage"] = max(
            10,
            self.state["energy_usage"] * (1 - reduction / 100) + noise
        )

        self.state["temperature"] += random.uniform(-0.3, 0.3)
        self.state["device_load"] = max(0.1, min(1.0,
                                                self.state["device_load"] + random.uniform(-0.05, 0.05)))

        reward = self.calculate_reward()

        done = self.step_count >= self.max_steps

        return self.state, reward, done

    # -------------------------------------------------------
    # REWARD FUNCTION
    # -------------------------------------------------------
    def calculate_reward(self):
        """
        Reward encourages lower energy consumption
        """

        baseline = 150
        reward = (baseline - self.state["energy_usage"]) / baseline

        comfort_penalty = abs(self.state["temperature"] - 24) * 0.02

        return float(reward - comfort_penalty)

    # -------------------------------------------------------
    # STATE SPACE
    # -------------------------------------------------------
    def observation_space(self):
        return 4

    def action_space(self):
        return 1

    # -------------------------------------------------------
    # HEALTH
    # -------------------------------------------------------
    def health_status(self):
        return {
            "status": "simulation_environment_ready",
            "current_step": self.step_count
        }
