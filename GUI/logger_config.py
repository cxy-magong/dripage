#!/usr/bin/env python
"""
Logger Configuration for Dripage GUI

配置日志系统，支持不同输出级别：
- DEBUG: 显示所有调试信息（开发用）
- INFO: 显示基本信息（默认）
- WARNING: 只显示警告
- ERROR: 只显示错误
"""
import sys
from pathlib import Path
from datetime import datetime

# 日志级别
LOG_LEVELS = {
    'DEBUG': 0,
    'INFO': 1,
    'WARNING': 2,
    'ERROR': 3,
    'CRITICAL': 4
}

class GUILogger:
    """GUI日志器"""

    def __init__(self, level='INFO', log_file=None, console=True):
        """
        初始化日志器

        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            log_file: 日志文件路径，None表示不写文件
            console: 是否在控制台输出
        """
        self.level = LOG_LEVELS.get(level.upper(), LOG_LEVELS['INFO'])
        self.log_file = log_file
        self.console = console

        # 创建日志目录
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

    def debug(self, message):
        """调试级别信息"""
        if self.level <= LOG_LEVELS['DEBUG']:
            self._print(f"[DEBUG] {message}")

    def info(self, message):
        """信息级别"""
        if self.level <= LOG_LEVELS['INFO']:
            self._print(f"[INFO] {message}")

    def warning(self, message):
        """警告级别"""
        if self.level <= LOG_LEVELS['WARNING']:
            self._print(f"[WARNING] {message}")

    def error(self, message):
        """错误级别"""
        if self.level <= LOG_LEVELS['ERROR']:
            self._print(f"[ERROR] {message}")

    def _print(self, message):
        """输出日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"

        # 控制台输出
        if self.console:
            print(full_message, file=sys.stdout if 'ERROR' not in message else sys.stderr)

        # 文件输出
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(full_message + '\n')


# 全局日志器实例
_logger = None

def setup_logger(level='INFO', log_file=None, console=True):
    """
    设置全局日志器

    Args:
        level: 日志级别
        log_file: 日志文件路径
        console: 是否在控制台输出
    """
    global _logger
    _logger = GUILogger(level=level, log_file=log_file, console=console)


def get_logger():
    """获取全局日志器"""
    return _logger


# 便捷函数
def debug(message):
    """调试日志"""
    if _logger:
        _logger.debug(message)


def info(message):
    """信息日志"""
    if _logger:
        _logger.info(message)


def warning(message):
    """警告日志"""
    if _logger:
        _logger.warning(message)


def error(message):
    """错误日志"""
    if _logger:
        _logger.error(message)
