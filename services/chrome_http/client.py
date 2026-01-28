#!/usr/bin/env python
"""
ChromeManager HTTP 客户端

提供简单的接口来调用 ChromeManager HTTP API。
"""

import httpx
from typing import Optional, Dict, Any


class ChromeManagerHTTPClient:
    """ChromeManager HTTP API 客户端"""

    def __init__(self, host: str = "localhost", port: int = 8000, timeout: int = 30):
        """
        初始化 HTTP 客户端

        Args:
            host: API 服务器主机
            port: API 服务器端口
            timeout: 请求超时（秒）
        """
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def start_browser(self, name: Optional[str] = None, address: str = "127.0.0.1:19222",
                    user_data_dir: str = "", browser_path: str = "") -> Dict[str, Any]:
        """启动浏览器"""
        payload = {
            "name": name,
            "address": address,
            "user_data_dir": user_data_dir,
            "browser_path": browser_path
        }
        response = self.client.post(f"{self.base_url}/api/browser/start", json=payload)
        response.raise_for_status()
        return response.json()

    def stop_browser(self, name: Optional[str] = None) -> Dict[str, Any]:
        """停止浏览器"""
        payload = {"name": name}
        response = self.client.post(f"{self.base_url}/api/browser/stop", json=payload)
        response.raise_for_status()
        return response.json()

    def get_status(self, name: Optional[str] = None) -> Dict[str, Any]:
        """获取浏览器状态"""
        params = {"name": name} if name else None
        response = self.client.get(f"{self.base_url}/api/browser/status", params=params)
        response.raise_for_status()
        return response.json()

    def get_cdp_url(self, name: Optional[str] = None) -> Dict[str, Any]:
        """获取 CDP URL"""
        params = {"name": name} if name else None
        response = self.client.get(f"{self.base_url}/api/browser/cdp", params=params)
        response.raise_for_status()
        return response.json()

    def load_browser_config(self, name: str) -> Dict[str, Any]:
        """加载浏览器配置"""
        response = self.client.get(f"{self.base_url}/api/browser/config/{name}")
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict[str, Any]:
        """健康检查"""
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def close(self):
        """关闭客户端"""
        self.client.close()


# 便捷函数
def get_client(host: str = "localhost", port: int = 8000, timeout: int = 30):
    """
    获取 HTTP 客户端实例

    Args:
        host: API 服务器主机
        port: API 服务器端口
        timeout: 请求超时（秒）

    Returns:
        ChromeManagerHTTPClient 实例
    """
    return ChromeManagerHTTPClient(host=host, port=port, timeout=timeout)
