from typing import Any

from zhenxun.services.log import logger

from .ByteReader import ByteReader
from .LevelRecord import LevelRecord


class GameRecord:
    """游戏记录"""

    name: str = "gameRecord"
    version: int = 1

    def __init__(self, data: bytes | str) -> None:
        """
        初始化

        :param data: 二进制数据
        """
        self.Record: dict[str, list[LevelRecord | None]] = {}
        self.data = ByteReader(data)

    async def init(self, song_data: list[Any]) -> None:
        """
        初始化记录

        :param song_data: 歌曲数据
        """
        try:
            self.songsnum =self.data.getVarInt()
            # if self.data.getByte() != self.version:
            #     print(self.data.getByte(),"/",GameRecord.version,"/", self.version)
            #     logger.error("[GameRecord]版本号已更新，请更新PhigrosLibrary。")
            #     raise ValueError("版本号已更新")

            while self.data.remaining() > 0:
                key = self.data.getString()
                song: list[LevelRecord | None] = []
                for _ in range(4):
                    if self.data.getVarInt() == 1:
                        record = LevelRecord()
                        record.fc = bool(self.data.getVarInt())
                        record.score = self.data.getVarInt()
                        record.acc = self.data.getFloat()
                        song.append(record)
                    else:
                        song.append(None)
                self.Record[key] = song

        except Exception as e:
            logger.error("初始化记录失败", "phi-plugin", e=e)
            raise ValueError("初始化记录失败") from e
