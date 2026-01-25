"""
智谱 AI 最简调用示例

运行: PYTHONPATH="G:\code\demo\LangGraph_demo" uv run Langchain_demo/zhipu_simple.py
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置不使用代理访问智谱 API
os.environ['NO_PROXY'] = 'open.bigmodel.cn'
os.environ['no_proxy'] = 'open.bigmodel.cn'

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import base64


def test_text():
    """GLM-4.7 文本对话"""
    print(f"Using base_url: {os.environ.get('ZAI_API_CODING')}")
    llm = ChatOpenAI(
        api_key=os.environ.get("ZAI_API_KEY"),
        base_url=os.environ.get("ZAI_API_CODING"),
        model="glm-4.7",
    )
    response = llm.invoke([HumanMessage("你好，请介绍一下你自己")])
    print(f"GLM-4.7: {response.content}")


def test_image():
    """GLM-4.1V 图像识别"""
    print(f"Using base_url: {os.environ.get('ZAI_API_BASE')}")
    # 读取本地图片
    image_path = r"C:\Users\mg\Downloads\free_stock_photo.jpg"
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')

    llm = ChatOpenAI(
        api_key=os.environ.get("ZAI_API_KEY"),
        base_url=os.environ.get("ZAI_API_BASE"),
        model="glm-4.1v-thinking-flashx",
    )

    response = llm.invoke([
        HumanMessage(content=[
            {"type": "text", "text": "描述这张图片"},
            {"type": "image_url", "image_url": {"url": f"{base64_image}"}}
        ])
    ])
    print(f"GLM-4.1V: {response.content}")


if __name__ == "__main__":
    print("=== GLM-4.7 ===")
    test_text()
    print("\n=== GLM-4.1V ===")
    test_image()
