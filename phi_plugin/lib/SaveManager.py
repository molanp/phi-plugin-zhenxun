import base64
from datetime import datetime
import hashlib
import json
from typing import Any
from urllib.parse import urljoin

from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from .AES import decrypt, encrypt
from .http import Builder, HttpClient
from .Summary import Summary


class SaveModel:
    """存档模型类"""

    summary: str | None
    object_id: str | None
    user_object_id: str | None
    game_object_id: str | None
    updated_time: str | None
    checksum: str | None

    def __init__(self):
        self.summary = None
        self.object_id = None
        self.user_object_id = None
        self.game_object_id = None
        self.updated_time = None
        self.checksum = None


class SaveManager:
    """存档管理器类"""

    baseUrl = "https://rak3ffdi.cloud.tds1.tapapis.cn/1.1"
    fileTokensUrl = urljoin(baseUrl, "/fileTokens")
    fileCallbackUrl = urljoin(baseUrl, "/fileCallback")
    saveUrl = urljoin(baseUrl, "/classes/_GameSave")
    userInfoUrl = urljoin(baseUrl, "/users/me")
    filesUrl = urljoin(baseUrl, "/files/")

    def __init__(self, user: Any, save_info: dict | None = None):
        """
        初始化存档管理器

        Args:
            user: 用户对象
            save_info: 存档信息
        """
        self.user = user
        self.client = HttpClient()
        self.data: bytes | None = None
        self.save_model = SaveModel()

        if save_info:
            try:
                if not isinstance(save_info, dict):
                    raise ValueError("存档信息格式错误")
                if any(
                    k not in save_info
                    for k in ("summary", "objectId", "user", "gameFile")
                ):
                    raise ValueError("存档信息缺少必要字段")
                if (
                    not isinstance(save_info["user"], dict)
                    or "objectId" not in save_info["user"]
                ):
                    raise ValueError("用户信息格式错误")
                if not isinstance(save_info["gameFile"], dict) or any(
                    k not in save_info["gameFile"]
                    for k in ("objectId", "updatedAt", "metaData", "url")
                ):
                    raise ValueError("游戏文件信息格式错误")
                if (
                    not isinstance(save_info["gameFile"]["metaData"], dict)
                    or "_checksum" not in save_info["gameFile"]["metaData"]
                ):
                    raise ValueError("元数据格式错误")

                self.save_model.summary = save_info["summary"]
                self.save_model.object_id = save_info["objectId"]
                self.save_model.user_object_id = save_info["user"]["objectId"]
                game_file = save_info["gameFile"]
                self.save_model.game_object_id = game_file["objectId"]
                self.save_model.updated_time = game_file["updatedAt"]
                self.save_model.checksum = game_file["metaData"]["_checksum"]
                user.save_url = game_file["url"]
            except Exception as e:
                logger.error(f"初始化存档信息失败: {e}")
                raise ValueError(f"初始化存档信息失败: {e}")

    @staticmethod
    async def getPlayerId(session: str) -> dict:
        """
        获取玩家 ID

        Args:
            session: 会话令牌

        Returns:
            玩家信息
        """
        return (
            await AsyncHttpx.get(
                SaveManager.userInfoUrl,
                headers={
                    "X-LC-Id": "rAK3FfdieFob2Nn8Am",
                    "X-LC-Key": "Qr9AEqtuoSVS3zeD6iVbM4ZC0AtkJcQ89tywVyi0",
                    "X-LC-Session": session,
                    "User-Agent": "LeanCloud-CSharp-SDK/1.0.3",
                    "Accept": "application/json",
                },
            )
        ).json()

    @staticmethod
    async def saveArray(session: str) -> list[dict]:
        response = await AsyncHttpx.get(
            SaveManager.saveUrl,
            headers={
                "X-LC-Id": "rAK3FfdieFob2Nn8Am",
                "X-LC-Key": "Qr9AEqtuoSVS3zeD6iVbM4ZC0AtkJcQ89tywVyi0",
                "X-LC-Session": session,
                "User-Agent": "LeanCloud-CSharp-SDK/1.0.3",
                "Accept": "application/json",
            },
        )
        return response["results"]

    @staticmethod
    async def saveCheck(session: str) -> list[dict]:
        """
        检查存档

        Args:
            session: 会话令牌

        Returns:
            存档列表

        Raises:
            ValueError: 存档列表为空
        """
        array = await SaveManager.saveArray(session)
        if not array:
            logger.error("TK 对应存档列表为空，请检查是否同步存档QAQ！")
            raise ValueError("TK 对应存档列表为空，请检查是否同步存档QAQ！")
        results = []
        for item in array:
            item["summary"] = Summary(item["summary"])
            item.update(await SaveManager.getPlayerId(session))
            date = datetime.fromisoformat(item["updatedAt"].replace("Z", "+00:00"))
            item["updatedAt"] = date.strftime("%Y %b.%d %H:%M:%S")
            if item.get("gameFile"):
                item["PlayerId"] = item["nickname"]
                results.append(item)
        return results

    @staticmethod
    async def save(session):
        array = await SaveManager.saveArray(session)
        size = len(array)
        if size == 0:
            raise ValueError("存档不存在")
        return array[0]

    @staticmethod
    async def delete(session: str, object_id: str) -> str:
        """
        删除存档

        Args:
            session: 会话令牌
            object_id: 存档 ID

        Returns:
            删除结果
        """
        response = await AsyncHttpx.post(
            urljoin(SaveManager.baseUrl, f"/classes/_GameSave/{object_id}"),
            headers={
                "X-LC-Id": "rAK3FfdieFob2Nn8Am",
                "X-LC-Key": "Qr9AEqtuoSVS3zeD6iVbM4ZC0AtkJcQ89tywVyi0",
                "X-LC-Session": session,
                "User-Agent": "LeanCloud-CSharp-SDK/1.0.3",
                "Accept": "application/json",
            },
            method="DELETE",
        )
        return response.text

    @staticmethod
    async def decrypt(data: bytes) -> bytes:
        """
        解密数据

        Args:
            data: 加密数据

        Returns:
            解密后的数据
        """
        return await decrypt(data)

    @staticmethod
    async def encrypt(data: bytes, key: str | bytes, iv: str | bytes) -> bytes:
        """
        加密数据

        Args:
            data: 原始数据
            key: 加密密钥
            iv: 初始化向量

        Returns:
            加密后的数据
        """
        return await encrypt(data, key, iv)

    @staticmethod
    def md5(data: str | bytes) -> str:
        """
        计算 MD5

        Args:
            data: 原始数据

        Returns:
            MD5 值
        """
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.md5(data).hexdigest()

    async def modify(self, clazz: Any, callback: Any) -> bool:
        """
        修改存档

        Args:
            clazz: 类
            callback: 回调函数

        Returns:
            是否成功
        """
        try:
            request = await Builder(self.user.save_url).GET().build()
            self.data = await self.client.send(request)

            if (
                self.data
                and self.save_model.checksum
                and self.md5(self.data) != self.save_model.checksum
            ):
                raise ValueError("文件校验不一致")

            # TODO: 实现 ZIP 文件处理逻辑
            # 这部分需要实现 ZIP 文件的读写和加密解密
            return True
        except Exception as e:
            logger.error("修改存档失败", e=e)
            return False

    async def uploadZip(self, score: int) -> bool:
        """
        上传 ZIP 文件

        Args:
            score: 分数

        Returns:
            是否成功
        """
        try:
            template = Builder(self.user.save_url)
            template.header("X-LC-Session", self.user.session)

            if not self.save_model.summary:
                raise ValueError("存档摘要为空")

            summary_bytes = list(base64.b64decode(self.save_model.summary))
            summary_bytes[1] = score & 0xFF
            summary_bytes[2] = (score >> 8) & 0xFF
            self.save_model.summary = base64.b64encode(bytes(summary_bytes)).decode()

            builder = template.copy()
            builder.uri(SaveManager.fileTokensUrl)
            builder.POST(
                json.dumps(
                    {
                        "name": ".save",
                        "__type": "File",
                        "ACL": {
                            self.save_model.user_object_id: {
                                "read": True,
                                "write": True,
                            }
                        },
                        "prefix": "gamesaves",
                        "metaData": {
                            "_checksum": self.md5(self.data) if self.data else "",
                            "_version": "1.0.0",
                        },
                    }
                )
            )
            response = await self.client.send(await builder.build())
            if not response:
                raise ValueError("获取上传令牌失败")
            return True
        except Exception as e:
            logger.error("上传 ZIP 文件失败", e=e)
            return False
