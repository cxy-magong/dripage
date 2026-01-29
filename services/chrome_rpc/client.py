"""
Chrome Manager RPC Client - Minimal Implementation

Client for calling ChromeManager methods via RPC.
"""

import Pyro4

# Configure serialization to match server
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.SERIALIZERS_ACCEPTED.add("pickle")
Pyro4.config.SERIALIZERS_ACCEPTED.add("marshal")
Pyro4.config.SERIALIZERS_ACCEPTED.add("serpent")
Pyro4.config.SERIALIZERS_ACCEPTED.add("json")


class ChromeManagerClient:
    """
    RPC client for ChromeManager - provides the same interface as ChromeManager.
    """

    def __init__(self, uri=None, host="localhost", port=9090):
        """
        Initialize the RPC client.

        Args:
            uri: Full Pyro4 URI (e.g., "PYRO:ChromeManager@localhost:9090")
            host: Server host (used if uri is not provided)
            port: Server port (used if uri is not provided)
        """
        if uri:
            self.uri = uri
        else:
            self.uri = f"PYRO:ChromeManager@{host}:{port}"

        self._proxy = Pyro4.Proxy(self.uri)

    # ChromeManager methods - all proxied
    def start_browser(self, name=None, address="127.0.0.1:19222",
                      user_data_dir="", browser_path=""):
        """Start a browser instance."""
        return self._proxy.start_browser(name, address, user_data_dir, browser_path)

    def stop_browser(self, name=None):
        """Stop a browser instance."""
        return self._proxy.stop_browser(name)

    def get_status(self, name=None):
        """Get browser status."""
        return self._proxy.get_status(name)

    def get_cdp_url(self, name=None):
        """Get CDP WebSocket URL for a browser."""
        return self._proxy.get_cdp_url(name)

    def load_browser_config(self, name):
        """Load browser configuration by name."""
        return self._proxy.load_browser_config(name)

    def close(self):
        """Close the proxy connection."""
        try:
            self._proxy._pyroRelease()
        except Exception:
            pass  # Ignore errors during cleanup


# Convenience function for quick usage
def get_client(uri=None, host="localhost", port=9090):
    """
    Get a ChromeManager RPC client instance.

    Args:
        uri: Full Pyro4 URI
        host: Server host
        port: Server port

    Returns:
        ChromeManagerClient instance
    """
    return ChromeManagerClient(uri, host, port)


if __name__ == "__main__":
    # Example usage
    import json

    client = get_client()

    # Example: Start a browser
    # result = client.start_browser(name="browser1")
    # print(json.dumps(result, indent=2, ensure_ascii=False))

    # Example: Get status
    # result = client.get_status()
    # print(json.dumps(result, indent=2, ensure_ascii=False))

    client.close()
