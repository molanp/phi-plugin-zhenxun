class SongLevel:
    """歌曲等级"""

    def __init__(
        self,
        id_: str = "",
        level: int = 0,
        s: int = 0,
        a: float = 0.0,
        c: bool = False,
        difficulty: float = 0.0,
        rks: float = 0.0,
    ) -> None:
        self.id: str = id_
        self.level: int = level
        self.s: int = s
        self.a: float = a
        self.c: bool = c
        self.difficulty: float = difficulty
        self.rks: float = rks

    def set(self, id_: str, level: int, fc: bool, difficulty: float) -> None:
        """
        设置歌曲等级信息
        :param id_: 歌曲ID
        :param level: 难度等级
        :param fc: 是否FC
        :param difficulty: 定数
        """
        self.id = id_
        self.level = level
        self.c = fc
        self.difficulty = difficulty

    def __str__(self) -> str:
        return f'{{"songId":"{self.id}","level":"{self.level}","score":{self.s},"acc":{self.a},"fc":{self.c},"定数":{self.difficulty:.1f},"单曲rks":{self.rks}}}'

    @staticmethod
    def compare(a: "SongLevel", b: "SongLevel") -> float:
        """
        比较两个歌曲等级
        :param a: 第一个歌曲等级
        :param b: 第二个歌曲等级
        :return: b.rks - a.rks
        """
        try:
            return b.rks - a.rks
        except Exception:
            return 0.0
