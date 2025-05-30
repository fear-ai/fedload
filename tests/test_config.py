import pytest
import json
import os
from config_manager import ConfigManager
from config_log import setup_logging

def test_logging_default():
    """Test default logging configuration"""
    manager = ConfigManager("nonexistent.json")
    config = manager.config
    
    # Test default values
    assert config["entity_recognition"]["use_fed_entities"] is True
    assert config["entity_recognition"]["enrich_existing_entities"] is True
    assert config["monitoring"]["timeout_seconds"] == 10
    assert config["monitoring"]["user_agent"] == "FedLoad Monitor/1.0"
    assert config["logging"]["max_size_mb"] == 10
    assert config["logging"]["backup_count"] == 5

def test_logging_with_config(tmp_path):
    """Test configuration loading with custom file"""
    # Create a temporary config file
    config_path = tmp_path / "test_config.json"
    test_config = {
        "entity_recognition": {
            "use_fed_entities": False,
            "enrich_existing_entities": False
        },
        "monitoring": {
            "timeout_seconds": 30,
            "user_agent": "Test Agent"
        },
        "logging": {
            "max_size_mb": 5,
            "backup_count": 3
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(test_config, f)
    
    # Test loading the config
    manager = ConfigManager(str(config_path))
    config = manager.config
    
    # Verify loaded values
    assert config["entity_recognition"]["use_fed_entities"] is False
    assert config["entity_recognition"]["enrich_existing_entities"] is False
    assert config["monitoring"]["timeout_seconds"] == 30
    assert config["monitoring"]["user_agent"] == "Test Agent"
    assert config["logging"]["max_size_mb"] == 5
    assert config["logging"]["backup_count"] == 3

def test_logging_missing_sections(tmp_path):
    """Test configuration loading with missing sections"""
    # Create a temporary config file with missing sections
    config_path = tmp_path / "test_config.json"
    test_config = {
        "monitoring": {
            "timeout_seconds": 30
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(test_config, f)
    
    # Test loading the config
    manager = ConfigManager(str(config_path))
    config = manager.config
    
    # Verify missing sections are filled with defaults
    assert config["entity_recognition"]["use_fed_entities"] is True
    assert config["entity_recognition"]["enrich_existing_entities"] is True
    assert config["monitoring"]["timeout_seconds"] == 30
    assert config["monitoring"].get("user_agent") == "FedLoad Monitor/1.0"
    assert config.get("logging", {}).get("max_size_mb") == 10
    assert config.get("logging", {}).get("backup_count") == 5

def test_config_invalid_json(tmp_path):
    """Test configuration loading with invalid JSON"""
    # Create a temporary invalid JSON file
    config_path = tmp_path / "test_config.json"
    with open(config_path, 'w') as f:
        f.write("{invalid json}")
    
    # Test loading the config
    manager = ConfigManager(str(config_path))
    config = manager.config
    
    # Verify defaults are used
    assert config["entity_recognition"]["use_fed_entities"] is True
    assert config["entity_recognition"]["enrich_existing_entities"] is True
    assert config["monitoring"]["timeout_seconds"] == 10
    assert config["monitoring"]["user_agent"] == "FedLoad Monitor/1.0"
    assert config["logging"]["max_size_mb"] == 10
    assert config["logging"]["backup_count"] == 5

def test_config_get_section():
    """Test configuration section retrieval"""
    manager = ConfigManager("nonexistent.json")
    
    # Test getting existing sections
    assert manager.get("entity_recognition")
    assert manager.get("monitoring")
    assert manager.get("logging")
    
    # Test getting non-existent section with default
    assert manager.get("nonexistent", {"key": "value"}) == {"key": "value"}
    
    # Test getting non-existent section without default
    assert manager.get("nonexistent") is None
