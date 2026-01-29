#!/usr/bin/env python
"""
Agent Tools - Agent 工具
提供视觉识别、坐标变换等工具

使用 Runtime 配置从 config/tools_runtime.yaml 获取默认配置
使用 ToolRuntime 在工具间共享上下文（按照 LangChain 文档使用 Command 更新状态）
"""

import os
import sys
import base64
import re
import json
import yaml
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from typing import Optional, List, Union, Dict, Any, TypedDict
from datetime import datetime
from PIL import Image
from langgraph.types import Command
from langchain.messages import RemoveMessage
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI


# 添加项目目录到路径
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from utils.drission_page import create_browser
from utils.logu import get_logger
from utils.model_config import get_config as get_global_config
from tools.tab_manager import get_tab_object

logger = get_logger('agent_tools')


# ==================== ToolRuntime 状态类型定义 ====================
# 注意：ToolRuntime 仅在 LangChain Agent 执行环境中有效

# 用于 ToolRuntime 的类型定义
class AgentState(TypedDict):
    """Agent 状态 - 在工具间共享的状态"""
    image_path: Optional[str]
    image_width: Optional[int]
    image_height: Optional[int]
    vision_analysis: Optional[str]
    converted_coordinates: Optional[Dict[str, Any]]


# ==================== 通用浏览器截图函数 ====================

def save_browser_screenshot(
    tab_id: Optional[Union[int, str]] = None,
    prefix: str = "screenshot",
    save: bool = True
) -> Optional[str]:
    """
    通用浏览器截图函数 - 支持指定标签

    Args:
        tab_id: 标签标识符（None=当前标签，int=索引，str=tab_id）
        prefix: 文件名前缀（默认 'screenshot'）
        save: 是否保存到文件（默认 True）

    Returns:
        保存的文件路径（如果 save=True），否则返回 None
    """
    from tools.tab_manager import get_tab_object

    config = get_config()

    if config.logging:
        logger.info(f"截取浏览器截图 (tab_id={tab_id}, prefix={prefix}, save={save})")

    try:
        # 获取指定标签对象
        tab, metadata = get_tab_object(tab_id)

        # 生成文件名
        timestamp = generate_timestamp()
        filename = f"{prefix}_{timestamp}.png"
        filepath = config.output_dir / filename

        # 截取截图
        screenshot_data = tab.get_screenshot(as_bytes=True)

        # 保存截图
        if save:
            with open(filepath, 'wb') as f:
                f.write(screenshot_data)

            if config.logging:
                logger.info(f"截图已保存到: {filepath} (标签: {metadata['title']})")

            return str(filepath)
        else:
            return None

    except Exception as e:
        error_msg = f"截图失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return None


