"""
Configuration management for Dripage CLI.

Manages default configuration and session profiles to avoid repetitive parameter passing.
"""
import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

import sys
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.paths import CONFIG_DIR, OUTPUT_DIR


# Configuration file paths
DEFAULT_CONFIG_FILE = CONFIG_DIR / "dripage_default.yaml"
SESSION_CONFIG_FILE = CONFIG_DIR / "dripage_session.yaml"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class BrowserConfig:
    """Browser configuration."""
    name: str = "default"
    address: str = "127.0.0.1:19222"
    browser_path: str = ""
    user_data_dir: str = ""
    ini_file: str = ""
    headless: bool = False


@dataclass
class VisionConfig:
    """Vision model configuration."""
    model: str = "glm-4v-flash"
    temperature: float = 0.7
    max_tokens: int = 1024
    api_key: Optional[str] = None


@dataclass
class CaptureConfig:
    """Packet capture configuration."""
    enabled: bool = False
    output_dir: str = str(OUTPUT_DIR / "packets")
    filters: Dict[str, Any] = field(default_factory=dict)
    save_all: bool = False


@dataclass
class DripageConfig:
    """Main configuration container."""
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    output: Dict[str, Any] = field(default_factory=lambda: {
        "directory": str(OUTPUT_DIR / "data")
    })


class ConfigManager:
    """Manages loading, saving, and switching configurations."""

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize ConfigManager.

        Args:
            config_file: Path to config file. Uses default if None.
        """
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self.session_file = SESSION_CONFIG_FILE
        self._config: Optional[DripageConfig] = None

    def load_config(self) -> DripageConfig:
        """Load configuration from file."""
        if not self.config_file.exists():
            # Return default config if file doesn't exist
            return DripageConfig()

        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        browser_data = data.get('browser', {})
        vision_data = data.get('vision', {})
        capture_data = data.get('capture', {})
        output_data = data.get('output', {})

        return DripageConfig(
            browser=BrowserConfig(
                name=browser_data.get('name', 'default'),
                address=browser_data.get('address', '127.0.0.1:19222'),
                browser_path=browser_data.get('browser_path', ''),
                user_data_dir=browser_data.get('user_data_dir', ''),
                ini_file=browser_data.get('ini_file', ''),
                headless=browser_data.get('headless', False),
            ),
            vision=VisionConfig(
                model=vision_data.get('model', 'glm-4v-flash'),
                temperature=vision_data.get('temperature', 0.7),
                max_tokens=vision_data.get('max_tokens', 1024),
                api_key=vision_data.get('api_key'),
            ),
            capture=CaptureConfig(
                enabled=capture_data.get('enabled', False),
                output_dir=capture_data.get('output_dir', 'output/packets'),
                filters=capture_data.get('filters', {}),
                save_all=capture_data.get('save_all', False),
            ),
            output=output_data,
        )

    def save_config(self, config: DripageConfig) -> None:
        """Save configuration to file."""
        data = {
            'browser': asdict(config.browser),
            'vision': {k: v for k, v in asdict(config.vision).items() if v is not None},
            'capture': {k: v for k, v in asdict(config.capture).items() if v is not None},
            'output': config.output,
        }

        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def save_session(self, session_id: str, config: DripageConfig) -> None:
        """Save session-specific configuration."""
        session_config = {
            'session_id': session_id,
            'browser': asdict(config.browser),
            'vision': {k: v for k, v in asdict(config.vision).items() if v is not None},
            'capture': {k: v for k, v in asdict(config.capture).items() if v is not None},
            'output': config.output,
        }

        with open(self.session_file, 'w', encoding='utf-8') as f:
            yaml.dump(session_config, f, allow_unicode=True, default_flow_style=False)

    def load_session(self, session_id: str) -> Optional[DripageConfig]:
        """Load session-specific configuration."""
        if not self.session_file.exists():
            return None

        with open(self.session_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        # Find the session
        sessions = data.get('sessions', [])
        for session in sessions:
            if session.get('session_id') == session_id:
                browser_data = session.get('browser', {})
                vision_data = session.get('vision', {})
                capture_data = session.get('capture', {})
                output_data = session.get('output', {})

                return DripageConfig(
                    browser=BrowserConfig(**browser_data),
                    vision=VisionConfig(
                        **{k: v for k, v in vision_data.items() if v is not None}
                    ),
                    capture=CaptureConfig(**capture_data),
                    output=output_data,
                )

        return None

    def list_sessions(self) -> list:
        """List all available sessions."""
        if not self.session_file.exists():
            return []

        with open(self.session_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        sessions = data.get('sessions', [])
        return [
            {'session_id': s.get('session_id'), 'browser': s.get('browser', {})}
            for s in sessions
        ]

    def get_current_session_id(self) -> Optional[str]:
        """Get current active session ID."""
        if not self.session_file.exists():
            return None

        with open(self.session_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        return data.get('current_session')

    def set_current_session(self, session_id: str) -> None:
        """Set current active session ID."""
        if not self.session_file.exists():
            data = {}
        else:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}

        data['current_session'] = session_id

        with open(self.session_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def get_default_config() -> DripageConfig:
    """Get default configuration (creates if needed)."""
    manager = ConfigManager()
    return manager.load_config()


def get_current_config() -> DripageConfig:
    """Get current configuration (default or session)."""
    manager = ConfigManager()
    session_id = manager.get_current_session_id()

    if session_id:
        session_config = manager.load_session(session_id)
        if session_config:
            return session_config

    return manager.load_config()


if __name__ == "__main__":
    # Test configuration manager
    manager = ConfigManager()

    # Print default config
    config = manager.load_config()
    print("Default Configuration:")
    print(f"  Browser: {config.browser.name} @ {config.browser.address}")
    print(f"  Vision: {config.vision.model}")
    print(f"  Capture: {'enabled' if config.capture.enabled else 'disabled'}")
    print()
