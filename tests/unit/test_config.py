"""Unit tests for configuration management."""

import pytest
import os
from emergent_playtest_designer.core.config import Config


def test_config_creation():
    """Test Config creation."""
    config = Config()
    
    assert config.database.url == "sqlite:///playtest.db"
    assert config.unity.executable_path == ""
    assert config.llm.provider == "openai"
    assert config.api.host == "0.0.0.0"
    assert config.api.port == 8000


def test_config_from_env():
    """Test Config creation from environment variables."""
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
    os.environ["UNITY_EXECUTABLE_PATH"] = "/path/to/unity"
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    config = Config.from_env()
    
    assert config.database.url == "postgresql://test:test@localhost:5432/test"
    assert config.unity.executable_path == "/path/to/unity"
    assert config.llm.api_key == "test_key"


def test_config_validation():
    """Test Config validation."""
    config = Config()
    
    # Should fail validation due to missing required fields
    with pytest.raises(ValueError):
        config.validate()
    
    # Set required fields
    config.unity.executable_path = "/path/to/unity"
    config.unity.project_path = "/path/to/project"
    config.llm.api_key = "test_key"
    
    # Should pass validation
    assert config.validate() is True


def test_config_to_dict():
    """Test Config serialization to dictionary."""
    config = Config()
    config.unity.executable_path = "/path/to/unity"
    config.unity.project_path = "/path/to/project"
    config.llm.api_key = "test_key"
    
    config_dict = config.to_dict()
    
    assert "database" in config_dict
    assert "unity" in config_dict
    assert "llm" in config_dict
    assert "api" in config_dict
    assert "logging" in config_dict
    assert "testing" in config_dict
    
    assert config_dict["unity"]["executable_path"] == "/path/to/unity"
    assert config_dict["unity"]["project_path"] == "/path/to/project"
    assert config_dict["llm"]["api_key"] == "***"


def test_database_config():
    """Test DatabaseConfig."""
    from emergent_playtest_designer.core.config import DatabaseConfig
    
    db_config = DatabaseConfig(
        url="postgresql://test:test@localhost:5432/test",
        pool_size=20,
        max_overflow=30,
        echo=True
    )
    
    assert db_config.url == "postgresql://test:test@localhost:5432/test"
    assert db_config.pool_size == 20
    assert db_config.max_overflow == 30
    assert db_config.echo is True


def test_unity_config():
    """Test UnityConfig."""
    from emergent_playtest_designer.core.config import UnityConfig
    
    unity_config = UnityConfig(
        executable_path="/path/to/unity",
        project_path="/path/to/project",
        headless_mode=True,
        timeout=300,
        max_memory_mb=2048
    )
    
    assert unity_config.executable_path == "/path/to/unity"
    assert unity_config.project_path == "/path/to/project"
    assert unity_config.headless_mode is True
    assert unity_config.timeout == 300
    assert unity_config.max_memory_mb == 2048


def test_llm_config():
    """Test LLMConfig."""
    from emergent_playtest_designer.core.config import LLMConfig
    
    llm_config = LLMConfig(
        provider="anthropic",
        model="claude-3-sonnet",
        api_key="test_key",
        max_tokens=2000,
        temperature=0.5,
        timeout=60
    )
    
    assert llm_config.provider == "anthropic"
    assert llm_config.model == "claude-3-sonnet"
    assert llm_config.api_key == "test_key"
    assert llm_config.max_tokens == 2000
    assert llm_config.temperature == 0.5
    assert llm_config.timeout == 60
