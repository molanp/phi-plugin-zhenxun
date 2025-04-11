import qrcode

from .LCHelper import LCHelper
from .TapTapHelper import TapTapHelper


class QRCodeGenerator:

    @classmethod
    async def get_request(cls):
        return await TapTapHelper.request_login_qr_code()

    @classmethod
    def generate_qr_code(cls, url):
        return qrcode.make(url)

    @classmethod
    async def check_qr_code_result(cls, request_data):
        return await TapTapHelper.check_qr_code_result(request_data)

    @classmethod
    async def get_session_token(cls, result):
        profile = await TapTapHelper.get_profile(result["data"])
        combined_data = {**profile["data"], **result["data"]}
        login_response = await LCHelper.login_with_auth_data(combined_data)
        return login_response["sessionToken"]
