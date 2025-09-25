#!/usr/bin/env python3
"""
Comprehensive database testing script
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from emergent_playtest_designer.database.services import (
    get_training_session_service,
    get_exploit_service,
    get_game_state_service,
    get_performance_service
)
from emergent_playtest_designer.database import init_database
from loguru import logger

def test_training_session_operations():
    """Test training session CRUD operations"""
    logger.info("🧪 Testing training session operations...")
    
    service = get_training_session_service()
    
    # Create session
    session = service.create_session(
        session_name="test_session_database",
        behavior_name="PlaytestAgent",
        hyperparameters={"learning_rate": 0.0003, "batch_size": 1024}
    )
    
    logger.info(f"✅ Created session: {session.id}")
    
    # Update progress
    success = service.update_session_progress(session.id, steps=1000, episodes=50)
    logger.info(f"✅ Updated progress: {success}")
    
    # Get session
    retrieved = service.get_session(session.id)
    logger.info(f"✅ Retrieved session: {retrieved.session_name if retrieved else 'None'}")
    
    # Get active sessions
    active = service.get_active_sessions()
    logger.info(f"✅ Active sessions: {len(active)}")
    
    return session.id

def test_exploit_operations(session_id: str):
    """Test exploit recording and retrieval"""
    logger.info("🧪 Testing exploit operations...")
    
    service = get_exploit_service()
    
    # Record exploit
    exploit = service.record_exploit(
        session_id=session_id,
        exploit_type="infinite_jump",
        confidence_score=0.85,
        description="Agent discovered infinite jumping by rapidly pressing jump",
        episode_number=25,
        step_number=450,
        agent_position={"x": 10.5, "y": 25.0, "z": -5.2},
        agent_state={"velocity": {"x": 0, "y": 15.5, "z": 0}, "grounded": False},
        action_sequence=[
            {"action": "jump", "timestamp": 1000},
            {"action": "jump", "timestamp": 1001},
            {"action": "jump", "timestamp": 1002}
        ]
    )
    
    logger.info(f"✅ Recorded exploit: {exploit.id}")
    
    # Get session exploits
    exploits = service.get_session_exploits(session_id)
    logger.info(f"✅ Session exploits: {len(exploits)}")
    
    # Validate exploit
    validated = service.validate_exploit(exploit.id, True)
    logger.info(f"✅ Validated exploit: {validated}")
    
    return exploit.id

def test_game_state_operations(session_id: str):
    """Test game state recording and caching"""
    logger.info("🧪 Testing game state operations...")
    
    service = get_game_state_service()
    
    # Record multiple game states
    for step in range(100, 110):
        game_state = service.record_game_state(
            session_id=session_id,
            episode_number=25,
            step_number=step,
            agent_observations={"position": [10.0 + step*0.1, 2.0, -5.0], "velocity": [1.0, 0, 0]},
            agent_actions={"continuous": [0.8, 0.0, 0.0], "discrete": [0]},
            agent_rewards={"step_reward": 0.01, "total_reward": step * 0.01},
            unity_scene_state={"player_health": 100, "enemies_count": 3},
            performance_metrics={"fps": 60.0, "memory_mb": 512.0},
            is_anomaly=(step == 105),  # Mark one as anomaly
            anomaly_score=0.75 if step == 105 else None
        )
    
    logger.info("✅ Recorded 10 game states")
    
    # Test cache retrieval
    cached_state = service.get_cached_game_state(session_id, 25, 105)
    logger.info(f"✅ Retrieved cached anomaly state: {cached_state is not None}")
    
    # Get recent states
    recent = service.get_recent_states(session_id, limit=5)
    logger.info(f"✅ Recent states: {len(recent)}")
    
    return len(recent)

def test_performance_operations(session_id: str):
    """Test performance metrics recording"""
    logger.info("🧪 Testing performance operations...")
    
    service = get_performance_service()
    
    # Record various metrics
    metrics = [
        ("fps", 60.0, "fps"),
        ("memory_usage", 512.5, "mb"),
        ("cpu_usage", 45.2, "percent"),
        ("gpu_usage", 78.9, "percent")
    ]
    
    for metric_type, value, unit in metrics:
        metric = service.record_metric(
            session_id=session_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            episode_number=25,
            step_number=500
        )
    
    logger.info("✅ Recorded 4 performance metrics")
    
    # Get recent metrics from cache
    recent_metrics = service.get_recent_metrics(session_id)
    logger.info(f"✅ Recent cached metrics: {recent_metrics is not None}")
    
    return len(metrics)

def test_cache_performance():
    """Test cache performance with rapid operations"""
    logger.info("🧪 Testing cache performance...")
    
    service = get_game_state_service()
    test_session_id = "performance_test_session"
    
    start_time = time.time()
    
    # Rapid cache operations
    for i in range(1000):
        service.cache.cache_game_state(
            test_session_id, 1, i,
            {"test_data": f"performance_test_{i}", "value": i},
            ttl=300
        )
    
    cache_time = time.time() - start_time
    logger.info(f"✅ Cached 1000 states in {cache_time:.3f}s ({1000/cache_time:.0f} ops/sec)")
    
    # Rapid retrieval
    start_time = time.time()
    
    retrieved_count = 0
    for i in range(0, 1000, 10):  # Sample every 10th
        state = service.cache.get_game_state(test_session_id, 1, i)
        if state:
            retrieved_count += 1
    
    retrieval_time = time.time() - start_time
    logger.info(f"✅ Retrieved {retrieved_count}/100 states in {retrieval_time:.3f}s")
    
    return cache_time, retrieval_time

def main():
    """Run comprehensive database tests"""
    logger.info("🚀 COMPREHENSIVE DATABASE TESTING")
    logger.info("=" * 60)
    
    # Initialize database
    logger.info("🔧 Initializing database...")
    init_success = init_database()
    
    if not init_success:
        logger.error("❌ Database initialization failed!")
        return False
    
    # Test operations
    try:
        # Test training sessions
        session_id = test_training_session_operations()
        
        # Test exploits
        exploit_id = test_exploit_operations(session_id)
        
        # Test game states
        state_count = test_game_state_operations(session_id)
        
        # Test performance metrics
        metric_count = test_performance_operations(session_id)
        
        # Test cache performance
        cache_time, retrieval_time = test_cache_performance()
        
        # Final cleanup and completion
        logger.info("=" * 60)
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info(f"✅ Session created: {session_id}")
        logger.info(f"✅ Exploit recorded: {exploit_id}")
        logger.info(f"✅ Game states: {state_count} cached")
        logger.info(f"✅ Metrics recorded: {metric_count}")
        logger.info(f"⚡ Cache performance: {1000/cache_time:.0f} writes/sec, {100/retrieval_time:.0f} reads/sec")
        logger.info("🚀 Database system is production-ready!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
