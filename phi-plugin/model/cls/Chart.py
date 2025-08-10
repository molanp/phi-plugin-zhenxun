from pydantic import BaseModel

from ..constNum import LevelItem


class Chart(BaseModel):
    id: str | None = None
    """idString"""
    rank: LevelItem | None = None
    """Level"""
    charter: str = ""
    """谱师"""
    difficulty: float = 0
    """定数"""
    tap: int = 0
    drag: int = 0
    hold: int = 0
    flick: int = 0
    combo: int = 0
    """物量"""
    maxTime: float = 0
    distribution: list[list[float]] = []
    is_new: bool = False
