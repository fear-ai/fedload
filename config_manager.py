import json
import os
from datetime import datetime

class ConfigManager:
    """Configuration manager to handle loading and validation"""
    
    DEFAULT_CONFIG = {
        "entity_recognition": {
            "use_fed_entities": True,
            "enrich_existing_entities": True
        },
        "monitoring": {
            "timeout_seconds": 10,
            "user_agent": "FedLoad Monitor/1.0"
        },
        "logging": {
            "max_size_mb": 10,
            "backup_count": 5
        }
    }
    
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """Load and validate configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                # Validate and merge all sections
                for section, default_section in self.DEFAULT_CONFIG.items():
                    if section not in config:
                        config[section] = default_section
                    else:
                        # Merge with defaults for missing keys
                        for key, value in default_section.items():
                            if key not in config[section]:
                                config[section][key] = value
                return config
        except FileNotFoundError:
            print(f"Config file {self.config_path} not found, using defaults")
            return self.DEFAULT_CONFIG
        except json.JSONDecodeError:
            print(f"Invalid JSON in {self.config_path}, using defaults")
            return self.DEFAULT_CONFIG
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.DEFAULT_CONFIG
    
    def get(self, section, default=None):
        """Get a configuration section with validation"""
        if section in self.config:
            return self.config[section]
        return default if default is not None else self.DEFAULT_CONFIG.get(section, None)
