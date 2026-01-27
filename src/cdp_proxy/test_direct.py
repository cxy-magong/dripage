"""
简单的CDP代理测试脚本
"""
import asyncio
import json
import sys

import httpx
import websockets


async def test_direct_cdp():
    """直接测试Chrome CDP端口"""
    print("🔍 测试1: 直接访问Chrome CDP (端口19222）")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("http://localhost:19222/json/version")

            if resp.status_code == 200:
                data = resp.json()
                print("✅ 直接CDP访问成功:")
                print(f"   Browser: {data.get('Browser', 'N/A')}")
                print(f"   WebSocket URL: {data.get('webSocketDebuggerUrl', 'N/A')}")
                return True
            else:
                print(f"❌ 直接CDP访问失败，状态码: {resp.status_code}")
                return False
    except Exception as e:
        print(f"❌ 直接CDP访问错误: {e}")
        return False


async def test_websocket_connection():
    """测试WebSocket连接到Chrome CDP"""
    print("\n🔌 测试2: WebSocket连接到Chrome CDP")

    try:
        async with websockets.connect(
            "ws://localhost:19222/devtools/browser/",
            ping_interval=20,
            ping_timeout=20,
            timeout=10.0
        ) as ws:
            print("✅ WebSocket连接成功")

            # 发送CDP命令
            cmd = {
                "id": 1,
                "method": "Page.navigate",
                "params": {"url": "about:blank"}
            }

            print(f"📤 发送命令: {json.dumps(cmd)}")
            await ws.send(json.dumps(cmd))

            try:
                # 接收响应（超时5秒）
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📥 收到响应: {json.dumps(data, indent=2)}")

                if 'result' in data:
                    print("✅ CDP命令执行成功")
                    return True
                elif 'error' in data:
                    print(f"⚠️  CDP返回错误: {data['error']}")
                    return True  # 连接本身是成功的
            except asyncio.TimeoutError:
                print("⚠️  等待CDP响应超时（可能浏览器没有导航到页面）")
                return True  # 连接本身是成功的

    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("🧪 CDP直接连接测试")
    print("=" * 60)

    results = []

    # 测试1: 直接HTTP访问CDP
    results.append(("直接CDP HTTP", await test_direct_cdp()))

    # 测试2: WebSocket连接
    results.append(("WebSocket连接", await test_websocket_connection()))

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)

    passed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name:15s} {status}")
        if result:
            passed += 1

    print("=" * 60)
    print(f"总计: {passed}/{len(results)} 测试通过")

    if passed == len(results):
        print("\n🎉 成功！Chrome CDP可以正常访问")
        print("\n💡 现在可以启动CDP代理服务器")
        print("   命令: uv run cdp-proxy")
        return 0
    else:
        print("\n❌ 失败！Chrome CDP访问有问题")
        print("\n🔧 故障排查:")
        print("   1. 确认Chrome浏览器已启动: uv run python -m utils.chrome_manager status")
        print("   2. 确认Chrome监听CDP端口: netstat -tuln | grep 19222")
        print("   3. 确认防火墙未阻止连接")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
