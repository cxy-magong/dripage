#!/usr/bin/env python
"""
LangChain Agent 调用示例

演示如何使用 LangChain 的 create_agent 和 invoke 方法
调用 agent_tools 中的视觉分析和坐标转换工具
"""

import os
import sys
import json
from pathlib import Path
from typing import TypedDict

# 添加项目目录到路径
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools import (
    vision_analyze,
    get_global_state,
    get_config as get_agent_config,
)


# ==================== Agent State Schema ====================

class AgentState(TypedDict):
    """Agent 状态 - 用于在工具间共享状态"""
    image_path: str | None
    image_width: int | None
    image_height: int | None
    vision_analysis: str | None
    converted_coordinates: dict


# ==================== 示例函数 ====================

def example_agent_invoke(query: str, image_path: str | None = None):
    """
    示例：使用 LangChain Agent invoke 方法调用工具

    Args:
        query: 要查找的元素描述，如"搜索输入框、搜索按钮"
        image_path: 图像文件路径（可选，不提供则使用浏览器截图）
    """
    # 获取 API key
    api_key = os.environ.get('ZAI_API_KEY')
    if not api_key:
        print("❌ ZAI_API_KEY not found in environment variables")
        return

    config = get_agent_config()

    print(f"\n{'='*80}")
    print(f"LangChain Agent 示例")
    print(f"{'='*80}")
    print(f"查询: {query}")
    print(f"图像路径: {image_path if image_path else '使用浏览器截图'}")
    print(f"{'='*80}\n")

    try:
        # 1. 创建模型
        # 使用配置中的 Agent 模型
        model = ChatOpenAI(
            api_key=api_key,
            base_url=os.getenv("ZAI_API_BASE"),
            model=config.agent_model,
            temperature=config.agent_temperature,
        )

        # 2. 定义工具列表
        # 包含视觉分析和坐标转换工具
        tools = [
            vision_analyze,           # 视觉分析工具
            coordinate_convert_box_tool,  # Box 坐标转换工具
        ]

        # 3. 创建 Agent
        # 定义 state_schema 用于在工具间共享状态
        agent = create_agent(
            model=model,
            tools=tools,
            state_schema=AgentState,
            system_prompt="你是一个视觉元素定位专家。你的任务是帮助用户定位图像中的元素位置。"
        )

        # 4. 准备输入
        # 构造符合 LangChain 格式的输入
        input_data = {
            "messages": [
                {
                    "role": "user",
                    "content": f"请帮我找到图像中的以下元素位置：{query}。\n\n"
                                  f"1. 使用 vision_analyze 工具分析图像\n"
                                  f"2. 使用 coordinate_convert_box_tool 将结果转换回原始图像坐标系\n"
                                  f"3. 返回所有找到的元素在原始图像中的坐标位置"
                }
            ]
        }

        # 如果指定了图像路径，添加到 state 中
        if image_path:
            input_data["image_path"] = image_path

        # 5. 调用 agent.invoke()
        print("🤖️  正在调用 LangChain Agent...")
        print("📋 输入:", json.dumps(input_data, ensure_ascii=False, indent=2))
        print()

        result = agent.invoke(input_data)

        # 6. 打印结果
        print(f"✅ Agent 执行完成")
        print(f"{'='*80}")

        # 提取最后的消息
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            print(f"📄 最终响应:")
            print(f"{last_message}")
            print()

        # 提取并打印 state
        state = result.get("state", {})
        print(f"🗂️  Agent State:")
        if state:
            for key, value in state.items():
                print(f"  - {key}: {value}")
        print()

        # 提取并打印工具调用结果
        tool_calls = result.get("tool_calls", [])
        if tool_calls:
            print(f"🔧 工具调用记录:")
            for i, tool_call in enumerate(tool_calls, 1):
                tool_name = tool_call.get("name", "unknown")
                tool_result = tool_call.get("result", {})
                print(f"  {i}. {tool_name}")
                if isinstance(tool_result, dict):
                    for k, v in tool_result.items():
                        print(f"     - {k}: {v}")
                else:
                    print(f"     结果: {tool_result}")
        print(f"{'='*80}\n")

        return result

    except Exception as e:
        error_msg = f"Agent 执行失败: {str(e)}"
        print(f"\n❌ {error_msg}\n")
        import traceback
        traceback.print_exc()
        return None


def example_simple_invoke():
    """
    简单示例：查找搜索框
    """
    return example_agent_invoke(
        query="搜索输入框",
    )


def example_multiple_elements():
    """
    多元素示例：查找搜索框、搜索按钮和提交按钮
    """
    return example_agent_invoke(
        query="搜索输入框、搜索按钮、提交按钮",
    )


def example_with_image(image_path: str):
    """
    使用指定图像文件的示例
    """
    return example_agent_invoke(
        query="页面上的所有按钮",
        image_path=image_path,
    )


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 80)
    print("LangChain Agent 示例程序")
    print("=" * 80)
    print()
    print("用法:")
    print("  python example_langchain_agent.py                    # 查找搜索框（默认示例）")
    print("  python example_langchain_agent.py --query \"搜索按钮\"    # 自定义查询")
    print("  python example_langchain_agent.py --image /path/to/image.png  # 使用指定图像")
    print()
    print("=" * 80)
    print()

    # 解析命令行参数
    query = "搜索输入框"  # 默认查询
    image_path = None

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--query" and i + 1 < len(sys.argv):
            query = sys.argv[i + 1]
        elif arg == "--image" and i + 1 < len(sys.argv):
            image_path = sys.argv[i + 1]
        elif arg.startswith("-") and not arg.startswith("--"):
            # 简短参数
            if arg == "-q" and i + 1 < len(sys.argv):
                query = sys.argv[i + 1]
            elif arg == "-i" and i + 1 < len(sys.argv):
                image_path = sys.argv[i + 1]

    # 执行示例
    result = example_agent_invoke(query=query, image_path=image_path)

    if result:
        print("\n✅ 示例执行成功！")
    else:
        print("\n❌ 示例执行失败！")
