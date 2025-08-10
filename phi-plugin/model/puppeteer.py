from pathlib import Path

from nonebot_plugin_htmlrender import template_to_pic

from ..config import Version
from .path import imgPath, pluginResources


class Puppeteer:
    @classmethod
    async def render(cls, path: str | Path, params: dict):
        """渲染 HTML 并转换为图片（异步支持）"""
        if isinstance(path, str):
            path = Path(path)
        app, tpl = path.parts

        template_path = f"html/{app}/{tpl}.html"

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
                    'Created By NoneBot<span class="version">'
                    f"{Version['nonebot']}</span> & phi-Plugin"
                    f'<span class="version">{Version["ver"]}</span>'
                ),
            },
            "Version": Version,
            "_plugin": "phi-plugin",
        }

        return await template_to_pic(
            template_path=str(pluginResources),
            template_name=template_path,
            templates=data,
        )
