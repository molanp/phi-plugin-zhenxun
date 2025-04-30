from nonebot.plugin import PluginMetadata

from zhenxun.configs.utils import PluginExtraData
from zhenxun.services.log import logger

from .config import CONFIG, VERSION

__plugin_meta__ = PluginMetadata(
    name="phi-plugin",
    description="Phigros查分及娱乐插件",
    usage="""

    """.strip(),
    extra=PluginExtraData(
        author="molanp",
        version=VERSION,
        configs=CONFIG[0],
    ).dict(),
)

logger.info("------φ^_^φ------")
logger.success("phi插件载入成功~", "phi-plugin")
logger.info("本插件由 molanp 进行移植，感谢原仓库 Catrong/phi-plugin")
logger.info("本项目云存档功能由 7aGiven/PhigrosLibrary 改写而来，感谢文酱的帮助！")
