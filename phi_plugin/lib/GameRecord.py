from typing import Any

from zhenxun.services.log import logger

from .ByteReader import ByteReader
from .LevelRecord import LevelRecord


class GameRecord:
    """游戏记录"""

    name: str = "gameRecord"
    version: int = 1

    def __init__(self, data: bytes) -> None:
        """
        初始化

        :param data: 二进制数据
        """
        self.Record: dict[str, list[LevelRecord | None]] = {}
        self.data = data

    async def init(self, song_data: list[Any]) -> None:
        """
        初始化记录

        :param song_data: 歌曲数据
        """
        try:
            reader = ByteReader(self.data)
            if reader.getByte() != self.version:
                logger.error("版本号已更新，请更新PhigrosLibrary。")
                raise ValueError("版本号已更新")

            while reader.remaining() > 0:
                key = reader.getString()
                song: list[LevelRecord | None] = []
                for _ in range(4):
                    if reader.getVarInt() == 1:
                        record = LevelRecord()
                        record.fc = bool(reader.getVarInt())
                        record.score = reader.getVarInt()
                        record.acc = reader.getFloat()
                        song.append(record)
                    else:
                        song.append(None)
                self.Record[key] = song

        except Exception as e:
            logger.error("初始化记录失败", e=e)
            raise ValueError("初始化记录失败") from e
