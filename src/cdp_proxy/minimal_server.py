"""
简化版CDP代理 - 只代理/devtools/browser/路径
"""
import asyncio
import logging
from typing import Any

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import Response

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "cdp-proxy-simple",
        "cdp_target": "localhost:19222"
    }


@app.websocket("/")
async def proxy_cdp(websocket: WebSocket):
    """代理CDP WebSocket连接"""
    target_url = "ws://localhost:19222/devtools/browser/"

    logger.info(f"WebSocket代理: {target_url}")

    try:
        async with websockets.connect(target_url, ping_interval=20, ping_timeout=20) as browser_ws:
            await websocket.accept()
            logger.info("WebSocket双向连接已建立")

            # 双向转发
            async def client_to_browser():
                try:
                    async for message in websocket.iter_text():
                        await browser_ws.send(message)
                        logger.debug(f"客户端→浏览器: {message[:50]}...")
                except WebSocketDisconnect:
                    logger.info("客户端断开")
                    raise
                except Exception as e:
                    logger.error(f"客户端消息转发错误: {e}")
                    raise

            async def browser_to_client():
                try:
                    async for message in browser_ws:
                        await websocket.send_text(message)
                        logger.debug(f"浏览器→客户端: {message[:50]}...")
                except Exception as e:
                    logger.error(f"浏览器消息转发错误: {e}")
                    raise

            # 并行运行转发任务
            try:
                await asyncio.gather(client_to_browser(), browser_to_client())
            except WebSocketDisconnect:
                logger.info("WebSocket连接已关闭")
            except Exception as e:
                logger.error(f"WebSocket转发错误: {e}")

    except WebSocketDisconnect:
        logger.info("客户端WebSocket断开")
    except Exception as e:
        logger.error(f"WebSocket代理错误: {e}")


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("🚀 简化CDP代理服务器启动中...")
    print("=" * 60)
    print("📍 监听地址: 0.0.0.0:8080")
    print("🎯 CDP目标: localhost:19222/devtools/browser/")
    print("=" * 60)
    print("\n📡 使用方法:")
    print("   WebSocket: ws://localhost:8080/")
    print("   Health:    http://localhost:8080/health")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8080)
