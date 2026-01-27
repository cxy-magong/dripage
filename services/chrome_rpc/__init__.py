"""
Chrome Manager RPC Package

Provides remote procedure call (RPC) functionality for ChromeManager using Pyro4.
"""

from .server import ChromeManagerRPC, start_server
from .client import ChromeManagerClient, get_client

__all__ = [
    "ChromeManagerRPC",
    "start_server",
    "ChromeManagerClient",
    "get_client",
]
