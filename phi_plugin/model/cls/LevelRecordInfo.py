from datetime import datetime
from pathlib import Path
from typing import TypedDict

from ...utils import Date
from ..fCompute import fCompute
from ..getInfo import getInfo


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


class LevelData(TypedDict):
    fc: bool
    """是否 Full Combo"""
    score: int
    """得分"""
    acc: float
    """准确率"""


class LevelRecordInfo:
    fc: bool
    """是否 Full Combo"""
    score: int
    """得分"""
    acc: float
    """准确率"""
    id: str
    """曲目id"""
    rank: str
    """Level"""
    Rating: str
    """评分等级"""
    song: str
    """曲名"""
    illustration: str | Path
    """曲绘链接"""
    difficulty: int
    """难度"""
    rks: float
    """等效RKS"""
    suggest: str
    """推分建议"""
    num: int
    """是 Best 几"""
    date: str | datetime
    """更新时间(iso)"""

    async def init(
        self, data: LevelData, id: str, rank: int | str
    ) -> "LevelRecordInfo":
        """
        :param data: 原始数据
        :param id: 曲目id
        :param rank: 难度
        """
        self.fc = data["fc"]
        self.score = data.get("score", 0)
        self.acc = data["acc"]
        self.id = id
        song = getInfo.idgetsong(id)
        info = await getInfo.info(song, True) if song else None
        self.rank = (
            getInfo.Level[rank] if isinstance(rank, int) else rank
        )  # AT IN HD EZ LEGACY
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

    def to_tuple(self) -> tuple[float, int, datetime, bool]:
        return (
            self.acc,
            self.score,
            Date(self.date),
            self.fc,
        )
