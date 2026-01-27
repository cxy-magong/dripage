"""
Chrome Manager RPC Server - Minimal Implementation

Exposes ChromeManager methods via Pyro4 for remote procedure calls.
"""

import Pyro4
from utils.chrome_manager import ChromeManager

# Enable Pyro4 features
Pyro4.config.REQUIRE_EXPOSE = False
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.SERIALIZERS_ACCEPTED.add("pickle")
Pyro4.config.SERIALIZERS_ACCEPTED.add("marshal")
Pyro4.config.SERIALIZERS_ACCEPTED.add("serpent")
Pyro4.config.SERIALIZERS_ACCEPTED.add("json")


@Pyro4.expose
class ChromeManagerRPC:
    """
    RPC wrapper for ChromeManager - exposes all public methods.
    """

    def __init__(self):
        self.manager = ChromeManager()

    # Expose all ChromeManager methods
    def start_browser(self, name=None, address="127.0.0.1:19222",
                      user_data_dir="", browser_path=""):
        """Start a browser instance."""
        return self.manager.start_browser(name, address, user_data_dir, browser_path)

    def stop_browser(self, name=None):
        """Stop a browser instance."""
        return self.manager.stop_browser(name)

    def get_status(self, name=None):
        """Get browser status."""
        return self.manager.get_status(name)

    def get_cdp_url(self, name=None):
        """Get CDP WebSocket URL for a browser."""
        return self.manager.get_cdp_url(name)

    def load_browser_config(self, name):
        """Load browser configuration by name."""
        return self.manager.load_browser_config(name)


def start_server(host="0.0.0.0", port=9090):
    """Start the ChromeManager RPC server."""
    daemon = Pyro4.Daemon(host, port)
    uri = daemon.register(ChromeManagerRPC, objectId="ChromeManager")

    print(f"ChromeManager RPC Server started!")
    print(f"RPC URI: {uri}")
    print(f"Listening on: {host}:{port}")
    print("\nWaiting for client connections...")
    print("Press Ctrl+C to stop the server.\n")

    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        daemon.close()


if __name__ == "__main__":
    start_server()
