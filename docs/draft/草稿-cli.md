帮我用 cli click 库创建一个命令行工具，导入 utils\drission_page.py 中的 create_browser 函数，默认 19222 端口。 example\drission_page_demo.py

cli 暂时先完成以下指令：
一个是 get2md 传参 url 返回 markdown 格式的页面内容。使用 markitdown 库解析。  https://github.com/microsoft/markitdown
一个是 screenshot id默认为none，不需要传参。默认获得当前页面截图保存到 output/images 路径
另一个是 vision 传参 query 字符串，返回视觉模型的结果。

视觉模型使用这个 视觉模型：
https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.6v#python-2
端点： https://open.bigmodel.cn/api/paas/v4
GLM-4.6V（旗舰版）、GLM-4.6V-FlashX（轻量高速版）、GLM-4.6V-Flash（完全免费）
也支持 "model": "glm-4.7"

