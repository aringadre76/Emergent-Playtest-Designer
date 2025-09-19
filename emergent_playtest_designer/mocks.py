"""
Mock implementations for heavy dependencies to enable shipping without Unity/ML packages.
These provide the same interface as the real implementations but with simulated behavior.
"""

import asyncio
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3
from pathlib import Path

# Mock Unity Controller
class MockUnityController:
    """Mock Unity controller that simulates game execution without Unity dependencies."""
    
    def __init__(self, game_path: str):
        self.game_path = game_path
        self.is_running = False
        self.current_state = {"player_x": 0, "player_y": 0, "health": 100, "score": 0}
        self.frame_count = 0
        
    async def start_game(self) -> bool:
        """Start the mock game."""
        await asyncio.sleep(0.1)  # Simulate startup time
        self.is_running = True
        return True
        
    async def stop_game(self) -> bool:
        """Stop the mock game."""
        self.is_running = False
        return True
        
    async def inject_input(self, action: str, value: float = 1.0) -> bool:
        """Simulate input injection."""
        if not self.is_running:
            return False
            
        # Simulate game state changes based on input
        if action == "move_right":
            self.current_state["player_x"] += value * 10
        elif action == "move_left":
            self.current_state["player_x"] -= value * 10
        elif action == "jump":
            self.current_state["player_y"] += value * 20
        elif action == "attack":
            self.current_state["score"] += random.randint(10, 50)
            
        self.frame_count += 1
        return True
        
    async def get_game_state(self) -> Dict[str, Any]:
        """Get current game state."""
        if not self.is_running:
            return {}
            
        # Simulate gravity
        if self.current_state["player_y"] > 0:
            self.current_state["player_y"] -= 5
            
        # Simulate random events
        if random.random() < 0.01:  # 1% chance
            self.current_state["health"] -= random.randint(1, 5)
            
        return self.current_state.copy()
        
    async def take_screenshot(self) -> str:
        """Simulate screenshot capture."""
        screenshot_path = f"/tmp/screenshot_{self.frame_count}.png"
        # In real implementation, this would capture actual screenshot
        return screenshot_path

# Mock OpenCV
class MockOpenCV:
    """Mock OpenCV for video/image processing."""
    
    @staticmethod
    def VideoWriter(filename: str, fourcc: int, fps: float, frame_size: Tuple[int, int]):
        return MockVideoWriter(filename, fps, frame_size)
        
    @staticmethod
    def imread(filename: str):
        """Mock image reading."""
        return MockImage(filename)
        
    @staticmethod
    def imwrite(filename: str, image):
        """Mock image writing."""
        return True
        
    @staticmethod
    def cvtColor(image, code):
        """Mock color conversion."""
        return image

class MockVideoWriter:
    """Mock video writer."""
    
    def __init__(self, filename: str, fps: float, frame_size: Tuple[int, int]):
        self.filename = filename
        self.fps = fps
        self.frame_size = frame_size
        self.frame_count = 0
        
    def write(self, frame):
        """Mock frame writing."""
        self.frame_count += 1
        return True
        
    def release(self):
        """Mock video release."""
        return True

