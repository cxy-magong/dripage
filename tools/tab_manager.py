#!/usr/bin/env python
"""
Tab Manager - 标签页管理通用工具
提供统一的标签获取和元数据管理

按照 DrissionPage 官方文档，不需要切换标签焦点，直接获取标签对象操作即可。
"""

import sys
from pathlib import Path
from typing import Optional, Union, Dict, Tuple, Any

# 添加项目目录到路径
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from utils.drission_page import create_browser
from utils.logu import get_logger

logger = get_logger('tab_manager')


def get_tab_object(tab_id: Optional[Union[int, str]] = None) -> Tuple[Any, Dict]:
    """
    获取标签页对象及其元数据（通用函数）

    Args:
        tab_id: 标签标识符
            - None: 使用 browser.latest_tab（当前最后激活的标签）
            - int: 标签索引（0-based，按激活顺序排列）
            - str: 标签的 tab_id（唯一标识字符串）

    Returns:
        (tab_object, tab_metadata): 标签对象和元数据字典

    Raises:
        ValueError: 当 tab_id 无效时
    """
    try:
        browser = create_browser()

        if tab_id is None:
            # 获取最后激活的标签
            tab = browser.latest_tab
            logger.debug("使用 browser.latest_tab")
        elif isinstance(tab_id, int):
            # 通过索引获取
            tab = browser.get_tab(tab_id)
            logger.debug(f"通过索引获取标签: {tab_id}")
        else:  # str
            # 通过 tab_id 字符串获取
            tab = browser.get_tab(tab_id)
            logger.debug(f"通过 tab_id 获取标签: {tab_id}")

        if not tab:
            raise ValueError(f"无法获取标签: tab_id={tab_id}")

        # 获取元数据
        metadata = get_tab_metadata(tab, browser)

        logger.info(f"成功获取标签: {metadata.get('title')} (id={metadata.get('tab_id')})")

        return tab, metadata

    except Exception as e:
        logger.error(f"获取标签对象失败: {e}")
        raise ValueError(f"获取标签失败: {str(e)}")


def get_tab_metadata(tab: Any, browser: Any = None) -> Dict:
    """
    获取标签页元数据

    Args:
        tab: 标签对象
        browser: 浏览器对象（可选，如果为 None 则创建）

    Returns:
        包含标签信息的字典: {tab_id, title, url, index, is_current}
    """
    if browser is None:
        browser = create_browser()

    try:
        # 获取标签 ID
        tab_id_value = getattr(tab, 'tab_id', None)

        # 获取标签索引
        tab_index = get_tab_index(tab, browser)

        # 构建元数据
        metadata = {
            "tab_id": tab_id_value,
            "title": tab.title,
            "url": tab.url,
            "index": tab_index,
        }

        # 判断是否为当前激活标签
        try:
            current_tab = browser.latest_tab
            current_tab_id = getattr(current_tab, 'tab_id', None)
            metadata["is_current"] = (tab_id_value == current_tab_id)
        except Exception as e:
            logger.warning(f"判断当前标签失败: {e}")
            metadata["is_current"] = False

        return metadata

    except Exception as e:
        logger.warning(f"获取标签元数据失败（返回部分信息）: {e}")
        # 返回基础信息
        return {
            "tab_id": getattr(tab, 'tab_id', None),
            "title": getattr(tab, 'title', 'Unknown'),
            "url": getattr(tab, 'url', ''),
            "index": None,
            "is_current": False
        }


def get_tab_index(target_tab: Any, browser: Any = None) -> Optional[int]:
    """
    获取标签页在列表中的索引

    Args:
        target_tab: 目标标签对象
        browser: 浏览器对象（可选）

    Returns:
        标签索引（0-based），如果未找到则返回 None
    """
    try:
        if browser is None:
            browser = create_browser()

        tabs = browser.get_tabs()
        target_tab_id = getattr(target_tab, 'tab_id', None)

        for i, tab in enumerate(tabs):
            tab_id = getattr(tab, 'tab_id', None)
            if tab_id == target_tab_id:
                return i

        logger.warning(f"未找到标签索引: tab_id={target_tab_id}")
        return None

    except Exception as e:
        logger.warning(f"获取标签索引失败: {e}")
        return None


