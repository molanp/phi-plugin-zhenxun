import struct
from zhenxun.services.log import logger

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
        self.name: str = "gameRecord"
        self.version: int = 1
        self.Record: dict[str, list[LevelRecord]] = {}
        levels = {
            "EZ": 1,
            "HD": 2,
            "IN": 4,
            "AT": 8,
        }
        try:
            data = data[1:]
            pos = int(data[0] < 0) + 1
            while pos < len(data):
                name_length = data[pos]
                pos += 1
                if name_length == 1:
                    continue
                name = data[pos : (pos + name_length)]
                name = name.decode("utf-8")

                pos += name_length
                score_length = data[pos]
                pos += 1

                score = data[pos : (pos + score_length)]
                pos += score_length

                has_score = score[0]
                full_combo = score[1]
                score_pos = 2

                song = {}

                for level, digit in levels.items():
                    if (has_score & digit) == digit:
                        song[level] = LevelRecord(
                            **{
                                "score": int.from_bytes(
                                    score[score_pos : (score_pos + 4)],
                                    byteorder="little",
                                    signed=True,
                                ),
                                "acc": struct.unpack(
                                    "<f", score[(score_pos + 4) : (score_pos + 8)]
                                )[0],
                                "fc": (full_combo & digit) == digit,
                            }
                        )
                if song:
                    self.Record[name] = list(song.values())
        except Exception as e:
            logger.error("[GameRecord]初始化记录失败", "phi-plugin", e=e)
            raise ValueError("[GameRecord]初始化记录失败") from e
