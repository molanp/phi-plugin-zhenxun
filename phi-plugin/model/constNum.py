from typing import Literal

Level: list[
    Literal[
        "EZ",
        "HD",
        "IN",
        "AT",
        "LEGACY",
    ]
] = [
    "EZ",
    "HD",
    "IN",
    "AT",
    "LEGACY",
]
"""难度映射"""
LevelNum: dict[
    Literal[
        "EZ",
        "HD",
        "IN",
        "AT",
        "LEGACY",
    ],
    int,
] = {
    "EZ": 0,
    "HD": 1,
    "IN": 2,
    "AT": 3,
    "LEGACY": 4,
}

MAX_DIFFICULTY: float = 17.6
"""最大难度"""
