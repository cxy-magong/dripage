#!/usr/bin/env python
"""
Tools Package - 浏览器和 Agent 工具包

提供浏览器操作工具和 Agent 工具（视觉识别、坐标变换等）
"""

# 浏览器工具
from tools.browser_tools import (
    browser_navigate,
    browser_get_current_page,
    browser_screenshot,
    browser_click,
    browser_input,
    browser_press_key,
    browser_scroll,
    get_config as get_browser_config,
    get_browser,
)

# Agent 工具
from tools.agent_tools import (
    vision_analyze,
    coordinate_convert_box,
    coordinate_convert_box_with_runtime,
    coordinate_convert_point_with_runtime,
    coordinate_parse_and_convert,
    coordinate_convert_from_image,
    CoordinateConverter,
    get_config as get_agent_config,
    locate_element,
    save_browser_screenshot,
    AgentState,
)

# 版本信息
__version__ = "0.1.0"

# 导出所有工具
__all__ = [
    # 浏览器工具
    'browser_navigate',
    'browser_get_current_page',
    'browser_screenshot',
    'browser_click',
    'browser_input',
    'browser_press_key',
    'browser_scroll',
    'get_browser_config',
    'get_browser',
    # Agent 工具
    'vision_analyze',
    'coordinate_convert_box',
    'coordinate_convert_box_with_runtime',
    'coordinate_convert_point_with_runtime',
    'coordinate_parse_and_convert',
    'coordinate_convert_from_image',
    'CoordinateConverter',
    'get_agent_config',
    'locate_element',
    'locate_element_tool',
    'save_browser_screenshot',
    'AgentState',
]


def get_all_tools():
    """
    获取所有工具函数
    
    Returns:
        dict: 工具名称到工具函数的映射
    """
    return {
        # 浏览器工具
        'browser_navigate': browser_navigate,
        'browser_get_current_page': browser_get_current_page,
        'browser_screenshot': browser_screenshot,
        'browser_click': browser_click,
        'browser_input': browser_input,
        'browser_press_key': browser_press_key,
        'browser_scroll': browser_scroll,
        'get_browser_config': get_browser_config,
        'get_browser': get_browser,
        # Agent 工具
        'vision_analyze': vision_analyze,
        'coordinate_convert_box': coordinate_convert_box,
        'coordinate_convert_box_with_runtime': coordinate_convert_box_with_runtime,
        'coordinate_convert_point_with_runtime': coordinate_convert_point_with_runtime,
        'coordinate_parse_and_convert': coordinate_parse_and_convert,
        'coordinate_convert_from_image': coordinate_convert_from_image,
        'locate_element': locate_element,
        'save_browser_screenshot': save_browser_screenshot,
    }


def get_browser_tools():
    """
    获取所有浏览器工具

    Returns:
        dict: 浏览器工具名称到工具函数的映射
    """
    return {
        'browser_navigate': browser_navigate,
        'browser_get_current_page': browser_get_current_page,
        'browser_screenshot': browser_screenshot,
        'browser_click': browser_click,
        'browser_input': browser_input,
        'browser_press_key': browser_press_key,
        'browser_scroll': browser_scroll,
    }


def get_agent_tools():
    """
    获取所有 Agent 工具
    
    Returns:
        dict: Agent 工具名称到工具函数的映射
    """
    return {
        'vision_analyze': vision_analyze,
        'coordinate_convert_box': coordinate_convert_box,
        'coordinate_convert_box_with_runtime': coordinate_convert_box_with_runtime,
        'coordinate_convert_point_with_runtime': coordinate_convert_point_with_runtime,
        'coordinate_parse_and_convert': coordinate_parse_and_convert,
        'coordinate_convert_from_image': coordinate_convert_from_image,
        'locate_element': locate_element,
        'save_browser_screenshot': save_browser_screenshot,
    }
