from typing import Any
from urllib.parse import urlparse

from zhenxun.utils.http_utils import AsyncHttpx


class HttpRequest:
    def __init__(self):
        self.url = ""
        self.method = "GET"
        self.headers: dict[str, str] = {}
        self.data = None


class Builder(HttpRequest):
    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def uri(self, url: str) -> "Builder":
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError("Invalid URL")
            self.url = url
            return self
        except Exception as e:
            raise ValueError(f"非法URL {e!s}")

    def header(self, name: str, value: Any) -> "Builder":
        self.headers[str(name)] = str(value)
        return self

    def copy(self) -> "Builder":
        result = Builder(self.url)
        result.method = self.method
        result.headers = self.headers.copy()
        result.data = self.data
        return result

    def DELETE(self) -> "Builder":
        self.method = "DELETE"
        return self

    def GET(self) -> "Builder":
        self.method = "GET"
        return self

    def POST(self, data: Any) -> "Builder":
        self.method = "POST"
        self.data = data
        return self

    async def build(self):
        if not self.url:
            raise ValueError("未设置URL")
        return await self._make_request()

    async def _make_request(self):
        if self.method == "GET":
            return await AsyncHttpx.get(url=self.url, headers=self.headers)
        elif self.method == "DELETE":
            return await AsyncHttpx.post(
                url=self.url, headers=self.headers, method="DELETE"
            )
        elif self.method == "POST":
            return await AsyncHttpx.post(
                url=self.url, headers=self.headers, data=self.data
            )
        else:
            raise ValueError(f"不支持的请求方法: {self.method}")


class HttpClient:
    def __init__(self):
        self.request = HttpRequest()

    async def send(self, response) -> Any:
        try:
            return await response.json()
        except Exception as e:
            print(f"Error parsing JSON response: {e}")
            return None


# 导出类
__all__ = ["HttpClient", "HttpRequest"]
