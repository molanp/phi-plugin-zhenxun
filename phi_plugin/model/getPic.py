from nonebot import require
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import Image

from zhenxun.services.log import logger

from .getInfo import getInfo
from .path import imgPath
from .picmodle import picmodle


class pic:
    @staticmethod
    async def GetSongsInfoAtlas(name: str, data: dict | None = None):
        """
        获取歌曲图鉴，曲名为原名

        :param str name: 曲名
        :param dict data: 自定义数据
        """
        data = data or getInfo.info(name)
        if data is None:
            return f"未找到{name}的相关曲目信息!QAQ"
        data["illustration"] = getInfo.getill(name)
        return await picmodle.alias(data)

    @staticmethod
    async def GetSongsIllAtlas(name: str, data: dict | None = None):
        """
        获取曲绘图鉴

        :param str name: 原曲名称
        :param dict data: 自定义数据
        """
        if data is not None:
            return await picmodle.ill(
                {
                    "illustration": data.get("illustration"),
                    "illustrator": data.get("illustrator"),
                }
            )
        else:
            return await picmodle.ill(
                {
                    "illustration": getInfo.getill(name),
                    "illustrator": getInfo.info(name).get("illustrator"),
                }
            )

    @staticmethod
    async def getChap(data: dict):
        return await picmodle.chap(data)

    @staticmethod
    def getimg(img, style="png"):
        """
        获取本地图片，文件格式默认png

        :param str img: 文件名
        :param str style: 文件格式，默认为png
        """
        url = imgPath / f"{img}.{style}"
        if url.exists():
            return Image(path=url)
        logger.warning(f"未找到 {img}.{style}", "phi-plugin")
        return False

    @staticmethod
    def getIll(name, kind="common"):
        """
        获取曲绘，返回地址

        :param str name: 原名
        :param {'common'|'blur'|'low'} [kind='common'] 清晰度
        :return {string} 文件地址
        """
        return Image(path=getInfo.getill(name, kind))
