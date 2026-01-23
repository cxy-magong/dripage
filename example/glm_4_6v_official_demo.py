#!/usr/bin/env python
"""
GLM-4.6V 官方示例测试
完全按照官方文档示例，不做任何修改
"""

import os
from zai import ZhipuAiClient
from utils.logu import get_logger

# 创建 logger
logger = get_logger('glm_4_6v_official_demo')

# 使用官方示例代码，完全按照文档
client = ZhipuAiClient(api_key=os.environ.get('ZAI_API_KEY'))

logger.info("========================================")
logger.info("GLM-4.6V Official Demo")
logger.info("========================================")

logger.info("Model: glm-4.6v")
logger.info("Image URL: https://cloudcovert-1305175928.cos.ap-guangzhou.myqcloud.com/%E5%9B%BE%E7%89%87grounding.PNG")
logger.info("Query: Where is the second bottle of beer from right on the table? Provide coordinates in [[xmin,ymin,xmax,ymax]] format")
logger.info("Thinking: enabled")

# 完全按照官方文档的示例代码
response = client.chat.completions.create(
    model="glm-4.6v",
    messages=[
        {
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://cloudcovert-1305175928.cos.ap-guangzhou.myqcloud.com/%E5%9B%BE%E7%89%87grounding.PNG"
                    }
                },
                {
                    "type": "text",
                    "text": "Where is the second bottle of beer from right on the table? Provide coordinates in [[xmin,ymin,xmax,ymax]] format"
                }
            ],
            "role": "user"
        }
    ],
    thinking={
        "type":"enabled"
    }
)

logger.info("========================================")
logger.info("Response from GLM-4.6V")
logger.info("========================================")

# 输出完整的响应对象
logger.info(f"Full Response Object: {response}")
logger.info(f"Response Type: {type(response)}")

# 输出 choices 信息
logger.info(f"Choices Length: {len(response.choices)}")

if response.choices:
    logger.info(f"Choice Index: {response.choices[0].index}")
    logger.info(f"Finish Reason: {response.choices[0].finish_reason}")
    logger.info(f"Message Type: {type(response.choices[0].message)}")
    logger.info(f"Message Content Type: {type(response.choices[0].message.content)}")

    # 输出完整 message
    message = response.choices[0].message
    logger.info(f"Complete Message Object: {message}")

    # 输出 content
    if hasattr(message, 'content'):
        logger.info(f"Content: {message.content}")

    # 输出 thinking content (如果有）
    if hasattr(message, 'reasoning_content') and message.reasoning_content:
        logger.info(f"Reasoning Content: {message.reasoning_content}")

    # 输出其他可能的字段
    for attr in dir(message):
        if not attr.startswith('_'):
            value = getattr(message, attr)
            if not callable(value):
                logger.debug(f"Message.{attr} = {value}")

# 输出 usage 信息（如果有）
if hasattr(response, 'usage'):
    logger.info(f"Usage: {response.usage}")

logger.info("========================================")
logger.info("Demo completed")
logger.info("========================================")

# 按照官方示例输出到控制台
print("\n" + "=" * 80)
print("Official Output (as per documentation):")
print("=" * 80)
print(response.choices[0].message)
print("=" * 80)