def list_all_tabs() -> Dict:
    """
    列出所有标签页及其完整信息

    Returns:
        JSON: 所有标签的详细信息
        {
            "status": "success",
            "tabs": [...],
            "count": N
        }
    """
    import json

    try:
        browser = create_browser()
        tabs = browser.get_tabs()
        current_tab = browser.latest_tab

        tab_list = []
        for i, tab in enumerate(tabs):
            metadata = get_tab_metadata(tab, browser)
            metadata["index"] = i  # 显式设置索引
            tab_list.append(metadata)

        result = {
            "status": "success",
            "tabs": tab_list,
            "count": len(tab_list)
        }

        logger.info(f"列出了 {len(tab_list)} 个标签")
        return result

    except Exception as e:
        error_msg = f"列出标签失败: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def new_tab_object(url: Optional[str] = None) -> Tuple[Any, Dict]:
    """
    新建标签页并返回对象及元数据

    Args:
        url: 可选的 URL，如果提供则导航到该 URL

    Returns:
        (tab_object, tab_metadata): 新标签对象和元数据字典
    """
    try:
        browser = create_browser()

        # 新建标签
        tab = browser.new_tab(url)

        # 等待标签初始化
        if url:
            import time
            time.sleep(0.5)

        # 获取元数据
        metadata = get_tab_metadata(tab, browser)

        logger.info(f"新建标签: {metadata.get('title')} (url={url})")

        return tab, metadata

    except Exception as e:
        logger.error(f"新建标签失败: {e}")
        raise RuntimeError(f"新建标签失败: {str(e)}")


def close_tab_object(tab_id: Union[int, str]) -> Dict:
    """
    关闭指定标签页

    Args:
        tab_id: 标签标识符（int=索引，str=tab_id）

    Returns:
        JSON: 操作结果
    """
    try:
        browser = create_browser()

        if isinstance(tab_id, int):
            # 通过索引获取标签
            target_tab = browser.get_tab(tab_id)
        else:
            # 通过 tab_id 获取
            target_tab = browser.get_tab(tab_id)

        if not target_tab:
            raise ValueError(f"无法找到标签: tab_id={tab_id}")

        # 关闭标签
        target_tab.close()

        # 等待浏览器更新
        import time
        time.sleep(0.3)

        logger.info(f"已关闭标签: tab_id={tab_id}")

        return {
            "status": "success",
            "message": f"标签 {tab_id} 已关闭"
        }

    except Exception as e:
        error_msg = f"关闭标签失败: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


# 导出函数
__all__ = [
    'get_tab_object',
    'get_tab_metadata',
    'get_tab_index',
    'list_all_tabs',
    'new_tab_object',
    'close_tab_object',
]


if __name__ == "__main__":
    # 测试标签管理功能
    print("=" * 80)
    print("Tab Manager 测试")
    print("=" * 80)

    # 测试 list_all_tabs
    print("\n1. 测试 list_all_tabs():")
    tabs_result = list_all_tabs()
    print(f"   {tabs_result}")

    # 测试 get_tab_object
    print("\n2. 测试 get_tab_object(None):")
    tab, metadata = get_tab_object(None)
    print(f"   标签标题: {metadata['title']}")
    print(f"   标签 URL: {metadata['url']}")
    print(f"   标签 ID: {metadata['tab_id']}")

    # 测试 get_tab_object with index
    print("\n3. 测试 get_tab_object(0):")
    try:
        tab, metadata = get_tab_object(0)
        print(f"   标签标题: {metadata['title']}")
    except Exception as e:
        print(f"   错误: {e}")

    print("\n" + "=" * 80)
