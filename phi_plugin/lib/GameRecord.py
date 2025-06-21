from typing import Any

from zhenxun.services.log import logger

from .ByteReader import ByteReader
from .LevelRecord import LevelRecord
from .Util import Util


class GameRecord:
    """游戏记录"""
    name: str = "gameRecord"
    version: int = 1

    def __init__(self, data: bytes | str) -> None:
        """
        初始化

        :param data: 二进制数据
        """
        self.name: str = "gameRecord"
        self.version: int = 1
        self.Record: dict[str, list[LevelRecord]] = {}
        self.data = ByteReader(data)

    async def init(self, song_data: list[Any]) -> None:
        """
        初始化记录

        :param song_data: 歌曲数据
        """
        try:
            self.songsnum = self.data.getVarInt()

            while self.data.remaining() > 0:
                key = self.data.getString()
                self.data.skipVarInt()
                length = self.data.getByte()
                fc = self.data.getByte()
                song: list[LevelRecord] = [LevelRecord()]*4
                for level in range(4):
                    if Util.getBit(length, level):
                        song[level].score = self.data.getInt()
                        song[level].acc = self.data.getFloat()
                        song[level].fc = (
                            True
                            if (song[level].score == 1000000 and song[level].acc == 100)
                            else Util.getBit(fc, level)
                        )

                self.Record[key] = song

        except Exception as e:
            logger.error("[GameRecord]初始化记录失败", "phi-plugin", e=e)
            raise ValueError("[GameRecord]初始化记录失败") from e
