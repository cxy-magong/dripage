#!/usr/bin/env python
"""
ChromeManager HTTP API 服务

提供 RESTful API 来管理浏览器实例。
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from utils.chrome_manager import ChromeManager
from utils.logu import get_logger

# Logger
logger = get_logger("chrome_http_server")


# Pydantic models
class StartBrowserRequest(BaseModel):
    name: Optional[str] = None
    address: str = "127.0.0.1:19222"
    user_data_dir: str = ""
    browser_path: str = ""


class StopBrowserRequest(BaseModel):
    name: Optional[str] = None


class StatusRequest(BaseModel):
    name: Optional[str] = None


class CdpUrlRequest(BaseModel):
    name: Optional[str] = None


class ConfigRequest(BaseModel):
    name: str


# Initialize
app = FastAPI(
    title="Chrome Manager API",
    description="HTTP API for managing Chrome browsers",
    version="1.0.0"
)

manager = ChromeManager()


# Health check
@app.get("/health")
async def health():
    """健康检查端点"""
    return {"status": "ok", "service": "chrome-manager-api"}


# Start browser
@app.post("/api/browser/start")
async def start_browser(request: StartBrowserRequest):
    """启动浏览器"""
    logger.info(f"启动浏览器请求: name={request.name}, address={request.address}")
    try:
        result = manager.start_browser(
            name=request.name,
            address=request.address,
            user_data_dir=request.user_data_dir,
            browser_path=request.browser_path
        )
        if result.get("success"):
            logger.info(f"浏览器启动成功: {request.name}")
        else:
            logger.warning(f"浏览器启动失败: {result.get('message')}")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"启动浏览器异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Stop browser
@app.post("/api/browser/stop")
async def stop_browser(request: StopBrowserRequest):
    """停止浏览器"""
    logger.info(f"停止浏览器请求: name={request.name}")
    try:
        result = manager.stop_browser(name=request.name)
        if result.get("success"):
            logger.info(f"浏览器停止成功: {request.name}")
        else:
            logger.warning(f"浏览器停止失败: {result.get('message')}")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"停止浏览器异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get status
@app.get("/api/browser/status")
async def get_status(name: Optional[str] = None):
    """获取浏览器状态"""
    logger.info(f"获取状态请求: name={name}")
    try:
        result = manager.get_status(name=name)
        logger.info(f"状态查询结果: {result.get('success')}")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"获取状态异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get CDP URL
@app.get("/api/browser/cdp")
async def get_cdp_url(name: Optional[str] = None):
    """获取 CDP URL"""
    logger.info(f"获取 CDP URL 请求: name={name}")
    try:
        result = manager.get_cdp_url(name=name)
        if result.get("success"):
            cdp_url = result.get("data", {}).get("cdp_url", "")
            logger.info(f"CDP URL 获取成功: {name} -> {cdp_url}")
        else:
            logger.warning(f"CDP URL 获取失败: {result.get('message')}")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"获取 CDP URL 异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Load config
@app.get("/api/browser/config/{name}")
async def load_browser_config(name: str):
    """加载浏览器配置"""
    logger.info(f"加载配置请求: {name}")
    try:
        result = manager.load_browser_config(name=name)
        if result:
            logger.info(f"配置加载成功: {name}")
            return JSONResponse(content={"success": True, "data": result})
        else:
            logger.warning(f"配置加载失败: 浏览器 '{name}' 不存在")
            raise HTTPException(status_code=404, detail=f"Browser '{name}' not found")
    except Exception as e:
        logger.error(f"加载配置异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Root endpoint
@app.get("/")
async def root():
    """根端点"""
    return {
        "service": "Chrome Manager API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "start_browser": "POST /api/browser/start",
            "stop_browser": "POST /api/browser/stop",
            "get_status": "GET /api/browser/status",
            "get_cdp_url": "GET /api/browser/cdp",
            "load_config": "GET /api/browser/config/{name}"
        }
    }


def start_server(host: str = "0.0.0.0", port: int = 8889):
    """启动 HTTP 服务器"""
    separator = "=" * 70
    logger.info(separator)
    logger.info("Chrome Manager HTTP API Server")
    logger.info(separator)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"API Docs: http://{host}:{port}/docs")
    logger.info(f"Health: http://{host}:{port}/health")
    logger.info("")
    logger.info("Waiting for requests...")
    logger.info("Press Ctrl+C to stop the server.")
    logger.info(separator)
    logger.info("")

    uvicorn.run(app, host=host, port=port, log_level="error")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chrome Manager HTTP API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")

    args = parser.parse_args()

    start_server(host=args.host, port=args.port)
