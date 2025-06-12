from typing import Literal

from nonebot import require

from ..utils import to_dict

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
        data_ = data or to_dict(await getInfo.info(name))
        if data_ is None:
            return f"未找到{name}的相关曲目信息!QAQ"
        data_["illustration"] = getInfo.getill(name)
        return await picmodle.alias(data_)

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
        info = await getInfo.info(name)
        return await picmodle.ill(
            {
                "illustration": await getInfo.getill(name),
                "illustrator": info.illustrator if info else None,
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
    async def getIll(name, kind: Literal["common", "blur", "low"] = "common") -> Image:
        """
        获取曲绘，返回图片消息段

        :param str name: 原名
        :param str kind: 清晰度
        :return: 图片消息段
        """
        res = await getInfo.getill(name, kind)
        return Image(url=res) if isinstance(res, str) else Image(path=res)
