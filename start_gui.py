#!/usr/bin/env python
"""
Dripage Browser Dashboard - Launcher

支持命令行参数的启动脚本：
- --debug: 调试模式，显示所有信息
- --info: 信息模式（默认）
- --quiet: 静默模式，只显示错误
- --log: 指定日志文件路径
- --no-console: 不在控制台输出
"""
import sys
from pathlib import Path
import argparse

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from GUI.logger_config import setup_logger


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Dripage 浏览器管理面板',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python start_gui_v2.py              # 默认模式（INFO级别）
  python start_gui_v2.py --debug     # 调试模式，显示所有信息
  python start_gui_v2.py --quiet     # 静默模式，只显示错误
  python start_gui_v2.py --log app.log  # 写日志到文件
  python start_gui_v2.py --no-console   # 不在控制台输出
        """
    )

    # 日志级别
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--debug',
        action='store_true',
        help='调试模式（显示所有信息）'
    )
    group.add_argument(
        '--quiet',
        action='store_true',
        help='静默模式（只显示错误）'
    )

    # 日志文件和控制台
    parser.add_argument(
        '--log',
        type=str,
        default=None,
        help='日志文件路径（例如：output/log/gui.log）'
    )
    parser.add_argument(
        '--no-console',
        action='store_true',
        help='不在控制台输出'
    )

    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()

    # 设置日志级别
    if args.debug:
        log_level = 'DEBUG'
        console_output = True
    elif args.quiet:
        log_level = 'ERROR'
        console_output = True
    else:
        log_level = 'INFO'
        console_output = not args.no_console

    # 默认日志文件路径
    if args.log is None and not args.quiet:
        args.log = str(project_root / 'output' / 'log' / 'gui.log')

    # 设置日志器
    setup_logger(
        level=log_level,
        log_file=args.log,
        console=console_output
    )

    from GUI.logger_config import info, error, debug

    info("=" * 60)
    info("正在启动 Dripage 浏览器管理面板...")
    info(f"日志级别: {log_level}")
    if args.log:
        info(f"日志文件: {args.log}")
    if not console_output:
        info("控制台输出: 已禁用")
    info("=" * 60)

    try:
        from GUI.GUI_dashboard import main as gui_main

        # 启动GUI
        debug("正在初始化GUI...")
        gui_main()

    except KeyboardInterrupt:
        info("")
        info("用户停止了程序")
        sys.exit(0)

    except Exception as e:
        error(f"启动GUI时出错: {e}")
        import traceback
        debug(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
