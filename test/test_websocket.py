#!/usr/bin/env python
"""
WebSocket 连接测试脚本

验证能否通过 CDP WebSocket URL 连接到浏览器并进行交互。
"""

import asyncio
import websockets
import json
import sys


async def test_websocket_connection(cdp_url: str):
    """测试 WebSocket 连接"""
    print("\n" + "=" * 70)
    print("  WebSocket 连接测试")
    print("=" * 70)
    print(f"\n🔌 连接到 WebSocket:")
    print(f"   {cdp_url}")
    print()

    try:
        async with websockets.connect(cdp_url) as websocket:
            print("✅ WebSocket 连接成功！")
            print("\n发送测试消息...")

            # 发送一个测试命令（例如：导航到页面）
            test_command = {
                "id": 1,
                "method": "Page.navigate",
                "params": {
                    "url": "https://www.baidu.com"
                }
            }

            await websocket.send(json.dumps(test_command))
            print("✅ 测试命令已发送")

            print("\n等待响应...")
            response = await asyncio.wait_for(
                websocket.recv(),
                timeout=5.0
            )
            print(f"📩 收到响应:")
            print(f"   {response}")

            # 测试获取页面信息
            get_info_command = {
                "id": 2,
                "method": "Page.getInfo",
                "params": {}
            }

            await websocket.send(json.dumps(get_info_command))
            print("✅ 获取页面信息命令已发送")

            response = await asyncio.wait_for(
                websocket.recv(),
                timeout=5.0
            )
            print(f"📩 页面信息:")
            print(f"   {json.dumps(json.loads(response), indent=2, ensure_ascii=False)}")

            print("\n" + "=" * 70)
            print("  ✅ WebSocket 测试成功！")
            print("  🎉 可以通过 WebSocket 与浏览器交互！")
            print("=" * 70)

    except asyncio.TimeoutError:
        print("❌ WebSocket 连接超时")
        return False
    except Exception as e:
        print(f"❌ WebSocket 连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        cdp_url = sys.argv[1]
    else:
        # 默认 CDP URL
        cdp_url = "ws://127.0.0.1:19222/devtools/browser/1fd3c31e-57fe-400a-a67a-ee98fc2a6add"

    print("WebSocket 测试脚本")
    print("=" * 50)
    print(f"CDP URL: {cdp_url}")
    print("=" * 50)

    # 运行测试
    success = asyncio.run(test_websocket_connection(cdp_url))

    if success:
        print("\n✅ WebSocket 测试通过")
        return 0
    else:
        print("\n❌ WebSocket 测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
