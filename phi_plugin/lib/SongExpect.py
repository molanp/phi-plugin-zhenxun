class SongExpect:
    """歌曲期望"""

    def __init__(self, id_: str, level: int, acc: float, expect: float) -> None:
        self.id: str = id_
        self.level: int = level
        self.acc: float = acc
        self.expect: float = expect
        self.rks: float = (acc - 55) / 45
        self.rks *= self.rks * expect

    def __str__(self) -> str:
        return f'{{"songId":"{self.id}","level":{self.level},"acc":{self.acc},"expect":{self.expect},"rks":{self.rks}}}'
