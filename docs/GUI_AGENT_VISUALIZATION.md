# GUI Agent 可视化功能

## 功能概述

使用 GLM-4.1V-Thinking-Flash 模型进行 GUI 自动化操作，支持：
- 识别网页元素位置
- 获取元素边界框（box）
- 获取元素中心点坐标
- 可视化标注（在截图上绘制 box 和 center 点）

## 使用方法

### 1. 运行完整示例

```bash
cd "G:\code\agent-use\dripage"
PYTHONPATH="G:\code\agent-use\dripage" uv run example/gui_agent_demo.py
```

### 2. 运行可视化测试

```bash
cd "G:\code\agent-use\dripage"
PYTHONPATH="G:\code\agent-use\dripage" uv run test/test_visualization.py
```

## 功能特性

### 1. 图片尺寸信息

自动获取并打印截图信息：
- 图片尺寸（宽 x 高）
- 颜色模式
- 文件大小

**输出示例：**
```
✓ Screenshot info:
  - Dimensions: 1920 x 945 pixels
  - Color mode: RGB
  - File size: 298,018 bytes
```

### 2. 元素识别

通过 GUI Agent 模型识别元素，返回：
- `element`: 元素描述
- `x`, `y`: 中心点坐标
- `box`: 边界框 [x1, y1, x2, y2]
- `confidence`: 置信度 (0-1)

**输出示例：**
```
✓ Search button found:
  - Element: 百度一下 按钮
  - Center: (677, 309)
  - Box: [647, 285, 708, 332]
  - Confidence: 0.95
```

### 3. 可视化标注

自动生成两张截图：
- 原始截图：`*_original_*.png`
- 标注截图：`*_annotated_*.png`

**标注内容：**
- 🔵 **蓝色圆点**：元素中心点
- 🟥 **红色矩形框**：元素边界
- 📝 **文字标注**：元素描述

## 输出文件

生成的截图保存在 `output/gui_agent_screenshots/` 目录：

```
output/gui_agent_screenshots/
├── search_input_original_20260124_012119.png
├── search_input_annotated_20260124_012119.png
├── search_button_original_20260124_012126.png
└── search_button_annotated_20260124_012126.png
```

## API 使用

### get_gui_agent_coordinates()

```python
from example.gui_agent_demo import get_gui_agent_coordinates, get_screenshot_info

# 获取截图信息
image_base64 = page.get_screenshot(as_base64=True)
image_info = get_screenshot_info(image_base64)

# 获取元素坐标
result = get_gui_agent_coordinates(
    image_base64=image_base64,
    query="搜索框在哪里？",
    model='GLM-4.1V-Thinking-Flash',
    image_info=image_info  # 可选：图片尺寸信息
)

# result 格式：
# {
#     "element": "百度搜索框",
#     "x": 500,
#     "y": 289,
#     "box": [286, 244, 712, 336],
#     "confidence": 0.95
# }
```

### save_screenshots_with_annotations()

```python
from utils.gui_agent_visualizer import save_screenshots_with_annotations

original_path, annotated_path = save_screenshots_with_annotations(
    image_base64=image_base64,
    element_info=result,
    output_dir=Path("output/screenshots"),
    filename_prefix="element_name"
)
```

## 环境要求

- Python 3.13+
- 依赖包：`uv add pillow`
- 环境变量：`ZAI_API_KEY` (智谱 AI API 密钥)

## 注意事项

1. 确保浏览器在 `127.0.0.1:19222` 运行
2. 设置 `ZAI_API_KEY` 环境变量
3. 坐标值不应超过图片尺寸范围
4. 使用 `GLM-4.1V-Thinking-Flash` 模型以获得最佳效果
