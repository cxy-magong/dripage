#!/usr/bin/env python
"""
Network packet listener tools using Chrome DevTools Protocol (CDP).
Based on DrissionPageMCP implementation.
"""
from typing import List, Literal, Union, Optional
from tools.tab_manager import get_tab_object


# Global storage for response listener data
response_listener_data = []


def get_url_with_response_listener(
    tab_id: Optional[Union[int, str]] = None,
    mimeType: Literal[
        # 文本类
        "text/html",
        "text/css",
        "text/javascript",
        "application/javascript",
        "text/plain",
        "text/xml",
        "text/csv",
        "application/json",
        # 应用类
        "application/octet-stream",
        "application/zip",
        "application/pdf",
        "multipart/form-data",
        "application/xml",
        # 图片类
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "image/x-icon",
        # 音视频类
        "audio/mpeg",
        "audio/ogg",
        "video/mp4",
        "video/webm",
        "video/ogg"
    ] = "application/json",
    url_include: str = ".",
    refresh: bool = False
) -> str:
    """开启网络数据包监听功能

    Args:
        tab_id: 标签页标识符 (None=当前标签页, int=索引, str=tab_id)
        mimeType: 需要监听的数据包的 mimeType 类型 (默认: application/json)
        url_include: 需要监听的数据包 URL 包含的关键字 (默认: "." 匹配所有)
        refresh: 是否刷新页面 (默认: False)

    Returns:
        str: 监听开启成功的消息
    """
    import json

    try:
        tab, metadata = get_tab_object(tab_id)

        # 启用 CDP Network 域
        tab.run_cdp("Network.enable")

        # 定义回调函数监听网络响应
        def response_callback(**event):
            _url = event.get("response", {}).get("url", "")
            _mimeType = event.get("response", {}).get("mimeType", "")

            # 筛选符合条件的响应
            if mimeType in _mimeType and url_include in _url:
                response_listener_data.append({
                    "event_name": "Network.responseReceived",
                    "event_data": event
                })

        # 设置回调监听
        tab.driver.set_callback("Network.responseReceived", response_callback)

        # 如果需要刷新页面
        if refresh:
            tab.refresh()

        return json.dumps({
            "status": "success",
            "message": f"开启监听成功",
            "tab": metadata,
            "config": {
                "mimeType": mimeType,
                "url_include": url_include,
                "refresh": refresh
            }
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"开启监听失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


def response_listener_stop(
    tab_id: Optional[Union[int, str]] = None,
    clear_data: bool = False
) -> str:
    """关闭网络数据包监听功能

    Args:
        tab_id: 标签页标识符 (None=当前标签页, int=索引, str=tab_id)
        clear_data: 是否清空已收集的数据 (默认: False)

    Returns:
        str: 监听关闭成功的消息
    """
    import json

    try:
        tab, metadata = get_tab_object(tab_id)

        # 关闭 CDP Network 监听
        tab.run_cdp("Network.disable")

        # 如果需要清空数据
        if clear_data:
            global response_listener_data
            response_listener_data.clear()

        return json.dumps({
            "status": "success",
            "message": f"监听网页发送的数据包关闭成功",
            "tab": metadata,
            "data_cleared": clear_data
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"关闭监听失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


def get_response_listener_data() -> str:
    """获取监听到的网络数据包

    Returns:
        str: JSON 格式的监听数据列表
    """
    import json

    try:
        return json.dumps({
            "status": "success",
            "count": len(response_listener_data),
            "data": response_listener_data
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"获取数据失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


def clear_response_listener_data() -> str:
    """清空已收集的监听数据

    Returns:
        str: 清空成功的消息
    """
    import json

    try:
        global response_listener_data
        response_listener_data.clear()

        return json.dumps({
            "status": "success",
            "message": "监听数据已清空"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"清空数据失败: {str(e)}"
        }, ensure_ascii=False, indent=2)
