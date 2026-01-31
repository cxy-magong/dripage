"""
启动CDP代理服务器的便捷脚本
"""
import sys
import argparse
from .server import CDPProxyServer
from .config import ProxyConfig


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="CDP代理服务器 - 为外部访问Chrome CDP提供HTTP/WebSocket代理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m cdp_proxy.start_proxy                           # 使用默认配置
  python -m cdp_proxy.start_proxy --cdp-port 19222      # 指定CDP端口
  python -m cdp_proxy.start_proxy --proxy-port 8080     # 指定代理端口
  python -m cdp_proxy.start_proxy --host 0.0.0.0     # 指定监听地址
  python -m cdp_proxy.start_proxy --debug                  # 启用调试日志
        """
    )

    parser.add_argument(
        "--cdp-port",
        type=int,
        default=19222,
        help="Chrome CDP端口（默认：19222）"
    )

    parser.add_argument(
        "--proxy-port",
        type=int,
        default=8080,
        help="代理服务器端口（默认：8080）"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="监听地址（默认：0.0.0.0，允许外部访问）"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="日志级别（默认：info）"
    )

    parser.add_argument(
        "--keepalive-interval",
        type=int,
        default=20,
        help="WebSocket keepalive ping间隔（秒，默认：20）"
    )

    parser.add_argument(
        "--keepalive-timeout",
        type=int,
        default=20,
        help="WebSocket keepalive ping超时（秒，默认：20）"
    )

    args = parser.parse_args()

    # 创建配置
    config = ProxyConfig(
        cdp_port=args.cdp_port,
        proxy_port=args.proxy_port,
        host=args.host,
        log_level=args.log_level,
        keepalive_ping_interval=args.keepalive_interval,
        keepalive_ping_timeout=args.keepalive_timeout,
    )

    print(f"\n{config}\n")

    # 启动服务器
    server = CDPProxyServer(config)
    server.run()


if __name__ == "__main__":
    main()
