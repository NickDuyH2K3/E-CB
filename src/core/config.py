# src/core/config.py
import json
import yaml
import os
from typing import Dict, Any, Optional

class ConfigLoader:
    """
    Handles loading and providing configuration for the chatbot.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = {}
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the config file (overrides the one set in constructor)
            
        Returns:
            Configuration dictionary
        """
        path = config_path or self.config_path
        
        if not path:
            raise ValueError("No configuration path provided")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        file_extension = os.path.splitext(path)[1].lower()
        
        try:
            if file_extension == '.json':
                with open(path, 'r') as f:
                    self.config = json.load(f)
            elif file_extension in ['.yaml', '.yml']:
                with open(path, 'r') as f:
                    self.config = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported configuration format: {file_extension}")
        except Exception as e:
            raise Exception(f"Error loading configuration: {e}")
        
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        parts = key.split('.')
        current = self.config
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Configuration value
        """
        parts = key.split('.')
        current = self.config
        
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to a file.
        
        Args:
            path: Path to save the config file (uses the original path if not provided)
        """
        save_path = path or self.config_path
        
        if not save_path:
            raise ValueError("No save path provided")
        
        file_extension = os.path.splitext(save_path)[1].lower()
        
        try:
            if file_extension == '.json':
                with open(save_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            elif file_extension in ['.yaml', '.yml']:
                with open(save_path, 'w') as f:
                    yaml.dump(self.config, f)
            else:
                raise ValueError(f"Unsupported configuration format: {file_extension}")
        except Exception as e:
            raise Exception(f"Error saving configuration: {e}")