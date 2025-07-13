from zhenxun.services.log import logger

from .ByteReader import ByteReader
from .LevelRecord import LevelRecord
from .Util import Util


class GameRecord:
    """游戏记录"""

    name: str = "gameRecord"
    version: int = 1

    def __init__(self, data: bytes) -> None:
        """
        初始化

        :param data: 二进制数据
        """
        self.name: str = "gameRecord"
        self.version: int = 1
        self.Record: dict[str, list[LevelRecord]] = {}
        self.data = ByteReader(data)
        try:
            self.songsnum = self.data.getVarInt()

            while self.data.remaining() > 0:
                key = self.data.getString()
                self.data.skipVarInt()
                length = self.data.getByte()
                fc = self.data.getByte()
                song = {}
                for level in range(4):
                    if Util.getBit(length, level):
                        score = self.data.getInt()
                        acc = self.data.getFloat()
                        if 0 <= score <= 1000000 and 0 <= acc <= 100:
                            song[level] = LevelRecord()
                            song[level].score = score
                            song[level].acc = acc
                            song[level].fc = (
                                True
                                if (
                                    song[level].score == 1000000
                                    and song[level].acc == 100
                                )
                                else Util.getBit(fc, level)
                            )
                if song:
                    self.Record[key] = list(song.values())
        except Exception as e:
            logger.error("[GameRecord]初始化记录失败", "phi-plugin", e=e)
            raise ValueError("[GameRecord]初始化记录失败") from e
