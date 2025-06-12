from typing import TypedDict


class Chart(TypedDict):
    id: str
    """idString"""
    rank: str
    """Level"""
    charter: str
    difficulty: int
    tap: float
    drag: float
    hold: float
    flick: float
    combo: float
    maxTime: float
    distribution: list[float]
