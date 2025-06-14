import hashlib
import time
from typing import Any
from urllib.parse import urljoin

from zhenxun.utils.http_utils import AsyncHttpx


class LCHelper:
    """LeanCloud 助手类"""

    APP_KEY = "Qr9AEqtuoSVS3zeD6iVbM4ZC0AtkJcQ89tywVyi0"
    CLIENT_ID = "rAK3FfdieFob2Nn8Am"
    BASE_URL = "https://rak3ffdi.cloud.tds1.tapapis.cn/1.1"

    def md5HashHexStringDefaultGetter(self, input_str: str) -> str:
        """
        计算 MD5 哈希值

        Args:
            input_str: 输入字符串

        Returns:
            MD5 哈希值
        """
        return hashlib.md5(input_str.encode()).hexdigest()

    async def loginWithAuthData(
        self, data: dict[str, Any], fail_on_not_exist: bool = False
    ) -> dict[str, Any]:
        """
        使用认证数据登录

        Args:
            data: 认证数据
            fail_on_not_exist: 是否在用户不存在时失败

        Returns:
            登录响应
        """
        auth_data = {"taptap": data}
        path = "users?failOnNotExist=true" if fail_on_not_exist else "users"
        return await self.request(path, "post", {"authData": auth_data})

    async def loginAndGetToken(
        self, data: dict[str, Any], fail_on_not_exist: bool = False
    ) -> str:
        """
        登录并获取令牌

        Args:
            data: 认证数据
            fail_on_not_exist: 是否在用户不存在时失败

        Returns:
            会话令牌
        """
        response = await self.loginWithAuthData(data, fail_on_not_exist)
        return response["sessionToken"]

    async def request(
        self,
        path: str,
        method: str,
        data: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
        with_api_version: bool = True,
    ) -> dict[str, Any]:
        """
        发送请求

        Args:
            path: 请求路径
            method: 请求方法
            data: 请求数据
            query_params: 查询参数
            with_api_version: 是否包含 API 版本

        Returns:
            响应数据
        """
        url = self.buildUrl(path, query_params, with_api_version)
        headers = {
            "X-LC-Id": self.CLIENT_ID,
            "Content-Type": "application/json",
        }
        self.fillHeaders(headers)

        method_lower = method.lower()
        if method_lower == "get":
            response = await AsyncHttpx.get(url, headers=headers, params=query_params)
        elif method_lower == "post":
            response = await AsyncHttpx.post(url, headers=headers, json=data)
        else:
            raise NotImplementedError(f"不支持的 HTTP 方法: {method}")
        return response.json()

    def buildUrl(
        self,
        path: str,
        query_params: dict[str, Any] | None = None,
        with_api_version: bool = True,
    ) -> str:
        """
        构建 URL

        Args:
            path: 路径
            query_params: 查询参数
            with_api_version: 是否包含 API 版本

        Returns:
            完整 URL
        """
        url = (
            self.BASE_URL
            if with_api_version
            else "https://rak3ffdi.cloud.tds1.tapapis.cn"
        )
        url = urljoin(url, path)

        if query_params:
            query_pairs = [
                f"{key}={value}"
                for key, value in query_params.items()
                if value is not None
            ]
            queries = "&".join(query_pairs)
            url = f"{url}?{queries}"

        return url

    def fillHeaders(
        self, headers: dict[str, str], req_headers: dict[str, str] | None = None
    ) -> None:
        """
        填充请求头

        Args:
            headers: 请求头
            req_headers: 额外请求头
        """
        if req_headers:
            headers.update(req_headers)

        timestamp = int(time.time())
        data = f"{timestamp}{self.APP_KEY}"
        hash_value = self.md5HashHexStringDefaultGetter(data)
        sign = f"{hash_value},{timestamp}"
        headers["X-LC-Sign"] = sign
