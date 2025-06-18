from nonebot_plugin_alconna import Image

from .TapTap.LCHelper import LCHelper
from .TapTap.TapTapHelper import TapTapHelper


class getQRcode:
    @staticmethod
    async def getRequest():
        return await TapTapHelper.requestLoginQRCode()

    @staticmethod
    def getQRcode(url: str) -> Image:
        return Image(url=f"https://api.2dcode.biz/v1/create-qr-code?data={url}")

    @staticmethod
    async def checkQRCodeResult(request: dict):
        return await TapTapHelper.checkQRCodeResult(request)

    @staticmethod
    async def getSessionToken(result: dict):
        profile = await TapTapHelper.getProfile(result["data"])
        return await LCHelper().loginAndGetToken({**profile["data"], **result["data"]})
