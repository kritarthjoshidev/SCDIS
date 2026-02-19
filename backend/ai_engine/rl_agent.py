"""
Reinforcement Learning Agent
Autonomous Decision Intelligence Core

Capabilities:
- Policy learning
- Q-learning decision selection
- Experience replay
- Reward-driven adaptation
- Model persistence
- Online learning
"""

import os
import json
import random
import logging
import numpy as np
from datetime import datetime
from typing import Dict, Any, List

from core.config import settings

logger = logging.getLogger(__name__)


class RLAgent:

    def __init__(self):

        self.state_size = settings.RL_STATE_SIZE
        self.action_size = settings.RL_ACTION_SIZE

        self.learning_rate = settings.RL_LEARNING_RATE
        self.discount_factor = settings.RL_DISCOUNT_FACTOR
        self.epsilon = settings.RL_EPSILON
        self.epsilon_decay = settings.RL_EPSILON_DECAY
        self.epsilon_min = settings.RL_EPSILON_MIN

        self.memory: List = []
        self.q_table = self.initialize_q_table()

        logger.info("RL Agent initialized")

    # ============================================================
    # Q TABLE INITIALIZATION
    # ============================================================
    def initialize_q_table(self):

        logger.info("Initializing Q-table")

        return {}

    # ============================================================
    # STATE HASHING
    # ============================================================
    def state_key(self, state_vector):

        return tuple(np.round(state_vector, 2))

    # ============================================================
    # ACTION SELECTION (EPSILON GREEDY)
    # ============================================================
    def choose_action(self, state_vector):

        state_key = self.state_key(state_vector)

        if random.random() < self.epsilon:
            action = random.randint(0, self.action_size - 1)
            logger.debug("Exploration action chosen: %d", action)
            return action

        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)

        action = int(np.argmax(self.q_table[state_key]))
        logger.debug("Exploitation action chosen: %d", action)

        return action

    # ============================================================
    # EXPERIENCE STORAGE
    # ============================================================
    def remember(self, state, action, reward, next_state, done):

        self.memory.append((state, action, reward, next_state, done))

        if len(self.memory) > settings.RL_MEMORY_LIMIT:
            self.memory.pop(0)

    # ============================================================
    # LEARNING STEP
    # ============================================================
    def learn(self):

        if not self.memory:
            return

        batch = random.sample(
            self.memory,
            min(len(self.memory), settings.RL_BATCH_SIZE)
        )

        for state, action, reward, next_state, done in batch:

            state_key = self.state_key(state)
            next_state_key = self.state_key(next_state)

            if state_key not in self.q_table:
                self.q_table[state_key] = np.zeros(self.action_size)

            if next_state_key not in self.q_table:
                self.q_table[next_state_key] = np.zeros(self.action_size)

            target = reward

            if not done:
                target += self.discount_factor * np.max(
                    self.q_table[next_state_key]
                )

            self.q_table[state_key][action] += self.learning_rate * (
                target - self.q_table[state_key][action]
            )

        self.decay_epsilon()

    # ============================================================
    # EPSILON DECAY
    # ============================================================
    def decay_epsilon(self):

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # ============================================================
    # MODEL SAVE
    # ============================================================
    def save(self):

        os.makedirs(settings.RL_MODEL_DIR, exist_ok=True)

        path = os.path.join(settings.RL_MODEL_DIR, "rl_qtable.json")

        serializable = {
            str(k): v.tolist()
            for k, v in self.q_table.items()
        }

        with open(path, "w") as f:
            json.dump(serializable, f)

        logger.info("RL model saved")

    # ============================================================
    # MODEL LOAD
    # ============================================================
    def load(self):

        path = os.path.join(settings.RL_MODEL_DIR, "rl_qtable.json")

        if not os.path.exists(path):
            logger.warning("No RL model found")
            return

        with open(path, "r") as f:
            data = json.load(f)

        self.q_table = {
            tuple(map(float, k.strip("()").split(","))): np.array(v)
            for k, v in data.items()
        }

        logger.info("RL model loaded")

    # ============================================================
    # TRAIN STEP (ONLINE)
    # ============================================================
    def train_step(self, state, action, reward, next_state, done):

        self.remember(state, action, reward, next_state, done)
        self.learn()

    # ============================================================
    # DECISION API OUTPUT
    # ============================================================
    def decision(self, state_vector):

        action = self.choose_action(state_vector)

        return {
            "action": int(action),
            "timestamp": datetime.utcnow().isoformat()
        }

    # ============================================================
    # DIAGNOSTICS
    # ============================================================
    def stats(self):

        return {
            "memory": len(self.memory),
            "epsilon": self.epsilon,
            "states_learned": len(self.q_table)
        }
