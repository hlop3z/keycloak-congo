"""Configuration file handling"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


DEFAULT_CONFIG_FILE = os.path.expanduser("~/.kc-test.yaml")


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file

    Args:
        config_file: Path to config file (default: ~/.kc-test.yaml)

    Returns:
        Configuration dictionary
    """
    config_path = config_file or DEFAULT_CONFIG_FILE

    # Return defaults if config doesn't exist
    if not os.path.exists(config_path):
        return get_default_config()

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
        return {**get_default_config(), **config}
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path}: {e}")
        return get_default_config()


def save_config(config: Dict[str, Any], config_file: Optional[str] = None):
    """
    Save configuration to file

    Args:
        config: Configuration dictionary
        config_file: Path to config file (default: ~/.kc-test.yaml)
    """
    config_path = config_file or DEFAULT_CONFIG_FILE

    try:
        # Ensure directory exists
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
        raise Exception(f"Failed to save config to {config_path}: {e}")


def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        "keycloak_url": os.environ.get("KC_TEST_KEYCLOAK_URL", "http://localhost:8080"),
        "kong_url": os.environ.get("KC_TEST_KONG_URL", "http://localhost:8000"),
        "default_realm": os.environ.get("KC_TEST_REALM", "kong-realm"),
        "default_user": "testuser",
        "client_id": "kong-client",
        "admin_user": "admin",
    }


def get_config_value(key: str, default: Any = None, config_file: Optional[str] = None) -> Any:
    """
    Get configuration value

    Args:
        key: Configuration key
        default: Default value if key not found
        config_file: Path to config file

    Returns:
        Configuration value
    """
    config = load_config(config_file)
    return config.get(key, default)


def create_default_config(config_file: Optional[str] = None):
    """
    Create default configuration file

    Args:
        config_file: Path to config file (default: ~/.kc-test.yaml)
    """
    config = get_default_config()
    save_config(config, config_file)
