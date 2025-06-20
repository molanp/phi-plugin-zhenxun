import io

from nonebot.utils import run_sync
from nonebot_plugin_alconna import Image
import qrcode

from .TapTap.LCHelper import LCHelper
from .TapTap.TapTapHelper import TapTapHelper


class getQRcode:
    @staticmethod
    async def getRequest():
        return await TapTapHelper.requestLoginQRCode()

    @run_sync
    @staticmethod
    def getQRcode(url: str) -> Image:
        qr = qrcode.QRCode(
            version=1,
            box_size=10,  # 对应scale参数
            border=4,  # 标准二维码边框宽度
        )

        # 添加数据
        qr.add_data(url)
        qr.make(fit=True)

        # 生成图像（符合PNG格式要求）
        img = qr.make_image(fill_color="black", back_color="white")

        # 转换为字节数据
        img_byte_array = io.BytesIO()
        img.save(img_byte_array)
        return Image(raw=img_byte_array.getvalue())

    @staticmethod
    async def checkQRCodeResult(request: dict):
        return await TapTapHelper.checkQRCodeResult(request)

    @staticmethod
    async def getSessionToken(result: dict):
        profile = await TapTapHelper.getProfile(result["data"])
        return await LCHelper().loginAndGetToken({**profile["data"], **result["data"]})
