"""
CDP 代理服务器实现
使用 fastapi-proxy-lib 实现HTTP/WebSocket代理
"""
import asyncio
import logging
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi_proxy_lib.fastapi.app import reverse_ws_app, reverse_http_app

from .config import ProxyConfig


logger = logging.getLogger(__name__)


class CDPProxyServer:
    """CDP代理服务器"""

    def __init__(self, config: Optional[ProxyConfig] = None):
        """
        初始化代理服务器

        Args:
            config: 代理配置，如果为None则从环境变量加载
        """
        self.config = config or ProxyConfig.from_env()
        self.app: Optional[FastAPI] = None
        self.server: Optional[uvicorn.Server] = None

        self._setup_logging()
        self._create_app()

    def _setup_logging(self):
        """配置日志"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info("日志系统已初始化")

    def _create_app(self):
        """创建FastAPI应用和代理路由"""
        logger.info("创建CDP代理应用...")

        # 创建httpx客户端（用于连接本地Chrome）
        # 禁用代理以避免循环
        client = httpx.AsyncClient(mounts={"all://": None})

        # 创建WebSocket代理（用于CDP WebSocket连接）
        ws_proxy_app = reverse_ws_app(
            client=client,
            base_url=f"ws://localhost:{self.config.cdp_port}/",
            keepalive_ping_interval_seconds=self.config.keepalive_ping_interval,
            keepalive_ping_timeout_seconds=self.config.keepalive_ping_timeout,
        )
        logger.info(f"WebSocket代理已配置: ws://localhost:{self.config.cdp_port}/")

        # 创建HTTP代理（用于CDP HTTP端点，如/json/version）
        http_proxy_app = reverse_http_app(
            client=client,
            base_url=f"http://localhost:{self.config.cdp_port}/",
        )
        logger.info(f"HTTP代理已配置: http://localhost:{self.config.cdp_port}/")

        # 创建主FastAPI应用
        self.app = FastAPI(
            title="CDP Proxy Server",
            description="Chrome DevTools Protocol HTTP/WebSocket Proxy",
            version="0.1.0",
        )

        # 挂载代理路由
        self.app.mount("/ws/", app=ws_proxy_app)
        self.app.mount("/", app=http_proxy_app)

        # 添加健康检查端点
        @self.app.get("/health")
        async def health_check():
            """健康检查端点"""
            return {
                "status": "ok",
                "service": "cdp-proxy",
                "cdp_port": self.config.cdp_port,
                "proxy_port": self.config.proxy_port,
            }

        # 添加根路径信息
        @self.app.get("/")
        async def root_info():
            """根路径信息"""
            return {
                "service": "CDP Proxy Server",
                "version": "0.1.0",
                "endpoints": {
                    "websocket": f"/ws/",
                    "http": "/",
                    "health": "/health",
                },
                "usage": {
                    "ws": f"ws://{{your_host}}:{self.config.proxy_port}/ws/devtools/browser/{{session_id}}",
                    "http": f"http://{{your_host}}:{self.config.proxy_port}/json/version",
                },
            }

        logger.info("FastAPI应用创建完成")

    def get_uvicorn_config(self) -> uvicorn.Config:
        """获取uvicorn配置"""
        return uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.proxy_port,
            log_level=self.config.log_level,
            access_log=True,
        )

    async def serve(self):
        """启动代理服务器"""
        config = self.get_uvicorn_config()
        self.server = uvicorn.Server(config)

        logger.info("=" * 60)
        logger.info("🚀 CDP代理服务器启动中...")
        logger.info("=" * 60)
        logger.info(f"📍 代理地址: {self.config.host}:{self.config.proxy_port}")
        logger.info(f"🎯 CDP目标: localhost:{self.config.cdp_port}")
        logger.info("=" * 60)
        logger.info("\n📡 访问端点:")
        logger.info(f"   WebSocket: ws://{{your-ip}}:{self.config.proxy_port}/ws/devtools/browser/...")
        logger.info(f"   HTTP:      http://{{your-ip}}:{self.config.proxy_port}/json/version")
        logger.info(f"   Health:    http://{{your-ip}}:{self.config.proxy_port}/health")
        logger.info("=" * 60)

        try:
            await self.server.serve()
        except KeyboardInterrupt:
            logger.info("\n🛑 代理服务器已停止")
        except Exception as e:
            logger.error(f"❌ 代理服务器错误: {e}", exc_info=True)
            raise

    def run(self):
        """同步运行代理服务器"""
        asyncio.run(self.serve())


async def main():
    """主函数"""
    config = ProxyConfig.from_env()
    logger.info(f"\n{config}\n")

    server = CDPProxyServer(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
