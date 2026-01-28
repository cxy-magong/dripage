#!/usr/bin/env python
"""
ChromeManager RPC 交互式客户端

提供交互式命令行界面来管理浏览器。
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_rpc.client import ChromeManagerClient
import json


class BrowserREPL:
    """交互式浏览器管理 REPL"""

    COMMANDS = {
        'help': '显示帮助',
        'start': '启动浏览器 (参数: name)',
        'stop': '停止浏览器 (参数: name, 可选)',
        'status': '获取状态 (参数: name, 可选)',
        'cdp': '获取CDP URL (参数: name)',
        'config': '加载配置 (参数: name)',
        'exit': '退出',
        'quit': '退出',
    }

    def __init__(self, host='localhost', port=9090):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        """连接到 RPC 服务器"""
        try:
            self.client = ChromeManagerClient(host=self.host, port=self.port)
            print(f"✅ 已连接到 RPC 服务器: {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

    def start_browser(self, name):
        """启动浏览器"""
        result = self.client.start_browser(name=name)
        self.print_result(f"启动浏览器 {name}", result)

    def stop_browser(self, name):
        """停止浏览器"""
        result = self.client.stop_browser(name=name)
        self.print_result(f"停止浏览器 {name}", result)

    def get_status(self, name):
        """获取状态"""
        result = self.client.get_status(name=name)
        self.print_result("状态", result)

    def get_cdp_url(self, name):
        """获取 CDP URL"""
        result = self.client.get_cdp_url(name=name)
        self.print_result(f"CDP URL {name}", result)

    def load_config(self, name):
        """加载配置"""
        result = self.client.load_browser_config(name=name)
        self.print_result(f"配置 {name}", result)

    def print_result(self, title, result):
        """打印结果"""
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print('=' * 60)
        if isinstance(result, dict):
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(result)

    def show_help(self):
        """显示帮助"""
        print("\n" + "=" * 60)
        print("  可用命令")
        print("=" * 60)
        for cmd, desc in self.COMMANDS.items():
            print(f"  {cmd:<15} - {desc}")
        print("\n示例:")
        print("  start browser1")
        print("  stop browser1")
        print("  status")
        print("  status browser1")
        print("  cdp browser1")
        print("")

    def run(self):
        """运行 REPL"""
        if not self.connect():
            return

        print("\n" + "=" * 60)
        print("  ChromeManager RPC 交互式客户端")
        print("=" * 60)
        print(f"  服务器: {self.host}:{self.port}")
        print("  输入 'help' 查看可用命令")
        print("  输入 'exit' 或 'quit' 退出")
        print("")

        while True:
            try:
                # 读取命令
                cmd_input = input("chrome-rpc> ").strip()

                if not cmd_input:
                    continue

                # 解析命令
                parts = cmd_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []

                # 执行命令
                if command in ['exit', 'quit']:
                    print("\n👋 退出")
                    break

                elif command == 'help':
                    self.show_help()

                elif command == 'start':
                    if not args:
                        print("❌ 用法: start <name>")
                        continue
                    self.start_browser(args[0])

                elif command == 'stop':
                    if not args:
                        print("❌ 用法: stop <name> (可选)")
                        continue
                    self.stop_browser(args[0])

                elif command == 'status':
                    if args:
                        self.get_status(args[0])
                    else:
                        self.get_status(None)

                elif command == 'cdp':
                    if not args:
                        print("❌ 用法: cdp <name>")
                        continue
                    self.get_cdp_url(args[0])

                elif command == 'config':
                    if not args:
                        print("❌ 用法: config <name>")
                        continue
                    self.load_config(args[0])

                else:
                    print(f"❌ 未知命令: {command}")
                    print(f"   输入 'help' 查看可用命令")

            except KeyboardInterrupt:
                print("\n\n👋 退出")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")

        # 清理
        if self.client:
            self.client.close()
            print("\n✅ 连接已关闭")


def main(host='localhost', port=9090):
    """主函数"""
    repl = BrowserREPL(host=host, port=port)
    repl.run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ChromeManager RPC 交互式客户端")
    parser.add_argument("--host", default="localhost", help="RPC 服务器主机 (默认: localhost)")
    parser.add_argument("--port", type=int, default=9090, help="RPC 服务器端口 (默认: 9090)")

    args = parser.parse_args()

    main(host=args.host, port=args.port)
