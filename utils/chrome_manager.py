import argparse
import json
import os
import socket
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from DrissionPage import ChromiumOptions, ChromiumPage

# Import paths from config
import sys
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.paths import BROWSERS_CONFIG_FILE, OUTPUT_DIR, PROJECT_ROOT


class ChromeManager:
    def __init__(self):
        output_dir = OUTPUT_DIR
        output_dir.mkdir(exist_ok=True)
        self.state_file = output_dir / "chrome_manager_state.json"
        self.browsers = {}  # Dictionary to hold multiple browser instances: {name: browser_object}

    def load_browser_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load browser configuration from config/browsers.yaml by name.

        Args:
            name: Browser name defined in browsers.yaml

        Returns:
            Dictionary with browser configuration or None if not found
        """
        if not BROWSERS_CONFIG_FILE.exists():
            return None

        try:
            with open(BROWSERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config or 'browsers' not in config:
                return None

            for browser in config['browsers']:
                if browser.get('name') == name:
                    # Resolve INI file path relative to project root
                    ini_file = browser.get('ini_file')
                    if ini_file and not Path(ini_file).is_absolute():
                        ini_file = str(PROJECT_ROOT / ini_file)
                    browser['ini_file'] = ini_file
                    return browser

            return None
        except Exception as e:
            print(f"Error loading browser config: {e}", file=sys.stderr)
            return None

    def get_defined_browsers(self) -> list:
        """
        Get list of browser names defined in config/browsers.yaml.

        Returns:
            List of browser names
        """
        if not BROWSERS_CONFIG_FILE.exists():
            return []

        try:
            with open(BROWSERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not config or 'browsers' not in config:
                return []

            return [b.get('name') for b in config['browsers'] if b.get('name')]
        except Exception as e:
            print(f"Error loading browsers config: {e}", file=sys.stderr)
            return []

    def start_browser(self, name: Optional[str] = None, address: str = "127.0.0.1:19222",
                     user_data_dir: str = "", browser_path: str = "") -> Dict[str, Any]:
        """
        Start a browser instance.

        Args:
            name: Browser name from config/browsers.yaml. If None, uses direct parameters.
            address: Browser CDP address (used when name is None)
            user_data_dir: User data directory (used when name is None)
            browser_path: Browser executable path (used when name is None)

        Returns:
            Dictionary with operation result
        """
        # If name is provided, load from config
        if name:
            browser_config = self.load_browser_config(name)
            if not browser_config:
                return {
                    "success": False,
                    "message": f"Browser '{name}' not found in config/browsers.yaml",
                    "data": {}
                }

            # Check if browser with this name is already running
            if name in self.browsers:
                state = self._load_state()
                if state and name in state and state[name].get("status") == "running":
                    return {
                        "success": False,
                        "message": f"Browser '{name}' is already running. Use 'stop' first or check status.",
                        "data": {}
                    }

            # Load INI file
            ini_file = browser_config.get('ini_file')
            if not ini_file or not Path(ini_file).exists():
                return {
                    "success": False,
                    "message": f"INI file not found: {ini_file}",
                    "data": {}
                }

            try:
                # Load configuration from INI file using ChromiumOptions
                chrome_options = ChromiumOptions(ini_path=ini_file)
                # Set to connect to existing browser only (WSL compatible)
                chrome_options.existing_only = True
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to load INI configuration: {str(e)}",
                    "data": {}
                }

            # Override with direct parameters if provided
            if address and address != "127.0.0.1:19222":
                chrome_options.set_address(address)
            if user_data_dir:
                chrome_options.set_user_data_path(user_data_dir)
            if browser_path:
                chrome_options.set_browser_path(browser_path)

            # Get address from INI config for tracking
            address = chrome_options.address

        else:
            # Legacy mode: use direct parameters
            # Check if browser is already running (backward compatibility)
            if self._is_running():
                return {
                    "success": False,
                    "message": "Browser is already running. Use 'stop' first or check status.",
                    "data": {}
                }

            chrome_options = ChromiumOptions(read_file=False)
            chrome_options.set_address(address)
            if user_data_dir:
                chrome_options.set_user_data_path(user_data_dir)
            if browser_path:
                chrome_options.set_browser_path(browser_path)
            # Set to connect to existing browser only (WSL compatible)
            chrome_options.existing_only = True

        try:
            # Create browser instance
            browser = ChromiumPage(addr_or_opts=chrome_options)
            cdp_url = browser.browser._ws_address
            pid = browser.process_id

            # Determine browser name for tracking
            browser_name = name if name else "default"

            # Store browser instance
            self.browsers[browser_name] = browser

            # Create state entry
            state = self._load_state() or {}
            state[browser_name] = {
                "pid": pid,
                "cdp_url": cdp_url,
                "address": address,
                "user_data_dir": user_data_dir,
                "browser_path": browser_path,
                "start_time": datetime.now().isoformat(),
                "status": "running",
                "ini_file": ini_file if name else None
            }

            # Save state
            self._save_state(state)

            return {
                "success": True,
                "message": f"Browser '{browser_name}' started successfully",
                "data": {
                    "name": browser_name,
                    "cdp_url": cdp_url,
                    "address": address,
                    "pid": pid
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to start browser: {str(e)}",
                "data": {}
            }

    def stop_browser(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Stop a browser instance.

        Args:
            name: Browser name. If None, stops the default browser (backward compatibility).

        Returns:
            Dictionary with operation result
        """
        state = self._load_state()

        if not state:
            return {
                "success": False,
                "message": "No browser state found",
                "data": {}
            }

        # If name is provided, stop specific browser
        if name:
            if name not in state or state[name].get("status") != "running":
                return {
                    "success": False,
                    "message": f"No running browser found with name '{name}'",
                    "data": {}
                }

            # Kill browser process
            try:
                pid = state[name].get("pid")
                if pid:
                    self._kill_process(pid)

                # Remove from browsers dict
                if name in self.browsers:
                    del self.browsers[name]

                # Update state
                state[name]["status"] = "stopped"
                state[name]["stop_time"] = datetime.now().isoformat()
                self._save_state(state)

                return {
                    "success": True,
                    "message": f"Browser '{name}' stopped successfully",
                    "data": {
                        "name": name
                    }
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to stop browser '{name}': {str(e)}",
                    "data": {}
                }

        # Legacy mode: stop default browser
        else:
            # Find any running browser
            running_browsers = [k for k, v in state.items() if v.get("status") == "running"]
            if not running_browsers:
                return {
                    "success": False,
                    "message": "No running browser found",
                    "data": {}
                }

            # Stop all running browsers (legacy behavior)
            results = []
            for browser_name in running_browsers:
                try:
                    pid = state[browser_name].get("pid")
                    if pid:
                        self._kill_process(pid)

                    if browser_name in self.browsers:
                        del self.browsers[browser_name]

                    state[browser_name]["status"] = "stopped"
                    state[browser_name]["stop_time"] = datetime.now().isoformat()
                    results.append(browser_name)
                except Exception as e:
                    results.append(f"Error stopping {browser_name}: {e}")

            self._save_state(state)

            return {
                "success": True,
                "message": f"Stopped browsers: {', '.join(results)}",
                "data": {
                    "stopped_browsers": results
                }
            }

    def get_status(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get browser status.

        Args:
            name: Browser name. If None, returns status of all browsers.

        Returns:
            Dictionary with browser status information
        """
        state = self._load_state()

        if not state:
            return {
                "success": True,
                "message": "No browser state found",
                "data": {
                    "status": "stopped",
                    "browsers": {}
                }
            }

        # Handle backward compatibility: check if state is old flat format or new nested format
        is_old_format = "pid" in state and "cdp_url" in state and not any(isinstance(v, dict) for v in state.values())

        # If name is provided, return specific browser status
        if name:
            if is_old_format:
                # Old format: return "default" browser status
                browser_state = state
                browser_name = "default"
            else:
                # New format
                if name not in state:
                    return {
                        "success": True,
                        "message": f"Browser '{name}' not found",
                        "data": {
                            "status": "not_found"
                        }
                    }
                browser_state = state[name]
                browser_name = name

            if isinstance(browser_state, dict) and browser_state.get("status") == "running":
                if self._is_running(browser_state.get("address", "127.0.0.1:19222")):
                    return {
                        "success": True,
                        "message": f"Browser '{browser_name}' status retrieved",
                        "data": {
                            "name": browser_name,
                            "status": "running",
                            "cdp_url": browser_state.get("cdp_url", ""),
                            "address": browser_state.get("address", ""),
                            "pid": browser_state.get("pid"),
                            "start_time": browser_state.get("start_time", "")
                        }
                    }
                else:
                    # Browser not actually running, update state
                    browser_state["status"] = "stopped"
                    browser_state["stop_time"] = datetime.now().isoformat()
                    self._save_state(state)
                    return {
                        "success": True,
                        "message": f"Browser '{browser_name}' status retrieved",
                        "data": {
                            "name": browser_name,
                            "status": "stopped"
                        }
                    }

            return {
                "success": True,
                "message": f"Browser '{browser_name}' status retrieved",
                "data": {
                    "name": browser_name,
                    "status": browser_state.get("status", "unknown") if isinstance(browser_state, dict) else "unknown"
                }
            }

        # Return all browsers status
        browsers_status = {}
        defined_browsers = self.get_defined_browsers()

        if is_old_format:
            # Old format: return single "default" browser (only if no defined browsers)
            if not defined_browsers:
                if state.get("status") == "running":
                    if self._is_running(state.get("address", "127.0.0.1:19222")):
                        browsers_status["default"] = {
                            "status": "running",
                            "cdp_url": state.get("cdp_url", ""),
                            "address": state.get("address", ""),
                            "pid": state.get("pid"),
                            "start_time": state.get("start_time", "")
                        }
                    else:
                        # Browser not actually running, update state
                        state["status"] = "stopped"
                        state["stop_time"] = datetime.now().isoformat()
                        browsers_status["default"] = {"status": "stopped"}
                        self._save_state(state)
                else:
                    browsers_status["default"] = {"status": state.get("status", "unknown")}
        else:
            # New format: return only browsers defined in browsers.yaml
            for browser_name in defined_browsers:
                browser_state = state.get(browser_name)
                if isinstance(browser_state, dict) and browser_state.get("status") == "running":
                    if self._is_running(browser_state.get("address", "127.0.0.1:19222")):
                        browsers_status[browser_name] = {
                            "status": "running",
                            "cdp_url": browser_state.get("cdp_url", ""),
                            "address": browser_state.get("address", ""),
                            "pid": browser_state.get("pid"),
                            "start_time": browser_state.get("start_time", "")
                        }
                    else:
                        # Browser not actually running, update state
                        browser_state["status"] = "stopped"
                        browser_state["stop_time"] = datetime.now().isoformat()
                        browsers_status[browser_name] = {"status": "stopped"}
                        self._save_state(state)
                elif isinstance(browser_state, dict):
                    browsers_status[browser_name] = {"status": browser_state.get("status", "stopped")}
                else:
                    # Browser not in state file, show as stopped
                    browsers_status[browser_name] = {"status": "stopped"}

        return {
            "success": True,
            "message": "All browsers status retrieved",
            "data": {
                "browsers": browsers_status,
                "total": len(browsers_status),
                "running": sum(1 for b in browsers_status.values() if b.get("status") == "running")
            }
        }

    def get_cdp_url(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get CDP WebSocket URL for a browser.

        Args:
            name: Browser name. If None, gets CDP URL for default browser (backward compatibility).

        Returns:
            Dictionary with CDP URL
        """
        state = self._load_state()

        if not state:
            return {
                "success": False,
                "message": "No browser state found",
                "data": {}
            }

        # If name is provided, get specific browser's CDP URL
        if name:
            if name not in state or state[name].get("status") != "running":
                return {
                    "success": False,
                    "message": f"No running browser found with name '{name}'",
                    "data": {}
                }

            browser_state = state[name]
            if not self._is_running(browser_state.get("address", "127.0.0.1:19222")):
                browser_state["status"] = "stopped"
                self._save_state(state)
                return {
                    "success": False,
                    "message": f"Browser '{name}' is not running",
                    "data": {}
                }

            return {
                "success": True,
                "message": f"CDP URL retrieved for '{name}'",
                "data": {
                    "name": name,
                    "cdp_url": browser_state.get("cdp_url", "")
                }
            }

        # Legacy mode: get default browser CDP URL
        # Find any running browser
        for browser_name, browser_state in state.items():
            # Skip non-dictionary entries (e.g., 'total', 'running' counters)
            if not isinstance(browser_state, dict):
                continue
            if browser_state.get("status") == "running":
                if self._is_running(browser_state.get("address", "127.0.0.1:19222")):
                    return {
                        "success": True,
                        "message": "CDP URL retrieved",
                        "data": {
                            "name": browser_name,
                            "cdp_url": browser_state.get("cdp_url", "")
                        }
                    }

        return {
            "success": False,
            "message": "No running browser found",
            "data": {}
        }

    def _kill_process(self, pid: int):
        """Kill the browser process by PID (cross-platform)."""
        try:
            if os.name == 'nt':  # Windows
                os.system(f'taskkill /F /PID {pid} >nul 2>&1')
            else:  # Unix/Linux/Mac
                os.kill(pid, 9)
        except ProcessLookupError:
            pass  # Process already terminated

    def _save_state(self, state: Dict[str, Any]):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> Optional[Dict[str, Any]]:
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _is_running(self, address: str = "127.0.0.1:19222") -> bool:
        """Check if browser is running by checking if CDP port is open."""
        try:
            host, port = address.split(":")
            port = int(port)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()

            return result == 0
        except Exception:
            return False


def main():
    parser = argparse.ArgumentParser(description="Chrome Browser Manager")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start browser")
    start_parser.add_argument("--name", help="Browser name from config/browsers.yaml")
    start_parser.add_argument("--address", default="127.0.0.1:19222", help="Browser address (used when --name is not specified)")
    start_parser.add_argument("--user-data-dir", default="", help="User data directory")
    start_parser.add_argument("--browser-path", default="", help="Browser path")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop browser")
    stop_parser.add_argument("--name", help="Browser name to stop")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get browser status")
    status_parser.add_argument("--name", help="Browser name (if not specified, returns all browsers)")

    # Get CDP URL command
    cdp_parser = subparsers.add_parser("get-cdp", help="Get CDP URL")
    cdp_parser.add_argument("--name", help="Browser name")

    args = parser.parse_args()
    manager = ChromeManager()

    result = None

    if args.command == "start":
        result = manager.start_browser(args.name, args.address, args.user_data_dir, args.browser_path)
    elif args.command == "stop":
        result = manager.stop_browser(args.name)
    elif args.command == "status":
        result = manager.get_status(args.name)
    elif args.command == "get-cdp":
        result = manager.get_cdp_url(args.name)

    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
