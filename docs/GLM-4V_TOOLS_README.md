# GLM-4V 视觉模型工具使用指南

## 概述

本项目提供了 GLM-4V 视觉模型的完整工具链，包括：
1. **坐标转换器** - 将 GLM-4V 返回的坐标从 999x999 转换回原始图像坐标系
2. **Bounding Box 绘制器** - 在图像上绘制矩形框并可视化

## 工具文件

### 1. 坐标转换器 `utils/glm_coordinate_converter.py`

GLM-4V 模型内部将所有图像缩放到固定尺寸 999x999 进行识别，因此返回的坐标需要转换回原始图像坐标系。

#### 主要类：`GLMCoordinateConverter`

```python
from utils.glm_coordinate_converter import GLMCoordinateConverter

# 从图像 URL 创建转换器
converter = GLMCoordinateConverter.from_image_url("https://example.com/image.jpg")

# 从本地图像路径创建转换器
converter = GLMCoordinateConverter.from_image_path("/path/to/image.jpg")

# 手动指定图像尺寸创建转换器
converter = GLMCoordinateConverter(1920, 1080)
```

#### 主要方法

##### 转换单个坐标
```python
# 转换 bounding box [xmin, ymin, xmax, ymax]
box = [100, 200, 300, 400]
converted_box = converter.convert_box(box)
print(converted_box)  # [82, 124, 248, 248] (根据缩放比例)
```

##### 批量转换坐标
```python
boxes = [
    [100, 200, 300, 400],
    [500, 600, 700, 800]
]
converted_boxes = converter.convert_boxes(boxes)
```

##### 从文本解析坐标
```python
text = "目标位置是 [[93,588,197,990]]"
boxes = converter.parse_coordinates_from_text(text)
print(boxes)  # [[93, 588, 197, 990]]
```

### 2. Bounding Box 绘制器 `utils/image_bbox_drawer.py`

在图像上绘制矩形框，支持自动保存到同一目录。

#### 主要函数

##### 绘制单个 Bounding Box
```python
from utils.image_bbox_drawer import draw_bbox_on_image

# 基本用法
output_path = draw_bbox_on_image(
    image_path="test.jpg",
    bbox=[100, 200, 300, 400],
    label="目标对象",
    color=(255, 0, 0)  # 红色
)

# 自定义样式
output_path = draw_bbox_on_image(
    image_path="test.jpg",
    bbox=[100, 200, 300, 400],
    label="物体",
    color=(0, 255, 0),  # 绿色
    line_width=5,       # 线条宽度
    alpha=0.5           # 透明度
)
```

##### 绘制多个 Bounding Boxes
```python
from utils.image_bbox_drawer import draw_bboxes_on_image

boxes = [
    [100, 200, 300, 400],
    [500, 600, 700, 800],
    [200, 300, 400, 500]
]
labels = ["物体1", "物体2", "物体3"]

output_path = draw_bboxes_on_image(
    image_path="test.jpg",
    bboxes=boxes,
    labels=labels
    # 不指定 color 会自动使用不同颜色
)
```

##### 使用 BBoxDrawer 类
```python
from utils.image_bbox_drawer import BBoxDrawer

drawer = BBoxDrawer(line_width=3, alpha=0.3)

# 绘制多个 boxes
output_path = drawer.draw_bboxes_on_image(
    image_path="test.jpg",
    bboxes=[[100, 200, 300, 400], [500, 600, 700, 800]],
    labels=["Box1", "Box2"],
    show_label=True
)
```

## 完整工作流程示例

### 示例 1: 基本使用
```python
from zai import ZhipuAiClient
from utils.glm_coordinate_converter import GLMCoordinateConverter
from utils.image_bbox_drawer import draw_bbox_on_image

# 1. 调用 GLM-4V 模型
client = ZhipuAiClient(api_key=os.environ.get('ZAI_API_KEY'))
response = client.chat.completions.create(
    model="GLM-4.1V-Thinking-Flash",
    messages=[...]
)

# 2. 解析坐标
content = response.choices[0].message.content
converter = GLMCoordinateConverter.from_image_url(image_url)
glm_boxes = converter.parse_coordinates_from_text(content)

# 3. 转换坐标
converted_boxes = converter.convert_boxes(glm_boxes)

# 4. 下载并绘制
import requests
from PIL import Image
from io import BytesIO

response = requests.get(image_url)
img = Image.open(BytesIO(response.content))
img.save("temp.jpg")

# 5. 绘制 bounding box
for i, box in enumerate(converted_boxes):
    output = draw_bbox_on_image(
        image_path="temp.jpg",
        bbox=box,
        label=f"目标{i+1}"
    )
    print(f"图像已保存到: {output}")
```

