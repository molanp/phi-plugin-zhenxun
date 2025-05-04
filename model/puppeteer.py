import asyncio
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from nonebot_plugin_htmlrender import html_to_pic

# 资源路径
PLUGIN_RESOURCES = "./resources"
IMG_PATH = "./images"

# 配置 Jinja2（启用异步模式）
env = Environment(
    loader=FileSystemLoader(PLUGIN_RESOURCES),
    autoescape=select_autoescape(['html', 'xml']),
    enable_async=True  # 关键：支持异步渲染
)

class NewPuppeteer:
    @classmethod
    async def render(cls, path: str, params: dict):
        """渲染 HTML 并转换为图片（异步支持）"""
        app, tpl = path.split('/')
        template = env.get_template(f"html/{app}/{tpl}.html")

        # 恢复完整参数结构
        layout_path = os.path.join(PLUGIN_RESOURCES, "html/common/layout/")

        data = {
            **params,  # 继承原来的传参
            "tplFile": f"./plugins/resources/html/{app}/{tpl}.html",
            "_res_path": PLUGIN_RESOURCES,
            "_imgPath": IMG_PATH,
            "_layout_path": layout_path,
            "defaultLayout": os.path.join(layout_path, "default.html"),
            "elemLayout": os.path.join(layout_path, "elem.html"),
            "sys": {
                "scale": "style=transform:scale(1)",
                "copyright": "Created By Python & NoneBot Plugin"
            }
        }

        # **异步渲染 Jinja2 模板**
        html_content = await template.render_async(data)

        # **异步转换 HTML 到图片**
        return await html_to_pic(html_content, wait=2)

# 入口函数
async def main():
    path = "app/tpl"
    params = {"name": "Python", "custom_key": "测试值"}

    # 渲染 HTML → 图片（完全异步）
    image = await NewPuppeteer.render(path, params)

    print(image)  # 这是 NoneBot 图片对象

asyncio.run(main())