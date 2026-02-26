"""
Configuration management for Dripage CLI.

Manages default configuration and session profiles to avoid repetitive parameter passing.
Supports multi-level configuration priority:
1. Environment variable DRIPAGE_BROWSER
2. Project-level config (.dripage/config)
3. User-level app config (~/.dripage/current_app)
4. Global default config
"""
import json
import os
import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

# Paths - use config.paths module for consistency
from config.paths import (
    CONFIG_DIR,
    OUTPUT_DIR,
    OUTPUT_DATA_DIR,
    OUTPUT_LOG_DIR,
    BROWSER_CONFIG_DIR
)

# Configuration file paths
DEFAULT_CONFIG_FILE = CONFIG_DIR / "dripage_default.yaml"
SESSION_CONFIG_FILE = CONFIG_DIR / "dripage_session.yaml"


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

        # Support both single session format and sessions array format
        sessions = data.get('sessions', [])
        if sessions:
            # Multi-session format
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
        else:
            # Single session format (current file format)
            if data.get('session_id') == session_id or data.get('current_session') == session_id:
                browser_data = data.get('browser', {})
                vision_data = data.get('vision', {})
                capture_data = data.get('capture', {})
                output_data = data.get('output', {})

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
    """Get current configuration with multi-level detection.

    Priority:
        1. DRIPAGE_BROWSER environment variable (highest)
        2. Project-level config (.dripage/config in CWD)
        3. User-level app config (~/.dripage/current_app)
        4. Session config (dripage_session.yaml current_session)
        5. Global default config (lowest)

    Returns:
        DripageConfig object with loaded configuration
    """
    manager = ConfigManager()

    # ========== Priority 1: Environment Variable ==========
    browser_name = os.getenv('DRIPAGE_BROWSER')
    if browser_name:
        browser_name = browser_name.strip()  # Remove whitespace
        config = _load_browser_config_by_name(browser_name)
        if config:
            config.browser.source = 'environment'
            config.browser.source_detail = f'DRIPAGE_BROWSER={browser_name}'
            print(f"ℹ️  Using browser from environment: {browser_name}", file=sys.stderr)
            return config

    # ========== Priority 2: Project-level config ==========
    project_config = _load_project_config()
    if project_config:
        project_config.browser.source = 'project'
        project_config.browser.source_detail = str(Path.cwd() / '.dripage' / 'config')
        print(f"ℹ️  Using browser from project config: {project_config.browser.name}", file=sys.stderr)
        return project_config

    # ========== Priority 3: User-level app config ==========
    user_app_config = _load_user_app_config()
    if user_app_config:
        user_app_config.browser.source = 'user'
        user_app_config.browser.source_detail = '~/.dripage/current_app'
        print(f"ℹ️  Using browser from user config: {user_app_config.browser.name}", file=sys.stderr)
        return user_app_config

    # ========== Priority 4: Session config ==========
    session_config = _load_session_config()
    if session_config:
        session_config.browser.source = 'session'
        session_config.browser.source_detail = 'dripage_session.yaml'
        print(f"ℹ️  Using browser from session config: {session_config.browser.name}", file=sys.stderr)
        return session_config

    # ========== Priority 5: Global default ==========
    config = manager.load_config()
    config.browser.source = 'default'
    config.browser.source_detail = 'dripage_default.yaml'
    print(f"ℹ️  Using global default browser: {config.browser.name}", file=sys.stderr)
    return config


