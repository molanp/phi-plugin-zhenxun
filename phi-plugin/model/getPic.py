import os

from nonebot_plugin_alconna import Image

from .getInfo import getInfo
from .path import imgPath
from .picmodle import picmodle  # 假设picmodle模块导出picmodle类


class Pic:
    def __init__(self):
        self.getInfoInstance = getInfo  # 保留getInfo的实例引用

    async def GetSongsInfoAtlas(self, e, name, data=None):
        data = data or self.getInfoInstance.info(name)
        if data:
            data["illustration"] = self.getInfoInstance.getill(name)
            return await picmodle.picmodle(e, data)
        else:
            return f"未找到{name}的相关曲目信息!QAQ"

    async def GetSongsIllAtlas(self, e, name, data=None):
        if data:
            return await picmodle.ill(
                e,
                {
                    "illustration": data["illustration"],
                    "illustrator": data["illustrator"],
                },
            )
        else:
            return await picmodle.ill(
                e,
                {
                    "illustration": self.getInfoInstance.getill(name),
                    "illustrator": self.getInfoInstance.info(name).illustrator,
                },
            )

    async def GetChap(self, e, data):
        return await picmodle.chap(e, data)

    def getimg(self, img, style="png"):
        url = f"{imgPath}/{img}.{style}"
        return Image(path=url) if os.path.exists(url) else False

    def getIll(self, name, kind="common"):
        img_url = self.getInfoInstance.getill(name, kind)
        return Image(path=img_url)


# 导出实例（Python中通过直接赋值）
pic_instance = Pic()