class MockImage:
    """Mock image object."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.shape = (480, 640, 3)  # Mock dimensions

# Mock PyTorch
class MockTorch:
    """Mock PyTorch for neural network operations."""
    
    @staticmethod
    def tensor(data):
        return MockTensor(data)
        
    @staticmethod
    def nn():
        return MockNN()
        
    @staticmethod
    def optim():
        return MockOptim()

class MockTensor:
    """Mock tensor."""
    
    def __init__(self, data):
        self.data = data
        
    def to(self, device):
        return self
        
    def cpu(self):
        return self
        
    def numpy(self):
        return self.data

class MockNN:
    """Mock neural network module."""
    
    @staticmethod
    def Linear(in_features: int, out_features: int):
        return MockLinear(in_features, out_features)
        
    @staticmethod
    def ReLU():
        return MockReLU()

class MockLinear:
    """Mock linear layer."""
    
    def __init__(self, in_features: int, out_features: int):
        self.in_features = in_features
        self.out_features = out_features
        
    def __call__(self, x):
        return MockTensor([[random.random() for _ in range(self.out_features)] for _ in range(len(x.data))])

class MockReLU:
    """Mock ReLU activation."""
    
    def __call__(self, x):
        return x

class MockOptim:
    """Mock optimizer."""
    
    @staticmethod
    def Adam(params, lr: float = 0.001):
        return MockAdam(params, lr)

class MockAdam:
    """Mock Adam optimizer."""
    
    def __init__(self, params, lr: float):
        self.params = params
        self.lr = lr
        
    def step(self):
        pass
        
    def zero_grad(self):
        pass

# Mock Unity ML-Agents
class MockUnityAgents:
    """Mock Unity ML-Agents."""
    
    @staticmethod
    def UnityEnvironment(file_name: str):
        return MockUnityEnvironment(file_name)

class MockUnityEnvironment:
    """Mock Unity environment."""
    
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.brain_names = ["PlayerBrain"]
        
    def reset(self):
        return {"PlayerBrain": MockTensor([[random.random() for _ in range(10)]])}
        
    def step(self, action):
        return (
            {"PlayerBrain": MockTensor([[random.random() for _ in range(10)]])},
            {"PlayerBrain": MockTensor([random.random()])},
            {"PlayerBrain": MockTensor([False])},
            {}
        )

# Mock LLM Client
class MockLLMClient:
    """Mock LLM client for testing without API keys."""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4", api_key: str = ""):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        
    async def generate_explanation(self, exploit_data: Dict[str, Any]) -> str:
        """Generate mock explanation."""
        exploit_type = exploit_data.get("exploit_type", "unknown")
        
        explanations = {
            "out_of_bounds": "The player character moved outside the intended game boundaries. This likely occurred due to insufficient collision detection or boundary checking in the movement system.",
            "infinite_resources": "The player gained unlimited resources through an exploit in the resource management system. This could be caused by integer overflow or improper validation.",
            "stuck_state": "The player became unresponsive, likely due to a state machine getting stuck in an invalid state or missing transition conditions.",
            "infinite_loop": "The game entered an endless loop, possibly due to improper loop termination conditions or recursive function calls.",
            "clipping": "The player passed through solid objects, indicating issues with collision detection or physics simulation.",
            "sequence_break": "The game sequence was broken or skipped, likely due to improper state management or missing validation checks."
        }
        
        return explanations.get(exploit_type, "An unknown exploit was detected. Further analysis is required to understand the root cause.")

# Mock Database
class MockDatabase:
    """Mock database for testing without PostgreSQL."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
        
    def _create_tables(self):
        """Create mock database tables."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS testing_sessions (
                id TEXT PRIMARY KEY,
                game_path TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                config TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exploits (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                exploit_type TEXT,
                severity TEXT,
                description TEXT,
                reproduction_data TEXT,
                timestamp TIMESTAMP
            )
        """)
        
        self.conn.commit()
        
    def save_session(self, session_id: str, game_path: str, config: Dict[str, Any]) -> bool:
        """Save testing session."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO testing_sessions (id, game_path, start_time, status, config)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, game_path, time.time(), "running", json.dumps(config)))
        self.conn.commit()
        return True
        
    def save_exploit(self, exploit_id: str, session_id: str, exploit_data: Dict[str, Any]) -> bool:
        """Save exploit data."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO exploits (id, session_id, exploit_type, severity, description, reproduction_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            exploit_id, session_id, exploit_data.get("type", "unknown"),
            exploit_data.get("severity", "medium"), exploit_data.get("description", ""),
            json.dumps(exploit_data), time.time()
        ))
        self.conn.commit()
        return True
        
    def get_exploits(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get exploits."""
        cursor = self.conn.cursor()
        if session_id:
            cursor.execute("SELECT * FROM exploits WHERE session_id = ?", (session_id,))
        else:
            cursor.execute("SELECT * FROM exploits")
            
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

# Mock Redis
class MockRedis:
    """Mock Redis for caching."""
    
    def __init__(self, url: str = ""):
        self.data = {}
        
    async def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
        
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self.data[key] = value
        return True
        
    async def delete(self, key: str) -> bool:
        if key in self.data:
            del self.data[key]
            return True
        return False

# Dependency injection function
def get_mock_dependencies():
    """Get all mock dependencies."""
    return {
        "unity_controller": MockUnityController,
        "opencv": MockOpenCV,
        "torch": MockTorch,
        "unityagents": MockUnityAgents,
        "llm_client": MockLLMClient,
        "database": MockDatabase,
        "redis": MockRedis
    }
