#!/usr/bin/env python
"""
测试 HTTP API 和 CDP WebSocket 连接

完整验证：
1. 通过 HTTP API 启动浏览器
2. 获取 CDP URL
3. 验证 CDP URL 格式（地址匹配）
4. 通过 WebSocket 连接到浏览器
5. 发送 CDP 命令验证交互
6. 清理
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_http.client import ChromeManagerHTTPClient
import websockets
import asyncio


async def test_cdp_connection(cdp_url: str):
    """测试 CDP WebSocket 连接"""
    print(f"\n{'=' * 70}")
    print("  测试 5: CDP WebSocket 连接")
    print('=' * 70)

    try:
        # 提取 WebSocket 地址
        ws_url = cdp_url.replace("webSocketDebuggerUrl", "")
        print(f"连接到 WebSocket: {ws_url}")

        # 连接到 CDP WebSocket
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket 连接成功")

            # 发送 CDP 命令
            commands = [
                {"id": 1, "method": "Page.enable", "params": {}},
                {"id": 2, "method": "Page.navigate", "params": {"url": "about:blank"}},
                {"id": 3, "method": "Runtime.enable", "params": {}}
            ]

            for cmd in commands:
                await websocket.send(json.dumps(cmd))
                print(f"  发送命令: {cmd['method']}")
                response = await websocket.recv()
                print(f"  收到响应: {response[:100]}...")

        print("\n✅ 测试 5 通过: WebSocket 连接和命令执行成功")
        return True

    except Exception as e:
        print(f"\n❌ WebSocket 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_http_api(client: ChromeManagerHTTPClient):
    """测试 HTTP API"""
    print("=" * 70)
    print("  Chrome Manager HTTP API 和 CDP 集成测试")
    print("=" * 70)

    # 测试 1: 健康检查
    print("\n" + "-" * 70)
    print("测试 1: 健康检查")
    print("-" * 70)
    health = client.health()
    print(f"健康检查结果: {json.dumps(health, indent=2, ensure_ascii=False)}")

    if health.get("status") != "ok":
        print("❌ 测试 1 失败: 服务器不健康")
        return False

    print("✅ 测试 1 通过: 服务器运行正常")

    # 测试 2: 启动浏览器（先检查是否已在运行）
    print("\n" + "-" * 70)
    print("测试 2: 启动浏览器（先检查状态）")
    print("-" * 70)

    # 先检查状态
    print("检查浏览器状态...")
    status_result = client.get_status(name="browser1")
    print(f"状态检查结果: {json.dumps(status_result, indent=2, ensure_ascii=False)}")

    is_running = False
    if status_result.get("success"):
        browsers = status_result.get("data", {}).get("browsers", {})
        browser1_status = browsers.get("browser1", {}).get("status", "")
        is_running = (browser1_status == "running")

    if is_running:
        print("⚠️  浏览器 browser1 已经在运行")
        print("跳过启动，直接使用现有浏览器")
        # 获取现有浏览器的 CDP URL
        cdp_result = client.get_cdp_url(name="browser1")
        cdp_url = cdp_result.get("data", {}).get("cdp_url", "")
        address = cdp_result.get("data", {}).get("address", "")
    else:
        print("浏览器未运行，启动新的浏览器实例...")
        result = client.start_browser(name="browser1")

        if not result.get("success"):
            print(f"❌ 启动浏览器失败: {result.get('message')}")
            return False

        browser_data = result.get("data", {})
        cdp_url = browser_data.get("cdp_url", "")
        address = browser_data.get("address", "")

    print(f"浏览器地址: {address}")
    print(f"CDP URL: {cdp_url}")

    # 验证地址匹配
    print("\n" + "-" * 70)
    print("验证: 地址匹配检查")
    print("-" * 70)

    expected_address = "127.0.0.1:19222"
    if address == expected_address:
        print(f"✅ 地址匹配: {address}")
    else:
        print(f"❌ 地址不匹配: 期望 {expected_address}, 实际 {address}")
        return False

    # 验证 CDP URL 格式
    print("\n" + "-" * 70)
    print("验证: CDP URL 格式检查")
    print("-" * 70)

    if "webSocketDebuggerUrl" in cdp_url:
        cdp_ws_url = cdp_url.replace("webSocketDebuggerUrl", "")
        print(f"✅ WebSocket URL: {cdp_ws_url}")
        print(f"✅ CDP URL 包含 webSocketDebuggerUrl 字段")
    else:
        print("❌ CDP URL 格式不正确")
        return False

    # 等待浏览器完全启动
    print("\n等待浏览器启动（3秒）...")
    time.sleep(3)

    # 测试 3: 获取 CDP URL
    print("\n" + "-" * 70)
    print("测试 3: 获取 CDP URL")
    print("-" * 70)
    result = client.get_cdp_url(name="browser1")
    cdp_url = result.get("data", {}).get("cdp_url", "")

    print(f"CDP URL: {cdp_url}")

    if not cdp_url:
        print("❌ 测试 3 失败: 无法获取 CDP URL")
        return False

    print("✅ 测试 3 通过: 成功获取 CDP URL")

    # 测试 4: WebSocket 连接
    print("\n" + "-" * 70)
    print("测试 4: WebSocket 连接测试")
    print("-" * 70)

    # 在新的事件循环中运行 WebSocket 测试
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_cdp_connection(cdp_url))

    if not success:
        print("❌ 测试 4 失败: WebSocket 连接失败")
        return False

    print("\n✅ 测试 4 通过: WebSocket 连接和交互成功")

    # 测试 5: 清理
    print("\n" + "-" * 70)
    print("测试 5: 清理")
    print("-" * 70)
    result = client.stop_browser(name="browser1")
    print(f"清理结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    if not result.get("success"):
        print("❌ 测试 5 失败: 清理失败")
        return False

    print("✅ 测试 5 通过: 浏览器已停止")

    return True


def main(host="localhost", port=8889):
    """主函数"""
    try:
        # 创建客户端
        print(f"\n{'=' * 70}")
        print(f"  连接到 HTTP API 服务器: {host}:{port}")
        print('=' * 70)

        client = ChromeManagerHTTPClient(host=host, port=port)

        # 测试 HTTP API
        success = test_http_api(client)

        if success:
            print("\n" + "=" * 70)
            print("  🎉 所有测试通过！🎉")
            print("=" * 70)
            print("\n✅ 测试总结:")
            print("   ✅ 服务器健康检查通过")
            print("   ✅ 浏览器启动成功")
            print("   ✅ 地址匹配验证通过 (127.0.0.1:19222)")
            print("   ✅ CDP URL 格式验证通过 (包含 webSocketDebuggerUrl)")
            print("   ✅ CDP URL 获取成功")
            print("   ✅ WebSocket 连接和交互成功")
            print("   ✅ 浏览器清理成功")
            print("\n💡 结论:")
            print("   HTTP API 完全正常工作")
            print("   CDP WebSocket 可以正常连接和交互")
            print("   地址配置正确 (127.0.0.1:19222)")
        else:
            print("\n" + "=" * 70)
            print("  ❌ 测试失败")
            print("=" * 70)

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            client.close()
            print("\n✅ 客户端连接已关闭")
        except Exception as e:
            print(f"关闭客户端时出错: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试 HTTP API 和 CDP WebSocket 连接")
    parser.add_argument("--host", default="localhost", help="API 服务器主机（默认: localhost）")
    parser.add_argument("--port", type=int, default=8889, help="API 服务器端口（默认: 8889）")

    args = parser.parse_args()

    success = main(host=args.host, port=args.port)
    sys.exit(0 if success else 1)
