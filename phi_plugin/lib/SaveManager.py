from datetime import datetime
from urllib.parse import urljoin

from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from .AES import decrypt, encrypt
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
        return response.json()["results"]

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
            logger.error("TK 对应存档列表为空，请检查是否同步存档QAQ！", "phi-plugin")
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
