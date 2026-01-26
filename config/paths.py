"""
Centralized path management for the Dripage project.

This module provides a single source of truth for all project paths,
making it easy to maintain and update directory structures.
"""
from pathlib import Path
from typing import Final


# ==================== Project Root ====================
# The root directory of the project (config directory's parent)
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent


# ==================== Output Directories ====================
# Main output directory
OUTPUT_DIR: Final[Path] = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Subdirectories under output
OUTPUT_DATA_DIR: Final[Path] = OUTPUT_DIR / "data"
OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_LOG_DIR: Final[Path] = OUTPUT_DIR / "log"
OUTPUT_LOG_DIR.mkdir(parents=True, exist_ok=True)


# ==================== Config Directories ====================
# Main config directory
CONFIG_DIR: Final[Path] = PROJECT_ROOT / "config"

# Individual config files
MCP_CONFIG_FILE: Final[Path] = CONFIG_DIR / "mcp_config.yaml"
MCPORTER_STDIO_FILE: Final[Path] = CONFIG_DIR / "mcporter.json"
MCPORTER_HTTP_FILE: Final[Path] = CONFIG_DIR / "mcporter-http.json"
MODELS_CONFIG_FILE: Final[Path] = CONFIG_DIR / "models_config.yaml"


# ==================== State Files ====================
# Process management state files
CHROME_MANAGER_STATE: Final[Path] = OUTPUT_DIR / "chrome_manager_state.json"
MCP_MANAGER_STATE: Final[Path] = OUTPUT_DIR / "mcp_manager_state.json"


# ==================== Utility Functions ====================
def ensure_output_dirs() -> None:
    """Ensure all output directories exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """Get the project root directory."""
    return PROJECT_ROOT


def get_output_dir() -> Path:
    """Get the main output directory."""
    return OUTPUT_DIR


def get_output_data_dir() -> Path:
    """Get the output data directory (for saved files)."""
    return OUTPUT_DATA_DIR


def get_output_log_dir() -> Path:
    """Get the output log directory."""
    return OUTPUT_LOG_DIR


def get_config_dir() -> Path:
    """Get the config directory."""
    return CONFIG_DIR


# ==================== Path Resolution Helper ====================
def resolve_path(relative_path: str) -> Path:
    """
    Resolve a relative path to an absolute path based on project root.

    Args:
        relative_path: Relative path from project root

    Returns:
        Absolute Path object
    """
    return PROJECT_ROOT / relative_path


# ==================== Path Validation ====================
def validate_paths() -> dict[str, bool]:
    """
    Validate that all critical paths exist or can be created.

    Returns:
        Dictionary with path names as keys and validity status as values
    """
    return {
        "project_root": PROJECT_ROOT.exists(),
        "output_dir": OUTPUT_DIR.exists(),
        "output_data_dir": OUTPUT_DATA_DIR.exists(),
        "output_log_dir": OUTPUT_LOG_DIR.exists(),
        "config_dir": CONFIG_DIR.exists(),
        "mcp_config": MCP_CONFIG_FILE.exists(),
        "mcporter_stdio": MCPORTER_STDIO_FILE.exists(),
        "mcporter_http": MCPORTER_HTTP_FILE.exists(),
    }


# ==================== Debug/Utility ====================
if __name__ == "__main__":
    """Print all path information for debugging."""
    import json

    print("=" * 60)
    print("Dripage Project Paths")
    print("=" * 60)
    print()

    print("Project Root:")
    print(f"  {PROJECT_ROOT}")
    print()

    print("Output Directories:")
    print(f"  Output:      {OUTPUT_DIR}")
    print(f"  Data:        {OUTPUT_DATA_DIR}")
    print(f"  Logs:        {OUTPUT_LOG_DIR}")
    print()

    print("Config Files:")
    print(f"  MCP Config:       {MCP_CONFIG_FILE}")
    print(f"  Mcporter STDIO:   {MCPORTER_STDIO_FILE}")
    print(f"  Mcporter HTTP:     {MCPORTER_HTTP_FILE}")
    print(f"  Models Config:     {MODELS_CONFIG_FILE}")
    print()

    print("State Files:")
    print(f"  Chrome Manager:    {CHROME_MANAGER_STATE}")
    print(f"  MCP Manager:       {MCP_MANAGER_STATE}")
    print()

    print("=" * 60)
    print("Path Validation")
    print("=" * 60)
    validation = validate_paths()
    for name, valid in validation.items():
        status = "✓" if valid else "✗"
        print(f"  {status} {name}")
    print()
