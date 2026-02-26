"""
Network packet capture module for Dripage CLI.

Provides background packet capture using DrissionPage's Network listener API.
Captures packets and saves them to files for filtering and analysis.
"""
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, asdict, field

from click import echo
from config.settings import get_current_config, ConfigManager
from cli.browser import get_page_object


# Global capture state
_capture_thread: Optional[threading.Thread] = None
_capture_running: bool = False
_capture_instance: Optional['NetworkCapture'] = None  # Forward reference
_capture_file: Optional[Any] = None
_packets_queue: List[Dict[str, Any]] = []
_lock = threading.Lock()


@dataclass
class PacketFilter:
    """Packet capture filter criteria."""
    url_contains: Optional[str] = None
    content_type: Optional[str] = None
    method: Optional[str] = None
    response_contains: Optional[str] = None
    status_code: Optional[int] = None


class NetworkCapture:
    """Manages network packet capture using DrissionPage's listener API."""

    def __init__(self, page_object: Optional[Any] = None, config: Optional[Dict] = None):
        """
        Initialize NetworkCapture.

        Args:
            page_object: Page object for capture. If None, will get from browser.
            config: Capture configuration from cli_config.
        """
        self.page = page_object
        self.config = config or get_current_config().capture

        # Output directory
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def start_capture(self, filter_criteria: Optional[PacketFilter] = None) -> bool:
        """
        Start background packet capture.

        Args:
            filter_criteria: Optional filter to apply to captured packets.

        Returns:
            True if started successfully, False otherwise.
        """
        global _capture_running, _capture_thread

        if _capture_running:
            echo("⚠️  Packet capture is already running")
            return False

        if not self.page:
            echo("✗ No browser page connected")
            return False

        try:
            # Build targets for DrissionPage listener
            targets = []
            if filter_criteria:
                if filter_criteria.url_contains:
                    targets.append(filter_criteria.url_contains)
                if filter_criteria.content_type:
                    targets.append(f'resourceType:"{filter_criteria.content_type}"')
                if filter_criteria.method:
                    targets.append(f'method:"{filter_criteria.method}"')
                if filter_criteria.response_contains:
                    targets.append(filter_criteria.response_contains)

            # Start listener with targets
            if targets:
                self.page.listen.start(*targets if targets else True)
            else:
                self.page.listen.start(targets=True)

            _capture_running = True
            echo(f"✓ Packet capture started (filters: {self._format_filter(filter_criteria)})")

            # Start background thread to capture packets
            _capture_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True
            )
            _capture_thread.start()

            return True

        except Exception as e:
            echo(f"✗ Failed to start packet capture: {e}")
            return False

    def stop_capture(self) -> bool:
        """
        Stop packet capture and save remaining packets.

        Returns:
            True if stopped successfully, False otherwise.
        """
        global _capture_running, _capture_thread, _capture_file, _packets_queue

        if not _capture_running:
            echo("⚠️  Packet capture is not running")
            return False

        try:
            # Stop listener
            self.page.listen.stop()

            # Save remaining packets to file
            if _packets_queue:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.output_dir / f"packets_{timestamp}.jsonl"

                echo(f"💾 Saving {_packets_queue} packets to {output_file}")

                with open(output_file, 'w', encoding='utf-8') as f:
                    for packet in _packets_queue:
                        f.write(json.dumps(packet, ensure_ascii=False) + '\n')

                echo(f"✓ Saved {_packets_queue} packets to {output_file}")
                echo(f"📊 Total packets: {_packets_queue}")
            else:
                echo("✓ No packets to save")

            _capture_running = False
            _packets_queue.clear()

            if _capture_thread and _capture_thread.is_alive():
                _capture_thread.join(timeout=5)

            echo("✓ Packet capture stopped")
            return True

        except Exception as e:
            echo(f"✗ Failed to stop packet capture: {e}")
            return False

    def _capture_loop(self, filter_criteria: Optional[PacketFilter] = None, timeout: Optional[float] = None):
        """
        Background loop to continuously capture packets.

        Args:
            filter_criteria: Filter to apply to captured packets.
            timeout: Timeout in seconds. None for unlimited.
        """
        global _capture_running, _packets_queue, _lock

        start_time = time.time()

        while _capture_running:
            try:
                # Wait for packet with timeout
                packet = self.page.listen.wait(count=1, timeout=timeout)

                if packet:
                    # Apply filter
                    if self._matches_filter(packet, filter_criteria):
                        with _lock:
                            packet_data = self._packet_to_dict(packet)
                            _packets_queue.append(packet_data)
                            # Print summary
                            echo(f"📦 Packet: {packet.url} | {packet.method} | {packet.response.status}")
                    else:
                        # Packet filtered out
                        echo(f"🚫 Filtered: {packet.url} | {packet.method}")
            except Exception as e:
                if _capture_running:
                    echo(f"⚠️  Capture error: {e}")
                break

            # Check timeout
            if timeout and (time.time() - start_time) >= timeout:
                echo(f"⏱️  Capture timeout reached ({timeout}s)")
                break

    def query_packets(self, limit: int = 100, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query captured packets from file.

        Args:
            limit: Maximum number of packets to return.
            filter_query: Optional jq-style filter query.

        Returns:
            List of packet dictionaries.
        """
        # Find most recent packet file
        packet_files = sorted(self.output_dir.glob("packets_*.jsonl"), reverse=True)

        if not packet_files:
            echo("ℹ️  No packet files found")
            return []

        # Load packets from most recent file
        latest_file = packet_files[0]
        results = []

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= limit:
                        break

                    try:
                        packet = json.loads(line.strip())
                        # Apply text filter if provided
                        if not filter_query or self._matches_text_filter(packet, filter_query):
                            results.append(packet)
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            echo(f"✗ Failed to load packets: {e}")
            return []

        echo(f"✓ Found {len(results)} packets")
        return results

    def _packet_to_dict(self, packet: Any) -> Dict[str, Any]:
        """Convert DrissionPage DataPacket object to dictionary."""
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'url': packet.url,
                'method': packet.method,
                'status_code': packet.response.status if packet.response else None,
                'resource_type': packet.resourceType if hasattr(packet, 'resourceType') else None,
                'tab_id': packet.tab_id if hasattr(packet, 'tab_id') else None,
                'frame_id': packet.frameId if hasattr(packet, 'frame_id') else None,
            }

            # Request info
            if packet.request:
                result['request_headers'] = dict(packet.request.headers) if hasattr(packet.request, 'headers') else {}
                result['request_body'] = packet.request.postData if hasattr(packet.request, 'postData') else None
            else:
                result['request_headers'] = {}
                result['request_body'] = None

            # Response info
            if packet.response:
                result['response_headers'] = dict(packet.response.headers) if hasattr(packet.response, 'headers') else {}
                result['response_body'] = packet.response.raw_body if hasattr(packet.response, 'raw_body') else None
                result['response_size'] = packet.response.encodedDataLength if hasattr(packet.response, 'encodedDataLength') else None
            else:
                result['response_headers'] = {}
                result['response_body'] = None
                result['response_size'] = None

            return result
        except Exception as e:
            echo(f"⚠️  Failed to convert packet: {e}")
            return {}

    def _matches_filter(self, packet: Any, filter_criteria: Optional[PacketFilter]) -> bool:
        """Check if packet matches filter criteria."""
        if not filter_criteria:
            return True

        packet_url = packet.url if hasattr(packet, 'url') else ''
        packet_method = packet.method if hasattr(packet, 'method') else ''
        packet_status = packet.response.status if packet.response and hasattr(packet.response, 'status') else None
        packet_type = packet.resourceType if hasattr(packet, 'resourceType') else ''

        # Check URL filter
        if filter_criteria.url_contains and filter_criteria.url_contains.lower() not in packet_url.lower():
            return False

        # Check content type filter
        if filter_criteria.content_type and packet_type:
            if filter_criteria.content_type.lower() not in packet_type.lower():
                return False

        # Check method filter
        if filter_criteria.method and packet_method != filter_criteria.method.lower():
            return False

        # Check status code filter
        if filter_criteria.status_code and packet_status != filter_criteria.status_code:
            return False

        # Check response contains filter
        if filter_criteria.response_contains:
            packet_response = packet.response.raw_body if packet.response and hasattr(packet.response, 'raw_body') else ''
            if isinstance(packet_response, str) and filter_criteria.response_contains.lower() not in packet_response.lower():
                return False

        return True

    def _matches_text_filter(self, packet: Dict[str, Any], filter_query: str) -> bool:
        """Check if packet matches text-based filter query (jq-like)."""
        try:
            # Simple implementation: check if any field contains the query
            query_lower = filter_query.lower()
            packet_str = json.dumps(packet).lower()

            # Support simple jq-like queries: .field, contains(), has()
            if '.contains(' in filter_query:
                field_name = filter_query.split('.')[1].strip()
                return field_name in packet and query_lower in packet[field_name].lower()

            if 'contains(' in filter_query:
                search_term = filter_query.replace('contains(', '').replace(')', '').strip()
                return search_term in packet_str

            if 'has(' in filter_query:
                field_name = filter_query.split('.')[1].strip()
                return field_name in packet and packet[field_name] is not None

            # Default: check if query is anywhere in packet
            return query_lower in packet_str

        except Exception:
            return True

    def _format_filter(self, filter_criteria: Optional[PacketFilter]) -> str:
        """Format filter criteria for display."""
        if not filter_criteria:
            return "all"

        parts = []
        if filter_criteria.url_contains:
            parts.append(f"url:{filter_criteria.url_contains}")
        if filter_criteria.content_type:
            parts.append(f"type:{filter_criteria.content_type}")
        if filter_criteria.method:
            parts.append(f"method:{filter_criteria.method}")
        if filter_criteria.status_code:
            parts.append(f"status:{filter_criteria.status_code}")

        return ", ".join(parts) if parts else "all"

    def is_running(self) -> bool:
        """Check if capture is currently running."""
        return _capture_running


def get_global_capture() -> NetworkCapture:
    """Get global capture instance."""
    # Need page object, will be created when needed
    return None


# Thread-safe access
def start_global_capture(page_object: Any, filter_criteria: Optional[PacketFilter] = None) -> bool:
    """Start global capture with given page and filter."""
    global _capture_running, _capture_instance

    if _capture_running:
        echo("⚠️  Capture is already running")
        return False

    capture = NetworkCapture(page_object=page_object)
    if capture.start_capture(filter_criteria):
        _capture_instance = capture
        return True
    return False


def stop_global_capture() -> bool:
    """Stop global capture."""
    global _capture_running, _capture_instance

    if not _capture_running or not _capture_instance:
        echo("⚠️  Packet capture is not running")
        return False

    return _capture_instance.stop_capture()


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--url', help='Page URL for capture test')
    def test_capture(url):
        from cli_browser import start_browser, stop_browser

        # Start browser
        start_result = start_browser()
        if not start_result['success']:
            print(f"Failed to start browser: {start_result['message']}")
            return

        try:
            # Get page
            from cli_browser import get_page_object
            page = get_page_object()

            if url:
                page.get(url)

            # Start capture
            capture = NetworkCapture(page_object=page)
            capture.start_capture()

            # Wait for packets
            import time
            time.sleep(5)

            # Stop capture
            capture.stop_capture()

            # Stop browser
            stop_browser()

        except Exception as e:
            print(f"Error: {e}")
            stop_browser()
