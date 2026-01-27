#!/usr/bin/env python
"""
测试 locate_element 工具

演示如何使用 locate_element 工具定位图像中的元素位置。
该工具内部使用 Agent 自动调用视觉分析和坐标转换工具。

运行: PYTHONPATH="G:\code\agent-use\dripage" uv run example/test_locate_element.py
"""

import os
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置不使用代理访问智谱 API
os.environ['NO_PROXY'] = 'open.bigmodel.cn'
os.environ['no_proxy'] = 'open.bigmodel.cn'

from tools import _locate_element as locate_element
from utils.logu import get_logger

logger = get_logger("test_locate_element")


def test_locate_element_with_image():
    """测试 locate_element 工具（使用本地图像）"""
    logger.info("=" * 80)
    logger.info("测试 locate_element 工具")
    logger.info("=" * 80)

    # 测试图像路径（请替换为实际的图像路径）
    image_path = r"G:\code\agent-use\dripage\output\data\screenshot_2026-01-25_20-59-59.png"

    # 检查图像是否存在
    if not os.path.exists(image_path):
        logger.warning(f"测试图像不存在: {image_path}")
        logger.info("将使用当前浏览器截图...")
        image_path = None

    # 测试查询 - 直接用自然语言描述多个元素
    query = "请帮我找到图像中的搜索输入框、提交按钮和导航栏的位置坐标"

    logger.info(f"\n查询: {query}")
    logger.info("-" * 80)

    try:
        result = locate_element(query=query, image_path=image_path)

        # 解析结果
        result_data = json.loads(result)

        if "error" in result_data:
            logger.error(f"错误: {result_data['error']}")
        else:
            logger.info(f"状态: {result_data.get('status', 'unknown')}")
            logger.info(f"结果:\n{result_data.get('result_text', result)}")

    except Exception as e:
        logger.error(f"测试失败: {str(e)}")

    print("\n")


def test_locate_element_without_image():
    """测试 locate_element 工具（使用浏览器截图）"""
    logger.info("=" * 80)
    logger.info("测试 locate_element 工具（使用浏览器截图）")
    logger.info("=" * 80)

    # 测试查询 - 直接用自然语言描述多个元素
    query = "给我图像中搜索输入框、搜索按钮的位置坐标box，以及页面中所有按钮的位置"

    logger.info(f"\n查询: {query}")
    logger.info("-" * 80)

    try:
        result = locate_element(query=query, image_path=None)

        # 解析结果
        result_data = json.loads(result)

        if "error" in result_data:
            logger.error(f"错误: {result_data['error']}")
        else:
            logger.info(f"状态: {result_data.get('status', 'unknown')}")
            logger.info(f"结果:\n{result_data.get('result_text', result)}")

    except Exception as e:
        logger.exception(f"测试失败: {str(e)}")

    print("\n")


def main():
    """主函数"""
    logger.info("\n" + "=" * 80)
    logger.info("locate_element 工具测试")
    logger.info("=" * 80)

    # 测试 1: 使用本地图像
    # test_locate_element_with_image()

    # 测试 2: 使用浏览器截图
    test_locate_element_without_image()

    logger.info("\n" + "=" * 80)
    logger.info("测试完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
