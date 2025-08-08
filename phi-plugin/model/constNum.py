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

LevelNum: dict[int, LevelItem] = {
    0: "EZ",
    1: "HD",
    2: "IN",
    3: "AT",
    4: "LEGACY",
}
"""难度映射"""

MAX_DIFFICULTY: float = 17.6
"""最大难度"""
