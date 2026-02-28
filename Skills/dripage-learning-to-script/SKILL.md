---
name: browser-learning-to-script
description: Convert interactive browser operations into reusable automation scripts using dripage CLI and DrissionPage
trigger-phrases:
  - 学习浏览器操作
  - 录制浏览器脚本
  - 生成自动化脚本
  - 固化操作流程
  - 学习为脚本
  - 自动化录制
  - 流程固化
  - 浏览器自动化学习
  - 将操作转换为脚本
  - 脚本生成
allowed-tools:
  - Bash(dripage:*)
  - Create
  - Edit
  - Read
---

# Browser Learning to Script

将交互式浏览器操作转换为可复用的自动化脚本。通过 dripage CLI 进行视觉学习和探索，最终生成基于 DrissionPage 的 Python 自动化脚本。

## Tool Restrictions (MUST OBEY)

### Allowed Tools
- ✅ `Bash(dripage:*)` - All dripage CLI commands
- ✅ `Create` - Create new script files
- ✅ `Edit` - Modify existing script files
- ✅ `Read` - Read existing scripts for reference

### Forbidden Tools
- ❌ `Bash` (non-dripage namespace) - Generic bash commands
- ❌ `Execute` - Use Bash(dripage:*) instead

---

## Trigger When
- User wants to convert manual browser operations into automation scripts
- User says "学习为脚本"、"录制操作"、"固化流程"
- User needs to create reusable automation from interactive exploration
- User wants to transform dripage CLI operations into Python scripts
- User mentions "将这个流程变成脚本"

---

## Core Workflow

### Phase 1: Interactive Learning (探索阶段)

**Goal**: Learn element locations and interaction patterns using dripage CLI

```bash
# 1. Start and check browser
dripage browser status
dripage browser start
dripage tab new --url <TARGET_URL>

# 2. Visual定位关键元素
dripage locate --query "搜索输入框"      # 定位输入框
dripage locate --query "搜索按钮"        # 定位按钮
dripage locate --query "提交表单"          # 定位提交按钮

# 3. 记录元素信息（xpath、class、id等）
# locate 命令会返回：
#   - 坐标位置 (x1, y1, x2, y2)
#   - 元素 HTML
#   - 元素属性 (id, class, name)
#   - XPath 信息（如果支持）

# 4. 验证元素定位
dripage locate --query "搜索输入框" --click  # 点击测试
```

**Critical Information to Record**:
- Target website URL
- List of elements to interact with
- XPath or CSS selectors for each element
- Interaction sequence (input → click → wait)
- Expected page transitions

### Phase 2: Script Generation (脚本生成阶段)

**Goal**: Generate Python automation script based on learned information

**Script Template**:

```python
#!/usr/bin/env python3
"""
自动化脚本: <任务名称>
使用方法: python <script_name>.py <参数>
"""

import argparse
import sys
from DrissionPage import ChromiumPage


class <TaskName>Automation:
    def __init__(self, browser_addr='127.0.0.1:19222'):
        self.browser_addr = browser_addr
        self.page = None

    def connect(self):
        """连接到浏览器"""
        print(f"正在连接到浏览器 {self.browser_addr}...")
        self.page = ChromiumPage(addr_or_opts=self.browser_addr)
        print("✓ 连接成功")

    def navigate_to_page(self, url):
        """导航到目标页面"""
        print(f"正在打开: {url}")
        self.page.get(url)
        self.page.wait.load_start()
        print("✓ 页面加载完成")

    def perform_action_1(self, value):
        """执行操作 1"""
        # 定位元素 (使用从 dripage locate 学到的 xpath)
        elem = self.page.ele('xpath://*[@id="element-id"]')
        if not elem:
            raise Exception("未找到元素")

        # 执行操作
        elem.clear()
        elem.input(value)
        print(f"✓ 已输入: {value}")

    def perform_action_2(self):
        """执行操作 2"""
        # 定位并点击元素
        elem = self.page.ele('xpath://button[@class="search-btn"]')
        if not elem:
            raise Exception("未找到元素")

        elem.click()
        print("✓ 已点击")

        # 等待页面加载
        self.page.wait.load_start()

    def extract_data(self):
        """提取数据"""
        # 获取页面内容
        html = self.page.html
        print(f"✓ 获取到内容 (长度: {len(html)})")
        return html

    def run(self, params):
        """执行完整流程"""
        try:
            self.connect()
            self.navigate_to_page("<TARGET_URL>")

            self.perform_action_1(params['value'])
            self.perform_action_2()

            data = self.extract_data()
            return data

        except Exception as e:
            print(f"✗ 执行失败: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description='<任务描述>')
    parser.add_argument('--browser-addr', default='127.0.0.1:19222', help='浏览器地址')
    parser.add_argument('value', help='输入值')

    args = parser.parse_args()

    automation = <TaskName>Automation(args.browser_addr)
    result = automation.run({'value': args.value})

    if result:
        print("\n✓ 任务完成！")
        sys.exit(0)
    else:
        print("\n✗ 任务失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Phase 3: Validation and Refinement (验证与优化)

```bash
# 1. 测试脚本
python <script_name>.py <测试参数>

