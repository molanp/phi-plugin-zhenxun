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
logger.info("正在载入phi插件...")
logger.info("--------------------------------------")
logger.success(f"phi插件{VERSION}载入完成~", "phi-plugin")
logger.info("作者：@Cartong | 移植：@molanp")
logger.info("仓库地址：https://github.com/molanp/zhenxun_plugin_phi-plugin")
logger.info("本项目云存档功能由 7aGiven/PhigrosLibrary 改写而来")
logger.info("--------------------------------------")
