import base64
import hmac
import time
import uuid

from zhenxun.utils.http_utils import AsyncHttpx

from .CompleteQRCodeData import CompleteQRCodeData


class TapTapHelper:
    TapSDKVersion = "2.1"
    WebHost = "https://accounts.tapapis.com"
    ChinaWebHost = "https://accounts.tapapis.cn"
    ApiHost = "https://open.tapapis.com"
    ChinaApiHost = "https://open.tapapis.cn"
    client_id = "rAK3FfdieFob2Nn8Am"

    @classmethod
    def get_china_profile_url(cls, has_public_profile=True):
        base = f"{cls.ChinaApiHost}/account/profile/v1?client_id="
        return (
            base + cls.client_id
            if has_public_profile
            else f"{cls.ChinaApiHost}/account/basic-info/v1?client_id={cls.client_id}"
        )

    @classmethod
    async def request_login_qr_code(
        cls, permissions=["public_profile"], use_china=True
    ):
        client_id = str(uuid.uuid4()).replace("-", "")

        form_data = {
            "client_id": cls.client_id,
            "response_type": "device_code",
            "scope": ",".join(permissions),
            "version": cls.TapSDKVersion,
            "platform": "unity",
            "info": f'{{"device_id": "{client_id}"}}',
        }

        url = (
            f"{cls.ChinaWebHost}/oauth2/v1/device/code"
            if use_china
            else f"{cls.WebHost}/oauth2/v1/device/code"
        )
        response = await AsyncHttpx.post(url, data=form_data)
        return {**response.json(), "deviceId": client_id}

    @classmethod
    async def check_qr_code_result(cls, data, use_china=True):
        qr_data = CompleteQRCodeData(data)

        form_data = {
            "grant_type": "device_token",
            "client_id": cls.client_id,
            "secret_type": "hmac-sha-1",
            "code": qr_data.device_code,
            "version": "1.0",
            "platform": "unity",
            "info": f'{{"device_id": "{qr_data.device_id}"}}',
        }

        url = (
            f"{cls.ChinaWebHost}/oauth2/v1/token"
            if use_china
            else f"{cls.WebHost}/oauth2/v1/token"
        )
        response = await AsyncHttpx.post(url, data=form_data)
        return response.json()

    @classmethod
    async def get_profile(cls, token, use_china=True):
        if "public_profile" not in token["scope"]:
            raise ValueError("Public profile permission required")

        base_url = cls.ChinaApiHost if use_china else cls.ApiHost
        url = f"{base_url}/account/profile/v1?client_id={cls.client_id}"

        auth_header = cls._generate_auth_header(url, token["kid"], token["mac_key"])
        headers = {"Authorization": auth_header}
        response = await AsyncHttpx.get(url, headers=headers)
        return response.json()

    @classmethod
    def _generate_auth_header(cls, request_url, key_id, mac_key):
        url = request_url
        method = "GET"
        time_str = str(int(time.time())).zfill(10)
        nonce = cls._generate_nonce()
        host = url.split("//")[1].split("/")[0]
        port = "443" if url.startswith("https") else "80"
        uri = url.split(host)[1]

        sign_data = f"{time_str}\n{nonce}\n{method}\n{uri}\n{host}\n{port}\n\n"

        hmac_signature = hmac.new(mac_key.encode(), sign_data.encode(), "sha1").digest()
        hmac_base64 = base64.b64encode(hmac_signature).decode()

        return (
            f'MAC id="{key_id}", ts="{time_str}", nonce="{nonce}", mac="{hmac_base64}"'
        )

    @staticmethod
    def _generate_nonce(length=16):
        return base64.b64encode(uuid.uuid4().bytes)[:length].decode()
