#!/usr/bin/env python
"""
Agent Tools - Agent 工具
提供视觉识别、坐标变换等工具

使用 Runtime 配置从 config/tools_runtime.yaml 获取默认配置
"""

import os
import sys
import base64
import re
import json
from pathlib import Path
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
from langchain_core.tools import tool
import yaml
from PIL import Image

# 添加项目目录到路径
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from utils.drission_page import create_browser
from utils.logu import get_logger

logger = get_logger('agent_tools')


class AgentToolConfig:
    """Agent 工具配置管理器 - 从 Runtime 配置加载"""

    def __init__(self):
        """从 config/tools_runtime.yaml 加载配置"""
        config_path = project_dir / 'config' / 'tools_runtime.yaml'

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        else:
            # 使用默认配置
            config = {
                'output': {'directory': 'output/data', 'images_subdir': 'images', 'timestamp_format': '%Y%m%d_%H%M%S'},
                'vision': {'model': 'glm-4v-flash', 'temperature': 0.7, 'max_tokens': 1024, 'glm_scaled_size': 999},
                'coordinate': {'glm_scaled_size': 999},
                'tools': {'logging': True, 'draw_bbox': False, 'bbox_line_width': 3}
            }

        self.output_dir = project_dir / config['output']['directory']
        self.images_subdir = config['output'].get('images_subdir', 'images')
        self.timestamp_format = config['output'].get('timestamp_format', '%Y%m%d_%H%M%S')

        self.vision_model = config['vision']['model']
        self.vision_temperature = config['vision']['temperature']
        self.vision_max_tokens = config['vision']['max_tokens']
        self.glm_scaled_size = config['vision'].get('glm_scaled_size', 999)

        self.coordinate_glm_scaled_size = config['coordinate'].get('glm_scaled_size', 999)

        self.logging = config['tools'].get('logging', True)
        self.draw_bbox = config['tools'].get('draw_bbox', False)
        self.bbox_line_width = config['tools'].get('bbox_line_width', 3)

        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if self.logging:
            logger.info(f"AgentTools 配置加载成功:")
            logger.info(f"  Vision 模型: {self.vision_model}")
            logger.info(f"  输出目录: {self.output_dir}")
            logger.info(f"  GLM 缩放尺寸: {self.glm_scaled_size}")


# 全局配置实例（单例）
_config_instance: Optional[AgentToolConfig] = None


def get_config() -> AgentToolConfig:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = AgentToolConfig()
    return _config_instance


def generate_timestamp() -> str:
    """生成时间戳"""
    config = get_config()
    return datetime.now().strftime(config.timestamp_format)


class CoordinateConverter:
    """坐标转换器 - GLM-4V 坐标转换"""

    def __init__(self, original_width: int, original_height: int, glm_scaled_size: int = None):
        """
        初始化坐标转换器

        Args:
            original_width: 原始图像宽度
            original_height: 原始图像高度
            glm_scaled_size: GLM-4V 内部缩放尺寸（默认从配置获取）
        """
        config = get_config()
        self.glm_scaled_size = glm_scaled_size or config.glm_scaled_size
        self.original_width = original_width
        self.original_height = original_height

        # 计算缩放比例
        self.scale_x = original_width / self.glm_scaled_size
        self.scale_y = original_height / self.glm_scaled_size

        if config.logging:
            logger.info(f"坐标转换器初始化:")
            logger.info(f"  原始图像尺寸: {original_width} x {original_height}")
            logger.info(f"  GLM 缩放尺寸: {self.glm_scaled_size} x {self.glm_scaled_size}")
            logger.info(f"  X 轴缩放比例: {self.scale_x:.4f}")
            logger.info(f"  Y 轴缩放比例: {self.scale_y:.4f}")

    def convert_box(self, box: Union[List[int], tuple]) -> List[int]:
        """
        转换单个 bounding box 坐标

        Args:
            box: [xmin, ymin, xmax, ymax] 格式的坐标

        Returns:
            转换后的坐标 [xmin, ymin, xmax, ymax]
        """
        xmin, ymin, xmax, ymax = box
        return [
            int(xmin * self.scale_x),
            int(ymin * self.scale_y),
            int(xmax * self.scale_x),
            int(ymax * self.scale_y)
        ]

    def convert_point(self, point: Union[List[int], tuple]) -> List[int]:
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
    def from_image_path(cls, image_path: str, glm_scaled_size: int = None) -> 'CoordinateConverter':
        """
        从图像路径创建转换器

        Args:
            image_path: 本地图像路径
            glm_scaled_size: GLM 缩放尺寸（可选）

        Returns:
            CoordinateConverter 实例
        """
        config = get_config()
        if config.logging:
            logger.info(f"从文件加载图像: {image_path}")

        img = Image.open(image_path)
        return cls(img.size[0], img.size[1], glm_scaled_size)