### 示例 2: 完整演示
运行提供的演示脚本：
```bash
# 完整演示（包含模型调用、坐标转换和 bbox 绘制）
uv run example/glm_4_1v_with_bbox_demo.py

# 仅坐标转换演示
uv run utils/glm_coordinate_converter.py

# 仅 bbox 绘制演示
uv run utils/image_bbox_drawer.py
```

## 文件说明

### 工具文件
- `utils/glm_coordinate_converter.py` - 坐标转换器
- `utils/image_bbox_drawer.py` - Bounding Box 绘制器

### 示例文件
- `example/glm_4_1v_thinking_flash_demo.py` - GLM-4.1V 模型基础测试
- `example/glm_4_1v_complete_demo.py` - 完整流程演示（不含 bbox 绘制）
- `example/glm_4_1v_with_bbox_demo.py` - 完整流程演示（含 bbox 绘制）

### 输出文件
- `output/original_image.png` - 原始图像
- `output/original_image_with_bbox.png` - 带有标注框的图像

## 坐标系统说明

### GLM-4V 内部坐标系
- 固定尺寸: 999 x 999
- 所有图像都被缩放到此尺寸进行识别

### 原始图像坐标系
- 实际图像尺寸（如 826 x 620）
- 需要通过缩放比例转换

### 转换公式
```python
scale_x = original_width / 999
scale_y = original_height / 999

original_x = glm_x * scale_x
original_y = glm_y * scale_y
```

## 参数说明

### GLMCoordinateConverter
- `original_width` - 原始图像宽度
- `original_height` - 原始图像高度
- `GLM_SCALED_SIZE` - GLM-4V 固定缩放尺寸 (999)

### BBoxDrawer
- `line_width` - 线条宽度（默认 3）
- `alpha` - 透明度 0-1（默认 0.5）

### draw_bbox_on_image
- `image_path` - 输入图像路径
- `bbox` - 坐标 [xmin, ymin, xmax, ymax]
- `output_path` - 输出路径（可选）
- `label` - 标签文本（默认 "Target"）
- `color` - 颜色 (R, G, B)（默认红色）
- `line_width` - 线条宽度（默认 3）
- `alpha` - 透明度（默认 0.5）

## 颜色预设

BBoxDrawer 提供了 10 种鲜艳颜色，自动循环使用：
1. 红色 (255, 0, 0)
2. 绿色 (0, 255, 0)
3. 蓝色 (0, 0, 255)
4. 黄色 (255, 255, 0)
5. 品红 (255, 0, 255)
6. 青色 (0, 255, 255)
7. 橙色 (255, 128, 0)
8. 紫色 (128, 0, 255)
9. 青绿色 (0, 255, 128)
10. 洋红色 (255, 0, 128)

## 注意事项

1. **坐标格式**: GLM-4V 返回的坐标格式为 `[[xmin, ymin, xmax, ymax]]`
2. **自动保存**: 不指定 `output_path` 时，会自动保存到原图同目录，文件名添加 `_with_bbox` 后缀
3. **字体支持**: 尝试加载 `arial.ttf`，如果失败则使用默认字体
4. **图像格式**: 支持所有 PIL 支持的图像格式（PNG, JPG, BMP 等）
5. **透明度**: 使用 RGBA 模式绘制半透明填充，不破坏原始图像

## 运行环境要求

- Python 3.13+
- 依赖包：
  - Pillow (图像处理)
  - requests (下载图像)
  - zai-sdk (GLM-4V API)
  - loguru (日志记录)

## 常见问题

**Q: 为什么 GLM-4V 返回的坐标不准确？**
A: GLM-4V 使用 999x999 固定尺寸，必须通过坐标转换器转换回原始图像坐标系。

**Q: 如何验证坐标是否正确？**
A: 使用 BBoxDrawer 在图像上绘制框，查看是否准确标记目标位置。

**Q: 可以同时绘制多个框吗？**
A: 可以，使用 `draw_bboxes_on_image` 函数，传入多个 box 坐标。

**Q: 如何自定义颜色？**
A: 使用 `color` 参数指定 RGB 值，格式为 (R, G, B)。

## 更新日志

- 2026-01-24: 初始版本
  - 添加坐标转换器
  - 添加 BBox 绘制器
  - 添加完整示例和文档
