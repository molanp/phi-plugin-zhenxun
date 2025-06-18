from datetime import datetime

from ...utils import Date, Rating
from ..fCompute import fCompute
from ..getInfo import getInfo


class scoreHistory:
    @staticmethod
    def create(acc: float, score: int, date: datetime, fc: bool):
        """生成成绩记录数组"""
        return [round(acc, 4), score, date, fc]

    @staticmethod
    async def extend(
        songsid: str,
        level: str,
        now: list | tuple,
        old: list | tuple | None = None,
    ):
        """
        扩充信息

        :param songsid: 曲目id
        :param level: 难度
        """
        song = await getInfo.idgetsong(songsid) or songsid
        if isinstance(now, tuple):
            now = list(now)
        if isinstance(old, tuple):
            old = list(old)
        now[0] = int(now[0])
        now[1] = int(now[1])
        if old:
            old[0] = int(old[0])
            old[1] = int(old[1])
        info = await getInfo.info(song, True)
        if not info or not info.chart.get(level) or not info.chart[level].difficulty:
            # 无难度信息
            return {
                "song": song,
                "rank": level,
                "illustration": await getInfo.getill(song),
                "Rating": Rating(now[1], now[3]),
                "acc_new": now[0],
                "acc_old": old[0] if old else None,
                "score_new": now[1],
                "score_old": old[1] if old else None,
                "date_new": now[2],
                "date_old": Date(old[2]) if old else None,
            }
        # 有难度信息
        difficulty = info.chart[level].difficulty
        assert isinstance(difficulty, float)
        return {
            "song": song,
            "rank": level,
            "illustration": await getInfo.getill(song),
            "Rating": Rating(now[1], now[3]),
            "rks_new": fCompute.rks(now[0], difficulty),
            "rks_old": (fCompute.rks(old[0], difficulty) if old is not None else None),
            "acc_new": now[0],
            "acc_old": old[0] if old else None,
            "score_new": now[1],
            "score_old": old[1] if old else None,
            "date_new": now[2],
            "date_old": Date(old[2]) if old else None,
        }

    @staticmethod
    def open(data: list) -> dict:
        """
        展开信息

        :param data: 历史成绩
        """
        return {
            "acc": data[0],
            "score": data[1],
            "date": Date(data[2]),
            "fc": data[3],
        }

    @staticmethod
    def date(data: tuple[float, int, datetime, bool]) -> datetime:
        """
        获取该成绩记录的日期

        :param data: 成绩记录
        :return: 该成绩的日期
        """
        return data[2]
