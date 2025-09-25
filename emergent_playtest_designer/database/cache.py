"""
Redis caching utilities for real-time game state management
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from loguru import logger

from .connection import get_redis_cache

class GameStateCache:
    """High-performance caching for real-time game states"""
    
    def __init__(self):
        self.redis = get_redis_cache()
        self.default_ttl = 3600  # 1 hour default expiration
    
    def cache_game_state(self, session_id: str, episode: int, step: int, 
                        game_state: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache a game state with automatic key generation"""
        key = f"gamestate:{session_id}:{episode}:{step}"
        
        state_data = {
            'timestamp': time.time(),
            'session_id': session_id,
            'episode': episode,
            'step': step,
            'data': game_state
        }
        
        return self.redis.set(key, state_data, expire=ttl or self.default_ttl)
    
    def get_game_state(self, session_id: str, episode: int, step: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific game state"""
        key = f"gamestate:{session_id}:{episode}:{step}"
        return self.redis.get(key)
    
    def get_recent_states(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent game states for a session"""
        pattern = f"gamestate:{session_id}:*"
        keys = self.redis.client.keys(pattern)
        
        # Sort by timestamp (most recent first)
        states = []
        for key in keys[:limit]:  # Limit to prevent memory issues
            state = self.redis.get(key)
            if state:
                states.append(state)
        
        # Sort by timestamp descending
        states.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return states[:limit]
    
    def cache_agent_observations(self, session_id: str, observations: Dict[str, Any], 
                               ttl: int = 300) -> bool:
        """Cache agent observations (short TTL for real-time use)"""
        key = f"observations:{session_id}:latest"
        
        obs_data = {
            'timestamp': time.time(),
            'session_id': session_id,
            'observations': observations
        }
        
        return self.redis.set(key, obs_data, expire=ttl)
    
    def get_latest_observations(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get latest agent observations"""
        key = f"observations:{session_id}:latest"
        return self.redis.get(key)

class SessionCache:
    """Caching for training session data"""
    
    def __init__(self):
        self.redis = get_redis_cache()
        self.session_ttl = 86400  # 24 hours for session data
    
    def cache_session_stats(self, session_id: str, stats: Dict[str, Any]) -> bool:
        """Cache training session statistics"""
        key = f"session:{session_id}:stats"
        
        stats_data = {
            'timestamp': time.time(),
            'session_id': session_id,
            'stats': stats
        }
        
        return self.redis.set(key, stats_data, expire=self.session_ttl)
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session statistics"""
        key = f"session:{session_id}:stats"
        return self.redis.get(key)
    
    def cache_active_sessions(self, sessions: List[str]) -> bool:
        """Cache list of active session IDs"""
        key = "sessions:active"
        return self.redis.set(key, sessions, expire=300)  # 5 minute TTL
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active sessions"""
        key = "sessions:active"
        sessions = self.redis.get(key)
        return sessions if isinstance(sessions, list) else []
    
    def add_active_session(self, session_id: str) -> bool:
        """Add a session to active list"""
        active_sessions = set(self.get_active_sessions())
        active_sessions.add(session_id)
        return self.cache_active_sessions(list(active_sessions))
    
    def remove_active_session(self, session_id: str) -> bool:
        """Remove a session from active list"""
        active_sessions = set(self.get_active_sessions())
        active_sessions.discard(session_id)
        return self.cache_active_sessions(list(active_sessions))

class ExploitCache:
    """Caching for exploit detection results"""
    
    def __init__(self):
        self.redis = get_redis_cache()
        self.exploit_ttl = 604800  # 1 week for exploit data
    
    def cache_exploit_detection(self, session_id: str, episode: int, step: int,
                              detection_result: Dict[str, Any]) -> bool:
        """Cache exploit detection result"""
        key = f"exploit:{session_id}:{episode}:{step}"
        
        exploit_data = {
            'timestamp': time.time(),
            'session_id': session_id,
            'episode': episode,
            'step': step,
            'detection': detection_result
        }
        
        return self.redis.set(key, exploit_data, expire=self.exploit_ttl)
    
    def get_exploit_detection(self, session_id: str, episode: int, step: int) -> Optional[Dict[str, Any]]:
        """Get specific exploit detection result"""
        key = f"exploit:{session_id}:{episode}:{step}"
        return self.redis.get(key)
    
    def cache_session_exploits(self, session_id: str, exploits: List[Dict[str, Any]]) -> bool:
        """Cache all exploits for a session"""
        key = f"exploits:{session_id}:summary"
        
        summary_data = {
            'timestamp': time.time(),
            'session_id': session_id,
            'exploit_count': len(exploits),
            'exploits': exploits
        }
        
        return self.redis.set(key, summary_data, expire=self.exploit_ttl)
    
    def get_session_exploits(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all exploits for a session"""
        key = f"exploits:{session_id}:summary"
        data = self.redis.get(key)
        return data.get('exploits', []) if data else []

class PerformanceCache:
    """Caching for system performance metrics"""
    
    def __init__(self):
        self.redis = get_redis_cache()
        self.metrics_ttl = 3600  # 1 hour for performance metrics
    
    def cache_performance_metrics(self, session_id: str, metrics: Dict[str, float]) -> bool:
        """Cache real-time performance metrics"""
        key = f"performance:{session_id}:latest"
        
        perf_data = {
            'timestamp': time.time(),
            'session_id': session_id,
            'metrics': metrics
        }
        
        return self.redis.set(key, perf_data, expire=300)  # 5 minute TTL for real-time data
    
    def get_performance_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get latest performance metrics"""
        key = f"performance:{session_id}:latest"
        return self.redis.get(key)
    
    def cache_performance_history(self, session_id: str, 
                                history: List[Dict[str, Any]]) -> bool:
        """Cache performance history for analysis"""
        key = f"performance:{session_id}:history"
        
        history_data = {
            'timestamp': time.time(),
            'session_id': session_id,
            'data_points': len(history),
            'history': history
        }
        
        return self.redis.set(key, history_data, expire=self.metrics_ttl)
    
    def get_performance_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get performance history"""
        key = f"performance:{session_id}:history"
        data = self.redis.get(key)
        return data.get('history', []) if data else []

# Convenience factory functions
def get_game_state_cache() -> GameStateCache:
    """Get game state cache instance"""
    return GameStateCache()

def get_session_cache() -> SessionCache:
    """Get session cache instance"""
    return SessionCache()

def get_exploit_cache() -> ExploitCache:
    """Get exploit cache instance"""
    return ExploitCache()

def get_performance_cache() -> PerformanceCache:
    """Get performance cache instance"""
    return PerformanceCache()
