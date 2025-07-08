"""Configuration module for reading .ptnclirc file from home directory."""

import os
import configparser
from pathlib import Path
from typing import Optional, Dict, Any


class PTNCLIConfig:
    """Configuration class for reading and managing .ptnclirc file."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration with optional custom config file path."""
        self.config_file = config_file or str(Path.home() / ".ptnclirc")
        self.config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from .ptnclirc file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value by section and key."""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def get_section(self, section: str) -> Dict[str, str]:
        """Get all key-value pairs from a section."""
        try:
            return dict(self.config.items(section))
        except configparser.NoSectionError:
            return {}

    def has_section(self, section: str) -> bool:
        """Check if section exists in configuration."""
        return self.config.has_section(section)

    def has_option(self, section: str, key: str) -> bool:
        """Check if option exists in section."""
        return self.config.has_option(section, key)

    def config_exists(self) -> bool:
        """Check if configuration file exists."""
        return os.path.exists(self.config_file)

    def get_config_path(self) -> str:
        """Get the path to the configuration file."""
        return self.config_file


def get_config() -> PTNCLIConfig:
    """Get the global configuration instance."""
    return PTNCLIConfig()

if __name__ == "__main__":
    config = get_config()
    print(f"Config file path: {config.get_config_path()}")
    print(f"Config exists: {config.config_exists()}")
    print(f"PTN path: {config.get('ptn', 'path')}")
