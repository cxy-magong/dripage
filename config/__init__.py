"""Configuration package for Dripage."""

from .settings import (
    ConfigManager,
    get_current_config,
    get_default_config,
    get_config_source,
    DEFAULT_CONFIG_FILE,
    SESSION_CONFIG_FILE
)
from .paths import (
    CONFIG_DIR,
    OUTPUT_DIR,
    OUTPUT_DATA_DIR,
    OUTPUT_LOG_DIR,
    BROWSER_CONFIG_DIR
)

__all__ = [
    # Settings
    'ConfigManager',
    'get_current_config',
    'get_default_config',
    'get_config_source',
    'DEFAULT_CONFIG_FILE',
    'SESSION_CONFIG_FILE',
    # Paths
    'CONFIG_DIR',
    'OUTPUT_DIR',
    'OUTPUT_DATA_DIR',
    'OUTPUT_LOG_DIR',
    'BROWSER_CONFIG_DIR',
]
