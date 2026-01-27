#!/usr/bin/env python
"""
Browser Tools - 浏览器操作工具
提供浏览器访问、点击、截图、输入等操作工具

使用 Runtime 配置从 config/tools_runtime.yaml 获取默认配置
"""

import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from langchain_core.tools import tool
import yaml

# 添加项目目录到路径
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from utils.drission_page import create_browser
from utils.logu import get_logger

logger = get_logger('browser_tools')


class BrowserToolConfig:
    """浏览器工具配置管理器 - 从 Runtime 配置加载"""

    def __init__(self):
        """从 config/tools_runtime.yaml 加载配置"""
        config_path = project_dir / 'config' / 'tools_runtime.yaml'

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        else:
            # 使用默认配置
            config = {
                'browser': {'address': '127.0.0.1:19222', 'headless': False, 'timeout': 30000},
                'output': {'directory': 'output/data', 'images_subdir': 'images', 'timestamp_format': '%Y%m%d_%H%M%S'},
                'tools': {'logging': True, 'auto_save_screenshots': True}
            }

        self.browser_address = config['browser']['address']
        self.headless = config['browser'].get('headless', False)
        self.timeout = config['browser'].get('timeout', 30000)

        self.output_dir = project_dir / config['output']['directory']
        self.images_subdir = config['output'].get('images_subdir', 'images')
        self.timestamp_format = config['output'].get('timestamp_format', '%Y%m%d_%H%M%S')

        self.logging = config['tools'].get('logging', True)
        self.auto_save_screenshots = config['tools'].get('auto_save_screenshots', True)

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.logging:
            logger.info(f"BrowserTools 配置加载成功:")
            logger.info(f"  浏览器地址: {self.browser_address}")
            logger.info(f"  输出目录: {self.output_dir}")
            logger.info(f"  超时时间: {self.timeout}ms")


# 全局配置实例（单例）
_config_instance: Optional[BrowserToolConfig] = None


def get_config() -> BrowserToolConfig:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = BrowserToolConfig()
    return _config_instance


def generate_timestamp() -> str:
    """生成时间戳"""
    config = get_config()
    return datetime.now().strftime(config.timestamp_format)


def get_browser():
    """获取浏览器实例"""
    config = get_config()
    return create_browser(address=config.browser_address)


