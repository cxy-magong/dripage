"""
简单的CDP代理实现（不使用fastapi-proxy-lib）
直接使用FastAPI + websockets
"""
import asyncio
from typing import Dict, Any

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.requests import Request
from starlette.responses import Response
import websockets
import sys
import os

# 导入统一的日志系统
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.logu import get_logger

logger = get_logger("cdp_proxy_simple", console=True, file_level="DEBUG")


app = FastAPI()


@app.get("/health")
async def health_check():
    """健康检查端点"""
    logger.info("健康检查请求")
    return {
        "status": "ok",
        "service": "cdp-proxy-simple",
        "cdp_target": "localhost:19222"
    }


@app.get("/")
async def root_info():
    """根路径信息"""
    logger.info("根路径信息请求")
    return {
        "service": "CDP Proxy Server",
        "version": "0.1.0",
        "endpoints": {
            "websocket": "/ws/",
            "http": "/",
            "health": "/health",
        },
        "usage": {
            "ws": "ws://{{your-host}}:8080/ws/devtools/browser/{{session_id}}",
            "http": "http://{{your-host}}:8080/json/version",
        },
    }


@app.get("/json/version")
async def proxy_http_version():
    """代理HTTP请求到Chrome /json/version"""
    url = "http://localhost:19222/json/version"
    logger.info(f"代理HTTP请求到: {url}")

    try:
        client = httpx.AsyncClient(timeout=30.0)
        resp = await client.get(url)
        logger.info(f"HTTP响应状态码: {resp.status_code}")

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            media_type=resp.headers.get("content-type", "application/json"),
        )
    except Exception as e:
        logger.error(f"HTTP代理错误: {e}", exc_info=True)
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=502,
            media_type="application/json",
        )


@app.get("/json")
async def proxy_http_json():
    """代理HTTP请求到Chrome /json"""
    url = "http://localhost:19222/json"
    logger.info(f"代理HTTP请求到: {url}")

    try:
        client = httpx.AsyncClient(timeout=30.0)
        resp = await client.get(url)
        logger.info(f"HTTP响应状态码: {resp.status_code}")

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            media_type=resp.headers.get("content-type", "application/json"),
        )
    except Exception as e:
        logger.error(f"HTTP代理错误: {e}", exc_info=True)
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=502,
            media_type="application/json",
        )


@app.get("/{path:path}")
async def proxy_http_path(path: str, request: Request):
    """代理所有HTTP请求到Chrome"""
    url = f"http://localhost:19222/{path}"
    logger.info(f"代理HTTP请求到: {url}")

    try:
        client = httpx.AsyncClient(timeout=30.0)
        resp = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
            params=request.query_params,
        )

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            media_type=resp.headers.get("content-type", resp.headers.get("content-type")),
        )
    except Exception as e:
        logger.error(f"HTTP代理错误: {e}", exc_info=True)
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=502,
            media_type="application/json",
        )


@app.websocket("/ws/{path:path}")
async def proxy_websocket(websocket: WebSocket, path: str):
    """代理WebSocket连接到Chrome CDP"""
    target_url = f"ws://localhost:19222/{path}"
    logger.info(f"WebSocket代理: {path} → {target_url}")

    try:
        async with websockets.connect(
            target_url,
            ping_interval=20,
            ping_timeout=20,
            max_size=2**20  # 1MB max message size
        ) as browser_ws:
            await websocket.accept()
            logger.info("✅ WebSocket连接已建立")
            logger.info(f"   客户端: {websocket.client.host if websocket.client else 'N/A'}")
            logger.info(f"   目标: {target_url}")

            # 双向转发
            async def client_to_browser():
                """从客户端到浏览器的消息转发"""
                try:
                    async for message in websocket.iter_text():
                        logger.info(f"📥 收到客户端消息 (长度: {len(message)})")
                        logger.debug(f"   内容: {message[:100]}..." if len(message) > 100 else message)
                        await browser_ws.send(message)
                except WebSocketDisconnect:
                    logger.info("🔴 客户端断开连接")
                    raise
                except Exception as e:
                    logger.error(f"❌ 客户端消息转发错误: {e}")
                    raise

            async def browser_to_client():
                """从浏览器到客户端的消息转发"""
                try:
                    async for message in browser_ws:
                        logger.info(f"📤 收到浏览器消息 (长度: {len(message)})")
                        logger.debug(f"   内容: {message[:100]}..." if len(message) > 100 else message)
                        await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"❌ 浏览器消息转发错误: {e}")
                    raise

            # 并行运行两个转发任务
            await asyncio.gather(client_to_browser(), browser_to_client())

            logger.info("✅ WebSocket连接已关闭")

    except WebSocketDisconnect:
        logger.info("客户端WebSocket断开")
    except Exception as e:
        logger.error(f"WebSocket代理错误: {e}", exc_info=True)


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("🚀 CDP代理服务器（简化版）启动中...")
    print("=" * 60)
    print("📍 监听地址: 0.0.0.0:8080")
    print("🎯 CDP目标: localhost:19222")
    print("=" * 60)
    print("\n📡 访问端点:")
    print("   WebSocket: ws://your-ip:8080/ws/devtools/browser/session-id")
    print("   HTTP:      http://your-ip:8080/json/version")
    print("   Health:    http://your-ip:8080/health")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8080)
