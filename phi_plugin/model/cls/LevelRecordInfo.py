from pathlib import Path

from ..fCompute import fCompute
from ..getInfo import getInfo


class LevelRecordInfo:
    fc: bool
    score: int | None
    acc: float
    id: str
    rank: str
    Rating: str
    song: str
    illustration: str | Path
    difficulty: int
    rks: float
    suggest: str = ""
    num: int = 0

    async def init(self, data: dict, id: str, rank: int) -> "LevelRecordInfo":
        """
        :param data: 原始数据
        :param id: 曲目id
        :param rank: 难度
        """
        self.fc = data["fc"]
        self.score = data.get("score")
        self.acc = data["acc"]
        self.id = id
        info = await getInfo.info(getInfo.idgetsong(id), True)
        self.rank = getInfo.Level[rank]  # AT IN HD EZ LEGACY
        self.Rating = Rating(self.score, self.fc)  # V S A
        if info is None:
            self.song = id
            self.difficulty = 0
            self.rks = 0
            return self
        self.song = info.song  # 曲名
        self.illustration = await getInfo.getill(self.song)  # 曲绘链接
        if info.chart and info.chart[self.rank].difficulty:
            self.difficulty = info.chart[self.rank].difficulty  # 难度
            self.rks = fCompute.rks(self.acc, self.difficulty)  # 等效rks
        else:
            self.difficulty = 0
            self.rks = 0
        return self


def Rating(score: int | None, fc: bool):
    if score is None:
        return "NEW"
    elif fc:
        return "FC"
    elif score >= 1000000:
        return "phi"
    elif score < 700000:
        return "F"
    elif score < 820000:
        return "C"
    elif score < 880000:
        return "B"
    elif score < 920000:
        return "A"
    elif score < 960000:
        return "S"
    else:
        return "V"
