"""Main orchestrator for the Emergent Playtest Designer system."""

import asyncio
import time
import uuid
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from loguru import logger
from .config import Config
from .types import GameState, Action, ExploitReport, TestingSession, AgentConfig
from ..unity_integration import UnityController, StateObserver, InputInjector
from ..agents import NoveltySearchAgent, EvolutionaryAgent, ReinforcementAgent
from ..detection import ExploitDetector
from ..reproduction import ReproductionGenerator
from ..explanation import ExplanationEngine


@dataclass
class TestingConfig:
    """Configuration for testing session."""
    game_path: str
    max_duration: int = 3600
    max_episodes: int = 1000
    agent_type: str = "novelty_search"
    exploit_detection_enabled: bool = True
    reproduction_enabled: bool = True
    explanation_enabled: bool = True


class PlaytestOrchestrator:
    """Main orchestrator for the playtest system."""
    
    def __init__(self, config: Config):
        """Initialize orchestrator."""
        self.config = config
        self.unity_controller = UnityController(config.unity)
        self.state_observer = StateObserver()
        self.input_injector = InputInjector()
        
        self.agent = self._create_agent(config.testing)
        self.exploit_detector = ExploitDetector({
            "confidence_threshold": config.testing.exploit_detection_threshold,
            "realtime_threshold": 0.8,
            "anomaly_config": {"contamination": 0.1},
            "pattern_config": {"min_pattern_length": 5}
        })
        
        self.reproduction_generator = ReproductionGenerator({
            "output_dir": "reproductions",
            "generate_video": config.testing.video_capture,
            "generate_screenshots": config.testing.screenshot_capture
        })
        
        self.explanation_engine = ExplanationEngine({
            "llm_config": config.llm,
            "causal_config": {"min_correlation": 0.7}
        })
        
        self.current_session: Optional[TestingSession] = None
        self.is_running = False
        self.callbacks: List[Callable[[ExploitReport], None]] = []
        
    def _create_agent(self, testing_config) -> Any:
        """Create AI agent based on configuration."""
        agent_config = AgentConfig(
            agent_type=testing_config.get("agent_type", "novelty_search"),
            exploration_rate=0.1,
            learning_rate=0.001,
            memory_size=10000,
            batch_size=32,
            target_update_frequency=1000,
            novelty_threshold=0.5,
            max_episode_length=1000
        )
        
        if agent_config.agent_type == "novelty_search":
            return NoveltySearchAgent(agent_config)
        elif agent_config.agent_type == "evolutionary":
            return EvolutionaryAgent(agent_config)
        elif agent_config.agent_type == "reinforcement":
            return ReinforcementAgent(agent_config)
        else:
            logger.warning(f"Unknown agent type: {agent_config.agent_type}, using novelty search")
            return NoveltySearchAgent(agent_config)
    
    async def start_testing_session(self, testing_config: TestingConfig) -> str:
        """Start a new testing session."""
        session_id = str(uuid.uuid4())
        
        logger.info(f"Starting testing session {session_id}")
        
        self.current_session = TestingSession(
            session_id=session_id,
            game_path=testing_config.game_path,
            start_time=time.time()
        )
        
        try:
            success = self.unity_controller.start_game(testing_config.game_path)
            if not success:
                raise RuntimeError("Failed to start Unity game")
            
            self.state_observer.start_monitoring()
            self.is_running = True
            
            await self._run_testing_loop(testing_config)
            
        except Exception as e:
            logger.error(f"Testing session failed: {e}")
            raise
        finally:
            await self._cleanup_session()
        
        return session_id
    
    async def _run_testing_loop(self, testing_config: TestingConfig) -> None:
        """Main testing loop."""
        episode_count = 0
        start_time = time.time()
        
        while (self.is_running and 
               episode_count < testing_config.max_episodes and
               time.time() - start_time < testing_config.max_duration):
            
            episode_count += 1
            logger.info(f"Starting episode {episode_count}")
            
            await self._run_episode()
            
            if episode_count % 10 == 0:
                await self._log_progress(episode_count, start_time)
        
        logger.info(f"Testing completed after {episode_count} episodes")
    
    async def _run_episode(self) -> None:
        """Run a single episode."""
        episode_states = []
        episode_actions = []
        
        try:
            current_state = self.unity_controller.get_game_state()
            if not current_state:
                logger.warning("No initial game state available")
                return
            
            episode_states.append(current_state)
            self.state_observer.update_state(current_state)
            
            episode_length = 0
            max_episode_length = self.agent.config.max_episode_length
            
            while (self.is_running and 
                   episode_length < max_episode_length and
                   current_state.player_health > 0):
                
                action = self.agent.select_action(current_state)
                episode_actions.append(action)
                
                success = self.input_injector.inject_action(action)
                if not success:
                    logger.warning(f"Failed to inject action: {action.action_type}")
                
                await asyncio.sleep(action.duration)
                
                next_state = self.unity_controller.get_game_state()
                if not next_state:
                    logger.warning("No game state after action")
                    break
                
                episode_states.append(next_state)
                self.state_observer.update_state(next_state)
                
                reward = self._calculate_reward(current_state, action, next_state)
                self.agent.update(current_state, action, reward, next_state)
                
                if testing_config.exploit_detection_enabled:
                    exploits = self.exploit_detector.analyze_realtime(next_state, action)
                    for exploit in exploits:
                        await self._handle_exploit(exploit)
                
                current_state = next_state
                episode_length += 1
            
            if episode_states and episode_actions:
                await self._analyze_episode(episode_states, episode_actions)
        
        except Exception as e:
            logger.error(f"Episode failed: {e}")
    
    def _calculate_reward(self, state: GameState, action: Action, next_state: GameState) -> float:
        """Calculate reward for state-action-next_state transition."""
        reward = 0.0
        
        health_change = next_state.player_health - state.player_health
        reward += health_change * 0.1
        
        position_change = self._calculate_position_change(state.player_position, next_state.player_position)
        reward += position_change * 0.01
        
        resource_change = sum(next_state.player_resources.values()) - sum(state.player_resources.values())
        reward += resource_change * 0.001
        
        if next_state.player_health <= 0:
            reward -= 10.0
        
        return reward
    
    def _calculate_position_change(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate position change."""
        return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2 + (pos2[2] - pos1[2])**2)**0.5
    
    async def _analyze_episode(self, states: List[GameState], actions: List[Action]) -> None:
        """Analyze completed episode for exploits."""
        if not self.current_session:
            return
        
        try:
            exploits = self.exploit_detector.analyze_game_session(states, actions)
            
            for exploit in exploits:
                await self._handle_exploit(exploit)
        
        except Exception as e:
            logger.error(f"Episode analysis failed: {e}")
    
    async def _handle_exploit(self, exploit: ExploitReport) -> None:
        """Handle discovered exploit."""
        if not self.current_session:
            return
        
        logger.info(f"Exploit discovered: {exploit.exploit_id}")
        
        self.current_session.exploits_found.append(exploit)
        
        try:
            if self.config.testing.video_capture:
                reproduction_data = self.reproduction_generator.generate_reproduction(exploit)
                exploit.video_path = reproduction_data.video_path
                exploit.screenshots = reproduction_data.screenshots
            
            if self.config.testing.screenshot_capture:
                explanation_result = await self.explanation_engine.generate_explanation(exploit)
                exploit.explanation = explanation_result.detailed_explanation
            
            for callback in self.callbacks:
                try:
                    callback(exploit)
                except Exception as e:
                    logger.error(f"Exploit callback error: {e}")
        
        except Exception as e:
            logger.error(f"Exploit handling failed: {e}")
    
    async def _log_progress(self, episode_count: int, start_time: float) -> None:
        """Log testing progress."""
        elapsed_time = time.time() - start_time
        exploits_found = len(self.current_session.exploits_found) if self.current_session else 0
        
        logger.info(f"Progress: {episode_count} episodes, {elapsed_time:.1f}s elapsed, {exploits_found} exploits found")
        
        if self.current_session:
            self.current_session.total_actions += episode_count * 100
            self.current_session.total_states += episode_count * 100
    
    async def _cleanup_session(self) -> None:
        """Cleanup testing session."""
        logger.info("Cleaning up testing session")
        
        self.is_running = False
        self.state_observer.stop_monitoring()
        self.unity_controller.stop_game()
        
        if self.current_session:
            self.current_session.end_time = time.time()
            logger.info(f"Session {self.current_session.session_id} completed")
    
    def register_exploit_callback(self, callback: Callable[[ExploitReport], None]) -> None:
        """Register callback for exploit discovery."""
        self.callbacks.append(callback)
    
    def stop_testing(self) -> None:
        """Stop current testing session."""
        self.is_running = False
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        if not self.current_session:
            return {"status": "no_session"}
        
        return {
            "session_id": self.current_session.session_id,
            "game_path": self.current_session.game_path,
            "start_time": self.current_session.start_time,
            "end_time": self.current_session.end_time,
            "is_running": self.is_running,
            "exploits_found": len(self.current_session.exploits_found),
            "total_actions": self.current_session.total_actions,
            "total_states": self.current_session.total_states
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = {
            "agent_type": self.agent.config.agent_type,
            "unity_running": self.unity_controller.is_game_running(),
            "monitoring_active": self.state_observer.is_monitoring,
            "callbacks_registered": len(self.callbacks)
        }
        
        stats.update(self.agent.get_statistics())
        stats.update(self.exploit_detector.get_statistics())
        stats.update(self.reproduction_generator.get_statistics())
        stats.update(self.explanation_engine.get_statistics())
        
        return stats
