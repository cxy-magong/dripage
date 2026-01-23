新增一条指令，让这个模型操作网页
[gui-agent](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.1v-thinking#gui-agent)

不要跟其他指令的模型混用，要独立模块化，这是 GUI 专用模型。不是图像识别模型。
默认配置：
- 模型：`GLM-4.1V-Thinking-Flash` ，可选 GLM-4.1V-Thinking-FlashX
- API 密钥：从环境变量 `ZAI_API_KEY` 获取

基本实现思路，复用已有的截图功能函数，作为输入调用返回坐标，再根据坐标操作网页。
example\action_demo.py 示例实现了基本的坐标点击功能。你需要新建一个文件示例，利用大模型 gui 的方式去操作。
验证成功才能结束：
- 访问 https://www.baidu.com
- 询问 llm 搜索按钮位置、输入框的位置
- 根据 搜索按钮位置，以坐标方式左键点击即可
 