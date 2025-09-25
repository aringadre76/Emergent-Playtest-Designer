"""
Database service layer - high-level operations for the application
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from .models import TrainingSession, ExploitRecord, GameState, PerformanceMetric
from .connection import get_database_manager
from .cache import get_game_state_cache, get_session_cache, get_exploit_cache, get_performance_cache

class TrainingSessionService:
    """Service for managing training sessions"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.cache = get_session_cache()
    
    def create_session(self, session_name: str, behavior_name: str, 
                      hyperparameters: Optional[Dict[str, Any]] = None) -> TrainingSession:
        """Create a new training session"""
        with self.db_manager.get_session() as db:
            session = TrainingSession(
                session_name=session_name,
                behavior_name=behavior_name,
                hyperparameters=hyperparameters or {},
                status='running'
            )
            
            db.add(session)
            db.flush()  # Get the ID
            
            # Cache active session
            self.cache.add_active_session(session.id)
            
            logger.info(f"📊 Created training session: {session.id} ({session_name})")
            return session
    
    def get_session(self, session_id: str) -> Optional[TrainingSession]:
        """Get a training session by ID"""
        with self.db_manager.get_session() as db:
            return db.query(TrainingSession).filter_by(id=session_id).first()
    
    def update_session_progress(self, session_id: str, steps: int, episodes: int) -> bool:
        """Update session progress"""
        with self.db_manager.get_session() as db:
            session = db.query(TrainingSession).filter_by(id=session_id).first()
            if session:
                session.total_steps = steps
                session.total_episodes = episodes
                
                # Cache stats
                stats = {
                    'total_steps': steps,
                    'total_episodes': episodes,
                    'status': session.status
                }
                self.cache.cache_session_stats(session_id, stats)
                
                return True
            return False
    
    def complete_session(self, session_id: str) -> bool:
        """Mark session as completed"""
        with self.db_manager.get_session() as db:
            session = db.query(TrainingSession).filter_by(id=session_id).first()
            if session:
                session.status = 'completed'
                session.end_time = datetime.utcnow()
                
                # Remove from active sessions
                self.cache.remove_active_session(session_id)
                
                logger.info(f"✅ Completed training session: {session_id}")
                return True
            return False
    
    def get_active_sessions(self) -> List[TrainingSession]:
        """Get all active training sessions"""
        # Try cache first
        cached_session_ids = self.cache.get_active_sessions()
        
        with self.db_manager.get_session() as db:
            if cached_session_ids:
                sessions = db.query(TrainingSession).filter(
                    TrainingSession.id.in_(cached_session_ids)
                ).all()
            else:
                # Fallback to database query
                sessions = db.query(TrainingSession).filter_by(status='running').all()
                
                # Update cache
                active_ids = [s.id for s in sessions]
                self.cache.cache_active_sessions(active_ids)
            
            return sessions

