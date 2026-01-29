#!/usr/bin/env python
"""
集成测试 - 启动服务器并运行测试

在同一进程中启动 HTTP API 服务器并运行测试。
"""

import json
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_http.client import ChromeManagerHTTPClient


def start_server_process(port):
    """启动 HTTP 服务器进程"""
    print(f"\n{'=' * 70}")
    print("  启动 HTTP API 服务器...")
    print('=' * 70)

    server_process = subprocess.Popen(
        ['uv', 'run', 'python', 'services/chrome_http/server.py', '--host', '0.0.0.0', '--port', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(project_root)
    )

    # 等待服务器启动
    print(f"等待服务器在端口 {port} 启动...")
    for i in range(10):  # 等待最多 10 秒
        time.sleep(1)
        try:
            import httpx
            response = httpx.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ 服务器已启动！")
                print()
                return server_process
        except Exception:
            if i < 9:
                print(f".", end="", flush=True)
            continue

    print()
    print("❌ 服务器启动失败")
    server_process.terminate()
    server_process.wait()
    return None


def run_tests(client):
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("  运行 HTTP API 测试")
    print("=" * 70)

    try:
        # 测试 1: 健康检查
        print("\n" + "─" * 70)
        print("测试 1: 健康检查")
        print("─" * 70)
        health = client.health()
        print_result("健康检查", health)
        if health.get("status") != "ok":
            print("❌ 测试 1 失败")
            return False
        print("✅ 测试 1 通过: 服务器运行正常")

        # 测试 2: 启动 browser1
        print("\n" + "─" * 70)
        print("测试 2: 启动 browser1")
        print("─" * 70)
        result = client.start_browser(name="browser1")
        print_result("启动 browser1", result)
        if not result.get("success"):
            print("❌ 测试 2 失败")
            return False
        print("✅ 测试 2 通过: browser1 启动成功")

        time.sleep(2)

        # 测试 3: 启动 browser2
        print("\n" + "─" * 70)
        print("测试 3: 启动 browser2")
        print("─" * 70)
        result = client.start_browser(name="browser2")
        print_result("启动 browser2", result)
        if not result.get("success"):
            print("❌ 测试 3 失败")
            return False
        print("✅ 测试 3 通过: browser2 启动成功")

        time.sleep(2)

        # 测试 4: 获取所有状态
        print("\n" + "─" * 70)
        print("测试 4: 获取所有浏览器状态")
        print("─" * 70)
        result = client.get_status()
        print_result("所有浏览器状态", result)
        if not result.get("success") or result.get("data", {}).get("running") != 2:
            print("❌ 测试 4 失败")
            return False
        print("✅ 测试 4 通过: 两个浏览器都在运行")

        # 测试 5: 停止 browser1
        print("\n" + "─" * 70)
        print("测试 5: 停止 browser1")
        print("─" * 70)
        result = client.stop_browser(name="browser1")
        print_result("停止 browser1", result)
        if not result.get("success"):
            print("❌ 测试 5 失败")
            return False
        print("✅ 测试 5 通过: browser1 停止成功")

        time.sleep(1)

        # 测试 6: 停止 browser2
        print("\n" + "─" * 70)
        print("测试 6: 停止 browser2")
        print("─" * 70)
        result = client.stop_browser(name="browser2")
        print_result("停止 browser2", result)
        if not result.get("success"):
            print("❌ 测试 6 失败")
            return False
        print("✅ 测试 6 通过: browser2 停止成功")

        time.sleep(1)

        # 测试 7: 最终状态检查
        print("\n" + "─" * 70)
        print("测试 7: 最终状态检查")
        print("─" * 70)
        result = client.get_status()
        print_result("最终状态", result)
        if not result.get("success") or result.get("data", {}).get("running") != 0:
            print("❌ 测试 7 失败")
            return False
        print("✅ 测试 7 通过: 所有浏览器已停止")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_result(title, result):
    """打印结果"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main(port=8000):
    """主函数"""
    server_process = None

    try:
        # 启动服务器
        server_process = start_server_process(port)
        if not server_process:
            print("❌ 无法启动服务器")
            return False

        # 创建客户端
        print("🔌 连接到 HTTP API 客户端...")
        client = ChromeManagerHTTPClient(host="localhost", port=port)

        # 运行测试
        success = run_tests(client)

        # 关闭客户端
        client.close()

        if success:
            print("\n" + "=" * 70)
            print("  🎉 所有测试通过！🎉")
            print("=" * 70)
            print("\n✅ 总结:")
            print("   - 健康检查: 通过")
            print("   - 启动两个浏览器: 通过")
            print("   - 获取状态: 通过")
            print("   - 停止浏览器: 通过")
            print("   - 最终状态检查: 通过")
            print()

        return success

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        return False

    finally:
        # 停止服务器
        if server_process:
            print("\n🛑 停止服务器...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️ 服务器未停止，强制关闭...")
                server_process.kill()
                print("✅ 服务器已强制关闭")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="集成测试 - HTTP API")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")

    args = parser.parse_args()

    success = main(port=args.port)
    sys.exit(0 if success else 1)
