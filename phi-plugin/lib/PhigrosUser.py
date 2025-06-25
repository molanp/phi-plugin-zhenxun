import io
import re
from typing import Any
import zipfile

from nonebot.utils import run_sync

from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from ..model.cls.common import SaveInfo
from .ByteReader import ByteReader
from .GameProgress import GameProgress
from .GameRecord import GameRecord
from .GameSettings import GameSettings
from .GameUser import GameUser
from .SaveManager import SaveManager


class readZip:
    def __init__(self, b: bytes):
        self.data = io.BytesIO(b)

    @run_sync
    def file(self, filename: str):
        with zipfile.ZipFile(self.data) as zf:
            with zf.open(filename) as file:
                return file.read()


class PhigrosUser:
    """Phigros 用户类"""

    sessionToken: str
    saveInfo: list[SaveInfo]
    gameRecord: dict[str, list[Any]]

    def __init__(self, sessionToken: str | None) -> None:
        """
        初始化

        :param sessionToken: 会话令牌
        """
        self.saveInfo = []
        self.gameRecord = {}
        if sessionToken is None:
            sessionToken = ""
        if not re.match(r"[a-z0-9A-Z]{25}", sessionToken):
            raise ValueError("SessionToken格式错误")
        self.sessionToken = sessionToken

    def chooseSave(self, choose: int) -> bool:
        """
        选择存档

        :param choose: 存档索引
        :return: 是否成功
        """
        if isinstance(self.saveInfo, list) and 0 <= choose < len(self.saveInfo):
            self.saveInfo = [self.saveInfo[choose]]
            return True
        return False

    async def getSaveInfo(self) -> SaveInfo:
        """
        获取存档信息

        :return: 存档信息
        """
        raw_save_info = await SaveManager.saveCheck(self.sessionToken)
        if (
            isinstance(raw_save_info, list)
            and raw_save_info
            and isinstance(raw_save_info[0], dict)
        ):
            self.saveInfo = [SaveInfo(**raw_save_info[0])]
        else:
            logger.error("错误的存档", "phi-plugin")
            logger.error(str(raw_save_info), "phi-plugin")
            raise ValueError("未找到存档QAQ！")
        try:
            if not isinstance(self.saveInfo, list):
                raise ValueError("存档信息格式错误")
            assert isinstance(self.saveInfo, list)
            if self.saveInfo[0].gameFile.url:
                self.saveUrl = self.saveInfo[0].gameFile.url
        except Exception as e:
            logger.error("设置saveUrl失败", "phi-plugin", e=e)
            raise ValueError("设置saveUrl失败") from e
        return self.saveInfo[0]

    async def buildRecord(self) -> bool:
        """
        返回未绑定的信息数组，没有则为false

        (注: 看实际逻辑感觉是构建记录，然后不会有返回，失败直接抛出)

        :return: 是否成功
        """
        if not hasattr(self, "saveUrl"):
            await self.getSaveInfo()

        if self.saveInfo[0].summary.saveVersion == "1":
            raise ValueError("存档版本过低，请更新Phigros！")

        if getattr(self, "saveUrl", None):
            # 从saveurl获取存档zip
            try:
                response = await AsyncHttpx.get(self.saveUrl)
                if not response:
                    raise ValueError("获取存档失败")
                savezip = readZip(response.content)

                # 插件存档版本
                self.Recordver = 1.0

                # 获取 gameProgress
                file = ByteReader(await savezip.file("gameProgress"))
                file.getByte()
                self.gameProgress = GameProgress(
                    await SaveManager.decrypt(file.getAllByte())
                )

                # 获取 gameuser
                file = ByteReader(await savezip.file("user"))
                file.getByte()
                self.gameuser = GameUser(await SaveManager.decrypt(file.getAllByte()))

                # 获取 gamesetting
                file = ByteReader(await savezip.file("settings"))
                file.getByte()
                self.gamesettings = GameSettings(
                    await SaveManager.decrypt(file.getAllByte())
                )

                # 获取gameRecord
                file = ByteReader(await savezip.file("gameRecord"))
                if file.getByte() != GameRecord.version:
                    self.gameRecord = {}
                    logger.info(
                        "[PhigrosUser]版本号已更新，请更新PhigrosLibrary。",
                        "phi-plugin",
                    )
                    raise ValueError("版本号已更新")

                record = GameRecord(await SaveManager.decrypt(file.getAllByte()))
                self.gameRecord = record.Record
                return True

            except Exception as e:
                if isinstance(e, ValueError):
                    raise e
                logger.error("解压zip文件失败", "phi-plugin", e=e)
                raise RuntimeError("解压zip文件失败") from e

        else:
            logger.info("获取存档链接失败！", "phi-plugin")
            raise RuntimeError("获取存档链接失败！")
