#!/usr/bin/env python
"""
GLM-4.1V-Thinking-Flash 完整演示
包含模型调用、坐标提取、坐标转换和图像绘制
"""

import os
from zai import ZhipuAiClient
from utils.logu import get_logger
from utils.glm_coordinate_converter import GLMCoordinateConverter
from utils.image_bbox_drawer import draw_bbox_on_image

# 创建 logger
logger = get_logger('glm_4_1v_with_bbox_demo')

# 使用官方示例代码
client = ZhipuAiClient(api_key=os.environ.get('ZAI_API_KEY'))

logger.info("========================================")
logger.info("GLM-4.1V-Thinking-Flash 完整演示（含 bbox 绘制）")
logger.info("========================================")

# 测试图像 URL
image_url = "https://cloudcovert-1305175928.cos.ap-guangzhou.myqcloud.com/%E5%9B%BE%E7%89%87grounding.PNG"
query = "给出右边绿色瓶子box 坐标"

logger.info(f"Image URL: {image_url}")
logger.info(f"Query: {query}")
logger.info("")

# 1. 获取原始图像尺寸并创建坐标转换器
logger.info("=" * 80)
logger.info("步骤 1: 初始化坐标转换器")
logger.info("=" * 80)
converter = GLMCoordinateConverter.from_image_url(image_url)
logger.info("")

# 2. 调用 GLM-4.1V-Thinking-Flash 模型
logger.info("=" * 80)
logger.info("步骤 2: 调用 GLM-4.1V-Thinking-Flash 模型")
logger.info("=" * 80)
response = client.chat.completions.create(
    model="GLM-4.1V-Thinking-Flash",
    messages=[
        {
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                },
                {
                    "type": "text",
                    "text": query
                }
            ],
            "role": "user"
        }
    ],
    thinking={
        "type":"enabled"
    }
)

# 3. 提取模型返回的内容
logger.info("=" * 80)
logger.info("步骤 3: 提取模型返回信息")
logger.info("=" * 80)
message = response.choices[0].message
logger.info(f"返回内容: {message.content}")
if hasattr(message, 'reasoning_content') and message.reasoning_content:
    logger.info(f"推理过程: {message.reasoning_content}")
logger.info("")

# 4. 解析坐标
logger.info("=" * 80)
logger.info("步骤 4: 解析 GLM-4V 返回的坐标")
logger.info("=" * 80)
glm_boxes = converter.parse_coordinates_from_text(message.content)

if glm_boxes:
    logger.info(f"解析出 {len(glm_boxes)} 个 bounding box:")
    for i, box in enumerate(glm_boxes):
        logger.info(f"  Box {i+1}: {box}")
    logger.info("")
else:
    logger.warning("未能从返回内容中解析出坐标")
    logger.info("")

# 5. 转换坐标到原始图像坐标系
logger.info("=" * 80)
logger.info("步骤 5: 转换坐标到原始图像坐标系")
logger.info("=" * 80)

if glm_boxes:
    converted_boxes = converter.convert_boxes(glm_boxes)

    logger.info("")
    logger.info("坐标转换详情:")
    for i, (original, converted) in enumerate(zip(glm_boxes, converted_boxes)):
        logger.info("")
        logger.info(f"Bounding Box {i+1}:")
        converter.log_conversion(original, converted)
    logger.info("")

    logger.info("=" * 80)
    logger.info("最终结果")
    logger.info("=" * 80)
    print("\n原始图像尺寸:", converter.original_width, "x", converter.original_height)
    print("\nGLM-4.1V-Thinking-Flash 返回的坐标 (基于 999x999):")
    for i, box in enumerate(glm_boxes):
        print(f"  Box {i+1}: {box}")

    print("\n转换到原始图像坐标系的坐标:")
    for i, box in enumerate(converted_boxes):
        print(f"  Box {i+1}: {box}")

    print("\n转换公式:")
    print(f"  original_x = glm_x * ({converter.original_width} / 999) = glm_x * {converter.scale_x:.4f}")
    print(f"  original_y = glm_y * ({converter.original_height} / 999) = glm_y * {converter.scale_y:.4f}")

    # 6. 下载原始图像并绘制 bounding box
    logger.info("")
    logger.info("=" * 80)
    logger.info("步骤 6: 下载图像并绘制 bounding box")
    logger.info("=" * 80)

    import requests
    from PIL import Image
    from io import BytesIO

    # 下载图像
    logger.info(f"下载图像: {image_url}")
    response = requests.get(image_url)
    original_image = Image.open(BytesIO(response.content))

    # 保存原始图像到本地
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    original_image_path = os.path.join(output_dir, "original_image.png")
    original_image.save(original_image_path)
    logger.info(f"原始图像已保存到: {original_image_path}")

    # 在图像上绘制 bounding box
    for i, box in enumerate(converted_boxes):
        label = f"目标对象 {i+1}"
        logger.info(f"\n绘制 bounding box {i+1}:")
        logger.info(f"  坐标: {box}")
        logger.info(f"  标签: {label}")

        # 绘制 box（红色）
        output_path = draw_bbox_on_image(
            image_path=original_image_path,
            bbox=box,
            label=label,
            color=(255, 0, 0),
            line_width=3
        )

        logger.info(f"  图像已保存到: {output_path}")

        print(f"\n{'=' * 80}")
        print(f"Bounding Box {i+1} 绘制完成")
        print(f"{'=' * 80}")
        print(f"GLM-4V 坐标 (999x999): {glm_boxes[i]}")
        print(f"原始图像坐标 ({converter.original_width}x{converter.original_height}): {box}")
        print(f"输出图像: {output_path}")
        print(f"{'=' * 80}")

else:
    logger.info("没有需要转换的坐标")

logger.info("")
logger.info("=" * 80)
logger.info("演示完成")
logger.info("=" * 80)
