# GUI Agent 模型配置说明

## 配置文件位置

`config/models_config.yaml`

## 支持的模型

### GLM-4.6V 系列（推荐使用）

#### 1. GLM-4.6V（旗舰版）✨
- **模型 ID**: `glm_4_6v`
- **描述**: 最新一代多模态模型，性能最强
- **上下文长度**: 128,000 tokens
- **温度**: 0.1
- **最大 Token**: 4,096
- **深度思考**: ✓ 支持，默认禁用
- **推荐**: ✓ 默认推荐

#### 2. GLM-4.6V-FlashX
- **模型 ID**: `glm_4_6v_flashx`
- **描述**: 轻量高速版，适合快速响应场景
- **上下文长度**: 128,000 tokens
- **温度**: 0.1
- **最大 Token**: 4,096
- **深度思考**: ✓ 支持，默认禁用

#### 3. GLM-4.6V-Flash（完全免费）
- **模型 ID**: `glm_4_6v_flash`
- **描述**: 完全免费，基础性能
- **上下文长度**: 128,000 tokens
- **温度**: 0.1
- **最大 Token**: 4,096
- **深度思考**: ✗ 不支持

### GLM-4.1V-Thinking 系列

#### 4. GLM-4.1V-Thinking
- **模型 ID**: `glm_4_1v_thinking`
- **描述**: 思维链增强版，支持复杂推理
- **上下文长度**: 128,000 tokens
- **温度**: 0.1
- **最大 Token**: 4,096
- **深度思考**: ✓ 支持，默认禁用

#### 5. GLM-4.1V-Thinking-Flash
- **模型 ID**: `glm_4_1v_thinking_flash`
- **描述**: 思维链轻量版，快速推理
- **上下文长度**: 128,000 tokens
- **温度**: 0.1
- **最大 Token**: 1,024
- **深度思考**: ✓ 支持，默认禁用

## 默认配置

### GUI Agent 配置
```yaml
gui_agent:
  model: glm_4_6v
  temperature: 0.1
  max_tokens: 4096
  thinking_enabled: false  # 默认不启用深度思考
```

**说明**:
- 使用旗舰版 `GLM-4.6V` 模型
- 温度设置为 0.1（低温度更准确）
- 最大 token 数为 4096
- 深度思考默认禁用

## 深度思考（Thinking）功能

### 概述
深度思考是 GLM 模型的思维链推理功能，可以让模型展示推理过程，提高复杂任务的准确性。

### 支持的模型
以下模型支持深度思考功能：
- ✓ GLM-4.6V
- ✓ GLM-4.6V-FlashX
- ✓ GLM-4.1V-Thinking
- ✓ GLM-4.1V-Thinking-Flash

不支持：
- ✗ GLM-4.6V-Flash

### 启用深度思考

#### 方法 1: 修改配置文件
编辑 `config/models_config.yaml`：

```yaml
gui_agent:
  model: glm_4_1v_thinking  # 使用 Thinking 模型
  temperature: 0.1
  max_tokens: 4096
  thinking_enabled: true  # 启用深度思考
```

#### 方法 2: 在代码中动态启用
```python
from utils.model_config import get_config

config = get_config()

# 检查并获取 thinking 配置
model_key = 'glm_4_1v_thinking'
thinking_config = config.get_thinking_config(model_key)

if thinking_config:
    # 在 API 调用中使用 thinking 参数
    response = client.chat.completions.create(
        model=config.get_model_name(model_key),
        messages=[...],
        thinking=thinking_config  # {"type": "enabled"}
    )
```

#### 方法 3: 使用 Thinking 系列模型并手动启用
```python
from zai import ZhipuAiClient

client = ZhipuAiClient(api_key=os.environ.get('ZAI_API_KEY'))

response = client.chat.completions.create(
    model="GLM-4.1V-Thinking-Flash",
    messages=[...],
    thinking={
        "type": "enabled"  # 手动启用
    }
)

# 读取推理过程
message = response.choices[0].message
if hasattr(message, 'reasoning_content') and message.reasoning_content:
    print(f"推理过程: {message.reasoning_content}")
print(f"答案: {message.content}")
```

### 读取推理过程
启用深度思考后，模型会返回 `reasoning_content` 属性：

```python
message = response.choices[0].message

# 最终答案
final_answer = message.content

# 推理过程（如果有）
if hasattr(message, 'reasoning_content') and message.reasoning_content:
    reasoning_process = message.reasoning_content
    print(f"推理过程: {reasoning_process}")
```

### 配置说明
```yaml
models:
  glm_4_1v_thinking:
    name: GLM-4.1V-Thinking
    description: 思维链增强版 - 支持复杂推理
    context_length: 128000
    temperature: 0.1
    max_tokens: 4096
    thinking_supported: true   # 是否支持 thinking
    thinking_enabled: false    # 默认是否启用
```

**配置项说明**：
- `thinking_supported`: 模型是否支持深度思考功能
- `thinking_enabled`: 默认是否启用（可被 gui_agent 或 default 配置覆盖）

### API 调用示例

