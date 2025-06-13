from pydantic import BaseModel


class Chart(BaseModel):
    id: str = ""
    """idString"""
    rank: str = ""
    """Level"""
    charter: str = ""
    difficulty: int
    tap: int
    drag: int
    hold: int
    flick: int
    combo: int
    maxTime: int = 0
    distribution: list[float] = []
    is_new: bool = False
