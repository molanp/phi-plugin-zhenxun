from ..get_info import getInfo


class LevelRecordInfo:
    def __init__(self, data: dict, id: str, rank: str):
        self.fc = data.get("fc", False)
        self.score = data.get("score", 0)
        self.acc = data.get("acc", 0.0)

        info = getInfo.info(id, original=True)

        if not info:
            return

        self.rank = getInfo.Level[rank]  # AT IN HD EZ LEGACY
        self.song = info.song  # 曲名
        self.illustration = getInfo.getill(self.song)  # 曲绘链接

        # 计算等效rks
        self.Rating = self._compute_rating()  # V S A

        # 处理难度和rks
        if info.chart and info.chart.get(self.rank, {}).get("difficulty"):
            difficulty = info.chart[self.rank]["difficulty"]
            self.difficulty = difficulty
            self.rks = self._compute_rks(difficulty)
        else:
            self.difficulty = 0.0
            self.rks = 0.0

    def _compute_rating(self) -> str:
        """计算评级（V/S/A等）"""
        score = self.score
        fc = self.fc
        if score == 1000000:
            return "phi"
        elif fc:
            return "FC"
        elif score == 0:
            return "NEW"
        elif score < 700000:
            return "F"
        elif 700000 <= score < 820000:
            return "C"
        elif 820000 <= score < 880000:
            return "B"
        elif 880000 <= score < 920000:
            return "A"
        elif 920000 <= score < 960000:
            return "S"
        else:
            return "V"

    def _compute_rks(self, difficulty: float) -> float:
        """计算等效rks"""
        if self.acc == 100:
            return difficulty
        elif self.acc < 70:
            return 0.0
        else:
            return difficulty * (((self.acc - 55) / 45) ** 2)
