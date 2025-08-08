from datetime import datetime
from typing import Any
from typing_extensions import Self

from nonebot.compat import field_validator
from pydantic import BaseModel

from ...utils import Date, to_dict


class RecordModel(BaseModel):
    date: datetime
    value: Any

    @field_validator("date")
    @classmethod
    def parse_iso(cls, value: Any) -> datetime:
        """自动将字符串转换为datetime对象"""
        return Date(value)


class LevelData(BaseModel):
    fc: bool = False
    """是否 Full Combo"""
    score: int = 0
    """得分"""
    acc: float = 0
    """准确率"""


class HistoryModel(LevelData):
    date: datetime
    """日期"""


class rksLine(BaseModel):
    rks_history: list[list[float]]
    """list[x1, y1, x2, y2]"""
    rks_range: list[float]
    """[min, max]"""
    rks_date: list[int]
    """[min, max]"""


class dataLine(BaseModel):
    data_history: list[list[float]]
    """list[x1, y1, x2, y2]"""
    data_range: list[float | str]
    """[min, max], 如果数字大于1024，则转为KiB，MiB，GiB，TiB，Pib"""
    data_date: list[int]
    """[min, max]"""


class rksLineWithdataLine(rksLine, dataLine):
    @classmethod
    def from_models(cls, rks: rksLine, data: dataLine) -> Self:
        """从两个模型实例创建合并实例"""
        merged_data = {**to_dict(rks), **to_dict(data)}
        return cls(**merged_data)
