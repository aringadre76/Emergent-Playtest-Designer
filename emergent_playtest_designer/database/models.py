"""
SQLAlchemy models for PostgreSQL database
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class TrainingSession(Base):
    """ML-Agents training session record"""
    __tablename__ = 'training_sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_name = Column(String(255), nullable=False)
    behavior_name = Column(String(255), nullable=False)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)
    total_steps = Column(Integer, default=0)
    total_episodes = Column(Integer, default=0)
    hyperparameters = Column(JSON)
    status = Column(String(50), default='running')  # running, completed, failed
    
    # Relationships
    exploits = relationship("ExploitRecord", back_populates="session")
    game_states = relationship("GameState", back_populates="session")
    metrics = relationship("PerformanceMetric", back_populates="session")
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_name': self.session_name,
            'behavior_name': self.behavior_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_steps': self.total_steps,
            'total_episodes': self.total_episodes,
            'hyperparameters': self.hyperparameters,
            'status': self.status
        }

class ExploitRecord(Base):
    """Discovered exploit/anomaly record"""
    __tablename__ = 'exploit_records'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('training_sessions.id'))
    
    # Exploit details
    exploit_type = Column(String(100), nullable=False)
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    confidence_score = Column(Float, nullable=False)
    description = Column(Text)
    
    # Discovery context
    discovered_at = Column(DateTime, default=func.now())
    episode_number = Column(Integer)
    step_number = Column(Integer)
    agent_position = Column(JSON)  # {x, y, z}
    agent_state = Column(JSON)     # velocity, health, etc.
    
    # Reproduction info
    action_sequence = Column(JSON)  # List of actions that led to exploit
    reproduction_count = Column(Integer, default=0)
    reproduction_success_rate = Column(Float, default=0.0)
    
    # Classification
    is_validated = Column(Boolean, default=False)
    is_false_positive = Column(Boolean, default=False)
    
    # Media
    video_path = Column(String(500))
    screenshot_path = Column(String(500))
    
    # Relationships
    session = relationship("TrainingSession", back_populates="exploits")
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'exploit_type': self.exploit_type,
            'severity': self.severity,
            'confidence_score': self.confidence_score,
            'description': self.description,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
            'episode_number': self.episode_number,
            'step_number': self.step_number,
            'agent_position': self.agent_position,
            'agent_state': self.agent_state,
            'action_sequence': self.action_sequence,
            'reproduction_count': self.reproduction_count,
            'reproduction_success_rate': self.reproduction_success_rate,
            'is_validated': self.is_validated,
            'is_false_positive': self.is_false_positive,
            'video_path': self.video_path,
            'screenshot_path': self.screenshot_path
        }

class GameState(Base):
    """Game state snapshots for analysis"""
    __tablename__ = 'game_states'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('training_sessions.id'))
    
    # Timing
    timestamp = Column(DateTime, default=func.now())
    episode_number = Column(Integer)
    step_number = Column(Integer)
    
    # Game state data
    agent_observations = Column(JSON)    # Raw ML-Agents observations
    agent_actions = Column(JSON)         # Actions taken
    agent_rewards = Column(JSON)         # Rewards received
    
    # Unity-specific data
    unity_scene_state = Column(JSON)     # Scene objects, positions, etc.
    performance_metrics = Column(JSON)   # FPS, memory usage, etc.
    
    # Analysis flags
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float)
    behavioral_signature = Column(JSON)  # For MAP-Elites classification
    
    # Relationships
    session = relationship("TrainingSession", back_populates="game_states")
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'episode_number': self.episode_number,
            'step_number': self.step_number,
            'agent_observations': self.agent_observations,
            'agent_actions': self.agent_actions,
            'agent_rewards': self.agent_rewards,
            'unity_scene_state': self.unity_scene_state,
            'performance_metrics': self.performance_metrics,
            'is_anomaly': self.is_anomaly,
            'anomaly_score': self.anomaly_score,
            'behavioral_signature': self.behavioral_signature
        }

class PerformanceMetric(Base):
    """System performance metrics during training"""
    __tablename__ = 'performance_metrics'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey('training_sessions.id'))
    
    timestamp = Column(DateTime, default=func.now())
    metric_type = Column(String(50))  # fps, memory, cpu, gpu_utilization, etc.
    value = Column(Float)
    unit = Column(String(20))         # fps, mb, percent, etc.
    
    # Context
    episode_number = Column(Integer)
    step_number = Column(Integer)
    additional_data = Column(JSON)
    
    # Relationships
    session = relationship("TrainingSession", back_populates="metrics")
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metric_type': self.metric_type,
            'value': self.value,
            'unit': self.unit,
            'episode_number': self.episode_number,
            'step_number': self.step_number,
            'additional_data': self.additional_data
        }
