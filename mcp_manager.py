import argparse
import json
import os
import subprocess
import sys
import socket
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import psutil
from psutil import TimeoutExpired

# Import centralized path management
from config.paths import (
    PROJECT_ROOT,
    OUTPUT_DIR,
    OUTPUT_LOG_DIR,
    MCP_MANAGER_STATE,
    get_output_dir,
    get_output_log_dir,
)


class MCPManager:
    """Manager for MCP server processes (HTTP/STDIO)."""

    def __init__(self):
        """Initialize MCPManager with centralized paths."""
        self.state_file = MCP_MANAGER_STATE
        self.log_dir = OUTPUT_LOG_DIR
        self.output_dir = OUTPUT_DIR

        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def start_server(
        self,
        transport: str = "http",
        port: int = 8000,
        host: str = "127.0.0.1",
        config_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start MCP server in background.

        Args:
            transport: Transport type ('http' or 'stdio')
            port: Port for HTTP transport (ignored for stdio)
            host: Host for HTTP transport
            config_file: Optional config file path

        Returns:
            Dict with success status and process info
        """
        if self._is_running():
            return {
                "success": False,
                "message": "MCP server is already running. Use 'stop' first or check status.",
                "data": {}
            }

        try:
            # Get project directory from centralized paths
            project_dir = PROJECT_ROOT

            # Set up environment
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_dir)

            # Build command
            cmd = ["uv", "run", "mcp_server.py"]
            if transport == "http":
                cmd.append("http")

            # Start process
            # Windows: CREATE_NEW_PROCESS_GROUP to avoid Ctrl+C affecting child
            # Unix: detach process
            creation_flags = 0
            if os.name == 'nt':  # Windows
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP

            # Create log file for both stdout and stderr
            log_file = self.log_dir / f"mcp_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

            # Open log file for writing
            log_handle = log_file.open('w', encoding='utf-8')
            log_handle.write(f"[{datetime.now().isoformat()}] Starting MCP server...\n")
            log_handle.write(f"[{datetime.now().isoformat()}] Command: {' '.join(cmd)}\n")
            log_handle.write(f"[{datetime.now().isoformat()}] Working directory: {project_dir}\n")
            log_handle.flush()

            # Start process with subprocess.PIPE to avoid blocking
            # Don't read from pipes - let them buffer
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,  # Use PIPE but don't read
                stderr=subprocess.PIPE,  # Use PIPE but don't read
                stdin=subprocess.PIPE,  # Keep stdin open
                cwd=str(project_dir),  # Set working directory
                env=env,  # Set environment
                creationflags=creation_flags if creation_flags else None,
                start_new_session=True  # Detach from parent
            )

            log_handle.write(f"[{datetime.now().isoformat()}] Process started with PID: {process.pid}\n")
            log_handle.flush()

            # Wait for process to start
            import time
            time.sleep(8)  # Give more time for uvicorn to fully start (increased from 5 to 8)

            # Check if process is still running
            if process.poll() is not None:
                # Process terminated
                exit_code = process.poll()
                log_handle.write(f"[{datetime.now().isoformat()}] Process terminated with exit code: {exit_code}\n")
                log_handle.flush()
                log_handle.close()

                # Read log content for error message
                with open(log_file, 'r', encoding='utf-8') as f:
                    error = f.read()
                return {
                    "success": False,
                    "message": f"Server failed to start (exit code: {exit_code}). Check log: {log_file}\n\nLast 500 chars of log:\n{error[-500:]}",
                    "data": {}
                }

            # For HTTP mode, verify port is listening
            if transport == "http":
                host = host if host else "127.0.0.1"
                port_to_check = port

                log_handle.write(f"[{datetime.now().isoformat()}] Checking if port {port_to_check} is listening...\n")
                log_handle.flush()

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port_to_check))
                sock.close()

                if result != 0:
                    # Port not open - wait a bit more and try again
                    log_handle.write(f"[{datetime.now().isoformat()}] Port {port_to_check} not yet open, waiting...\n")
                    log_handle.flush()
                    time.sleep(7)  # Increased from 3 to 7 seconds

                    # Second check
                    if process.poll() is not None:
                        exit_code = process.poll()
                        log_handle.write(f"[{datetime.now().isoformat()}] Process exited during startup (exit code: {exit_code})\n")
                        log_handle.write(f"[{datetime.now().isoformat()}] Process may have failed to bind to port\n")
                        log_handle.close()

                        with open(log_file, 'r', encoding='utf-8') as f:
                            error = f.read()
                        return {
                            "success": False,
                            "message": f"Server exited before port was open (exit code: {exit_code}). Check log: {log_file}",
                            "data": {}
                        }

                    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock2.settimeout(2)
                    result2 = sock2.connect_ex((host, port_to_check))
                    sock2.close()

                    if result2 != 0:
                        log_handle.write(f"[{datetime.now().isoformat()}] ERROR: Port {port_to_check} still not open after 6 seconds\n")
                        log_handle.write(f"[{datetime.now().isoformat()}] Process may be running but HTTP server failed to start. Check log: {log_file}\n")
                        log_handle.close()

                        return {
                            "success": False,
                            "message": f"Server started but port {port_to_check} is not listening after 6 seconds. The process may be running but HTTP server failed to start. Check log: {log_file}",
                            "data": {}
                        }

                log_handle.write(f"[{datetime.now().isoformat()}] Port {port_to_check} is open - server ready\n")
                log_handle.flush()

            # For HTTP mode, find actual uvicorn child process and verify health
            # because uv spawns Python which spawns uvicorn. We need to find uvicorn.
            if transport == "http":
                try:
                    log_handle.write(f"[{datetime.now().isoformat()}] Finding actual HTTP server PID...\n")
                    log_handle.flush()

                    actual_pid = self._find_http_server_pid(host, port)
                    if actual_pid and actual_pid != process.pid:
                        log_handle.write(f"[{datetime.now().isoformat()}] Found actual HTTP server PID: {actual_pid}\n")
                        log_handle.flush()
                    elif actual_pid is None:
                        # Could not find uvicorn PID, use parent PID
                        actual_pid = process.pid
                        log_handle.write(f"[{datetime.now().isoformat()}] Could not find uvicorn PID, using parent PID: {actual_pid}\n")
                        log_handle.flush()

                    # Update state with actual PID
                    state = {
                        "pid": actual_pid,
                        "parent_pid": process.pid if actual_pid != process.pid else None,
                        "transport": transport,
                        "port": port,
                        "host": host,
                        "config_file": config_file,
                        "start_time": datetime.now().isoformat(),
                        "status": "running",
                        "command": " ".join(cmd),
                        "log_file": str(log_file)
                    }
                    self._save_state(state)

                    # Perform health check BEFORE reporting success
                    log_handle.write(f"[{datetime.now().isoformat()}] Performing health check...\n")
                    log_handle.flush()

                    is_healthy, health_message = self._verify_server_health(host, port, timeout=15)

                    if is_healthy:
                        log_handle.write(f"[{datetime.now().isoformat()}] Health check passed: {health_message}\n")
                        log_handle.write(f"[{datetime.now().isoformat()}] MCP server startup complete - HEALTHY\n")
                        log_handle.flush()

                        parent_msg = f", Parent PID: {process.pid}" if state.get("parent_pid") else ""
                        return {
                            "success": True,
                            "message": f"MCP server started successfully (PID: {actual_pid}{parent_msg}) - {health_message}",
                            "data": {
                                "pid": actual_pid,
                                "parent_pid": state.get("parent_pid"),
                                "transport": transport,
                                "url": f"http://{host}:{port}",
                                "health": "healthy",
                                "health_message": health_message
                            }
                        }
                    else:
                        log_handle.write(f"[{datetime.now().isoformat()}] Health check failed: {health_message}\n")
                        log_handle.write(f"[{datetime.now().isoformat()}] Server port is open but HTTP verification failed\n")
                        log_handle.flush()

                        # Update state to unhealthy
                        state["status"] = "unhealthy"
                        state["health_message"] = health_message
                        self._save_state(state)

                        return {
                            "success": False,
                            "message": f"MCP server port is open but health check failed: {health_message}. The process may be running but HTTP server is not responding correctly. Check log: {log_file}",
                            "data": {
                                "pid": actual_pid,
                                "transport": transport,
                                "url": f"http://{host}:{port}",
                                "health": "unhealthy",
                                "health_message": health_message,
                                "log_file": str(log_file)
                            }
                        }
                finally:
                    # Ensure log handle is closed
                    try:
                        if not log_handle.closed:
                            log_handle.close()
                    except:
                        pass
            else:
                # Non-HTTP mode - close log handle
                log_handle.write(f"[{datetime.now().isoformat()}] MCP server startup complete\n")
                log_handle.close()

            # Save state
            state = {
                "pid": process.pid,
                "transport": transport,
                "port": port if transport == "http" else None,
                "host": host,
                "config_file": config_file,
                "start_time": datetime.now().isoformat(),
                "status": "running",
                "command": " ".join(cmd),
                "log_file": str(log_file)
            }

            self._save_state(state)

            return {
                "success": True,
                "message": f"MCP server started successfully (PID: {process.pid})",
                "data": {
                    "pid": process.pid,
                    "transport": transport,
                    "url": f"http://{host}:{port}" if transport == "http" else None
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to start MCP server: {str(e)}",
                "data": {}
            }

    def stop_server(self) -> Dict[str, Any]:
        """Stop MCP server with graceful shutdown and verification."""
        state = self._load_state()

        if not state or state.get("status") != "running":
            return {
                "success": False,
                "message": "No running MCP server found",
                "data": {}
            }

        try:
            pid = state.get("pid")
            parent_pid = state.get("parent_pid")
            transport = state.get("transport")
            host = state.get("host", "127.0.0.1")
            port = state.get("port", 8000)

            # Log the stop action
            log_file = self.log_dir / "mcp_manager_debug.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Stopping MCP server (PID: {pid}, Parent PID: {parent_pid}, Transport: {transport})\n")

            # For HTTP mode, verify port is still open before stopping
            if transport == "http":
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    port_open = sock.connect_ex((host, port)) == 0
                    sock.close()

                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[{datetime.now().isoformat()}] Port {host}:{port} is {'open' if port_open else 'closed'} before stopping\n")
                except Exception as e:
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[{datetime.now().isoformat()}] Error checking port before stop: {e}\n")

            # Try graceful shutdown first (SIGTERM)
            # This allows uvicorn to close libuv handles properly
            if pid:
                self._kill_process_graceful(pid)

            # Also kill parent process if different
            if parent_pid and parent_pid != pid:
                # Give a short delay before killing parent
                import time
                time.sleep(1)
                self._kill_process_graceful(parent_pid)

            # Wait for port to close (HTTP mode)
            if transport == "http":
                import time
                max_wait = 15  # Wait up to 15 seconds for port to close
                wait_interval = 0.5
                elapsed = 0

                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] Waiting for port {host}:{port} to close...\n")

                while elapsed < max_wait:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        port_open = sock.connect_ex((host, port)) == 0
                        sock.close()

                        if not port_open:
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f"[{datetime.now().isoformat()}] Port {host}:{port} closed after {elapsed:.1f}s\n")
                            break

                        elapsed += wait_interval
                        time.sleep(wait_interval)
                    except Exception as e:
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f"[{datetime.now().isoformat()}] Error checking port during wait: {e}\n")
                        elapsed += wait_interval
                        time.sleep(wait_interval)

                # Verify processes are actually gone
                import psutil
                for check_pid in [pid, parent_pid]:
                    if check_pid:
                        try:
                            psutil.Process(check_pid)
                            # Process still exists - try force kill
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f"[{datetime.now().isoformat()}] PID {check_pid} still exists after {elapsed}s, force killing\n")
                            self._kill_process_force(check_pid)
                        except psutil.NoSuchProcess:
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f"[{datetime.now().isoformat()}] PID {check_pid} confirmed terminated\n")

            # Remove state file
            if self.state_file.exists():
                self.state_file.unlink()

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] MCP server stopped successfully\n")

            return {
                "success": True,
                "message": "MCP server stopped successfully",
                "data": {
                    "stopped_pid": pid
                }
            }

        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Error stopping MCP server: {e}\n")
            return {
                "success": False,
                "message": f"Failed to stop MCP server: {str(e)}",
                "data": {}
            }

    def restart_server(
        self,
        transport: str = "http",
        port: int = 8000,
        host: str = "127.0.0.1"
    ) -> Dict[str, Any]:
        """Restart MCP server."""
        stop_result = self.stop_server()

        if not stop_result["success"] and "already" not in stop_result["message"].lower():
            # Failed to stop and not because it wasn't running
            return stop_result

        # Wait a moment for cleanup
        import time
        time.sleep(1)

        return self.start_server(transport, port, host)

    def _verify_server_health(self, host: str, port: int, timeout: int = 15) -> tuple[bool, str]:
        """Verify MCP server health.

        FastMCP uses SSE (Server-Sent Events) for HTTP transport.
        We verify health by checking if the server responds to HTTP requests.

        Args:
            host: Server host
            port: Server port
            timeout: Timeout for health check in seconds

        Returns:
            Tuple of (is_healthy, message)
        """
        import requests
        import socket

        try:
            # First, check if port is listening
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            port_result = sock.connect_ex((host, port))
            sock.close()

            if port_result != 0:
                return False, f"Port {port} is not listening"

            # Port is open, now try to access MCP endpoint
            server_url = f"http://{host}:{port}/mcp"

            log_handle = self.log_dir / "mcp_manager_debug.log"
            with open(log_handle, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Attempting HTTP health check to {server_url}\n")

            # FastMCP HTTP mode responds with JSON-RPC error when accessed with wrong headers
            # This confirms the server is running
            try:
                response = requests.get(server_url, timeout=timeout)
                with open(log_handle, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] HTTP health check: {server_url} returned {response.status_code}\n")

                # Any response from FastMCP indicates it's running
                # Response will be an error (need SSE) or JSON-RPC response
                if response.status_code in [200, 400, 404, 406, 500]:
                    # Try to parse as JSON to confirm it's FastMCP
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            with open(log_handle, 'a', encoding='utf-8') as f:
                                f.write(f"[{datetime.now().isoformat()}] HTTP health check: FastMCP server confirmed running (status {response.status_code})\n")
                            return True, "Server is healthy (FastMCP responding)"
                    except:
                        # Not JSON, but still responding
                        with open(log_handle, 'a', encoding='utf-8') as f:
                            f.write(f"[{datetime.now().isoformat()}] HTTP health check: Server responding (not JSON, status {response.status_code})\n")
                        return True, "Server is healthy (HTTP responding)"
            except requests.RequestException as e:
                with open(log_handle, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] HTTP health check failed: {e}\n")

            return False, "Server port is open but HTTP verification failed"

        except Exception as e:
            return False, f"Health check error: {str(e)}"

    def _is_running(self) -> bool:
        """Check if MCP server process is running."""
        state = self._load_state()

        if not state or state.get("status") != "running":
            return False

        pid = state.get("pid")
        transport = state.get("transport")

        # For HTTP mode, first check if port is open (more reliable than PID)
        if transport == "http":
            host = state.get("host", "127.0.0.1")
            port = state.get("port", 8000)

            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()

                if result != 0:
                    # Port not open - try to find actual server process
                    actual_pid = self._find_http_server_pid(host, port)
                    if actual_pid:
                        log_file = self.log_dir / "mcp_manager_debug.log"
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f"[{datetime.now().isoformat()}] Port not open, found server at PID {actual_pid}\n")
                        # Update state with correct PID
                        state["pid"] = actual_pid
                        self._save_state(state)
                        return True  # Consider it running if we found the process

                    # No process found, definitely not running
                    log_file = self.log_dir / "mcp_manager_debug.log"
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[{datetime.now().isoformat()}] Port {host}:{port} not open, no server process found\n")
                    return False

            except Exception as e:
                log_file = self.log_dir / "mcp_manager_debug.log"
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] Error checking port {host}:{port}: {e}\n")
                return False

        # Check if process exists using psutil
        try:
            proc = psutil.Process(pid)
            process_running = proc.is_running()

            # Also check status - avoid zombie processes
            status = proc.status()
            if status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                return False

            if not process_running:
                return False

        except psutil.NoSuchProcess:
            return False
        except Exception as e:
            # Log error for debugging
            log_file = self.log_dir / "mcp_manager_debug.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Error checking process {pid}: {e}\n")
            return False

        return True

    def _find_http_server_pid(self, host: str, port: int) -> Optional[int]:
        """Find the actual HTTP server process PID.

        uv spawns Python which spawns uvicorn. We need to find uvicorn.
        """
        log_file = self.log_dir / "mcp_manager_debug.log"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] Searching for HTTP server PID on port {port}...\n")

        try:
            found_pids = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    info = proc.as_dict(['pid', 'name', 'cmdline'])

                    # Check cmdline for uvicorn or mcp_server processes
                    cmdline = info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()

                        # Look for uvicorn process with our port
                        if 'uvicorn' in cmdline_str and str(port) in cmdline_str:
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f"[{datetime.now().isoformat()}] Found uvicorn PID: {info['pid']}\n")
                            found_pids.append(info['pid'])
                            # Don't return immediately - there might be multiple

                        # Also look for mcp_server process directly
                        if 'mcp_server.py' in cmdline_str and str(port) in cmdline_str:
                            with open(log_file, 'a', encoding='utf-8') as f:
                                f.write(f"[{datetime.now().isoformat()}] Found mcp_server PID: {info['pid']}\n")
                            found_pids.append(info['pid'])

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Total found PIDs: {found_pids}\n")

            # Return first found PID or None
            return found_pids[0] if found_pids else None

        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Error finding HTTP server PID: {e}\n")
            import traceback
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Traceback: {traceback.format_exc()}\n")

        return None

    def _kill_process_graceful(self, pid: int, timeout: int = 10):
        """Kill process gracefully (SIGTERM) with extended timeout for uvicorn.

        Args:
            pid: Process PID to terminate
            timeout: Seconds to wait for graceful termination (default: 10s for uvicorn)
        """
        log_file = self.log_dir / "mcp_manager_debug.log"

        try:
            process = psutil.Process(pid)

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Attempting graceful termination of PID {pid} (timeout: {timeout}s)\n")

            # Send SIGTERM
            process.terminate()

            # Wait for process to exit
            try:
                process.wait(timeout=timeout)
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] PID {pid} terminated gracefully\n")
            except psutil.TimeoutExpired:
                # Process didn't exit gracefully
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] PID {pid} did not terminate gracefully after {timeout}s\n")
                raise TimeoutExpired("Process did not terminate gracefully", timeout)

        except psutil.NoSuchProcess:
            # Process already gone
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] PID {pid} not found (already terminated)\n")
        except TimeoutExpired:
            # Re-raise to let caller know graceful shutdown failed
            raise
        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Error in graceful termination of PID {pid}: {e}\n")

    def _kill_process_force(self, pid: int):
        """Force kill process (SIGKILL) - used as last resort.

        Args:
            pid: Process PID to force kill
        """
        log_file = self.log_dir / "mcp_manager_debug.log"

        try:
            process = psutil.Process(pid)

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Force killing PID {pid}\n")

            process.kill()

            # Wait briefly to confirm
            try:
                process.wait(timeout=2)
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] PID {pid} killed forcefully\n")
            except psutil.TimeoutExpired:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] PID {pid} may still be running after force kill\n")

        except psutil.NoSuchProcess:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] PID {pid} not found (already gone)\n")
        except Exception as e:
            # Fallback to OS-specific kill
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] psutil failed to force kill PID {pid}: {e}, trying OS-specific method\n")

            try:
                if os.name == 'nt':  # Windows
                    result = os.system(f"taskkill /F /PID {pid} >nul 2>&1")
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[{datetime.now().isoformat()}] Used taskkill /F to kill PID {pid} (result: {result})\n")
                else:  # Unix/Linux/Mac
                    os.kill(pid, 9)  # SIGKILL
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"[{datetime.now().isoformat()}] Used SIGKILL to terminate PID {pid}\n")
            except Exception as e2:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{datetime.now().isoformat()}] OS-specific force kill also failed: {e2}\n")

    def _kill_process(self, pid: int):
        """Legacy method - delegates to graceful then force kill.

        Args:
            pid: Process PID to terminate
        """
        log_file = self.log_dir / "mcp_manager_debug.log"

        try:
            # Try graceful first
            self._kill_process_graceful(pid, timeout=10)
        except TimeoutExpired:
            # Graceful failed, force kill
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Graceful termination failed for PID {pid}, force killing\n")
            self._kill_process_force(pid)
        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] Error in _kill_process for PID {pid}: {e}, force killing\n")
            self._kill_process_force(pid)

    def _save_state(self, state: Dict[str, Any]):
        """Save process state to file."""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> Optional[Dict[str, Any]]:
        """Load process state from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _calculate_uptime(self, start_time: str) -> str:
        """Calculate human-readable uptime."""
        if not start_time:
            return "unknown"

        try:
            start = datetime.fromisoformat(start_time)
            delta = datetime.now() - start

            total_seconds = int(delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except Exception:
            return "unknown"

    def _get_exit_reason(self, pid: int, transport: str) -> str:
        """Determine why the process exited."""

        try:
            proc = psutil.Process(pid)
            status = proc.status()

            if status == psutil.STATUS_ZOMBIE:
                return "zombie process"
            elif status == psutil.STATUS_DEAD:
                return "dead process"

            # Check if HTTP port is open for HTTP transport
            if transport == "http":
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(("127.0.0.1", 8000))
                    sock.close()

                    if result != 0:
                        return "port not listening"

                except:
                    pass

            return "process terminated"

        except psutil.NoSuchProcess:
            return "process not found"
        except Exception as e:
            return f"check error: {str(e)}"

    def get_status(self) -> Dict[str, Any]:
        """Get MCP server status with comprehensive health check."""
        state = self._load_state()

        if not state:
            return {
                "success": True,
                "message": "No MCP server state found",
                "data": {
                    "status": "stopped"
                }
            }

        if state.get("status") == "running":
            transport = state.get("transport")
            host = state.get("host", "127.0.0.1")
            port = state.get("port", 8000)

            # For HTTP transport, verify actual server health
            if transport == "http":
                is_healthy, health_message = self._verify_server_health(host, port, timeout=5)

                if is_healthy:
                    # Server is truly healthy
                    uptime = self._calculate_uptime(state.get("start_time"))
                    return {
                        "success": True,
                        "message": "MCP server status retrieved",
                        "data": {
                            "status": "running",
                            "health": "healthy",
                            "health_message": health_message,
                            "pid": state.get("pid"),
                            "transport": transport,
                            "url": f"http://{host}:{port}",
                            "start_time": state.get("start_time"),
                            "uptime": uptime,
                            "log_file": state.get("log_file")
                        }
                    }
                else:
                    # Server reported unhealthy
                    state["status"] = "unhealthy"
                    state["health_message"] = health_message
                    self._save_state(state)

                    return {
                        "success": True,
                        "message": f"MCP server is unhealthy - {health_message}",
                        "data": {
                            "status": "unhealthy",
                            "health_message": health_message,
                            "pid": state.get("pid"),
                            "transport": transport,
                            "url": f"http://{host}:{port}",
                            "start_time": state.get("start_time"),
                            "log_file": state.get("log_file")
                        }
                    }

            # For stdio, just check process
            if self._is_running():
                return {
                    "success": True,
                    "message": "MCP server status retrieved",
                    "data": {
                        "status": "running",
                        "pid": state.get("pid"),
                        "transport": transport,
                        "start_time": state.get("start_time"),
                        "uptime": self._calculate_uptime(state.get("start_time"))
                    }
                }
            else:
                # Process died or port not open - update state
                state["status"] = "stopped"
                exit_reason = self._get_exit_reason(state.get("pid"), state.get("transport"))
                state["exit_reason"] = exit_reason
                self._save_state(state)

                return {
                    "success": True,
                    "message": f"MCP server status retrieved (process died - {exit_reason})",
                    "data": {
                        "status": "stopped",
                        "exit_reason": exit_reason,
                        "log_file": state.get("log_file")
                    }
                }

        return {
            "success": True,
            "message": "MCP server status retrieved",
            "data": state
        }

    def get_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Get recent logs (if available)."""
        state = self._load_state()

        if not state or state.get("status") != "running":
            return {
                "success": False,
                "message": "No running MCP server found",
                "data": {}
            }

        # Logs are written by server to output/log/
        log_dir = OUTPUT_LOG_DIR
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log"))
            if log_files:
                latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest_log, 'r', encoding='utf-8') as f:
                        log_lines = f.readlines()
                        recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines

                    return {
                        "success": True,
                        "message": f"Retrieved recent logs from {latest_log.name}",
                        "data": {
                            "log_file": str(latest_log),
                            "recent_lines": [line.strip() for line in recent_logs]
                        }
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Failed to read logs: {str(e)}",
                        "data": {}
                    }

        return {
            "success": False,
            "message": "No log files found",
            "data": {}
        }


def main():
    parser = argparse.ArgumentParser(
        description="Dripage MCP Server Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start HTTP server
  uv run mcp_manager.py start

  # Start HTTP server on custom port
  uv run mcp_manager.py start --port 8080

  # Check status
  uv run mcp_manager.py status

  # Stop server
  uv run mcp_manager.py stop

  # Restart server
  uv run mcp_manager.py restart

  # View recent logs
  uv run mcp_manager.py logs --lines 100
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start MCP server")
    start_parser.add_argument(
        "--transport",
        choices=["http", "stdio"],
        default="http",
        help="Transport type (default: http)"
    )
    start_parser.add_argument("--port", type=int, default=8000, help="Port for HTTP transport (default: 8000)")
    start_parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP transport (default: 127.0.0.1)")

    # Stop command
    subparsers.add_parser("stop", help="Stop MCP server")

    # Restart command
    restart_parser = subparsers.add_parser("restart", help="Restart MCP server")
    restart_parser.add_argument(
        "--transport",
        choices=["http", "stdio"],
        default="http",
        help="Transport type (default: http)"
    )
    restart_parser.add_argument("--port", type=int, default=8000, help="Port for HTTP transport (default: 8000)")
    restart_parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP transport (default: 127.0.0.1)")

    # Status command
    subparsers.add_parser("status", help="Get MCP server status")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View recent logs")
    logs_parser.add_argument("--lines", type=int, default=50, help="Number of log lines to show (default: 50)")

    args = parser.parse_args()
    manager = MCPManager()

    result = None

    if args.command == "start":
        result = manager.start_server(
            transport=args.transport,
            port=args.port,
            host=args.host
        )
    elif args.command == "stop":
        result = manager.stop_server()
    elif args.command == "restart":
        result = manager.restart_server(
            transport=args.transport,
            port=args.port,
            host=args.host
        )
    elif args.command == "status":
        result = manager.get_status()
    elif args.command == "logs":
        result = manager.get_logs(lines=args.lines)

    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