class AgentToolConfig:
    """Agent 工具配置管理器 - 从 Runtime 配置加载"""

    def __init__(self):
        """从 config/tools_runtime.yaml 和 config/models_config.yaml 加载配置"""
        config_path = project_dir / 'config' / 'tools_runtime.yaml'

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        else:
            # 使用默认配置
            config = {
                'output': {'directory': 'output/data', 'images_subdir': 'images', 'timestamp_format': '%Y%m%d_%H%M%S'},
                'vision': {'model_key': 'glm_4_1v_thinking', 'temperature': 0.1, 'max_tokens': 4096, 'glm_scaled_size': 999},
                'coordinate': {'glm_scaled_size': 999},
                'tools': {'logging': True, 'draw_bbox': False, 'bbox_line_width': 3}
            }

        # 加载模型配置
        models_config_path = project_dir / 'config' / 'models_config.yaml'
        model_key = config['vision'].get('model_key', 'glm_4_1v_thinking')
        model_config = {}

        if models_config_path.exists():
            with open(models_config_path, 'r', encoding='utf-8') as f:
                models_config = yaml.safe_load(f)
                if model_key in models_config.get('models', {}):
                    model_config = models_config['models'][model_key]
                    logger.info(f"从 models_config.yaml 加载模型配置: {model_key}")
                else:
                    logger.warning(f"未在 models_config.yaml 中找到模型: {model_key}")
        else:
            logger.warning(f"models_config.yaml 不存在，使用默认配置")

        self.output_dir = project_dir / config['output']['directory']
        self.images_subdir = config['output'].get('images_subdir', 'images')
        self.timestamp_format = config['output'].get('timestamp_format', '%Y%m%d_%H%M%S')

        # Vision 配置：优先使用 models_config.yaml 中的值，然后是 tools_runtime.yaml 中的值
        self.vision_model = model_config.get('name', model_key)
        self.vision_temperature = config['vision'].get('temperature', model_config.get('temperature', 0.1))
        self.vision_max_tokens = config['vision'].get('max_tokens', model_config.get('max_tokens', 4096))
        self.glm_scaled_size = config['vision'].get('glm_scaled_size', 999)

        # Agent 配置
        self.agent_model = config.get('agent', {}).get('model', 'glm-4.7')
        self.agent_temperature = config.get('agent', {}).get('temperature', 0.3)

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
    tab_id: Optional[Union[int, str]] = None,
    runtime: ToolRuntime = None,
) -> str:
    """
    使用 GLM-4.1V 视觉模型分析图像（支持指定标签）

    Args:
        query: 关于图像的问题或查询
        image_path: 图像文件路径（可选，如果不提供则截取指定标签的页面）
        tab_id: 标签标识符（None=当前标签，int=索引，str=tab_id）
        runtime: ToolRuntime 参数（自动注入，用于共享状态）

    Returns:
        视觉分析结果（JSON 字符串格式，包含分析结果、图片尺寸、文件路径、标签信息）
    """
    from tools.tab_manager import get_tab_object

    config = get_config()

    if config.logging:
        logger.info(f"视觉分析: query='{query}', image_path={image_path}, tab_id={tab_id}")

    try:
        # 获取 API key
        api_key = os.environ.get('ZAI_API_KEY')
        if not api_key:
            raise ValueError("ZAI_API_KEY not found in environment variables")

        # 确定图像来源和文件路径
        saved_file_path = None
        tab_metadata = {}

        if image_path:
            # 使用提供的图像文件
            img_path = Path(image_path)
            if not img_path.exists():
                raise ValueError(f"图像文件不存在: {image_path}")
        else:
            # 截取指定标签的页面
            saved_file_path = save_browser_screenshot(tab_id=tab_id, prefix="vision", save=True)

            if saved_file_path is None:
                raise RuntimeError("截图失败")

            # 获取标签元数据
            _, tab_metadata = get_tab_object(tab_id)
            img_path = Path(saved_file_path)

        # 获取图片尺寸
        img = Image.open(img_path)
        image_width, image_height = img.size

        # 编码图像为 base64
        with open(img_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')

        # 使用 ChatOpenAI 初始化视觉模型（OpenAI 兼容接口）
        vision_llm = ChatOpenAI(
            api_key=api_key,
            base_url=os.getenv("ZAI_API_BASE"),
            model=config.vision_model,
            temperature=config.vision_temperature,
            max_tokens=config.vision_max_tokens,
        )

        # 构建消息（使用 HumanMessage）
        from langchain_core.messages import HumanMessage
        response = vision_llm.invoke([
            HumanMessage(content=[
                {"type": "image_url", "image_url": {"url": image_base64}},
                {"type": "text", "text": query}
            ])
        ])

        result = response.content

        # 更新 runtime.state 中的图像信息
        if runtime is not None:
            runtime.state["image_path"] = str(img_path)
            runtime.state["image_width"] = image_width
            runtime.state["image_height"] = image_height
            runtime.state["vision_analysis"] = result

            if config.logging:
                logger.info(f"已更新 runtime.state: image_path={img_path}, size={image_width}x{image_height}")

        # 返回分析结果（包含标签信息）
        result_dict = {
            "analysis": result,
            "image_size": {"width": image_width, "height": image_height},
            "image_path": str(img_path),
            "tab": tab_metadata
        }

        return json.dumps(result_dict, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"视觉分析失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False, indent=2)


@tool
def coordinate_convert_box_with_runtime(
    box: List[int],
    runtime: ToolRuntime = None,
) -> Command:
    """
    将 GLM-4V 坐标转换回原始图像坐标系（从 runtime.state 获取图像尺寸）

    Args:
        box: GLM-4V 返回的 bounding box [xmin, ymin, xmax, ymax]
        runtime: ToolRuntime 参数（自动注入，用于获取图像信息）

    Returns:
        Command 对象，用于更新 runtime.state 中的 converted_coordinates
    """
    config = get_config()
    try:
        # 从 runtime.state 获取图像尺寸
        if runtime is None:
            raise ValueError("ToolRuntime is None")

        image_width = runtime.state.get("image_width")
        image_height = runtime.state.get("image_height")

        if image_width is None or image_height is None:
            raise ValueError("图像尺寸未在 runtime.state 中设置，请先调用 vision_analyze")

        # 使用 GLMCoordinateConverter 转换坐标
        converter = CoordinateConverter(image_width, image_height, None)
        converted_box = converter.convert_box(box)

        if config.logging:
            logger.info(f"转换坐标: {box} -> {converted_box}")

        # 返回 Command 对象，直接用字典更新状态
        return Command(
            update={
                "converted_coordinates": {
                    f"box_{box}": {
                        "original_box": box,
                        "converted_box": converted_box,
                        "original_size": {"width": image_width, "height": image_height},
                        "glm_scaled_size": converter.glm_scaled_size,
                        "scale_x": converter.scale_x,
                        "scale_y": converter.scale_y
                    }
                }
            }
        )

    except Exception as e:
        error_msg = f"坐标转换失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


@tool
def coordinate_convert_point_with_runtime(
    point: List[int],
    runtime: ToolRuntime = None,
) -> Command:
    """
    转换单个点坐标回原始图像坐标系（从 runtime.state 获取图像尺寸）

    Args:
        point: GLM-4V 返回的点坐标 [x, y]
        runtime: ToolRuntime 参数（自动注入，用于获取图像信息）

    Returns:
        Command 对象，用于更新 runtime.state 中的 converted_coordinates
    """
    config = get_config()
    try:
        # 从 runtime.state 获取图像尺寸
        if runtime is None:
            raise ValueError("ToolRuntime is None")

        image_width = runtime.state.get("image_width")
        image_height = runtime.state.get("image_height")

        if image_width is None or image_height is None:
            raise ValueError("图像尺寸未在 runtime.state 中设置，请先调用 vision_analyze")

        # 使用 GLMCoordinateConverter 转换坐标
        converter = CoordinateConverter(image_width, image_height, None)
        converted_point = converter.convert_point(point)

        if config.logging:
            logger.info(f"转换坐标: {point} -> {converted_point}")

        # 返回 Command 对象，直接用字典更新状态
        return Command(
            update={
                "converted_coordinates": {
                    f"point_{point}": {
                        "original_point": point,
                        "converted_point": converted_point,
                        "original_size": {"width": image_width, "height": image_height},
                        "glm_scaled_size": converter.glm_scaled_size,
                        "scale_x": converter.scale_x,
                        "scale_y": converter.scale_y
                    }
                }
            }
        )

    except Exception as e:
        error_msg = f"点坐标转换失败: {str(e)}"
        if config.logging:
            logger.error(error_msg)
        return error_msg


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


@tool
def locate_element(
    query: str,
    image_path: Optional[str] = None,
    tab_id: Optional[Union[int, str]] = None,
    runtime: ToolRuntime = None,
) -> Command:
    """
    定位元素位置信息 - 支持指定标签（使用视觉分析 + 坐标转换）

    Args:
        query: 描述要查找的元素，如"搜索输入框"、"提交按钮"等
        image_path: 图像文件路径（可选，如果不提供则截取指定标签的页面）
        tab_id: 标签标识符（None=当前标签，int=索引，str=tab_id）
        runtime: ToolRuntime 参数（自动注入，用于共享状态）

    Returns:
        Command 对象，更新 runtime.state 中的定位结果
    """
    from langchain.chat_models import init_chat_model

    config = get_config()
    query = query+"返回格式： box坐标列表，每个box坐标为[x1,y1,x2,y2]，x1,y1为左上角坐标，x2,y2为右下角坐标。"
    if config.logging:
        logger.info(f"定位元素: query='{query}', image_path={image_path}, tab_id={tab_id}")

    # 如果 runtime 为 None，创建临时的 ToolRuntime
    if runtime is None:
        logger.info("runtime is None，创建临时 ToolRuntime")
        # 使用普通字典而不是 TypedDict，以便可以动态更新
        state = {
            "image_path": None,
            "image_width": None,
            "image_height": None,
            "vision_analysis": None,
            "converted_coordinates": None
        }
        runtime = ToolRuntime(
            state=state,
            context=None,
            tool_call_id="",
            store=None,
            stream_writer=lambda _: None,
            config={}
        )

    try:
        # 步骤 1: 调用 vision_analyze 获取视觉结果（传递 tab_id）
        if image_path:
            vision_result = vision_analyze.func(query, image_path=image_path, tab_id=tab_id, runtime=runtime)
        else:
            vision_result = vision_analyze.func(query, image_path=None, tab_id=tab_id, runtime=runtime)

        # 获取 API key
        api_key = os.environ.get('ZAI_API_KEY')
        if not api_key:
            raise ValueError("ZAI_API_KEY not found in environment variables")
        logger.info(f"使用模型: {config.agent_model}")
        logger.info(f"base_url: {os.getenv('ZAI_API_BASE')}")
        # 初始化 GLM-4.7 模型
        sub_model = ChatOpenAI(
            model=config.agent_model,
            api_key=api_key,
            base_url=os.getenv("ZAI_API_CODING"),
            temperature=config.agent_temperature,
        )

        # 步骤 2: 绑定坐标转换工具到模型
        model_with_tools = sub_model.bind_tools([
            coordinate_convert_box_with_runtime,
            coordinate_convert_point_with_runtime
        ])

        # 步骤 3: 将视觉分析结果作为上下文，让模型执行坐标转换
        user_message = f"""任务：转换坐标

以下是视觉分析的结果：
{vision_result}

请执行坐标转换：
1. 从以上结果中提取坐标（格式如 [[293,244,710,327]]）
2. 调用 coordinate_convert_box_with_runtime 工具转换 box 坐标
3. 如果有点坐标，调用 coordinate_convert_point_with_runtime 工具转换 point 坐标
4. 返回转换后的坐标
"""

        # 调用模型执行坐标转换
        response = model_with_tools.invoke(user_message)
        
        # 获取转换结果
        converted_result = response.content
        logger.info(f"模型返回: {response}")
        # 手动并发调用工具（解析 tool_calls）
        tool_results = []
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call['name'] == 'coordinate_convert_box_with_runtime':
                    # 使用 .func() 方法直接调用底层函数，传递 runtime 参数
                    box = tool_call['args']['box']
                    result = coordinate_convert_box_with_runtime.func(box, runtime=runtime)
                    # 提取 Command 对象中的 update 属性
                    tool_results.append({"tool": "coordinate_convert_box_with_runtime", "result": result.update})
                elif tool_call['name'] == 'coordinate_convert_point_with_runtime':
                    # 使用 .func() 方法直接调用底层函数，传递 runtime 参数
                    point = tool_call['args']['point']
                    result = coordinate_convert_point_with_runtime.func(point, runtime=runtime)
                    # 提取 Command 对象中的 update 属性
                    tool_results.append({"tool": "coordinate_convert_point_with_runtime", "result": result.update})
        
        # 获取标签元数据
        _, tab_metadata = get_tab_object(tab_id)

        # 构建返回结果
        result_dict = {
            "query": query,
            "vision_result": vision_result,
            "coordinate_conversion": converted_result,
            "tool_calls": tool_results,
            "tab": tab_metadata,
            "status": "success"
        }

        if config.logging:
            logger.info(f"元素定位完成，工具调用数量: {len(tool_results)}")

        # 使用 Command 更新 runtime.state
        return Command(
            update={
                "locate_element_result": result_dict
            }
        )

    except Exception as e:
        error_msg = f"定位元素失败: {str(e)}"
        if config.logging:
            logger.exception(error_msg)
        return Command(
            update={
                "locate_element_result": {"error": error_msg}
            }
        )


# 导出所有工具函数，方便 FastMCP 或其他框架调用
__all__ = [
    'vision_analyze',
    'coordinate_convert_box',
    'coordinate_convert_box_with_runtime',
    'coordinate_convert_point_with_runtime',
    'coordinate_parse_and_convert',
    'coordinate_convert_from_image',
    'CoordinateConverter',
    'get_config',
    'locate_element',
    'save_browser_screenshot',
    'AgentState',
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
