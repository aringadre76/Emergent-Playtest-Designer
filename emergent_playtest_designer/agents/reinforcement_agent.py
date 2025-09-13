"""Reinforcement learning agent for game exploration."""

import numpy as np
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from loguru import logger
from ..core.types import GameState, Action, AgentConfig


@dataclass
class Experience:
    """Represents a single experience for RL."""
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool


class ReplayBuffer:
    """Experience replay buffer for RL agent."""
    
    def __init__(self, capacity: int = 10000):
        """Initialize replay buffer."""
        self.capacity = capacity
        self.buffer: List[Experience] = []
        self.position = 0
    
    def push(self, experience: Experience) -> None:
        """Add experience to buffer."""
        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
        else:
            self.buffer[self.position] = experience
            self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Sample batch of experiences."""
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def __len__(self) -> int:
        """Get buffer size."""
        return len(self.buffer)


class ReinforcementAgent:
    """Reinforcement learning agent using DQN."""
    
    def __init__(self, config: AgentConfig):
        """Initialize RL agent."""
        self.config = config
        self.state_size = 20
        self.action_size = 8
        self.learning_rate = config.learning_rate
        self.exploration_rate = config.exploration_rate
        self.exploration_decay = 0.995
        self.exploration_min = 0.01
        self.memory = ReplayBuffer(config.memory_size)
        self.batch_size = config.batch_size
        self.target_update_frequency = config.target_update_frequency
        
        self.q_network = self._build_network()
        self.target_network = self._build_network()
        self.update_target_network()
        
        self.step_count = 0
        self.current_state: Optional[np.ndarray] = None
        self.current_episode = []
        
    def select_action(self, state: GameState) -> Action:
        """Select action using epsilon-greedy policy."""
        state_vector = self._state_to_vector(state)
        
        if random.random() < self.exploration_rate:
            action_index = random.randint(0, self.action_size - 1)
        else:
            q_values = self.q_network.predict(state_vector.reshape(1, -1))
            action_index = np.argmax(q_values[0])
        
        return self._action_index_to_action(action_index, state)
    
    def update(self, state: GameState, action: Action, reward: float, next_state: GameState) -> None:
        """Update agent with new experience."""
        state_vector = self._state_to_vector(state)
        next_state_vector = self._state_to_vector(next_state)
        action_index = self._action_to_index(action)
        
        experience = Experience(
            state=state_vector,
            action=action_index,
            reward=reward,
            next_state=next_state_vector,
            done=False
        )
        
        self.memory.push(experience)
        self.current_episode.append(experience)
        
        if len(self.memory) >= self.batch_size:
            self._train()
        
        self.step_count += 1
        
        if self.step_count % self.target_update_frequency == 0:
            self.update_target_network()
        
        self.exploration_rate = max(
            self.exploration_min,
            self.exploration_rate * self.exploration_decay
        )
    
    def _build_network(self) -> Any:
        """Build neural network (simplified version)."""
        class SimpleNetwork:
            def __init__(self, input_size: int, output_size: int, learning_rate: float):
                self.weights = np.random.randn(input_size, output_size) * 0.1
                self.bias = np.zeros(output_size)
                self.learning_rate = learning_rate
            
            def predict(self, x: np.ndarray) -> np.ndarray:
                return np.dot(x, self.weights) + self.bias
            
            def fit(self, x: np.ndarray, y: np.ndarray) -> None:
                predictions = self.predict(x)
                error = y - predictions
                
                self.weights += self.learning_rate * np.dot(x.T, error)
                self.bias += self.learning_rate * np.mean(error, axis=0)
        
        return SimpleNetwork(self.state_size, self.action_size, self.learning_rate)
    
    def _state_to_vector(self, state: GameState) -> np.ndarray:
        """Convert game state to vector."""
        vector = np.zeros(self.state_size)
        
        vector[0:3] = state.player_position
        vector[3] = state.player_health
        vector[4] = sum(state.player_resources.values())
        
        if "velocity" in state.physics_state:
            velocity = state.physics_state["velocity"]
            vector[5:8] = velocity
        
        if "acceleration" in state.physics_state:
            acceleration = state.physics_state["acceleration"]
            vector[8:11] = acceleration
        
        vector[11:15] = list(state.player_resources.values())[:4]
        
        if state.game_objects:
            vector[15:20] = list(state.game_objects.values())[:5]
        
        return vector
    
    def _action_to_index(self, action: Action) -> int:
        """Convert action to index."""
        action_mapping = {
            "key_press": {"w": 0, "a": 1, "s": 2, "d": 3},
            "key_release": {"w": 0, "a": 1, "s": 2, "d": 3},
            "mouse_click": {"left": 4, "right": 5},
            "mouse_move": {"move": 6},
            "joystick_input": {"input": 7}
        }
        
        action_type = action.action_type
        if action_type in action_mapping:
            key = action.parameters.get("key", "w")
            if key in action_mapping[action_type]:
                return action_mapping[action_type][key]
        
        return 0
    
    def _action_index_to_action(self, action_index: int, state: GameState) -> Action:
        """Convert action index to action."""
        action_mapping = [
            ("key_press", {"key": "w"}),
            ("key_press", {"key": "a"}),
            ("key_press", {"key": "s"}),
            ("key_press", {"key": "d"}),
            ("mouse_click", {"button": "left", "x": 960, "y": 540}),
            ("mouse_click", {"button": "right", "x": 960, "y": 540}),
            ("mouse_move", {"x": 960, "y": 540, "delta_x": 0, "delta_y": 0}),
            ("joystick_input", {"axis": "horizontal", "value": 0.0})
        ]
        
        action_type, parameters = action_mapping[action_index]
        
        return Action(
            action_type=action_type,
            parameters=parameters,
            timestamp=state.timestamp,
            duration=0.1
        )
    
    def _train(self) -> None:
        """Train the network on a batch of experiences."""
        batch = self.memory.sample(self.batch_size)
        
        states = np.array([exp.state for exp in batch])
        actions = np.array([exp.action for exp in batch])
        rewards = np.array([exp.reward for exp in batch])
        next_states = np.array([exp.next_state for exp in batch])
        
        current_q_values = self.q_network.predict(states)
        next_q_values = self.target_network.predict(next_states)
        
        target_q_values = current_q_values.copy()
        
        for i in range(len(batch)):
            target_q_values[i][actions[i]] = rewards[i] + 0.95 * np.max(next_q_values[i])
        
        self.q_network.fit(states, target_q_values)
    
    def update_target_network(self) -> None:
        """Update target network with current network weights."""
        self.target_network.weights = self.q_network.weights.copy()
        self.target_network.bias = self.q_network.bias.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "step_count": self.step_count,
            "exploration_rate": self.exploration_rate,
            "memory_size": len(self.memory),
            "learning_rate": self.learning_rate,
            "episode_count": len(self.current_episode),
            "avg_reward": np.mean([exp.reward for exp in self.current_episode]) if self.current_episode else 0.0
        }
    
    def reset(self) -> None:
        """Reset agent state."""
        self.current_state = None
        self.current_episode.clear()
        self.step_count = 0
        self.exploration_rate = self.config.exploration_rate