#### 启用深度思考
```python
from utils.model_config import get_config
from zai import ZhipuAiClient

config = get_config()
model_key = 'glm_4_1v_thinking'

# 获取 thinking 配置
thinking_config = config.get_thinking_config(model_key, context='gui_agent')

# 构建 API 调用参数
api_params = {
    "model": config.get_model_name(model_key),
    "messages": [...],
    "temperature": 0.1,
    "max_tokens": 4096
}

# 如果启用了 thinking，添加 thinking 参数
if thinking_config:
    api_params["thinking"] = thinking_config

# 发送请求
response = client.chat.completions.create(**api_params)

# 处理响应
message = response.choices[0].message
if thinking_config:
    print(f"推理过程: {message.reasoning_content}")
print(f"答案: {message.content}")
```

#### 检查模型是否支持 thinking
```python
from utils.model_config import get_config

config = get_config()
model_key = 'glm_4_1v_thinking'

if config.is_thinking_supported(model_key):
    print(f"{config.get_model_name(model_key)} 支持深度思考")

    if config.is_thinking_enabled(model_key, context='gui_agent'):
        print("深度思考已启用")
    else:
        print("深度思考已禁用")
else:
    print("该模型不支持深度思考")
```

## 使用配置文件

### 1. 查看所有可用模型

```bash
cd "G:\code\agent-use\dripage"
PYTHONPATH="G:\code\agent-use\dripage" uv run python -c "from utils.model_config import get_config; config = get_config(); config.print_models()"
```

### 2. 运行 Demo（使用配置文件中的默认模型）

```bash
cd "G:\code\agent-use\dripage"
PYTHONPATH="G:\code\agent-use\dripage" uv run example/gui_agent_demo.py
```

### 3. 在代码中使用配置

```python
from utils.model_config import get_config

# 获取配置实例
config = get_config()

# 获取 GUI Agent 配置
gui_config = config.get_gui_agent_config()

# 使用配置
model = gui_config['model']  # GLM-4.6V
temperature = gui_config['temperature']  # 0.1
max_tokens = gui_config['max_tokens']  # 4096

# 获取特定模型的配置
model_config = config.get_model_config('glm_4_6v')
print(model_config['name'])  # GLM-4.6V
print(model_config['description'])  # 旗舰版 - 最新一代多模态模型，性能最强
```

### 4. 更换模型

编辑 `config/models_config.yaml`，修改 `gui_agent.model` 字段：

```yaml
gui_agent:
  model: glm_4_6v_flash  # 改为使用 Flash 版本
  temperature: 0.1
  max_tokens: 4096
```

或者直接修改 `default.model`：

```yaml
default:
  model: glm_4_6v_flash  # 默认模型
  temperature: 0.1
  max_tokens: 4096
```

## 参数说明

### Temperature（温度）
- **范围**: 0.0 - 1.0
- **默认**: 0.1
- **说明**: 温度越低，输出越确定和准确；温度越高，输出越多样和随机
- **推荐**: GUI 任务使用 0.1-0.3，创意任务使用 0.5-0.8

### Max Tokens（最大 Token 数）
- **范围**: 根据模型上下文长度
- **默认**: 4,096（旗舰版）
- **说明**: 控制模型输出的最大长度
- **推荐**: GUI 任务 1024-4096，复杂推理任务 4096-8192

### Context Length（上下文长度）
- **说明**: 模型支持的最大输入 token 数
- **当前所有模型**: 128,000 tokens

## 运行结果示例

使用旗舰版 `GLM-4.6V` 的输出：

```
Model Configuration:
  - Model: GLM-4.6V
  - Description: 旗舰版 - 最新一代多模态模型，性能最强
  - Temperature: 0.1
  - Max Tokens: 4,096
  - Context Length: 128,000 tokens

[4] Asking GUI Agent for search input box position...
   Using model: GLM-4.6V
   Temperature: 0.1
   Max tokens: 4096
   ✓ Extracted from JSON: element=百度搜索框, x=499, y=291, box=[292, 244, 706, 338]

✓ Search input box found:
  - Element: 百度搜索框
  - Center: (499, 291)
  - Box: [292, 244, 706, 338]
  - Confidence: 1.0
```

## 注意事项

1. **模型选择**
   - 生产环境推荐使用 `GLM-4.6V`（旗舰版）
   - 快速测试可使用 `GLM-4.6V-Flash` 或 `GLM-4.6V-FlashX`
   - 预算有限可使用 `GLM-4.6V-Flash`（完全免费）

2. **API 密钥**
   - 确保设置了 `ZAI_API_KEY` 环境变量
   - 不同模型可能需要不同的 API 权限

3. **上下文长度**
   - 确保输入内容不超过模型的上下文长度（128,000 tokens）
   - 图片会占用较多 token，需要注意

4. **温度设置**
   - GUI 任务建议使用低温度（0.1-0.3）
   - 可以根据实际需求调整

## 参考链接

- [GLM-4.6V 文档](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.6v)
- [GLM-4.1V-Thinking 文档](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.1v-thinking)
- [智谱 AI 官网](https://bigmodel.cn)
