from datetime import datetime

from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from ..utils import to_dict
from .AES import Decrypt
from .Summary import Summary


class SaveManager:
    """存档管理器类"""

    baseUrl = "https://rak3ffdi.cloud.tds1.tapapis.cn/1.1"
    fileTokensUrl = baseUrl + "/fileTokens"
    fileCallbackUrl = baseUrl + "/fileCallback"
    saveUrl = baseUrl + "/classes/_GameSave"
    userInfoUrl = baseUrl + "/users/me"
    filesUrl = baseUrl + "/files/"

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
            item["summary"] = to_dict(Summary(item["summary"]))
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
        return await Decrypt(data)

