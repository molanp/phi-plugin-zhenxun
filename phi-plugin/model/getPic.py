from pathlib import Path
from typing import Literal

from nonebot_plugin_alconna import Image
from pydantic import BaseModel

from zhenxun.services.log import logger

from ..utils import to_dict
from .getInfo import getInfo
from .path import imgPath
from .picmodle import picmodle


class SongsIllAtlasData(BaseModel):
    illustration: str | Path
    """曲绘地址"""
    illustrator: str | None
    """画师"""


class pic:
    @staticmethod
    async def GetSongsInfoAtlas(name: str, data: dict | None = None):
        """
        获取歌曲图鉴，曲名为原名

        :param name: 曲名
        :param data: 自定义数据
        """
        data = data or to_dict(getInfo.info(name))
        if not data:
            return f"未找到{name}的相关曲目信息!QAQ"
        data["illustration"] = getInfo.getill(name)
        return await picmodle.atlas(data)

    @staticmethod
    async def GetSongsIllAtlas(name: str, data: SongsIllAtlasData | None = None):
        """
        获取曲绘图鉴

        :param name: 原曲名称
        :param data: 自定义数据
        """
        if data is not None:
            return await picmodle.ill(
                {
                    "illustration": data.illustration,
                    "illustrator": data.illustrator,
                }
            )
        info = getInfo.info(name)
        return await picmodle.ill(
            {
                "illustration": getInfo.getill(name),
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

        :param img: 文件名
        :param style: 文件格式，默认为png
        """
        url = imgPath / f"{img}.{style}"
        if url.exists():
            return Image(path=url)
        logger.warning(f"未找到 {img}.{style}", "phi-plugin")
        return False

    @staticmethod
    async def getIll(
        name: str, kind: Literal["common", "blur", "low"] = "common"
    ) -> Image:
        """
        获取曲绘，返回图片消息段

        :param name: 原名
        :param kind: 清晰度
        :return: 图片消息段
        """
        res = getInfo.getill(name, kind)
        return Image(url=res) if isinstance(res, str) else Image(path=res)
