#!/usr/bin/env python
"""
简单的 WebSocket CDP 连接测试

快速验证 CDP WebSocket 是否可以连接并发送命令。
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_http.client import ChromeManagerHTTPClient
import websockets


async def test_cdp_quick(cdp_url: str):
    """快速 CDP WebSocket 测试"""
    print(f"\n连接到 CDP WebSocket: {cdp_url}")

    try:
        async with websockets.connect(cdp_url, timeout=10) as ws:
            print("✅ WebSocket 连接成功")

            # 发送一个简单的命令
            command = {
                "id": 1,
                "method": "Page.enable",
                "params": {}
            }

            await ws.send(json.dumps(command))
            print(f"已发送命令: {command['method']}")

            # 等待响应
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            print(f"收到响应: {response[:200]}")

            return True

    except asyncio.TimeoutError:
        print("❌ WebSocket 连接超时")
        return False
    except Exception as e:
        print(f"❌ WebSocket 连接失败: {e}")
        return False


async def main():
    """主函数"""
    # 创建客户端
    client = ChromeManagerHTTPClient(host="localhost", port=8889)

    try:
        # 获取 CDP URL
        print("\n" + "=" * 70)
        print("  CDP WebSocket 快速测试")
        print("=" * 70)

        print("\n步骤 1: 获取 CDP URL")
        cdp_result = client.get_cdp_url(name="browser1")

        if not cdp_result.get("success"):
            print("❌ 获取 CDP URL 失败")
            return False

        cdp_url = cdp_result.get("data", {}).get("cdp_url", "")
        address = cdp_result.get("data", {}).get("address", "")

        print(f"浏览器地址: {address}")
        print(f"CDP URL: {cdp_url}")

        # 验证 CDP URL 格式
        if "devtools/browser/" in cdp_url:
            print("✅ CDP URL 格式正确（包含 devtools/browser/）")
        else:
            print("❌ CDP URL 格式不正确")
            return False

        # 验证地址匹配
        if address == "127.0.0.1:19222":
            print("✅ 地址匹配配置 (127.0.0.1:19222)")
        else:
            print(f"❌ 地址不匹配: 期望 127.0.0.1:19222，实际 {address}")
            return False

        # 测试 WebSocket 连接
        print("\n步骤 2: 测试 WebSocket 连接")
        ws_success = await test_cdp_quick(cdp_url)

        # 清理
        print("\n" + "=" * 70)
        if ws_success:
            print("  🎉 所有测试通过！🎉")
            print("=" * 70)
            print("\n💡 总结:")
            print("   ✅ CDP URL 获取成功")
            print("   ✅ 地址配置正确 (127.0.0.1:19222)")
            print("   ✅ CDP URL 格式正确 (包含 devtools/browser/)")
            print("   ✅ WebSocket 可以成功连接")
            print("   ✅ 可以发送 CDP 命令并接收响应")
            print()
            print("📝 下一步: 可以通过 WebSocket 与浏览器进行自动化交互")
            print()
        else:
            print("  ❌ WebSocket 测试失败")
            print("=" * 70)

        return ws_success

    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
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
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
