"""Unity ML-Agents environment wrapper for the Emergent Playtest Designer."""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
from mlagents_envs.side_channel.side_channel import SideChannel, IncomingMessage, OutgoingMessage
import uuid
from loguru import logger
from ..core.types import GameState, Action
from ..core.config import UnityConfig


class PlaytestSideChannel(SideChannel):
    """Custom side channel for sending commands and receiving game state data."""
    
    def __init__(self):
        super().__init__(uuid.uuid4())
        self.received_messages: List[Dict[str, Any]] = []
        
    def on_message_received(self, msg: IncomingMessage) -> None:
        """Handle messages from Unity."""
        try:
            message_type = msg.read_string()
            
            if message_type == "EXPLOIT_DETECTED":
                exploit_data = {
                    "type": msg.read_string(),
                    "severity": msg.read_string(),
                    "position": [msg.read_float32() for _ in range(3)],
                    "description": msg.read_string(),
                    "frame": msg.read_int32()
                }
                self.received_messages.append({
                    "type": "exploit",
                    "data": exploit_data
                })
                logger.warning(f"Exploit detected: {exploit_data}")
                
            elif message_type == "PERFORMANCE_DATA":
                perf_data = {
                    "fps": msg.read_float32(),
                    "memory_mb": msg.read_float32(),
                    "cpu_usage": msg.read_float32(),
                    "frame": msg.read_int32()
                }
                self.received_messages.append({
                    "type": "performance",
                    "data": perf_data
                })
                
            elif message_type == "GAME_EVENT":
                event_data = {
                    "event_name": msg.read_string(),
                    "parameters": msg.read_string(),  # JSON string
                    "timestamp": msg.read_float32()
                }
                self.received_messages.append({
                    "type": "game_event", 
                    "data": event_data
                })
                
        except Exception as e:
            logger.error(f"Error processing message from Unity: {e}")
    
    def send_command(self, command: str, parameters: Dict[str, Any] = None):
        """Send command to Unity."""
        msg = OutgoingMessage()
        msg.write_string(command)
        
        if parameters:
            import json
            msg.write_string(json.dumps(parameters))
        else:
            msg.write_string("{}")
            
        self.queue_message_to_send(msg)
        
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all received messages and clear the queue."""
        messages = self.received_messages.copy()
        self.received_messages.clear()
        return messages


class MLAgentsPlaytestEnvironment:
    """ML-Agents environment wrapper for automated playtesting."""
    
    def __init__(self, config: UnityConfig):
        """Initialize the ML-Agents environment."""
        self.config = config
        self.env: Optional[UnityEnvironment] = None
        self.side_channel = PlaytestSideChannel()
        self.behavior_names: List[str] = []
        self.current_step = 0
        self.max_steps = config.max_episode_steps
        self.is_running = False
        
        # Game state tracking
        self.last_observation = None
        self.last_reward = 0.0
        self.episode_rewards = []
        self.exploit_count = 0
        
    def start_environment(self, unity_executable_path: str = None) -> bool:
        """Start the Unity ML-Agents environment."""
        try:
            # Use executable path or default to built game
            env_path = unity_executable_path or self.config.executable_path
            
            self.env = UnityEnvironment(
                file_name=env_path,
                no_graphics=self.config.headless_mode,
                side_channels=[self.side_channel],
                timeout_wait=60,
                log_folder="./unity_logs"
            )
            
            # Reset environment to get behavior names
            self.env.reset()
            self.behavior_names = list(self.env.behavior_specs.keys())
            
            if not self.behavior_names:
                logger.error("No behaviors found in Unity environment")
                return False
                
            logger.info(f"ML-Agents environment started with behaviors: {self.behavior_names}")
            self.is_running = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to start ML-Agents environment: {e}")
            return False
    
    def stop_environment(self) -> bool:
        """Stop the Unity ML-Agents environment."""
        try:
            if self.env:
                self.env.close()
                self.env = None
            self.is_running = False
            logger.info("ML-Agents environment stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping ML-Agents environment: {e}")
            return False
    
    def reset_episode(self) -> Dict[str, np.ndarray]:
        """Reset the environment for a new episode."""
        if not self.env:
            raise RuntimeError("Environment not started")
            
        self.env.reset()
        self.current_step = 0
        self.episode_rewards = []
        
        # Get initial observations
        decision_steps, terminal_steps = self.env.get_steps(self.behavior_names[0])
        
        if len(decision_steps) > 0:
            self.last_observation = decision_steps.obs[0]
            return {"observation": self.last_observation}
        else:
            logger.warning("No agents available after reset")
            return {"observation": np.zeros((1,))}  # Placeholder
    
    def step(self, actions: Dict[str, np.ndarray]) -> Tuple[Dict[str, np.ndarray], float, bool, Dict[str, Any]]:
        """Take a step in the environment."""
        if not self.env or not self.is_running:
            raise RuntimeError("Environment not started")
            
        behavior_name = self.behavior_names[0]
        
        # Convert actions to ActionTuple
        if behavior_name in actions:
            action_array = actions[behavior_name]
            if len(action_array.shape) == 1:
                action_array = action_array.reshape(1, -1)
            action_tuple = ActionTuple(continuous=action_array)
        else:
            # Default action if no action provided
            action_tuple = ActionTuple(continuous=np.zeros((1, self._get_action_size())))
        
        # Set actions
        self.env.set_actions(behavior_name, action_tuple)
        
        # Step the environment
        self.env.step()
        
        # Get results
        decision_steps, terminal_steps = self.env.get_steps(behavior_name)
        
        # Process results
        done = False
        reward = 0.0
        info = {}
        
        if len(decision_steps) > 0:
            self.last_observation = decision_steps.obs[0]
            reward = decision_steps.reward[0] if len(decision_steps.reward) > 0 else 0.0
        elif len(terminal_steps) > 0:
            self.last_observation = terminal_steps.obs[0]
            reward = terminal_steps.reward[0] if len(terminal_steps.reward) > 0 else 0.0
            done = True
            
        # Check for episode termination
        self.current_step += 1
        if self.current_step >= self.max_steps:
            done = True
            
        self.last_reward = reward
        self.episode_rewards.append(reward)
        
        # Process side channel messages
        messages = self.side_channel.get_messages()
        exploits_this_step = []
        
        for msg in messages:
            if msg["type"] == "exploit":
                exploits_this_step.append(msg["data"])
                self.exploit_count += 1
            elif msg["type"] == "performance":
                info["performance"] = msg["data"]
            elif msg["type"] == "game_event":
                info.setdefault("game_events", []).append(msg["data"])
        
        if exploits_this_step:
            info["exploits"] = exploits_this_step
            
        observation = {"observation": self.last_observation}
        
        return observation, reward, done, info
    
    def send_command(self, command: str, parameters: Dict[str, Any] = None):
        """Send command to Unity via side channel."""
        self.side_channel.send_command(command, parameters)
        
    def get_observation_space(self) -> Dict[str, int]:
        """Get observation space information."""
        if not self.env or not self.behavior_names:
            return {}
            
        behavior_name = self.behavior_names[0]
        spec = self.env.behavior_specs[behavior_name]
        
        obs_shapes = {}
        for i, obs_spec in enumerate(spec.observation_specs):
            obs_shapes[f"obs_{i}"] = obs_spec.shape
            
        return obs_shapes
    
    def get_action_space(self) -> Dict[str, int]:
        """Get action space information."""
        if not self.env or not self.behavior_names:
            return {}
            
        behavior_name = self.behavior_names[0]
        spec = self.env.behavior_specs[behavior_name]
        
        return {
            "continuous_actions": spec.action_spec.continuous_size,
            "discrete_actions": spec.action_spec.discrete_size
        }
    
    def _get_action_size(self) -> int:
        """Get the size of continuous action space."""
        if not self.env or not self.behavior_names:
            return 0
            
        behavior_name = self.behavior_names[0]
        spec = self.env.behavior_specs[behavior_name]
        return spec.action_spec.continuous_size
    
    def get_episode_stats(self) -> Dict[str, Any]:
        """Get statistics for the current episode."""
        return {
            "total_steps": self.current_step,
            "total_reward": sum(self.episode_rewards),
            "average_reward": np.mean(self.episode_rewards) if self.episode_rewards else 0.0,
            "exploit_count": self.exploit_count,
            "last_reward": self.last_reward
        }
    
    def configure_testing_parameters(self, parameters: Dict[str, Any]):
        """Configure testing parameters via side channel."""
        self.send_command("CONFIGURE_TESTING", parameters)
        
    def start_recording(self, output_path: str):
        """Start recording gameplay for reproduction."""
        self.send_command("START_RECORDING", {"output_path": output_path})
        
    def stop_recording(self):
        """Stop recording gameplay."""
        self.send_command("STOP_RECORDING")
    
    def inject_exploit_test(self, exploit_sequence: List[Dict[str, Any]]):
        """Inject a specific exploit test sequence."""
        self.send_command("INJECT_EXPLOIT_TEST", {"sequence": exploit_sequence})
