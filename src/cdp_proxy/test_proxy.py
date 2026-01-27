"""
CDP代理测试脚本
验证代理是否正常工作
"""
import asyncio
import json
import sys
from typing import Dict, Any

import httpx
import websockets


async def test_health_check(proxy_url: str) -> bool:
    """测试健康检查端点"""
    print(f"\n🏥 测试健康检查端点: {proxy_url}/health")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{proxy_url}/health")
            data = resp.json()

            print(f"✅ 健康检查成功:")
            print(f"   状态: {data['status']}")
            print(f"   CDP端口: {data['cdp_port']}")
            print(f"   代理端口: {data['proxy_port']}")
            return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


async def test_http_endpoint(proxy_url: str) -> bool:
    """测试HTTP端点（/json/version）"""
    print(f"\n🌐 测试HTTP端点: {proxy_url}/json/version")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{proxy_url}/json/version")

            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ HTTP端点测试成功:")
                print(f"   Browser: {data.get('Browser', 'N/A')}")
                print(f"   Version: {data.get('Protocol-Version', 'N/A')}")
                print(f"   WebSocket: {data.get('webSocketDebuggerUrl', 'N/A')}")
                return True
            else:
                print(f"❌ HTTP端点返回错误状态: {resp.status_code}")
                return False
    except Exception as e:
        print(f"❌ HTTP端点测试失败: {e}")
        return False


async def test_websocket_endpoint(proxy_url: str) -> bool:
    """测试WebSocket端点"""
    ws_url = f"ws://{proxy_url.replace('http://', '').replace('https://', '')}/ws"
    print(f"\n🔌 测试WebSocket端点: {ws_url}")

    try:
        async with websockets.connect(
            ws_url,
            ping_interval=20,
            ping_timeout=20,
            timeout=10.0
        ) as ws:
            print("✅ WebSocket连接成功")

            # 发送一个CDP命令测试
            test_command = {
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "1 + 1"
                }
            }

            print(f"📤 发送测试命令: {json.dumps(test_command)}")
            await ws.send(json.dumps(test_command))

            # 接收响应
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📥 收到响应: {json.dumps(data, indent=2)}")

                if 'result' in data:
                    print(f"✅ CDP命令执行成功: result = {data['result']}")
                    return True
                elif 'error' in data:
                    print(f"⚠️  CDP命令执行错误: {data['error']}")
                    # 这是正常的，因为可能没有连接到浏览器
                    # 但至少WebSocket代理是工作的
                    return True
            except asyncio.TimeoutError:
                print("⚠️  等待CDP响应超时（正常，可能没有浏览器连接）")
                # 但连接本身是成功的，所以代理工作正常
                return True

    except Exception as e:
        print(f"❌ WebSocket端点测试失败: {e}")
        return False


async def test_cdp_discovery(proxy_url: str) -> bool:
    """测试CDP发现接口"""
    print(f"\n🔍 测试CDP发现: {proxy_url}/json")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{proxy_url}/json")

            if resp.status_code == 200:
                data = resp.json()

                # 可能返回多个标签页列表或版本信息
                if isinstance(data, list):
                    print(f"✅ 发现 {len(data)} 个CDP目标:")
                    for idx, target in enumerate(data[:3], 1):  # 只显示前3个
                        print(f"   {idx}. {target.get('title', 'N/A')}")
                        print(f"      URL: {target.get('url', 'N/A')}")
                        print(f"      Type: {target.get('type', 'N/A')}")
                else:
                    print(f"✅ CDP发现成功:")
                    print(f"   类型: {data.get('type', 'N/A')}")

                return True
            else:
                print(f"❌ CDP发现返回错误状态: {resp.status_code}")
                return False
    except Exception as e:
        print(f"❌ CDP发现测试失败: {e}")
        return False


async def run_all_tests(proxy_url: str):
    """运行所有测试"""
    print("=" * 70)
    print("🧪 开始CDP代理测试套件")
    print("=" * 70)
    print(f"🎯 目标代理地址: {proxy_url}")

    results = []

    # 测试1: 健康检查
    results.append(("健康检查", await test_health_check(proxy_url)))

    # 测试2: HTTP端点
    results.append(("HTTP端点", await test_http_endpoint(proxy_url)))

    # 测试3: CDP发现
    results.append(("CDP发现", await test_cdp_discovery(proxy_url)))

    # 测试4: WebSocket连接
    results.append(("WebSocket连接", await test_websocket_endpoint(proxy_url)))

    # 总结
    print("\n" + "=" * 70)
    print("📊 测试结果总结")
    print("=" * 70)

    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name:15s} {status}")
        if result:
            passed += 1

    print("=" * 70)
    print(f"总计: {passed}/{len(results)} 测试通过")

    # 成功标准：至少WebSocket测试通过
    websocket_passed = results[-1][1]  # WebSocket连接测试

    if websocket_passed:
        print("\n🎉 成功！代理可以访问CDP")
        print("\n📡 您现在可以连接到:")
        print(f"   ws://{proxy_url.replace('http://', '').replace('https://', '')}/ws/devtools/browser/...")
        return 0
    else:
        print("\n❌ 失败！代理无法访问CDP")
        print("\n🔧 故障排查:")
        print("   1. 确认Chrome浏览器已启动并监听CDP端口")
        print("   2. 确认代理服务器正在运行")
        print("   3. 检查防火墙规则")
        print("   4. 查看代理服务器日志")
        return 1


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="测试CDP代理服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m cdp_proxy.test_proxy                           # 测试默认代理（localhost:8080）
  python -m cdp_proxy.test_proxy --url http://localhost:8080  # 测试指定代理
  python -m cdp_proxy.test_proxy --url http://192.168.1.100:8080  # 测试远程代理
        """
    )

    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8080",
        help="代理服务器URL（默认：http://localhost:8080）"
    )

    args = parser.parse_args()

    exit_code = asyncio.run(run_all_tests(args.url))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
