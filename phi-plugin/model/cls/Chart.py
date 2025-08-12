from pydantic import BaseModel

from ..constNum import LevelItem


class Chart(BaseModel):
    """谱面信息"""

    id: str = ""
    """曲目ID(一般包含.0)"""
    rank: LevelItem | str = ""
    """Level"""
    charter: str = ""
    """谱师"""
    difficulty: float | str = 0.0
    """定数"""
    tap: int = 0
    drag: int = 0
    hold: int = 0
    flick: int = 0
    combo: int = 0
    """物量"""
    maxTime: float = 0
    distribution: list[list[float]] = []


class UpdateChart(BaseModel):
    """谱面更新信息"""

    difficulty: list[float]
    """定数更新信息"""
    tap: list[float]
    drag: list[float]
    hold: list[float]
    flick: list[float]
    combo: list[float]
    """物量更新信息"""
    isNew: bool
    """是否全新"""
