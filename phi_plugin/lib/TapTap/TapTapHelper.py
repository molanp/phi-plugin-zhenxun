import base64
from hashlib import sha1
import hmac
import secrets
import time
from urllib.parse import urlparse
import uuid

import ujson

from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from .CompleteQRCodeData import CompleteQRCodeData


class TapTapHelper:
    TapSDKVersion = "2.1"
    WebHost = "https://accounts.tapapis.com"
    ChinaWebHost = "https://accounts.tapapis.cn"
    ApiHost = "https://open.tapapis.com"
    ChinaApiHost = "https://open.tapapis.cn"
    CodeUrl = f"{WebHost}/oauth2/v1/device/code"
    ChinaCodeUrl = f"{ChinaWebHost}/oauth2/v1/device/code"
    TokenUrl = f"{WebHost}/oauth2/v1/token"
    ChinaTokenUrl = f"{ChinaWebHost}/oauth2/v1/token"

    @classmethod
    def GetChinaProfileUrl(cls, havePublicProfile=True) -> str:
        if havePublicProfile:
            return f"{cls.ChinaApiHost}/account/profile/v1?client_id="
        else:
            return f"{cls.ChinaApiHost}/account/basic-info/v1?client_id="

    @classmethod
    async def requestLoginQRCode(
        cls, permissions: list[str] | None = None, useChinaEndpoint: bool = True
    ) -> dict:
        if permissions is None:
            permissions = ["public_profile"]
        clientId = str(uuid.uuid4()).replace("-", "")
        data = {
            "client_id": "rAK3FfdieFob2Nn8Am",
            "response_type": "device_code",
            "scope": ",".join(permissions),
            "version": cls.TapSDKVersion,
            "platform": "unity",
            "info": ujson.dumps({"device_id": clientId}),
        }
        url = cls.ChinaCodeUrl if useChinaEndpoint else cls.CodeUrl
        response = await AsyncHttpx.post(url, data=data)
        return {**response.json(), "devideId": clientId}

    @classmethod
    async def checkQRCodeResult(cls, data: dict, useChinaEndpoint: bool = True) -> dict:
        """
        :param data: qrCodeData
        :param useChinaEndpoint:
        """
        qrCodeData = CompleteQRCodeData(data)
        data = {
            "grant_type": "device_token",
            "client_id": "rAK3FfdieFob2Nn8Am",
            "secret_type": "hmac-sha-1",
            "code": qrCodeData.deviceCode,
            "version": "1.0",
            "platform": "unity",
            "info": ujson.dumps({"device_id": qrCodeData.deviceID}),
        }
        url = cls.ChinaTokenUrl if useChinaEndpoint else cls.TokenUrl
        try:
            response = await AsyncHttpx.post(url, data=data)
            return response.json()
        except Exception as e:
            logger.error("Error checking QR code result", "phi-plugin", e=e)
            return {}

    @classmethod
    async def getProfile(
        cls, token: dict, useChinaEndpoint: bool = True, timestamp: int = 0
    ) -> dict:
        if "public_profile" not in token.get("scope", []):
            raise ValueError("Public profile permission is required.")
        if useChinaEndpoint:
            url = f"{cls.ChinaApiHost}/account/profile/v1?client_id=rAK3FfdieFob2Nn8Am"
        else:
            url = f"{cls.ApiHost}/account/profile/v1?client_id=rAK3FfdieFob2Nn8Am"
        authorizationHeader = getAuthorization(
            url, "GET", token["kid"], token["mac_key"]
        )
        response = await AsyncHttpx.get(
            url, headers={"Authorization": authorizationHeader}
        )
        return response.json()


def getAuthorization(requestUrl, method, keyId, macKey):
    url = urlparse(requestUrl)
    timeStr = str(int(time.time())).zfill(10)
    randomStr = getRandomString(16)
    host = url.hostname
    uri = f"{url.path}?{url.query}" if url.query else url.path
    if ":" in url.netloc:
        port = url.netloc.split(":")[-1]
    else:
        port = "443" if url.scheme == "https" else "80"
    other = ""
    sign = signData(
        mergaData(timeStr, randomStr, method, uri, host, port, other), macKey
    )
    return f'MAC id="{keyId}", ts="{timeStr}", nonce="{randomStr}", mac="{sign}"'


def getRandomString(length):
    return base64.b64encode(secrets.token_bytes(length)).decode("utf-8")


def mergaData(time, randomCode, httpType, uri, domain, port, other: str | None = None):
    prefix = f"{time}\n{randomCode}\n{httpType}\n{uri}\n{domain}\n{port}\n"
    return f"{prefix}{other}\n" if other else prefix + "\n"


def signData(signatureBaseString: str, key: str):
    """
    生成HMAC-SHA1签名并返回Base64编码结果

    :param signature_base_string: 签名原文
    :param key: 加密密钥

    :return: Base64编码的签名结果（去除填充字符=）
    """
    signature_bytes = signatureBaseString.encode("utf-8")
    key_bytes = key.encode("utf-8")
    hmac_obj = hmac.new(key_bytes, signature_bytes, sha1)
    digest = hmac_obj.digest()
    # Base64编码并去除填充字符
    return base64.b64encode(digest).decode("utf-8").rstrip("=")