def _load_session_config() -> Optional[DripageConfig]:
    """Load session config from dripage_session.yaml.

    Returns:
        DripageConfig if session is configured, None otherwise
    """
    if not SESSION_CONFIG_FILE.exists():
        return None

    try:
        with open(SESSION_CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        if not data:
            return None

        # Check for current_session or session_id
        session_id = data.get('current_session') or data.get('session_id')
        if not session_id:
            return None

        # If session_id is a browser name, load that browser config
        browser_name = session_id
        config = _load_browser_config_by_name(browser_name)
        if config:
            return config

        # Fallback: load browser config from session file directly
        browser_data = data.get('browser', {})
        if browser_data:
            manager = ConfigManager()
            default_config = manager.load_config()

            default_config.browser.name = browser_data.get('name', 'default')
            default_config.browser.address = browser_data.get('address', '127.0.0.1:19222')
            default_config.browser.browser_path = browser_data.get('browser_path', '')
            default_config.browser.user_data_dir = browser_data.get('user_data_dir', '')
            default_config.browser.ini_file = browser_data.get('ini_file', '')
            default_config.browser.headless = browser_data.get('headless', False)

            return default_config

    except Exception as e:
        print(f"⚠️  Warning: Failed to load session config: {e}", file=sys.stderr)

    return None


def _load_project_config() -> Optional[DripageConfig]:
    """Load project-level config from CWD/.dripage/config."""
    cwd = Path.cwd()
    config_path = cwd / '.dripage' / 'config'

    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        if not data:
            return None

        browser_name = data.get('browser')
        if not browser_name:
            return None

        config = _load_browser_config_by_name(browser_name)
        if config:
            # Set app_id if provided
            app_id = data.get('app_id', cwd.name)
            if not hasattr(config.browser, 'app_id'):
                config.browser.app_id = app_id
            else:
                config.browser.app_id = app_id

            # Override output directory if specified
            if 'output' in data and 'directory' in data['output']:
                config.output['directory'] = data['output']['directory']

            # Override vision config if specified
            if 'vision' in data:
                for key, value in data['vision'].items():
                    if hasattr(config.vision, key):
                        setattr(config.vision, key, value)

            return config

    except Exception as e:
        print(f"⚠️  Warning: Failed to load project config from {config_path}: {e}",
              file=sys.stderr)

    return None


def _load_user_app_config() -> Optional[DripageConfig]:
    """Load user-level app config from ~/.dripage/current_app."""
    home = Path.home()
    config_path = home / '.dripage' / 'current_app'

    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        if not data:
            return None

        browser_name = data.get('browser')
        if browser_name:
            config = _load_browser_config_by_name(browser_name)
            if config and hasattr(config.browser, 'app_id'):
                config.browser.app_id = data.get('app_id')
            return config

    except Exception as e:
        print(f"⚠️  Warning: Failed to load user app config: {e}", file=sys.stderr)

    return None


def _load_browser_config_by_name(browser_name: str) -> DripageConfig:
    """Load browser config by name from config/browsers.yaml.

    Args:
        browser_name: Browser name from browsers.yaml

    Returns:
        DripageConfig with loaded browser configuration
    """
    manager = ConfigManager()
    config = manager.load_config()

    from utils.chrome_manager import ChromeManager
    import configparser

    chrome_mgr = ChromeManager()
    browser_config = chrome_mgr.load_browser_config(browser_name)

    if browser_config:
        config.browser.name = browser_name
        config.browser.ini_file = browser_config.get('ini_file', '')

        # Load address from INI file
        ini_file = config.browser.ini_file
        if ini_file and Path(ini_file).exists():
            try:
                ini_config = configparser.ConfigParser()
                ini_config.read(ini_file, encoding='utf-8')
                if 'chromium_options' in ini_config:
                    address = ini_config['chromium_options'].get('address')
                    if address:
                        config.browser.address = address
            except Exception as e:
                print(f"⚠️  Warning: Failed to load INI file {ini_file}: {e}", file=sys.stderr)
    else:
        print(f"⚠️  Warning: Browser '{browser_name}' not found in config/browsers.yaml", file=sys.stderr)

    return config


def get_config_source() -> str:
    """Get information about current configuration source.

    Returns:
        String describing configuration source and current browser
    """
    manager = ConfigManager()
    config = get_current_config()

    source = getattr(config.browser, 'source', 'unknown')
    source_detail = getattr(config.browser, 'source_detail', 'N/A')

    result = {
        'source': source,
        'detail': source_detail,
        'browser': config.browser.name,
        'address': config.browser.address,
        'app_id': getattr(config.browser, 'app_id', 'N/A'),
        'cwd': str(Path.cwd())
    }

    return result


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
