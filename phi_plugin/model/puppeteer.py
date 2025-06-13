from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from nonebot_plugin_htmlrender import html_to_pic

from ..config import VERSION

# 资源路径（统一为 Path 类型）
PLUGIN_RESOURCES = Path("./resources")
IMG_PATH = Path("./images")

# 配置 Jinja2（启用异步模式）
env = Environment(
    loader=FileSystemLoader(PLUGIN_RESOURCES),  # FileSystemLoader 接受字符串路径
    autoescape=select_autoescape(["html", "xml"]),
    enable_async=True,  # 支持异步渲染
)


class newPuppeteer:
    @classmethod
    async def render(cls, path: str | Path, params: dict):
        """渲染 HTML 并转换为图片（异步支持）"""
        if isinstance(path, str):
            path = Path(path)
        app, tpl = path.parts

        # 获取模板文件
        template_path = PLUGIN_RESOURCES / "html" / app / f"{tpl}.html"
        template = env.get_template(str(template_path.relative_to(PLUGIN_RESOURCES)))

        # 构造 layout 路径
        layout_path = PLUGIN_RESOURCES / "html" / "common" / "layout"
        default_layout = layout_path / "default.html"
        elem_layout = layout_path / "elem.html"

        # 构造模板数据
        data = {
            **params,
            "tplFile": f"html/{app}/{tpl}.html",
            "_res_path": str(PLUGIN_RESOURCES),
            "pluResPath": str(PLUGIN_RESOURCES),
            "_imgPath": str(IMG_PATH),
            "_layout_path": str(layout_path),
            "defaultLayout": str(default_layout),
            "elemLayout": str(elem_layout),
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

        # 异步渲染 Jinja2 模板
        html_content = await template.render_async(data)

        # 异步转换 HTML 到图片
        return await html_to_pic(html_content, wait=2)
