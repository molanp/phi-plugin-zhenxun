import hashlib
import time

from zhenxun.utils.http_utils import AsyncHttpx


class LCHelper:
    AppKey = "Qr9AEqtuoSVS3zeD6iVbM4ZC0AtkJcQ89tywVyi0"
    ClientId = "rAK3FfdieFob2Nn8Am"

    @staticmethod
    def md5_hash_hex(input_str):
        md5 = hashlib.md5()
        md5.update(input_str.encode("utf-8"))
        return md5.hexdigest()

    @classmethod
    async def login_with_auth_data(cls, data, fail_on_not_exist=False) -> dict:
        auth_data = {"taptap": data}
        path = "users?failOnNotExist=true" if fail_on_not_exist else "users"
        url = f"https://rak3ffdi.cloud.tds1.tapapis.cn/1.1/{path}"
        headers = {"X-LC-Id": cls.ClientId, "Content-Type": "application/json"}
        cls.fill_headers(headers)
        response = await AsyncHttpx.post(
            url, json={"authData": auth_data}, headers=headers
        )
        return response.json()

    @classmethod
    async def request(
        cls, path, method, data=None, query_params=None, with_api_version=True
    ):
        base_url = "https://rak3ffdi.cloud.tds1.tapapis.cn"
        if with_api_version:
            base_url += "/1.1"
        url = f"{base_url}/{path}"
        if query_params:
            url += f"?{'&'.join([f'{k}={v}' for k, v in query_params.items() if v is not None])}"

        headers = {"X-LC-Id": cls.ClientId, "Content-Type": "application/json"}
        cls.fill_headers(headers)

        if method.lower() == "post":
            response = await AsyncHttpx.post(url, json=data, headers=headers)
        elif method.lower() == "get":
            response = await AsyncHttpx.get(url, headers=headers)
        return response  # type: ignore

    @classmethod
    def fill_headers(cls, headers, req_headers=None):
        if req_headers:
            headers.update(req_headers)

        timestamp = int(time.time())
        data_str = f"{timestamp}{cls.AppKey}"
        md5_hash = cls.md5_hash_hex(data_str)
        sign = f"{md5_hash},{timestamp}"
        headers["X-LC-Sign"] = sign
