from pydantic import BaseModel


class Chart(BaseModel):
    id: str | None
    """idString"""
    rank: str = ""
    """allLevelKind"""
    charter: str
    difficulty: int
    tap: float
    drag: float
    hold: float
    flick: float
    combo: float
    maxTime: float
    distribution: list[float]
