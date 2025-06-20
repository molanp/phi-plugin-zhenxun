from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from nonebot_plugin_htmlrender import html_to_pic

from ..config import VERSION
from .path import imgPath, pluginResources

# 配置 Jinja2（启用异步模式）
env = Environment(
    loader=FileSystemLoader(pluginResources),
    autoescape=False,
    enable_async=True,
)


class Puppeteer:
    @classmethod
    async def render(cls, path: str | Path, params: dict):
        """渲染 HTML 并转换为图片（异步支持）"""
        if isinstance(path, str):
            path = Path(path)
        app, tpl = path.parts

        template_path = f"html/{app}/{tpl}.html"
        template = env.get_template(template_path)

        layout_path = "html/common/layout"
        default_layout = f"{layout_path}/default.html"
        elem_layout = f"{layout_path}/elem.html"

        data = {
            **params,
            "tplFile": f"html/{app}/{tpl}.html",
            "_res_path": "",
            "pluResPath": "",
            "_imgPath": str(imgPath.relative_to(pluginResources)),
            "_layout_path": layout_path,
            "defaultLayout": default_layout,
            "elemLayout": elem_layout,
            "saveId": (params.get("saveId") or params.get("save_id") or tpl)
            + f"-{id(cls)}",
            "sys": {
                "scale": f'style="transform:scale({params.get("scale", 1)})"',
                "copyright": (
                    f"Created By phi-Plugin<span class='version'>{VERSION}</span>"
                ),
            },
            "Version": VERSION,
            "_plugin": "phi-plugin",
        }

        html_content = await template.render_async(data)
        return await html_to_pic(
            html_content, wait=2, template_path=f"file:///{pluginResources}"
        )
