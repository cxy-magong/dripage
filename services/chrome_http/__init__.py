"""
Chrome Manager HTTP API Service

提供基于 FastAPI 的 HTTP RESTful API 来管理浏览器实例。
"""

from .server import start_server, app
from .client import ChromeManagerHTTPClient, get_client

__all__ = [
    "start_server",
    "app",
    "ChromeManagerHTTPClient",
    "get_client",
]