# 2. 验证结果
# - 检查是否成功连接浏览器
# - 验证元素定位是否正确
# - 确认操作顺序是否正确
# - 验证数据提取是否成功

# 3. 调试和优化
# - 添加错误处理
# - 增加重试机制
# - 优化等待时间
# - 添加日志输出
```

---

## Mandatory Rules

### Rule 1: MUST Learn Elements Using Dripage First

Before generating scripts:
- ✅ **MUST**: Use `dripage locate --query "<element>"` to identify elements
- ✅ **MUST**: Record xpath selectors from locate results
- ✅ **MUST**: Verify element accessibility before scripting
- ❌ **NEVER**: Guess xpath selectors without visual verification

**Why**: Visual learning ensures accurate element identification. Guessing leads to brittle scripts.

### Rule 2: MUST Use DrissionPage for Automation

Script generation:
- ✅ **MUST**: Use `ChromiumPage` from DrissionPage
- ✅ **MUST**: Connect to existing browser: `ChromiumPage(addr_or_opts='127.0.0.1:19222')`
- ✅ **MUST**: Use xpath selectors learned from dripage locate
- ❌ **NEVER**: Use Selenium or other automation libraries
- ❌ **NEVER**: Start new browser instances unnecessarily

**Why**: DrissionPage integrates seamlessly with dripage CLI's browser sessions.

### Rule 3: MUST Structure Scripts as Reusable Classes

Script organization:
- ✅ **MUST**: Wrap automation logic in a class
- ✅ **MUST**: Separate methods for each action (input, click, wait)
- ✅ **MUST**: Add command-line argument parsing
- ✅ **MUST**: Include docstrings and comments
- ❌ **NEVER**: Write monolithic scripts without structure
- ❌ **NEVER**: Hardcode values (use parameters)

**Why**: Structured code is maintainable, testable, and reusable.

### Rule 4: MUST Include Error Handling

Robustness:
- ✅ **MUST**: Check if elements exist before interaction
- ✅ **MUST**: Use try-except blocks for critical operations
- ✅ **MUST**: Provide meaningful error messages
- ✅ **MUST**: Use `page.wait.load_start()` after page transitions
- ❌ **NEVER**: Assume elements always exist
- ❌ **NEVER**: Skip waiting for page loads

**Why**: Error handling ensures scripts work reliably across different network conditions.

---

## Recommended Workflow Examples

### Example 1: Search Automation

**User Request**: "将1688搜索操作学习为脚本"

**Phase 1: Learning**
```bash
# Explore 1688 search flow
dripage locate --query "搜索输入框"   # Returns: id="alisearch-input"
dripage locate --query "搜索按钮"     # Returns: class="input-button-text"
```

**Phase 2: Script Generation**
```python
# Generated script with learned xpaths
input_xpath = 'xpath://*[@id="alisearch-input"]'
button_xpath = 'xpath://span[@class="input-button-text"]'

# Implementation in class methods
def search(self, keyword):
    input_elem = self.page.ele(input_xpath)
    input_elem.input(keyword)

    button_elem = self.page.ele(button_xpath)
    button_elem.click()

    self.page.wait.load_start()