@tool
def vision_analyze(
    query: str,
    image_path: Optional[str] = None,
) -> str:
    """
    使用 GLM-4V 视觉模型分析图像

    Args:
        query: 关于图像的问题或查询
        image_path: 图像文件路径（可选，如果不提供则截取当前页面截图）

    Returns:
        视觉分析结果（JSON 字符串格式，包含分析结果、图片尺寸、文件路径）
    """
    from PIL import Image
    from zhipuai import ZhipuAI
    config = get_config()

    if config.logging:
        logger.info(f"视觉分析: query='{query}', image_path={image_path}")

    try:
        # 获取 API key
        api_key = os.environ.get('ZAI_API_KEY')
        if not api_key:
            raise ValueError("ZAI_API_KEY not found in environment variables")

        # 从配置文件读取模型
        vision_model = config.vision_model

        # 初始化客户端
        client = ZhipuAI(api_key=api_key)

        # 确定图像来源和文件路径
        saved_file_path = None
        if image_path:
            # 使用提供的图像文件
            img_path = Path(image_path)
            if not img_path.exists():
                raise ValueError(f"图像文件不存在: {image_path}")
        else:
            # 截取当前页面截图
            from tools.browser_tools import get_browser
            page = get_browser()
            screenshot_data = page.get_screenshot(as_bytes=True)

            # 保存到输出目录
            timestamp = generate_timestamp()
            img_path = config.output_dir / f"vision_{timestamp}.png"
            with open(img_path, 'wb') as f:
                f.write(screenshot_data)

            saved_file_path = str(img_path)

            if config.logging:
                logger.info(f"临时截图已保存到: {img_path}")

        # 获取图片尺寸
        img = Image.open(img_path)
        image_width, image_height = img.size

        # 编码图像为 base64
        with open(img_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')

        # 调用视觉模型
        response = client.chat.completions.create(
            model=vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": query
                        }
                    ]
                }
            ],
            temperature=config.vision_temperature,
            max_tokens=config.vision_max_tokens
        )

        result = response.choices[0].message.content

        # 构建返回结果字典
        response_data = {
            "analysis": result,
            "image_size": {
                "width": image_width,
                "height": image_height
            },
            "model": vision_model
        }

        # 如果保存了新文件，添加文件路径
        if saved_file_path:
            response_data["image_path"] = saved_file_path

        if config.logging:
            logger.info(f"视觉分析完成，结果长度: {len(result)}, 图片尺寸: {image_width}x{image_height}")

        return json.dumps(response_data, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"视觉分析失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False, indent=2)


@tool
def coordinate_convert_box(
    box: List[int],
    original_width: int,
    original_height: int,
) -> str:
    """
    将 GLM-4V 返回的坐标转换回原始图像坐标系

    Args:
        box: GLM-4V 返回的 bounding box [xmin, ymin, xmax, ymax]
        original_width: 原始图像宽度
        original_height: 原始图像高度

    Returns:
        JSON 格式的转换后坐标
    """
    import json
    config = get_config()

    if config.logging:
        logger.info(f"坐标转换: box={box}, size={original_width}x{original_height}")

    try:
        converter = CoordinateConverter(original_width, original_height, None)
        converted_box = converter.convert_box(box)

        result = {
            "original_box": box,
            "converted_box": converted_box,
            "original_size": {"width": original_width, "height": original_height},
            "glm_scaled_size": converter.glm_scaled_size,
            "scale_x": converter.scale_x,
            "scale_y": converter.scale_y
        }

        if config.logging:
            logger.info(f"转换结果: {converted_box}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"坐标转换失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def coordinate_parse_and_convert(
    text: str,
    original_width: int,
    original_height: int,
) -> str:
    """
    从文本解析坐标并转换回原始图像坐标系

    Args:
        text: 包含坐标的文本（如视觉模型返回的响应）
        original_width: 原始图像宽度
        original_height: 原始图像高度

    Returns:
        JSON 格式的转换后坐标列表
    """
    import json
    config = get_config()

    if config.logging:
        logger.info(f"从文本解析坐标并转换: text='{text[:100]}...'")

    try:
        converter = CoordinateConverter(original_width, original_height, None)

        # 解析坐标
        glm_boxes = converter.parse_coordinates_from_text(text)

        if not glm_boxes:
            return json.dumps({"error": "未能从文本中解析出坐标"}, ensure_ascii=False, indent=2)

        # 转换坐标
        converted_boxes = [converter.convert_box(box) for box in glm_boxes]

        result = {
            "parsed_boxes": glm_boxes,
            "converted_boxes": converted_boxes,
            "count": len(converted_boxes),
            "original_size": {"width": original_width, "height": original_height},
            "glm_scaled_size": converter.glm_scaled_size
        }

        if config.logging:
            logger.info(f"解析并转换了 {len(converted_boxes)} 个坐标")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"坐标解析和转换失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def coordinate_convert_from_image(
    text: str,
    image_path: str,
) -> str:
    """
    从文本解析坐标，根据图像尺寸自动转换回原始坐标系

    Args:
        text: 包含坐标的文本（如视觉模型返回的响应）
        image_path: 图像文件路径（用于获取原始尺寸）

    Returns:
        JSON 格式的转换后坐标列表
    """
    import json
    config = get_config()

    if config.logging:
        logger.info(f"从图像自动转换坐标: image_path={image_path}")

    try:
        # 从图像创建转换器
        converter = CoordinateConverter.from_image_path(image_path, None)

        # 解析坐标
        glm_boxes = converter.parse_coordinates_from_text(text)

        if not glm_boxes:
            return json.dumps({"error": "未能从文本中解析出坐标"}, ensure_ascii=False, indent=2)

        # 转换坐标
        converted_boxes = [converter.convert_box(box) for box in glm_boxes]

        result = {
            "parsed_boxes": glm_boxes,
            "converted_boxes": converted_boxes,
            "count": len(converted_boxes),
            "image_path": str(image_path),
            "original_size": {"width": converter.original_width, "height": converter.original_height},
            "glm_scaled_size": converter.glm_scaled_size
        }

        if config.logging:
            logger.info(f"自动转换了 {len(converted_boxes)} 个坐标")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"坐标转换失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


# 导出所有工具函数，方便 FastMCP 或其他框架调用
__all__ = [
    'vision_analyze',
    'coordinate_convert_box',
    'coordinate_parse_and_convert',
    'coordinate_convert_from_image',
    'CoordinateConverter',
    'get_config',
]


if __name__ == "__main__":
    # 测试配置加载
    config = get_config()

    print("\n" + "=" * 80)
    print("Agent Tools 配置测试")
    print("=" * 80)
    print(f"Vision 模型: {config.vision_model}")
    print(f"输出目录: {config.output_dir}")
    print(f"GLM 缩放尺寸: {config.glm_scaled_size}")
    print("=" * 80)
