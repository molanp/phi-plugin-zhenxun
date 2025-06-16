from io import BytesIO

from nonebot.utils import run_sync
import qrcode  # type: ignore

from .TapTap.LCHelper import LCHelper
from .TapTap.TapTapHelper import TapTapHelper


class GetQRcode:
    async def getRequest(self):
        return await TapTapHelper.requestLoginQRCode()

    @run_sync
    def __generateQRCode(self, url):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG") # type: ignore
        return buffer.getvalue()

    async def getQRcode(self, url):
        return await self.__generateQRCode(url)

    async def checkQRCodeResult(self, request):
        """返回 authorization_pending 或 authorization_waiting"""
        return await TapTapHelper.checkQRCodeResult(request)

    async def getSessionToken(self, result: dict):
        profile = await TapTapHelper.getProfile(result["data"])
        return await LCHelper().loginAndGetToken({**profile["data"], **result["data"]})


# 创建单例实例
get_qrcode = GetQRcode()
