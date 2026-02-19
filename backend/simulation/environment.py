"""
Simulation Environment
Simulates campus infrastructure environment for RL decision learning
"""

import random
import logging
from typing import Tuple, Dict

logger = logging.getLogger(__name__)


class SimulationEnvironment:
    """
    Simulated system environment for reinforcement learning
    """

    def __init__(self):
        self.current_state = "normal"

        self.actions = [
            "reduce_lighting",
            "optimize_hvac",
            "shift_load",
            "activate_backup",
            "no_action"
        ]

        logger.info("Simulation Environment initialized")

    # --------------------------------------------------
    # GET CURRENT STATE
    # --------------------------------------------------
    def get_state(self) -> str:
        """
        Returns simulated system state
        """

        self.current_state = random.choice([
            "low_load",
            "normal",
            "high_load",
            "peak_load"
        ])

        return self.current_state

    # --------------------------------------------------
    # RANDOM ACTION
    # --------------------------------------------------
    def random_action(self):
        return random.choice(self.actions)

    # --------------------------------------------------
    # EXECUTE ACTION
    # --------------------------------------------------
    def execute_action(self, action: str) -> Tuple[str, Dict]:
        """
        Executes simulated action and returns next_state + metrics
        """

        energy_usage = random.uniform(100, 500)

        if action == "reduce_lighting":
            energy_usage *= 0.95
        elif action == "optimize_hvac":
            energy_usage *= 0.90
        elif action == "shift_load":
            energy_usage *= 0.92
        elif action == "activate_backup":
            energy_usage *= 1.05

        next_state = self.get_state()

        system_metrics = {
            "energy_usage": energy_usage,
            "comfort_score": random.uniform(0.7, 1.0),
            "system_stability": random.uniform(0.8, 1.0)
        }

        return next_state, system_metrics
