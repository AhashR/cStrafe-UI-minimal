"""
Configuration manager for key bindings and other settings.
Stores config in %APPDATA%\cStrafe\ directory for a clean application folder.
"""
import json
import os
from pathlib import Path


def get_config_dir() -> str:
    """Get the cStrafe config directory in AppData. Creates it if needed."""
    if os.name == 'nt':  # Windows
        config_dir = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'cStrafe')
    else:  # Linux/Mac
        config_dir = os.path.expanduser('~/.cstrafe')
    
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_config_path() -> str:
    """Get the path to the config file."""
    config_dir = get_config_dir()
    return os.path.join(config_dir, 'keybindings_config.json')


def load_config() -> dict:
    """Load configuration from file. Returns defaults if file doesn't exist."""
    defaults = {
        "FORWARD": "W",
        "BACKWARD": "S",
        "LEFT": "A",
        "RIGHT": "D"
    }
    
    config_path = get_config_path()
    
    if not os.path.exists(config_path):
        # Try to create the default config file
        try:
            save_config(defaults)
        except Exception as e:
            print(f"Warning: Could not create default config file: {e}")
        return defaults
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        # Validate and normalize
        for key in defaults:
            if key not in config or not isinstance(config[key], str):
                config[key] = defaults[key]
            else:
                normalized = config[key].strip().upper()[:1]
                config[key] = normalized if normalized else defaults[key]
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        return defaults


def save_config(config: dict) -> bool:
    """Save configuration to file. Returns True if successful."""
    try:
        config_path = get_config_path()
        
        # Normalize and validate
        normalized = {
            "FORWARD": (str(config.get("FORWARD", "W")).strip().upper()[:1] or "W"),
            "BACKWARD": (str(config.get("BACKWARD", "S")).strip().upper()[:1] or "S"),
            "LEFT": (str(config.get("LEFT", "A")).strip().upper()[:1] or "A"),
            "RIGHT": (str(config.get("RIGHT", "D")).strip().upper()[:1] or "D")
        }
        
        with open(config_path, 'w') as f:
            json.dump(normalized, f, indent=2)
        
        print(f"Config saved to {config_path}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def reset_config() -> bool:
    """Reset configuration to defaults."""
    defaults = {
        "FORWARD": "W",
        "BACKWARD": "S",
        "LEFT": "A",
        "RIGHT": "D"
    }
    return save_config(defaults)