class ExploitService:
    """Service for managing exploit records"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.cache = get_exploit_cache()
    
    def record_exploit(self, session_id: str, exploit_type: str, 
                      confidence_score: float, description: str,
                      episode_number: int, step_number: int,
                      agent_position: Dict[str, float],
                      agent_state: Dict[str, Any],
                      action_sequence: List[Dict[str, Any]]) -> ExploitRecord:
        """Record a discovered exploit"""
        
        with self.db_manager.get_session() as db:
            exploit = ExploitRecord(
                session_id=session_id,
                exploit_type=exploit_type,
                confidence_score=confidence_score,
                description=description,
                episode_number=episode_number,
                step_number=step_number,
                agent_position=agent_position,
                agent_state=agent_state,
                action_sequence=action_sequence
            )
            
            db.add(exploit)
            db.flush()
            
            # Cache the exploit detection
            detection_result = {
                'exploit_id': exploit.id,
                'exploit_type': exploit_type,
                'confidence_score': confidence_score,
                'description': description
            }
            
            self.cache.cache_exploit_detection(
                session_id, episode_number, step_number, detection_result
            )
            
            logger.info(f"🚨 Recorded exploit: {exploit_type} (confidence: {confidence_score:.2f})")
            return exploit
    
    def get_session_exploits(self, session_id: str) -> List[ExploitRecord]:
        """Get all exploits for a session"""
        # Try cache first
        cached_exploits = self.cache.get_session_exploits(session_id)
        
        if cached_exploits:
            return cached_exploits
        
        with self.db_manager.get_session() as db:
            exploits = db.query(ExploitRecord).filter_by(session_id=session_id).all()
            
            # Update cache
            exploit_dicts = [e.to_dict() for e in exploits]
            self.cache.cache_session_exploits(session_id, exploit_dicts)
            
            return exploits
    
    def validate_exploit(self, exploit_id: str, is_valid: bool) -> bool:
        """Mark an exploit as validated or false positive"""
        with self.db_manager.get_session() as db:
            exploit = db.query(ExploitRecord).filter_by(id=exploit_id).first()
            if exploit:
                exploit.is_validated = is_valid
                exploit.is_false_positive = not is_valid
                
                logger.info(f"✓ Exploit {exploit_id} validated: {is_valid}")
                return True
            return False

class GameStateService:
    """Service for managing game states"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.cache = get_game_state_cache()
    
    def record_game_state(self, session_id: str, episode_number: int, step_number: int,
                         agent_observations: Dict[str, Any],
                         agent_actions: Dict[str, Any],
                         agent_rewards: Dict[str, Any],
                         unity_scene_state: Dict[str, Any],
                         performance_metrics: Dict[str, Any],
                         is_anomaly: bool = False,
                         anomaly_score: Optional[float] = None) -> GameState:
        """Record a game state snapshot"""
        
        # Always cache for real-time access
        game_state_data = {
            'agent_observations': agent_observations,
            'agent_actions': agent_actions,
            'agent_rewards': agent_rewards,
            'unity_scene_state': unity_scene_state,
            'performance_metrics': performance_metrics,
            'is_anomaly': is_anomaly,
            'anomaly_score': anomaly_score
        }
        
        self.cache.cache_game_state(session_id, episode_number, step_number, game_state_data)
        
        # Store in database for persistence (less frequently)
        if step_number % 10 == 0 or is_anomaly:  # Every 10 steps or if anomaly
            with self.db_manager.get_session() as db:
                game_state = GameState(
                    session_id=session_id,
                    episode_number=episode_number,
                    step_number=step_number,
                    agent_observations=agent_observations,
                    agent_actions=agent_actions,
                    agent_rewards=agent_rewards,
                    unity_scene_state=unity_scene_state,
                    performance_metrics=performance_metrics,
                    is_anomaly=is_anomaly,
                    anomaly_score=anomaly_score
                )
                
                db.add(game_state)
                return game_state
        
        # Return cached version for consistency
        return self.get_cached_game_state(session_id, episode_number, step_number)
    
    def get_cached_game_state(self, session_id: str, episode_number: int, step_number: int) -> Optional[Dict[str, Any]]:
        """Get game state from cache (fastest access)"""
        return self.cache.get_game_state(session_id, episode_number, step_number)
    
    def get_recent_states(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent game states (cache first, fallback to DB)"""
        return self.cache.get_recent_states(session_id, limit)

class PerformanceService:
    """Service for managing performance metrics"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        self.cache = get_performance_cache()
    
    def record_metric(self, session_id: str, metric_type: str, value: float, 
                     unit: str, episode_number: Optional[int] = None,
                     step_number: Optional[int] = None,
                     additional_data: Optional[Dict[str, Any]] = None) -> PerformanceMetric:
        """Record a performance metric"""
        
        # Always cache for real-time monitoring
        metrics = {metric_type: {'value': value, 'unit': unit}}
        self.cache.cache_performance_metrics(session_id, metrics)
        
        # Store in database
        with self.db_manager.get_session() as db:
            metric = PerformanceMetric(
                session_id=session_id,
                metric_type=metric_type,
                value=value,
                unit=unit,
                episode_number=episode_number,
                step_number=step_number,
                additional_data=additional_data or {}
            )
            
            db.add(metric)
            return metric
    
    def get_recent_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get latest performance metrics from cache"""
        return self.cache.get_performance_metrics(session_id)

# Convenience factory functions
def get_training_session_service() -> TrainingSessionService:
    """Get training session service instance"""
    return TrainingSessionService()

def get_exploit_service() -> ExploitService:
    """Get exploit service instance"""
    return ExploitService()

def get_game_state_service() -> GameStateService:
    """Get game state service instance"""
    return GameStateService()

def get_performance_service() -> PerformanceService:
    """Get performance service instance"""
    return PerformanceService()
