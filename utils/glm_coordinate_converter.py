#!/usr/bin/env python
"""
GLM-4V 坐标转换工具

GLM-4V 视觉模型内部将图像缩放到固定尺寸 999x999 进行识别。
因此返回的坐标是基于 999x99 尺寸的，需要转换回原始图像坐标系。

转换公式：
    original_x = scaled_x * (original_width / 999)
    original_y = scaled_y * (original_height / 999)
"""

import re
import json
from typing import Tuple, List, Union, Optional
from PIL import Image
import requests
from io import BytesIO
from utils.logu import get_logger

logger = get_logger('glm_coordinate_converter')


class GLMCoordinateConverter:
    """GLM-4V 坐标转换器"""

    # GLM-4V 内部使用的固定缩放尺寸
    GLM_SCALED_SIZE = 999

    def __init__(self, original_width: int, original_height: int):
        """
        初始化转换器

        Args:
            original_width: 原始图像宽度
            original_height: 原始图像高度
        """
        self.original_width = original_width
        self.original_height = original_height

        # 计算缩放比例
        self.scale_x = original_width / self.GLM_SCALED_SIZE
        self.scale_y = original_height / self.GLM_SCALED_SIZE

        logger.info(f"初始化坐标转换器:")
        logger.info(f"  原始图像尺寸: {original_width} x {original_height}")
        logger.info(f"  GLM 缩放尺寸: {self.GLM_SCALED_SIZE} x {self.GLM_SCALED_SIZE}")
        logger.info(f"  X 轴缩放比例: {self.scale_x:.4f}")
        logger.info(f"  Y 轴缩放比例: {self.scale_y:.4f}")

    def convert_box(self, box: Union[List[int], Tuple[int, int, int, int]]) -> List[int]:
        """
        转换单个 bounding box 坐标

        Args:
            box: [xmin, ymin, xmax, ymax] 格式的坐标

        Returns:
            转换后的坐标 [xmin, ymin, xmax, ymax]
        """
        xmin, ymin, xmax, ymax = box

        original_xmin = int(xmin * self.scale_x)
        original_ymin = int(ymin * self.scale_y)
        original_xmax = int(xmax * self.scale_x)
        original_ymax = int(ymax * self.scale_y)

        return [original_xmin, original_ymin, original_xmax, original_ymax]

    def convert_boxes(self, boxes: List[List[int]]) -> List[List[int]]:
        """
        批量转换多个 bounding box 坐标

        Args:
            boxes: 多个 [xmin, ymin, xmax, ymax] 格式的坐标

        Returns:
            转换后的坐标列表
        """
        return [self.convert_box(box) for box in boxes]

    def convert_point(self, point: Union[List[int], Tuple[int, int]]) -> List[int]:
        """
        转换单个点坐标

        Args:
            point: [x, y] 格式的坐标

        Returns:
            转换后的坐标 [x, y]
        """
        x, y = point
        return [int(x * self.scale_x), int(y * self.scale_y)]

    def parse_coordinates_from_text(self, text: str) -> List[List[int]]:
        """
        从文本中解析坐标

        支持以下格式：
        - [[xmin,ymin,xmax,ymax]]
        - [[xmin, ymin, xmax, ymax]]
        - [[x1,y1,x2,y2],[x3,y3,x4,y4]]
        - JSON 格式的数组

        Args:
            text: 包含坐标的文本

        Returns:
            解析出的坐标列表
        """
        # 尝试匹配 [[x1,y1,x2,y2]] 或 [[x1, y1, x2, y2]] 格式
        pattern = r'\[\s*\[(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]\s*\]'
        matches = re.findall(pattern, text)

        if matches:
            boxes = []
            for match in matches:
                boxes.append([int(match[0]), int(match[1]), int(match[2]), int(match[3])])
            return boxes

        # 尝试解析 JSON 格式
        try:
            data = json.loads(text)
            if isinstance(data, list):
                if isinstance(data[0], list) and len(data[0]) == 4:
                    return data
        except (json.JSONDecodeError, IndexError):
            pass

        return []

    @classmethod
    def from_image_url(cls, image_url: str) -> 'GLMCoordinateConverter':
        """
        从图像 URL 创建转换器

        Args:
            image_url: 图像 URL

        Returns:
            GLMCoordinateConverter 实例
        """
        logger.info(f"从 URL 下载图像: {image_url}")
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return cls(img.size[0], img.size[1])

    @classmethod
    def from_image_path(cls, image_path: str) -> 'GLMCoordinateConverter':
        """
        从本地图像路径创建转换器

        Args:
            image_path: 本地图像路径

        Returns:
            GLMCoordinateConverter 实例
        """
        logger.info(f"从文件加载图像: {image_path}")
        img = Image.open(image_path)
        return cls(img.size[0], img.size[1])

    def log_conversion(self, original_box: List[int], converted_box: List[int]):
        """记录转换详情"""
        logger.info(f"坐标转换:")
        logger.info(f"  GLM-4V 坐标 (999x999): {original_box}")
        logger.info(f"  原始图像坐标 ({self.original_width}x{self.original_height}): {converted_box}")
        logger.info(f"  转换比例: X={self.scale_x:.4f}, Y={self.scale_y:.4f}")


def demo_coordinate_conversion():
    """演示坐标转换功能"""

    logger.info("=" * 80)
    logger.info("GLM-4V 坐标转换演示")
    logger.info("=" * 80)

    # 1. 从图像 URL 创建转换器
    image_url = "https://cloudcovert-1305175928.cos.ap-guangzhou.myqcloud.com/%E5%9B%BE%E7%89%87grounding.PNG"
    converter = GLMCoordinateConverter.from_image_url(image_url)

    logger.info("=" * 80)
    logger.info("测试坐标转换")
    logger.info("=" * 80)

    # 2. 示例：GLM-4V 返回的坐标
    glm_boxes = [[93, 588, 197, 990]]
    logger.info(f"\nGLM-4V 返回的坐标: {glm_boxes}")

    # 3. 转换坐标
    converted_boxes = converter.convert_boxes(glm_boxes)

    # 4. 打印转换结果
    for i, (original, converted) in enumerate(zip(glm_boxes, converted_boxes)):
        converter.log_conversion(original, converted)

    logger.info("=" * 80)
    logger.info("坐标转换完成")
    logger.info("=" * 80)

    # 5. 测试坐标解析
    test_text = "[[93,588,197,990]]"
    parsed_boxes = converter.parse_coordinates_from_text(test_text)
    logger.info(f"\n从文本 '{test_text}' 解析的坐标: {parsed_boxes}")

    return converter, converted_boxes


if __name__ == "__main__":
    demo_coordinate_conversion()
