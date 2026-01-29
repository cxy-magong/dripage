#!/usr/bin/env python
"""
测试 Chrome Manager HTTP API

验证所有 HTTP API 端点功能。
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_http.client import ChromeManagerHTTPClient


def print_result(title, result):
    """打印结果"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def test_http_api(host="localhost", port=8000):
    """测试 HTTP API"""
    print("\n" + "=" * 60)
    print("  Chrome Manager HTTP API 测试")
    print(f"  Server: {host}:{port}")
    print("=" * 60)

    try:
        # 创建客户端
        print("\n🔌 连接到 HTTP API 服务器...")
        client = ChromeManagerHTTPClient(host=host, port=port)

        # 测试健康检查
        print("\n" + "─" * 60)
        print("测试 1: 健康检查")
        print("─" * 60)
        health = client.health()
        print_result("健康检查", health)
        if health.get("status") == "ok":
            print("✅ 测试 1 通过: 服务器运行正常")
        else:
            print("❌ 测试 1 失败")
            return False

        # 测试启动 browser1
        print("\n" + "─" * 60)
        print("测试 2: 启动 browser1")
        print("─" * 60)
        result = client.start_browser(name="browser1")
        print_result("启动 browser1", result)
        if result.get("success"):
            print("✅ 测试 2 通过: browser1 启动成功")
        else:
            print("❌ 测试 2 失败")
            return False

        import time
        time.sleep(2)  # 等待浏览器启动

        # 测试启动 browser2
        print("\n" + "─" * 60)
        print("测试 3: 启动 browser2")
        print("─" * 60)
        result = client.start_browser(name="browser2")
        print_result("启动 browser2", result)
        if result.get("success"):
            print("✅ 测试 3 通过: browser2 启动成功")
        else:
            print("❌ 测试 3 失败")
            return False

        time.sleep(2)

        # 测试获取所有状态
        print("\n" + "─" * 60)
        print("测试 4: 获取所有浏览器状态")
        print("─" * 60)
        result = client.get_status()
        print_result("所有浏览器状态", result)
        if result.get("success") and result.get("data", {}).get("running") == 2:
            print("✅ 测试 4 通过: 两个浏览器都在运行")
        else:
            print("❌ 测试 4 失败")
            return False

        # 测试获取 browser1 状态
        print("\n" + "─" * 60)
        print("测试 5: 获取 browser1 状态")
        print("─" * 60)
        result = client.get_status(name="browser1")
        print_result("Browser1 状态", result)
        if result.get("success") and result.get("data", {}).get("status") == "running":
            print("✅ 测试 5 通过: browser1 运行中")
        else:
            print("❌ 测试 5 失败")
            return False

        # 测试获取 browser1 CDP URL
        print("\n" + "─" * 60)
        print("测试 6: 获取 browser1 CDP URL")
        print("─" * 60)
        result = client.get_cdp_url(name="browser1")
        print_result("Browser1 CDP URL", result)
        if result.get("success") and result.get("data", {}).get("cdp_url"):
            print("✅ 测试 6 通过: CDP URL 获取成功")
        else:
            print("❌ 测试 6 失败")
            return False

        # 测试获取 browser2 CDP URL
        print("\n" + "─" * 60)
        print("测试 7: 获取 browser2 CDP URL")
        print("─" * 60)
        result = client.get_cdp_url(name="browser2")
        print_result("Browser2 CDP URL", result)
        if result.get("success") and result.get("data", {}).get("cdp_url"):
            print("✅ 测试 7 通过: CDP URL 获取成功")
        else:
            print("❌ 测试 7 失败")
            return False

        # 测试停止 browser1
        print("\n" + "─" * 60)
        print("测试 8: 停止 browser1")
        print("─" * 60)
        result = client.stop_browser(name="browser1")
        print_result("停止 browser1", result)
        if result.get("success"):
            print("✅ 测试 8 通过: browser1 停止成功")
        else:
            print("❌ 测试 8 失败")
            return False

        time.sleep(1)

        # 测试停止 browser2
        print("\n" + "─" * 60)
        print("测试 9: 停止 browser2")
        print("─" * 60)
        result = client.stop_browser(name="browser2")
        print_result("停止 browser2", result)
        if result.get("success"):
            print("✅ 测试 9 通过: browser2 停止成功")
        else:
            print("❌ 测试 9 失败")
            return False

        time.sleep(1)

        # 测试最终状态
        print("\n" + "─" * 60)
        print("测试 10: 最终状态检查")
        print("─" * 60)
        result = client.get_status()
        print_result("最终状态", result)
        if result.get("success") and result.get("data", {}).get("running") == 0:
            print("✅ 测试 10 通过: 所有浏览器已停止")
        else:
            print("❌ 测试 10 失败")
            return False

        # 所有测试通过
        print("\n" + "=" * 60)
        print("  🎉 所有 HTTP API 测试通过！🎉")
        print("=" * 60)
        print("\n✅ 总结:")
        print("   - 健康检查: 通过")
        print("   - 启动两个浏览器: 通过")
        print("   - 获取所有状态: 通过")
        print("   - 获取单个状态: 通过")
        print("   - 获取 CDP URLs: 通过")
        print("   - 停止浏览器: 通过")
        print("   - 最终状态检查: 通过")
        print()

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            client.close()
            print("✅ 客户端连接已关闭")
        except Exception as e:
            print(f"关闭客户端错误: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试 Chrome Manager HTTP API")
    parser.add_argument("--host", default="localhost", help="服务器主机 (默认: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")

    args = parser.parse_args()

    success = test_http_api(host=args.host, port=args.port)
    sys.exit(0 if success else 1)
