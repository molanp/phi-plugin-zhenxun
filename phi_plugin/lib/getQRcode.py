from io import BytesIO

from nonebot.utils import run_sync
import qrcode

from .TapTap.LCHelper import LCHelper
from .TapTap.TapTapHelper import TapTapHelper


class GetQRcode:
    async def getRequest(self):
        return await TapTapHelper.request_login_qr_code()

    @run_sync
    def _generate_qr_code(self, url):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    async def getQRcode(self, url):
        return await self._generate_qr_code(url)

    async def checkQRCodeResult(self, request):
        """返回 authorization_pending 或 authorization_waiting"""
        return await TapTapHelper.check_qr_code_result(request)

    async def getSessionToken(self, result):
        profile = await TapTapHelper.get_profile(result.data)
        return (
            await LCHelper().loginAndGetToken({**profile.data, **result.data})
        )


# 创建单例实例
get_qrcode = GetQRcode()
