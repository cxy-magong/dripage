# LangChain Agent 示例

本目录包含使用 LangChain `create_agent` 和 `invoke` 方法调用工具的示例。

## 示例文件

### example_langchain_agent.py

演示如何使用 LangChain Agent 调用视觉分析和坐标转换工具。

#### 功能

- 使用 LangChain `create_agent` 创建 Agent
- 使用 `agent.invoke()` 方法同步调用
- 自动调用 `vision_analyze` 工具分析图像
- Agent 自动决定是否需要坐标转换

#### 运行方式

```bash
# 基本用法：查找搜索框（使用浏览器截图）
uv run python example/example_langchain_agent.py

# 自定义查询
uv run python example/example_langchain_agent.py --query "搜索按钮"

# 使用指定图像
uv run python example/example_langchain_agent.py --query "提交按钮" --image /path/to/screenshot.png

# 多元素查询
uv run python example/example_langchain_agent.py -q "搜索框、搜索按钮、提交按钮"
```

#### 工作流程

1. **创建模型**：使用配置中的 GLM-4.7 模型
2. **定义工具**：包含 `vision_analyze` 视觉分析工具
3. **创建 Agent**：使用 `create_agent(model, tools, state_schema)`
4. **构建输入**：符合 LangChain 格式的消息列表
5. **调用 Agent**：使用 `agent.invoke(input_data)`
6. **返回结果**：
   - `messages`: Agent 和模型之间的对话历史
   - `state`: Agent 状态（包含图像信息）
   - `tool_calls`: 工具调用记录

#### 输出示例

```
================================================================================
LangChain Agent 示例
================================================================================
查询: 搜索输入框
图像路径: 使用浏览器截图

🤖️  正在调用 LangChain Agent...
📋 输入:
  {
    "messages": [
      {
        "role": "user",
        "content": "请帮我找到图像中的以下元素位置：搜索输入框。\n\n1. 使用 vision_analyze 工具分析图像\n2. 使用 coordinate_convert_box_tool 将结果转换回原始图像坐标系\n3. 返回所有找到的元素在原始图像中的坐标位置"
      }
    ]
  }

✅ Agent 执行完成

================================================================================

📄 最终响应:
根据 vision_analyze 工具的分析结果，我已识别出以下元素：

1. **搜索输入框**
   - 位置: [100, 200, 300, 230]
   - 坐标: [150, 210]
   
2. **搜索按钮**
   - 位置: [310, 200, 400, 230]
   - 坐标: [355, 215]

================================================================================

🗂️  Agent State:
  - image_path: G:\code\agent-use\dripage\output\data\vision_20250126_123456.png
  - image_width: 1920
  - image_height: 1080
  - vision_analysis: {...}

================================================================================

🔧 工具调用记录:
  1. vision_analyze
     - analysis: {...}
     - image_size: {...}
     - model: glm-4.1v-thinking

================================================================================

✅ 示例执行成功！
```

## 技术细节

### LangChain Agent 架构

```
create_agent(
    model: str | BaseChatModel,
    tools: Sequence[BaseTool | Callable] | None,
    state_schema: type[AgentState] | None,
    system_prompt: str | None,
)
```

### Agent State Schema

```python
class AgentState(TypedDict):
    """Agent 状态 - 用于在工具间共享状态"""
    image_path: str | None
    image_width: int | None
    image_height: int | None
    vision_analysis: str | None
    converted_coordinates: dict
```

### 工具类型

- **vision_analyze**: 使用 GLM-4.1V 视觉模型分析图像
  - 使用 `ToolRuntime` 参数自动注入 runtime
  - 更新 `runtime.state["image_path"]`
  - 更新 `runtime.state["image_width"]`
  - 更新 `runtime.state["image_height"]`

### 工具调用流程

1. Agent 接收用户输入
2. Agent 决定调用哪些工具
3. 执行工具并更新 state
4. Agent 生成最终响应
5. 返回完整结果

## 相关文件

- `tools/agent_tools.py`: 定义工具
- `config/tools_runtime.yaml`: 配置文件
- `config/models_config.yaml`: 模型配置

## 环境变量

需要设置以下环境变量：

```bash
# 智谱 API 密钥
export ZAI_API_KEY="your_api_key_here"

# API 基础 URL（可选）
export ZAI_API_BASE="https://open.bigmodel.cn/api/paas/v4/"
```