@tool
def browser_navigate(url: str) -> str:
    """
    导航浏览器到指定 URL

    Args:
        url: 要访问的 URL

    Returns:
        成功消息，包含页面标题
    """
    config = get_config()
    if config.logging:
        logger.info(f"导航到: {url}")

    try:
        page = get_browser()
        page.get(url)
        title = page.title

        if config.logging:
            logger.info(f"成功导航到: {url} (标题: {title})")

        return f"成功导航到 {url}。页面标题: {title}"

    except Exception as e:
        error_msg = f"导航到 {url} 失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def browser_get_current_page() -> str:
    """
    获取当前页面信息

    Returns:
        当前页面的标题和 URL（JSON 格式）
    """
    import json
    config = get_config()

    try:
        page = get_browser()
        page_info = {
            "title": page.title,
            "url": page.url
        }

        if config.logging:
            logger.info(f"当前页面: {page_info}")

        return json.dumps(page_info, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"获取当前页面信息失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def browser_screenshot(full_page: bool = True, save: bool = True) -> str:
    """
    截取当前页面截图

    Args:
        full_page: 是否截取整个页面（默认 True）
        save: 是否自动保存截图（默认 True）

    Returns:
        截图文件路径
    """
    config = get_config()

    if config.logging:
        logger.info(f"截取页面截图 (full_page={full_page}, save={save})")

    try:
        page = get_browser()

        # 生成文件名
        timestamp = generate_timestamp()
        filename = f"screenshot_{timestamp}.png"
        filepath = config.output_dir / filename

        # 截取截图
        screenshot_data = page.get_screenshot(as_bytes=True, full_page=full_page)

        # 保存截图
        if save or config.auto_save_screenshots:
            with open(filepath, 'wb') as f:
                f.write(screenshot_data)

            if config.logging:
                logger.info(f"截图已保存到: {filepath}")

        return str(filepath)

    except Exception as e:
        error_msg = f"截图失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def browser_click(x: int, y: int) -> str:
    """
    在指定坐标点击

    Args:
        x: X 坐标
        y: Y 坐标

    Returns:
        成功消息
    """
    config = get_config()

    if config.logging:
        logger.info(f"点击坐标: ({x}, {y})")

    try:
        page = get_browser()
        tab = page.latest_tab

        # 使用 actions API 点击
        tab.actions.move_to((x, y))
        tab.actions.click()

        if config.logging:
            logger.info(f"成功点击坐标: ({x}, {y})")

        return f"成功点击坐标 ({x}, {y})"

    except Exception as e:
        error_msg = f"点击 ({x}, {y}) 失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def browser_input(x: int, y: int, text: str, clear: bool = True) -> str:
    """
    在指定坐标的输入框输入文本

    Args:
        x: 输入框的 X 坐标
        y: 输入框的 Y 坐标
        text: 要输入的文本
        clear: 是否先清除已有内容（默认 True）

    Returns:
        成功消息
    """
    from DrissionPage.common import Keys
    import time
    config = get_config()

    if config.logging:
        logger.info(f"在坐标 ({x}, {y}) 输入文本: '{text}' (clear={clear})")

    try:
        page = get_browser()
        tab = page.latest_tab

        # 点击以聚焦输入框
        tab.actions.move_to((x, y))
        tab.actions.click()
        time.sleep(0.3)

        # 如果需要清除已有内容
        if clear:
            # Ctrl+A 全选，然后 Delete 删除
            tab.actions.type(Keys.CTRL_A)
            time.sleep(0.2)

        # 输入文本
        tab.actions.input(text)

        if config.logging:
            logger.info(f"成功输入文本: '{text}'")

        return f"成功在坐标 ({x}, {y}) 输入文本: '{text}'"

    except Exception as e:
        error_msg = f"在 ({x}, {y}) 输入文本失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def browser_press_key(key: str, times: int = 1) -> str:
    """
    按下键盘按键

    Args:
        key: 按键名称（如 'enter', 'escape', 'space', 'tab'）
        times: 按下次数（默认 1）

    Returns:
        成功消息
    """
    config = get_config()

    if config.logging:
        logger.info(f"按下按键: {key} (次数: {times})")

    try:
        page = get_browser()
        tab = page.latest_tab

        for _ in range(times):
            tab.actions.key_press(key)

        if config.logging:
            logger.info(f"成功按下按键: {key} x{times}")

        return f"成功按下按键: {key} x{times}"

    except Exception as e:
        error_msg = f"按下按键 {key} 失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def browser_scroll(direction: str = "down", amount: int = 500) -> str:
    """
    滚动页面

    Args:
        direction: 滚动方向，'up' 或 'down'（默认 'down'）
        amount: 滚动像素量（默认 500）

    Returns:
        成功消息
    """
    config = get_config()

    if config.logging:
        logger.info(f"滚动页面: {direction} {amount}px")

    try:
        page = get_browser()
        tab = page.latest_tab

        if direction == "down":
            tab.scroll.down(amount)
        elif direction == "up":
            tab.scroll.up(amount)
        else:
            raise ValueError(f"无效的滚动方向: {direction}")

        if config.logging:
            logger.info(f"成功滚动页面: {direction} {amount}px")

        return f"成功滚动页面: {direction} {amount}px"

    except Exception as e:
        error_msg = f"滚动页面失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


# 导出所有工具函数，方便 FastMCP 或其他框架调用
__all__ = [
    'browser_navigate',
    'browser_get_current_page',
    'browser_screenshot',
    'browser_click',
    'browser_input',
    'browser_press_key',
    'browser_scroll',
    'get_config',
    'get_browser',
]


if __name__ == "__main__":
    # 测试配置加载
    config = get_config()

    print("\n" + "=" * 80)
    print("Browser Tools 配置测试")
    print("=" * 80)
    print(f"浏览器地址: {config.browser_address}")
    print(f"输出目录: {config.output_dir}")
    print(f"无头模式: {config.headless}")
    print(f"超时时间: {config.timeout}ms")
    print("=" * 80)
