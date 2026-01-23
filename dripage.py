#!/usr/bin/env python
"""
Dripage CLI wrapper script.
This allows running the CLI with: uv run python dripage.py
"""
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from cli import cli

if __name__ == '__main__':
    cli()
