"""
CDP Proxy 配置管理
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProxyConfig:
    """代理配置"""
    # Chrome CDP端口（本地）
    cdp_port: int = 19222

    # 代理服务器端口（外部访问）
    proxy_port: int = 8080

    # 监听地址（0.0.0.0表示所有接口）
    host: str = "0.0.0.0"

    # 日志级别
    log_level: str = "info"

    # WebSocket keepalive配置
    keepalive_ping_interval: int = 20
    keepalive_ping_timeout: int = 20

    @classmethod
    def from_env(cls) -> 'ProxyConfig':
        """从环境变量加载配置"""
        return cls(
            cdp_port=int(os.getenv("CDP_PORT", "19222")),
            proxy_port=int(os.getenv("PROXY_PORT", "8080")),
            host=os.getenv("PROXY_HOST", "0.0.0.0"),
            log_level=os.getenv("LOG_LEVEL", "info"),
            keepalive_ping_interval=int(os.getenv("KEEPALIVE_INTERVAL", "20")),
            keepalive_ping_timeout=int(os.getenv("KEEPALIVE_TIMEOUT", "20")),
        )

    def __str__(self) -> str:
        return (
            f"ProxyConfig("
            f"  CDP端口: {self.cdp_port}\n"
            f"  代理端口: {self.proxy_port}\n"
            f"  监听地址: {self.host}\n"
            f"  日志级别: {self.log_level}"
        )
