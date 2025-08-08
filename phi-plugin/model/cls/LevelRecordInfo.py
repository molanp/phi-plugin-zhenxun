from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from ...utils import Rating
from ..fCompute import fCompute
from ..getInfo import getInfo


class LevelRecordInfo(BaseModel):
    fc: bool = False
    """是否 Full Combo"""
    score: int = 0
    """得分"""
    acc: float = 0
    """准确率"""
    id: str = ""
    """曲目id"""
    rank: str = ""
    """Level"""
    Rating: str = ""
    """评分等级"""
    song: str = ""
    """曲名"""
    illustration: str | Path = ""
    """曲绘链接"""
    difficulty: float = 0.0
    """难度"""
    rks: float = 0.0
    """等效RKS"""
    suggest: str = ""
    """推分建议"""
    num: int = 0
    """是 Best 几"""
    date: datetime = datetime.now()
    """更新时间(iso)"""

    @classmethod
    async def init(cls, data: dict, id: str, rank: int | str) -> "LevelRecordInfo":
        """
        :param data: 原始数据
        :param id: 曲目id
        :param rank: 难度
        """
        data_ = {"fc": data["fc"], "score": data["score"], "acc": data["acc"], "id": id}
        song = getInfo.idgetsong(id)
        info = await getInfo.info(song, True) if song else None
        data_["rank"] = (
            getInfo.Level[rank] if isinstance(rank, int) else rank
        )  # EZ HD IN AT LEGACY
        data_["Rating"] = Rating(data_["score"], data_["fc"])  # V S A
        if info is None:
            data_["song"] = id
            data_["difficulty"] = 0
            data_["rks"] = 0
            return cls(**data_)
        data_["song"] = info.song  # 曲名
        data_["illustration"] = await getInfo.getill(data_["song"])  # 曲绘链接
        difficulty = (
            info.chart[data_["rank"]].difficulty
            if data_["rank"] in info.chart
            else None
        )
        if info.chart and difficulty:
            assert isinstance(difficulty, float)
            data_["difficulty"] = difficulty  # 难度
            data_["rks"] = fCompute.rks(data_["acc"], data_["difficulty"])  # 等效rks
        else:
            data_["difficulty"] = 0
            data_["rks"] = 0
        return cls(**data_)

    @classmethod
    def to_tuple(cls) -> tuple[float, int, datetime, bool]:
        return (
            cls.acc,
            cls.score,
            cls.date,
            cls.fc,
        )
