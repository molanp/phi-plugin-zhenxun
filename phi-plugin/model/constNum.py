from typing import Literal

LevelItem = Literal[
    "EZ",
    "HD",
    "IN",
    "AT",
    "LEGACY",
]

Level: list[LevelItem] = [
    "EZ",
    "HD",
    "IN",
    "AT",
    "LEGACY",
]
"""难度列表"""

LevelNum: dict[LevelItem, int] = {
    "EZ": 0,
    "HD": 1,
    "IN": 2,
    "AT": 3,
    "LEGACY": 4,
}
"""难度映射"""

MAX_DIFFICULTY: float = 17.6
"""最大难度"""
