"""Configuration management for the Emergent Playtest Designer."""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis configuration."""
    url: str
    max_connections: int = 10
    socket_timeout: int = 5


@dataclass
class UnityConfig:
    """Unity integration configuration."""
    executable_path: str
    project_path: str
    headless_mode: bool = True
    timeout: int = 300
    max_memory_mb: int = 2048
    max_episode_steps: int = 10000


@dataclass
class LLMConfig:
    """LLM configuration for explanations."""
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: str = ""
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    debug: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file_path: str = "logs/playtest_designer.log"
    max_file_size: int = 10 * 1024 * 1024
    backup_count: int = 5
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"


@dataclass
class TestingConfig:
    """Testing configuration."""
    test_game_path: str = ""
    max_testing_time: int = 3600
    max_episodes: int = 1000
    exploit_detection_threshold: float = 0.8
    video_capture: bool = True
    screenshot_capture: bool = True


@dataclass
class Config:
    """Main configuration class."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    unity: UnityConfig = field(default_factory=UnityConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    testing: TestingConfig = field(default_factory=TestingConfig)
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """Load configuration from environment variables."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        return cls(
            database=DatabaseConfig(
                url=os.getenv("DATABASE_URL", "sqlite:///playtest.db"),
                pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
                echo=os.getenv("DB_ECHO", "false").lower() == "true",
            ),
            redis=RedisConfig(
                url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
                socket_timeout=int(os.getenv("REDIS_SOCKET_TIMEOUT", "5")),
            ),
            unity=UnityConfig(
                executable_path=os.getenv("UNITY_EXECUTABLE_PATH", ""),
                project_path=os.getenv("UNITY_PROJECT_PATH", ""),
                headless_mode=os.getenv("HEADLESS_MODE", "true").lower() == "true",
                timeout=int(os.getenv("UNITY_TIMEOUT", "300")),
                max_memory_mb=int(os.getenv("UNITY_MAX_MEMORY_MB", "2048")),
            ),
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "openai"),
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                api_key=os.getenv("OPENAI_API_KEY", ""),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                timeout=int(os.getenv("LLM_TIMEOUT", "30")),
            ),
            api=APIConfig(
                host=os.getenv("API_HOST", "0.0.0.0"),
                port=int(os.getenv("API_PORT", "8000")),
                workers=int(os.getenv("API_WORKERS", "4")),
                debug=os.getenv("API_DEBUG", "false").lower() == "true",
            ),
            logging=LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                file_path=os.getenv("LOG_FILE", "logs/playtest_designer.log"),
                max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
                backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5")),
                format=os.getenv("LOG_FORMAT", "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"),
            ),
            testing=TestingConfig(
                test_game_path=os.getenv("TEST_GAME_PATH", ""),
                max_testing_time=int(os.getenv("MAX_TESTING_TIME", "3600")),
                max_episodes=int(os.getenv("MAX_EPISODES", "1000")),
                exploit_detection_threshold=float(os.getenv("EXPLOIT_DETECTION_THRESHOLD", "0.8")),
                video_capture=os.getenv("VIDEO_CAPTURE", "true").lower() == "true",
                screenshot_capture=os.getenv("SCREENSHOT_CAPTURE", "true").lower() == "true",
            ),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "database": {
                "url": self.database.url,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "echo": self.database.echo,
            },
            "redis": {
                "url": self.redis.url,
                "max_connections": self.redis.max_connections,
                "socket_timeout": self.redis.socket_timeout,
            },
            "unity": {
                "executable_path": self.unity.executable_path,
                "project_path": self.unity.project_path,
                "headless_mode": self.unity.headless_mode,
                "timeout": self.unity.timeout,
                "max_memory_mb": self.unity.max_memory_mb,
            },
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "api_key": "***" if self.llm.api_key else "",
                "max_tokens": self.llm.max_tokens,
                "temperature": self.llm.temperature,
                "timeout": self.llm.timeout,
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "workers": self.api.workers,
                "debug": self.api.debug,
            },
            "logging": {
                "level": self.logging.level,
                "file_path": self.logging.file_path,
                "max_file_size": self.logging.max_file_size,
                "backup_count": self.logging.backup_count,
                "format": self.logging.format,
            },
            "testing": {
                "test_game_path": self.testing.test_game_path,
                "max_testing_time": self.testing.max_testing_time,
                "max_episodes": self.testing.max_episodes,
                "exploit_detection_threshold": self.testing.exploit_detection_threshold,
                "video_capture": self.testing.video_capture,
                "screenshot_capture": self.testing.screenshot_capture,
            },
        }
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        errors = []
        
        if not self.unity.executable_path:
            errors.append("Unity executable path is required")
        
        if not self.unity.project_path:
            errors.append("Unity project path is required")
        
        if not self.llm.api_key:
            errors.append("LLM API key is required")
        
        if self.testing.max_testing_time <= 0:
            errors.append("Max testing time must be positive")
        
        if self.testing.max_episodes <= 0:
            errors.append("Max episodes must be positive")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        return True
