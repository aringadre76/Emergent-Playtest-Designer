"""Database models and storage for the Emergent Playtest Designer."""

import json
import sqlite3
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from loguru import logger
from .types import ExploitReport, TestingSession, GameState, ActionSequence


@dataclass
class DatabaseSession:
    """Database session model."""
    session_id: str
    game_path: str
    start_time: float
    end_time: Optional[float]
    agent_type: str
    max_duration: int
    max_episodes: int
    exploits_found: int
    total_actions: int
    total_states: int
    status: str = "running"


@dataclass
class DatabaseExploit:
    """Database exploit model."""
    exploit_id: str
    session_id: str
    exploit_type: str
    severity: str
    description: str
    confidence_score: float
    discovery_time: float
    reproduction_steps: str
    action_sequence: str
    game_states: str
    video_path: Optional[str]
    screenshots: str
    explanation: Optional[str]


class DatabaseManager:
    """Manages database operations."""
    
    def __init__(self, db_path: str = "playtest_designer.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    game_path TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    agent_type TEXT NOT NULL,
                    max_duration INTEGER NOT NULL,
                    max_episodes INTEGER NOT NULL,
                    exploits_found INTEGER DEFAULT 0,
                    total_actions INTEGER DEFAULT 0,
                    total_states INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'running',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exploits (
                    exploit_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    exploit_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    discovery_time REAL NOT NULL,
                    reproduction_steps TEXT NOT NULL,
                    action_sequence TEXT NOT NULL,
                    game_states TEXT NOT NULL,
                    video_path TEXT,
                    screenshots TEXT,
                    explanation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    test_case_id TEXT PRIMARY KEY,
                    exploit_id TEXT NOT NULL,
                    test_framework TEXT NOT NULL,
                    test_content TEXT NOT NULL,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exploit_id) REFERENCES exploits (exploit_id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def save_session(self, session: TestingSession, agent_type: str, max_duration: int, max_episodes: int) -> None:
        """Save testing session to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (session_id, game_path, start_time, end_time, agent_type, max_duration, max_episodes, 
                     exploits_found, total_actions, total_states, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    session.game_path,
                    session.start_time,
                    session.end_time,
                    agent_type,
                    max_duration,
                    max_episodes,
                    len(session.exploits_found),
                    session.total_actions,
                    session.total_states,
                    "completed" if session.end_time else "running"
                ))
                
                conn.commit()
                logger.info(f"Session {session.session_id} saved to database")
                
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            raise
    
    def save_exploit(self, exploit: ExploitReport, session_id: str) -> None:
        """Save exploit to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO exploits 
                    (exploit_id, session_id, exploit_type, severity, description, confidence_score, 
                     discovery_time, reproduction_steps, action_sequence, game_states, video_path, 
                     screenshots, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    exploit.exploit_id,
                    session_id,
                    exploit.exploit_type.value,
                    exploit.severity.value,
                    exploit.description,
                    exploit.confidence_score,
                    exploit.discovery_time,
                    json.dumps(exploit.reproduction_steps),
                    json.dumps(exploit.action_sequence.to_dict()),
                    json.dumps([state.to_dict() for state in exploit.game_states]),
                    exploit.video_path,
                    json.dumps(exploit.screenshots or []),
                    exploit.explanation
                ))
                
                conn.commit()
                logger.info(f"Exploit {exploit.exploit_id} saved to database")
                
        except Exception as e:
            logger.error(f"Failed to save exploit: {e}")
            raise
    
    def save_test_case(self, exploit_id: str, test_framework: str, test_content: str, file_path: Optional[str] = None) -> str:
        """Save test case to database."""
        try:
            test_case_id = f"test_{exploit_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO test_cases 
                    (test_case_id, exploit_id, test_framework, test_content, file_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    test_case_id,
                    exploit_id,
                    test_framework,
                    test_content,
                    file_path
                ))
                
                conn.commit()
                logger.info(f"Test case {test_case_id} saved to database")
                
            return test_case_id
            
        except Exception as e:
            logger.error(f"Failed to save test case: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[DatabaseSession]:
        """Get session by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT session_id, game_path, start_time, end_time, agent_type, max_duration, 
                           max_episodes, exploits_found, total_actions, total_states, status
                    FROM sessions WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return DatabaseSession(*row)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def get_exploits_by_session(self, session_id: str) -> List[DatabaseExploit]:
        """Get all exploits for a session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT exploit_id, session_id, exploit_type, severity, description, confidence_score,
                           discovery_time, reproduction_steps, action_sequence, game_states, video_path,
                           screenshots, explanation
                    FROM exploits WHERE session_id = ?
                    ORDER BY discovery_time DESC
                """, (session_id,))
                
                rows = cursor.fetchall()
                exploits = []
                
                for row in rows:
                    exploits.append(DatabaseExploit(*row))
                
                return exploits
                
        except Exception as e:
            logger.error(f"Failed to get exploits: {e}")
            return []
    
    def get_exploit(self, exploit_id: str) -> Optional[DatabaseExploit]:
        """Get exploit by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT exploit_id, session_id, exploit_type, severity, description, confidence_score,
                           discovery_time, reproduction_steps, action_sequence, game_states, video_path,
                           screenshots, explanation
                    FROM exploits WHERE exploit_id = ?
                """, (exploit_id,))
                
                row = cursor.fetchone()
                if row:
                    return DatabaseExploit(*row)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get exploit: {e}")
            return None
    
    def get_recent_sessions(self, limit: int = 10) -> List[DatabaseSession]:
        """Get recent sessions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT session_id, game_path, start_time, end_time, agent_type, max_duration,
                           max_episodes, exploits_found, total_actions, total_states, status
                    FROM sessions 
                    ORDER BY start_time DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                sessions = []
                
                for row in rows:
                    sessions.append(DatabaseSession(*row))
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to get recent sessions: {e}")
            return []
    
    def get_exploit_statistics(self) -> Dict[str, Any]:
        """Get exploit statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM exploits")
                total_exploits = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT exploit_type, COUNT(*) 
                    FROM exploits 
                    GROUP BY exploit_type
                """)
                exploit_types = dict(cursor.fetchall())
                
                cursor.execute("""
                    SELECT severity, COUNT(*) 
                    FROM exploits 
                    GROUP BY severity
                """)
                severity_counts = dict(cursor.fetchall())
                
                cursor.execute("SELECT AVG(confidence_score) FROM exploits")
                avg_confidence = cursor.fetchone()[0] or 0.0
                
                return {
                    "total_exploits": total_exploits,
                    "total_sessions": total_sessions,
                    "exploit_types": exploit_types,
                    "severity_counts": severity_counts,
                    "average_confidence": avg_confidence
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30) -> int:
        """Clean up old data."""
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM sessions WHERE start_time < ?", (cutoff_time,))
                deleted_sessions = cursor.rowcount
                
                cursor.execute("DELETE FROM exploits WHERE discovery_time < ?", (cutoff_time,))
                deleted_exploits = cursor.rowcount
                
                cursor.execute("DELETE FROM test_cases WHERE created_at < datetime(?, 'unixepoch')", (cutoff_time,))
                deleted_test_cases = cursor.rowcount
                
                conn.commit()
                
                total_deleted = deleted_sessions + deleted_exploits + deleted_test_cases
                logger.info(f"Cleaned up {total_deleted} old records")
                
                return total_deleted
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM sessions")
                session_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM exploits")
                exploit_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM test_cases")
                test_case_count = cursor.fetchone()[0]
                
                return {
                    "database_path": self.db_path,
                    "session_count": session_count,
                    "exploit_count": exploit_count,
                    "test_case_count": test_case_count
                }
                
        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return {}
