#!/usr/bin/env python
"""
图像 Bounding Box 绘制工具
用于在图像上绘制矩形框并保存
"""

import os
from typing import List, Tuple, Union, Optional
from PIL import Image, ImageDraw, ImageFont
import random
from utils.logu import get_logger

logger = get_logger('image_bbox_drawer')


class BBoxDrawer:
    """Bounding Box 绘制器"""

    def __init__(self, line_width: int = 3):
        """
        初始化绘制器

        Args:
            line_width: 线条宽度
        """
        self.line_width = line_width
        logger.info(f"初始化 BBox 绘制器: line_width={line_width}")

    @staticmethod
    def get_random_color(index: int) -> Tuple[int, int, int]:
        """
        获取随机颜色，确保每个 box 颜色不同

        Args:
            index: box 索引

        Returns:
            RGB 颜色元组
        """
        # 使用预设的颜色方案，确保颜色鲜艳且可见
        colors = [
            (255, 0, 0),      # 红色
            (0, 255, 0),      # 绿色
            (0, 0, 255),      # 蓝色
            (255, 255, 0),    # 黄色
            (255, 0, 255),    # 品红
            (0, 255, 255),    # 青色
            (255, 128, 0),    # 橙色
            (128, 0, 255),    # 紫色
            (0, 255, 128),    # 青绿色
            (255, 0, 128),    # 洋红色
        ]
        return colors[index % len(colors)]

    def draw_bboxes_on_image(
        self,
        image_path: str,
        bboxes: List[Union[List[int], Tuple[int, int, int, int]]],
        output_path: Optional[str] = None,
        labels: Optional[List[str]] = None,
        color: Optional[Tuple[int, int, int]] = None,
        show_label: bool = False
    ) -> str:
        """
        在图像上绘制 bounding box

        Args:
            image_path: 输入图像路径
            bboxes: bounding box 列表，每个 box 格式为 [xmin, ymin, xmax, ymax]
            output_path: 输出图像路径（可选，默认与原图同目录）
            labels: 每个 box 的标签列表（可选）
            color: 绘制颜色，格式为 (R, G, B)（可选，默认使用不同颜色）
            show_label: 是否显示标签（只显示数字序号）

        Returns:
            输出图像的路径
        """
        logger.info(f"读取图像: {image_path}")

        # 打开图像
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)

        # 确定输出路径
        if output_path is None:
            dir_name = os.path.dirname(image_path)
            base_name = os.path.basename(image_path)
            name_without_ext = os.path.splitext(base_name)[0]
            ext = os.path.splitext(base_name)[1]
            output_path = os.path.join(dir_name, f"{name_without_ext}_with_bbox{ext}")
            logger.info(f"自动生成输出路径: {output_path}")

        # 绘制每个 bounding box
        for i, box in enumerate(bboxes):
            xmin, ymin, xmax, ymax = box

            # 确定颜色
            if color is not None:
                box_color = color
            else:
                box_color = self.get_random_color(i)

            # 绘制边框（仅线条）
            draw.rectangle([xmin, ymin, xmax, ymax], outline=box_color, width=self.line_width)

            # 绘制标签
            if show_label:
                # 只显示数字序号
                label = str(i + 1)

                # 尝试加载字体
                try:
                    font = ImageFont.truetype("arial.ttf", 30)
                except:
                    font = ImageFont.load_default()

                # 计算文本位置
                bbox = draw.textbbox((0, 0), label, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # 文本位置：box 的左上角稍微向下偏移
                text_x = xmin + 5
                text_y = ymin + 5

                # 确保文本不超出图像边界
                if text_y + text_height > ymax:
                    text_y = ymin - text_height - 5
                if text_y < 0:
                    text_y = ymin + 5

                # 绘制标签文本（带黑色描边效果，提高可见性）
                # 黑色描边
                for offset_x in [-1, 0, 1]:
                    for offset_y in [-1, 0, 1]:
                        draw.text((text_x + offset_x, text_y + offset_y), label, fill=(0, 0, 0), font=font)

                # 白色填充
                draw.text((text_x, text_y), label, fill=(255, 255, 255), font=font)

                logger.info(f"  Box {i+1}: {box} - 颜色: {box_color}, 标签: {label}")

        # 保存图像
        img.save(output_path)
        logger.info(f"图像已保存到: {output_path}")

        return output_path

    def draw_single_bbox(
        self,
        image_path: str,
        bbox: Union[List[int], Tuple[int, int, int, int]],
        output_path: Optional[str] = None,
        label: str = "Target",
        color: Tuple[int, int, int] = (255, 0, 0),
        show_label: bool = False
    ) -> str:
        """
        在图像上绘制单个 bounding box（简化版）

        Args:
            image_path: 输入图像路径
            bbox: bounding box，格式为 [xmin, ymin, xmax, ymax]
            output_path: 输出图像路径（可选）
            label: 标签文本（仅当 show_label=True 时使用，只显示数字）
            color: 绘制颜色，格式为 (R, G, B)
            show_label: 是否显示数字标签（默认 False）

        Returns:
            输出图像的路径
        """
        return self.draw_bboxes_on_image(
            image_path=image_path,
            bboxes=[bbox],
            output_path=output_path,
            labels=[label],
            color=color,
            show_label=show_label
        )


def draw_bbox_on_image(
    image_path: str,
    bbox: Union[List[int], Tuple[int, int, int, int]],
    output_path: Optional[str] = None,
    label: str = "Target",
    color: Tuple[int, int, int] = (255, 0, 0),
    line_width: int = 3,
    show_label: bool = True
) -> str:
    """
    便捷函数：在图像上绘制单个 bounding box

    Args:
        image_path: 输入图像路径
        bbox: bounding box，格式为 [xmin, ymin, xmax, ymax]
        output_path: 输出图像路径（可选）
        label: 标签文本（仅当 show_label=True 时使用，只显示数字）
        color: 绘制颜色，格式为 (R, G, B)
        line_width: 线条宽度
        show_label: 是否显示数字标签（默认 False）

    Returns:
        输出图像的路径

    Example:
        >>> output = draw_bbox_on_image("test.jpg", [100, 200, 300, 400])
        >>> print(f"图像已保存到: {output}")
    """
    drawer = BBoxDrawer(line_width=line_width)
    return drawer.draw_single_bbox(
        image_path=image_path,
        bbox=bbox,
        output_path=output_path,
        label=label,
        color=color,
        show_label=show_label
    )


def draw_bboxes_on_image(
    image_path: str,
    bboxes: List[Union[List[int], Tuple[int, int, int, int]]],
    output_path: Optional[str] = None,
    labels: Optional[List[str]] = None,
    color: Optional[Tuple[int, int, int]] = None,
    line_width: int = 3,
    show_label: bool = False
) -> str:
    """
    便捷函数：在图像上绘制多个 bounding box

    Args:
        image_path: 输入图像路径
        bboxes: bounding box 列表
        output_path: 输出图像路径（可选）
        labels: 标签列表（可选）
        color: 统一颜色（可选，默认使用不同颜色）
        line_width: 线条宽度
        show_label: 是否显示数字标签（默认 False）

    Returns:
        输出图像的路径

    Example:
        >>> boxes = [[100, 200, 300, 400], [500, 600, 700, 800]]
        >>> output = draw_bboxes_on_image("test.jpg", boxes, labels=["Box1", "Box2"])
        >>> print(f"图像已保存到: {output}")
    """
    drawer = BBoxDrawer(line_width=line_width)
    return drawer.draw_bboxes_on_image(
        image_path=image_path,
        bboxes=bboxes,
        output_path=output_path,
        labels=labels,
        color=color,
        show_label=show_label
    )


def demo_bbox_drawing():
    """演示 bbox 绘制功能"""
    from PIL import Image

    logger.info("=" * 80)
    logger.info("Bounding Box 绘制演示")
    logger.info("=" * 80)

    # 创建测试图像
    test_image_path = "test_bbox_demo.jpg"
    logger.info(f"创建测试图像: {test_image_path}")

    # 创建一个简单的测试图像
    img = Image.new('RGB', (800, 600), color='white')
    img.save(test_image_path)

    # 绘制单个 box
    logger.info("=" * 80)
    logger.info("测试 1: 绘制单个 bounding box")
    logger.info("=" * 80)

    output1 = draw_bbox_on_image(
        image_path=test_image_path,
        bbox=[100, 100, 300, 400],
        label="目标对象",
        color=(255, 0, 0)
    )
    logger.info(f"输出图像: {output1}\n")

    # 绘制多个 boxes
    logger.info("=" * 80)
    logger.info("测试 2: 绘制多个 bounding boxes")
    logger.info("=" * 80)

    boxes = [
        [400, 100, 600, 200],
        [500, 300, 700, 500],
        [100, 450, 250, 550]
    ]
    labels = ["物体1", "物体2", "物体3"]

    output2 = draw_bboxes_on_image(
        image_path=test_image_path,
        bboxes=boxes,
        labels=labels
    )
    logger.info(f"输出图像: {output2}\n")

    # 清理测试文件
    import os
    try:
        os.remove(test_image_path)
        if os.path.exists(output1):
            os.remove(output1)
        if os.path.exists(output2):
            os.remove(output2)
        logger.info("测试文件已清理")
    except:
        logger.warning("清理测试文件时出错")

    logger.info("=" * 80)
    logger.info("演示完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    demo_bbox_drawing()
