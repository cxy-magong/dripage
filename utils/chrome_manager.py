import argparse
import json
import os
import socket
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from .drission_page import create_browser

class ChromeManager:
    def __init__(self):
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        self.state_file = output_dir / "chrome_manager_state.json"
        self.browser = None

    def start_browser(self, address: str = "127.0.0.1:19222", user_data_dir: str = "", browser_path: str = "") -> Dict[str, Any]:
        if self._is_running():
            return {
                "success": False,
                "message": "Browser is already running. Use 'stop' first or check status.",
                "data": {}
            }
        
        try:
            self.browser = create_browser(address=address, user_data_dir=user_data_dir, browser_path=browser_path)
            cdp_url = self.browser.browser._ws_address
            pid = self.browser.process_id
            
            state = {
                "pid": pid,
                "cdp_url": cdp_url,
                "address": address,
                "user_data_dir": user_data_dir,
                "browser_path": browser_path,
                "start_time": datetime.now().isoformat(),
                "status": "running"
            }
            
            self._save_state(state)
            
            return {
                "success": True,
                "message": "Browser started successfully",
                "data": {
                    "cdp_url": cdp_url,
                    "address": address
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to start browser: {str(e)}",
                "data": {}
            }

    def stop_browser(self) -> Dict[str, Any]:
        state = self._load_state()
        
        if not state or state.get("status") != "running":
            return {
                "success": False,
                "message": "No running browser found",
                "data": {}
            }
        
        try:
            pid = state.get("pid")
            if pid:
                self._kill_process(pid)
            
            state_file = self.state_file
            if state_file.exists():
                state_file.unlink()
            
            return {
                "success": True,
                "message": "Browser stopped successfully",
                "data": {}
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to stop browser: {str(e)}",
                "data": {}
            }

    def get_status(self) -> Dict[str, Any]:
        state = self._load_state()
        
        if not state:
            return {
                "success": True,
                "message": "No browser state found",
                "data": {
                    "status": "stopped"
                }
            }
        
        if state.get("status") == "running":
            if self._is_running():
                return {
                    "success": True,
                    "message": "Browser status retrieved",
                    "data": {
                        "status": "running",
                        "cdp_url": state.get("cdp_url", ""),
                        "address": state.get("address", ""),
                        "start_time": state.get("start_time", "")
                    }
                }
            else:
                state["status"] = "stopped"
                self._save_state(state)
                return {
                    "success": True,
                    "message": "Browser status retrieved",
                    "data": {
                        "status": "stopped"
                    }
                }
        
        return {
            "success": True,
            "message": "Browser status retrieved",
            "data": state
        }

    def get_cdp_url(self) -> Dict[str, Any]:
        state = self._load_state()
        
        if not state or state.get("status") != "running":
            return {
                "success": False,
                "message": "No running browser found",
                "data": {}
            }
        
        if not self._is_running():
            state["status"] = "stopped"
            self._save_state(state)
            return {
                "success": False,
                "message": "Browser is not running",
                "data": {}
            }
        
        return {
            "success": True,
            "message": "CDP URL retrieved",
            "data": {
                "cdp_url": state.get("cdp_url", "")
            }
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

    def _is_running(self) -> bool:
        state = self._load_state()
        if not state or state.get("status") != "running":
            return False
        
        try:
            address = state.get("address", "127.0.0.1:19222")
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

    start_parser = subparsers.add_parser("start", help="Start browser")
    start_parser.add_argument("--address", default="127.0.0.1:19222", help="Browser address")
    start_parser.add_argument("--user-data-dir", default="", help="User data directory")
    start_parser.add_argument("--browser-path", default="", help="Browser path")

    subparsers.add_parser("stop", help="Stop browser")
    subparsers.add_parser("status", help="Get browser status")
    subparsers.add_parser("get-cdp", help="Get CDP URL")

    args = parser.parse_args()
    manager = ChromeManager()

    result = None
    
    if args.command == "start":
        result = manager.start_browser(args.address, args.user_data_dir, args.browser_path)
    elif args.command == "stop":
        result = manager.stop_browser()
    elif args.command == "status":
        result = manager.get_status()
    elif args.command == "get-cdp":
        result = manager.get_cdp_url()

    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
