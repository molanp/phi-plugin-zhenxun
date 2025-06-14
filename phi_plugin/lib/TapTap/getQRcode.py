# from io import BytesIO
# from typing import Any

# import qrcode

# from .LCHelper import LCHelper
# from .TapTapHelper import TapTapHelper


# class GetQRCode:
#     """获取 TapTap QR 码的类"""

#     def __init__(self) -> None:
#         self.lc_helper = LCHelper()
#         self.tap_tap_helper = TapTapHelper()

#     async def get_request(self) -> dict[str, Any]:
#         """
#         获取登录 QR 码请求

#         Returns:
#             登录 QR 码请求数据
#         """
#         return await self.tap_tap_helper.request_login_qr_code()

#     async def get_qrcode(self, url: str) -> bytes:
#         """
#         生成 QR 码图片

#         Args:
#             url: QR 码 URL

#         Returns:
#             QR 码图片数据
#         """
#         qr = qrcode.QRCode(version=1, box_size=10, border=5)
#         qr.add_data(url)
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")
#         buffer = BytesIO()
#         img.save(buffer, format="PNG")
#         return buffer.getvalue()

#     async def check_qrcode_result(self, request: dict[str, Any]) -> dict[str, Any]:
#         """
#         检查 QR 码扫描结果

#         Args:
#             request: QR 码请求数据

#         Returns:
#             QR 码扫描结果
#         """
#         return await self.tap_tap_helper.check_qrcode_result(request)

#     async def get_profile(self, result: dict[str, Any]) -> dict[str, Any]:
#         """
#         获取用户资料

#         Args:
#             result: QR 码扫描结果

#         Returns:
#             用户资料
#         """
#         return await self.tap_tap_helper.get_profile(result["data"])

#     async def get_session_token(
#         self, profile: dict[str, Any], result: dict[str, Any]
#     ) -> str:
#         """
#         获取会话令牌

#         Args:
#             profile: 用户资料
#             result: QR 码扫描结果

#         Returns:
#             会话令牌
#         """
#         return await self.lc_helper.login_and_get_token(
#             {**profile["data"], **result["data"]}
#         )


# # 创建单例实例
# get_qrcode = GetQRCode()
