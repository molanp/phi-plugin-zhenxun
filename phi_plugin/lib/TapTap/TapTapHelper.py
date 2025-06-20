import base64
import binascii
import time
from urllib.parse import urlparse

import Crypto
from Crypto.Hash import HMAC, SHA1
import Crypto.Random

from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from .CompleteQRCodeData import CompleteQRCodeData


def generate_uuid_v4_without_hyphens():
    """
    使用 PyCryptodome 生成符合 UUID v4 规范的无连字符字符串

    Returns:
        str: 32 位小写无连字符 UUID（如 550e8400e29b41d4910a41a54a74966a）
    """
    # 1. 生成 16 字节随机数据
    data = bytearray(Crypto.Random.get_random_bytes(16))
    # 2. 设置 UUID v4 特征位
    # - 第 7 字节（索引 6）的高 4 位必须为 0100（即 0x40-0x4f）
    data[6] = (data[6] & 0x0F) | 0x40
    # - 第 9 字节（索引 8）的高 2 位必须为 10xx（即 0x80-0xbf）
    data[8] = (data[8] & 0x3F) | 0x80
    # 3. 转换为十六进制字符串
    hex_str = binascii.hexlify(data).decode("utf-8")
    # 4. 插入 UUID 标准格式的连字符位置并移除
    return f"{hex_str[:8]}{hex_str[8:12]}{hex_str[12:16]}{hex_str[16:20]}{hex_str[20:]}".replace(
        "-", ""
    )


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
        clientId = generate_uuid_v4_without_hyphens()
        data = {
            "client_id": "rAK3FfdieFob2Nn8Am",
            "response_type": "device_code",
            "scope": ",".join(permissions),
            "version": cls.TapSDKVersion,
            "platform": "unity",
            "info": '{"device_id":"' + clientId + '"}',
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
            "info": '{"device_id":"' + qrCodeData.deviceID + '"}',
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
    return (
        base64.b64encode(Crypto.Random.get_random_bytes(length))
        .decode("utf-8")
        .replace("\n", "")
    )


# return crypto.randomBytes(length).toString('base64');


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
    encoded_data = signatureBaseString.encode("utf-8")
    encoded_key = key.encode("utf-8")
    # 创建HMAC-SHA1签名对象（使用PyCryptodome）
    hmac_obj = HMAC.new(encoded_key, digestmod=SHA1)
    hmac_obj.update(encoded_data)
    # 生成Base64编码结果（与Node.js digest('base64')格式一致）
    signature = base64.b64encode(hmac_obj.digest()).decode("utf-8")
    # 移除换行符确保格式一致（跨语言加密规范#3）
    return signature.replace("\n", "")


# function signData(signatureBaseString, key) {
#     const hmac = crypto.createHmac('sha1', key);
#     hmac.update(signatureBaseString);
#     return hmac.digest('base64');
# }