```

### Example 2: Form Submission

**User Request**: "将表单提交流程固化为脚本"

**Phase 1: Learning**
```bash
# Identify all form elements
dripage locate --query "用户名输入框"  # id="username"
dripage locate --query "密码输入框"      # id="password"
dripage locate --query "登录按钮"        # class="login-btn"
```

**Phase 2: Script Generation**
```python
def login(self, username, password):
    username_elem = self.page.ele('xpath://*[@id="username"]')
    username_elem.input(username)

    password_elem = self.page.ele('xpath://*[@id="password"]')
    password_elem.input(password)

    login_btn = self.page.ele('xpath://button[@class="login-btn"]')
    login_btn.click()

    self.page.wait.load_start()
```

### Example 3: Data Extraction

**User Request**: "学习商品列表页面的数据提取"

**Phase 1: Learning**
```bash
# Locate product elements
dripage locate --query "商品标题"
dripage locate --query "商品价格"
dripage locate --query "商品链接"
```

**Phase 2: Script Generation**
```python
def extract_products(self):
    products = []

    # Find all product cards
    product_cards = self.page.eles('xpath://div[@class="product-card"]')

    for card in product_cards:
        product = {
            'title': card.ele('xpath:.//h3').text,
            'price': card.ele('xpath:.//span[@class="price"]').text,
            'link': card.ele('xpath:.//a').attr('href')
        }
        products.append(product)

    return products
```

---

## Common Patterns

### Pattern 1: Input → Click → Wait

```python
def input_and_submit(self, input_xpath, value, button_xpath):
    """输入并提交"""
    input_elem = self.page.ele(input_xpath)
    input_elem.clear()
    input_elem.input(value)

    button_elem = self.page.ele(button_xpath)
    button_elem.click()

    self.page.wait.load_start()
```

### Pattern 2: Navigate → Verify → Act

```python
def navigate_and_verify(self, url, expected_element):
    """导航并验证"""
    self.page.get(url)
    self.page.wait.load_start()

    if not self.page.ele(expected_element):
        raise Exception(f"页面未加载成功: {url}")
```

### Pattern 3: Multiple Elements Extraction

```python
def extract_list(self, item_xpath):
    """提取列表数据"""
    items = self.page.eles(item_xpath)
    data = []

    for item in items:
        data.append(item.text)

    return data
```

---

## Error Handling Best Practices

### 1. Element Not Found
```python
elem = self.page.ele('xpath://*[@id="target"]')
if not elem:
    raise Exception("未找到目标元素，请检查页面加载状态")
```

### 2. Page Load Timeout
```python
from DrissionPage import errors

try:
    self.page.wait.load_start(timeout=10)
except errors.TimeoutError:
    raise Exception("页面加载超时")
```

### 3. Network Error
```python
try:
    self.page.get(url)
except Exception as e:
    raise Exception(f"网络请求失败: {e}")
```

---

## Output and Results

### Script Structure
```
<project>/ai/task/
├── <task_name>.py          # 主脚本文件
├── README.md               # 使用说明
└── requirements.txt        # 依赖列表
```

### Script Output
- Console logs with progress indicators
- Error messages with context
- Optional file output (CSV, JSON, MD)
- Return code for success/failure

---

## Quick Reference

| Phase | Command | Purpose |
|-------|---------|---------|
| Learning | `dripage locate --query "元素"` | 定位元素 |
| Learning | `dripage browser status` | 检查浏览器状态 |
| Generation | Create/edit Python script | 生成脚本 |
| Validation | `python script.py <args>` | 测试脚本 |
| Debug | Add print statements | 查看执行过程 |

---

## Important Notes

1. **Browser Reuse**: Always connect to existing browser session, don't start new ones
2. **Xpath Accuracy**: Use exact xpaths from dripage locate, don't guess
3. **Error Messages**: Provide helpful error messages for debugging
4. **Script Location**: Save scripts in `ai/task/` directory for consistency
5. **Documentation**: Add docstrings and usage examples to every script

---

## Integration with Dripage CLI

This skill complements the `dripage-cli` skill:
- **dripage-cli**: Interactive exploration and visual learning
- **browser-learning-to-script**: Script generation and automation

Use both skills together for complete browser automation workflow.
