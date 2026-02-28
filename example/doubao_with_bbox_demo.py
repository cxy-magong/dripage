#!/usr/bin/env python
"""
豆包（Doubao）视觉模型完整演示
从配置文件读取模型配置，包含模型调用、坐标提取、坐标转换和图像绘制
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from utils.logu import get_logger
from utils.glm_coordinate_converter import GLMCoordinateConverter
from utils.image_bbox_drawer import draw_bbox_on_image

# 创建 logger
logger = get_logger()

# 从环境变量读取配置
api_key = os.environ.get('ARK_API_KEY')
base_url = os.environ.get('ARK_API_CODING')

if not api_key:
    raise ValueError("请设置环境变量 ARK_API_KEY")

if not base_url:
    base_url = "https://api.openai.com/v1"  # 默认 OpenAI 端点

logger.info("========================================")
logger.info("豆包视觉模型完整演示（含 bbox 绘制）")
logger.info("========================================")
logger.info(f"API Key: {api_key[:10]}...{api_key[-4:]}")
logger.info(f"Base URL: {base_url}")
logger.info("")

# 使用本地图片路径 [Image 1]
image_path = "output/screenshot_20260125_093556.png"
query = "定位文件上传图标，返回JSON数组格式：[[x1,y1,x2,y2]]"

logger.info(f"Image Path: {image_path}")
logger.info(f"Query: {query}")
logger.info("")

# 1. 获取原始图像尺寸并创建坐标转换器
logger.info("=" * 80)
logger.info("步骤 1: 初始化坐标转换器")
logger.info("=" * 80)
# 从本地图片路径读取，使用类方法
converter = GLMCoordinateConverter.from_image_path(image_path)
logger.info("")

# 2. 调用豆包模型（使用 OpenAI 兼容接口）
logger.info("=" * 80)
logger.info("步骤 2: 调用豆包模型")
logger.info("=" * 80)

# 读取本地图片并编码为 base64
logger.info(f"读取本地图片: {image_path}")
import base64
from PIL import Image

# 读取图片
with open(image_path, 'rb') as f:
    image_data = f.read()

# 转换为 base64
image_base64 = f"data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}"
logger.info(f"图片已编码为 base64，长度: {len(image_base64)}")

# 创建 OpenAI 兼容的客户端（支持豆包端点）
vision_llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="doubao-seed-code-preview-251028",  # 豆包模型
    temperature=0.1,
    max_tokens=1024,
)

# 调用模型
from langchain_core.messages import HumanMessage

response = vision_llm.invoke([
    HumanMessage(content=[
        {"type": "image_url", "image_url": {"url": image_base64}},
        {"type": "text", "text": query}
    ])
])

# 3. 提取模型返回的内容
logger.info("=" * 80)
logger.info("步骤 3: 提取模型返回信息")
logger.info("=" * 80)
message = response.content[0] if isinstance(response.content, list) else response.content
logger.info(f"返回内容: {message}")
logger.info("")

# 4. 解析坐标
logger.info("=" * 80)
logger.info("步骤 4: 解析豆包返回的坐标")
logger.info("=" * 80)

# 豆包可能返回 XML 标签格式：<bbox>x1 y1 x2 y2</bbox> 或 JSON 格式
# 需要提取坐标数据

import re

# 尝试多种解析方式
model_boxes = None

# 方式 1: 解析 XML 标签格式 <bbox>457 470 542 856</bbox>
bbox_match = re.search(r'<bbox>\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*</bbox>', str(message))
if bbox_match:
    # 转换为嵌套列表格式 [[x1, y1, x2, y2]]
    x1, y1, x2, y2 = map(int, bbox_match.groups())
    model_boxes = [[x1, y1, x2, y2]]
    logger.info(f"检测到 XML 格式: <bbox>{x1} {y1} {x2} {y2}</bbox>")
else:
    # 方式 2: 使用原有的解析逻辑（JSON 数组格式）
    model_boxes = converter.parse_coordinates_from_text(str(message))

if model_boxes:
    logger.info(f"解析出 {len(model_boxes)} 个 bounding box:")
    for i, box in enumerate(model_boxes):
        logger.info(f"  Box {i+1}: {box}")
    logger.info("")
else:
    logger.warning("未能从返回内容中解析出坐标")
    logger.warning("原始返回内容:")
    logger.warning(str(message)[:500])  # 打印前500个字符用于调试
    logger.info("")

# 5. 转换坐标到原始图像坐标系
logger.info("=" * 80)
logger.info("步骤 5: 转换坐标到原始图像坐标系")
logger.info("=" * 80)

if model_boxes:
    converted_boxes = converter.convert_boxes(model_boxes)

    logger.info("")
    logger.info("坐标转换详情:")
    for i, (original, converted) in enumerate(zip(model_boxes, converted_boxes)):
        logger.info("")
        logger.info(f"Bounding Box {i+1}:")
        converter.log_conversion(original, converted)
    logger.info("")

    logger.info("=" * 80)
    logger.info("最终结果")
    logger.info("=" * 80)
    print("\n原始图像尺寸:", converter.original_width, "x", converter.original_height)
    print("\n豆包模型返回的坐标:")
    for i, box in enumerate(model_boxes):
        print(f"  Box {i+1}: {box}")

    print("\n转换到原始图像坐标系的坐标:")
    for i, box in enumerate(converted_boxes):
        print(f"  Box {i+1}: {box}")

    print("\n转换公式:")
    print(f"  original_x = model_x * ({converter.original_width} / {GLMCoordinateConverter.GLM_SCALED_SIZE}) = model_x * {converter.scale_x:.4f}")
    print(f"  original_y = model_y * ({converter.original_height} / {GLMCoordinateConverter.GLM_SCALED_SIZE}) = model_y * {converter.scale_y:.4f}")

    # 6. 在本地图像上绘制 bounding box（不需要下载）
    logger.info("")
    logger.info("=" * 80)
    logger.info("步骤 6: 在本地图像上绘制 bounding box")
    logger.info("=" * 80)

    from PIL import Image
    import shutil

    # 复制本地图片到输出目录，避免修改原图
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成输出文件名
    import os
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    original_image_path = os.path.join(output_dir, f"doubao_original_{timestamp}.png")
    
    logger.info(f"复制本地图片: {image_path} -> {original_image_path}")
    shutil.copy2(image_path, original_image_path)
    logger.info(f"原图已保存到: {original_image_path}")

    # 在图像上绘制 bounding box
    for i, box in enumerate(converted_boxes):
        label = f"目标对象 {i+1}"
        logger.info(f"\n绘制 bounding box {i+1}:")
        logger.info(f"  坐标: {box}")
        logger.info(f"  标签: {label}")

        # 绘制 box（使用蓝色，区别于智谱的红色）
        output_path = draw_bbox_on_image(
            image_path=original_image_path,
            bbox=box,
            label=label,
            color=(0, 0, 255),  # 蓝色
            line_width=3
        )

        logger.info(f"  图像已保存到: {output_path}")

        print(f"\n{'=' * 80}")
        print(f"Bounding Box {i+1} 绘制完成")
        print(f"{'=' * 80}")
        print(f"豆包坐标: {model_boxes[i]}")
        print(f"原始图像坐标 ({converter.original_width}x{converter.original_height}): {box}")
        print(f"输出图像: {output_path}")
        print(f"{'=' * 80}")

else:
    logger.info("没有需要转换的坐标")

logger.info("")
logger.info("=" * 80)
logger.info("演示完成")
logger.info("=" * 80)
