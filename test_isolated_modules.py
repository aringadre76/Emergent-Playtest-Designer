#!/usr/bin/env python3
"""
Test script that imports individual modules directly to avoid package init dependencies.
"""

import sys
import os
import importlib.util

def import_module_from_file(module_name, file_path):
    """Import a module directly from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def test_types_module():
    """Test the types module directly."""
    try:
        # Import types module directly
        types_path = os.path.join(os.path.dirname(__file__), 'emergent_playtest_designer', 'core', 'types.py')
        types_module = import_module_from_file('epd_types', types_path)
        
        print("✓ Types module imported successfully")
        
        # Test GameState creation
        GameState = types_module.GameState
        state = GameState(
            timestamp=1.0,
            player_position=(10.0, 20.0, 30.0),
            player_health=75.0,
            player_resources={"health": 75.0, "mana": 25.0},
            game_objects={"enemy": {"position": [5, 0, 0]}},
            physics_state={"velocity": [1, 0, 0]},
            ui_state={"score": 100},
            custom_metrics={"distance": 50.0}
        )
        print("✓ GameState creation successful")
        
        # Test Action creation
        Action = types_module.Action
        action = Action(
            action_type="key_press",
            parameters={"key": "w"},
            timestamp=2.0,
            duration=0.1
        )
        print("✓ Action creation successful")
        
        # Test ExploitType enum
        ExploitType = types_module.ExploitType
        exploit_type = ExploitType.OUT_OF_BOUNDS
        print(f"✓ ExploitType enum working: {exploit_type.value}")
        
        # Test serialization
        state_dict = state.to_dict()
        action_dict = action.to_dict()
        print("✓ Serialization successful")
        
        # Validate data
        assert state_dict["timestamp"] == 1.0
        assert action_dict["action_type"] == "key_press"
        print("✓ Data validation successful")
        
        return True
    except Exception as e:
        print(f"✗ Types module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_module():
    """Test the config module directly."""
    try:
        # Import config module directly
        config_path = os.path.join(os.path.dirname(__file__), 'emergent_playtest_designer', 'core', 'config.py')
        config_module = import_module_from_file('epd_config', config_path)
        
        print("✓ Config module imported successfully")
        
        # Test Config creation (it uses default_factory for fields, but some require args)
        Config = config_module.Config
        DatabaseConfig = config_module.DatabaseConfig
        RedisConfig = config_module.RedisConfig
        UnityConfig = config_module.UnityConfig
        LLMConfig = config_module.LLMConfig
        
        # Create config with proper defaults
        config = Config(
            database=DatabaseConfig(url="sqlite:///test.db"),
            redis=RedisConfig(url="redis://localhost:6379/0"),
            unity=UnityConfig(executable_path="/path/to/unity", project_path="/path/to/project"),
            llm=LLMConfig(api_key="test_key")
        )
        print("✓ Config creation successful")
        
        # Test individual configs (already created above)
        db_config = DatabaseConfig(url="sqlite:///test2.db")
        unity_config = UnityConfig(executable_path="/other/unity", project_path="/other/project")
        llm_config = LLMConfig(api_key="other_key")
        print("✓ Individual config creation successful")
        
        # Test config field access (they're already set from creation)
        assert config.database.url == "sqlite:///test.db"
        assert config.unity.executable_path == "/path/to/unity"
        assert config.llm.api_key == "test_key"
        print("✓ Config field access successful")
        
        # Test serialization
        config_dict = config.to_dict()
        print("✓ Config serialization successful")
        
        # Validate data
        assert config_dict["database"]["url"] == "sqlite:///test.db"
        assert config_dict["unity"]["executable_path"] == "/path/to/unity"
        assert config_dict["llm"]["api_key"] == "***"  # Should be masked
        print("✓ Config validation successful")
        
        return True
    except Exception as e:
        print(f"✗ Config module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Testing isolated core modules...")
    
    types_passed = test_types_module()
    config_passed = test_config_module()
    
    if types_passed and config_passed:
        print("\n🎉 All isolated module tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
