from datetime import datetime
from typing import Literal

from ...utils import Date
from ..fCompute import fCompute
from ..getInfo import getInfo


def Rating(score: int, fc: bool):
    if fc:
        return "FC"
    elif score >= 1000000:
        return "phi"
    elif score < 700000:
        return "F"
    elif score < 820000:
        return "C"
    elif score < 880000:
        return "B"
    elif score < 920000:
        return "A"
    elif score < 960000:
        return "S"
    else:
        return "V"


class scoreHistory:
    @staticmethod
    def create(acc: float, score: int, date: datetime, fc: bool):
        """生成成绩记录数组"""
        return [round(acc, 4), score, date, fc]

    @staticmethod
    async def extend(
        songsid: str,
        level: Literal["EZ", "HD", "IN", "AT", "LEGACY"],
        now: list,
        old: list | None = None,
    ):
        """
        扩充信息

        :param songsid: 曲目id
        :param level: 难度
        """
        song = getInfo.idgetsong(songsid) or songsid
        now[0] = int(now[0])
        now[1] = int(now[1])
        if old:
            old[0] = int(old[0])
            old[1] = int(old[1])
        info = await getInfo.info(song, True)
        if info and info.chart.get(level) and info.chart[level].difficulty:
            # 有难度信息
            return {
                "song": song,
                "rank": level,
                "illustration": await getInfo.getill(song),
                "Rating": Rating(now[1], now[3]),
                "rks_new": fCompute.rks(now[0], info.chart[level].difficulty),
                "rks_old": (
                    fCompute.rks(old[0], info.chart[level].difficulty)
                    if old is not None
                    else None
                ),
                "acc_new": now[0],
                "acc_old": old[0] if old else None,
                "score_new": now[1],
                "score_old": old[1] if old else None,
                "date_new": Date(now[2]),
                "date_old": Date(old[2]) if old else None,
            }
        else:
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
                "date_new": Date(now[2]),
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
    def date(data: list) -> datetime | None:
        """
        获取该成绩记录的日期

        :param data: 成绩记录
        :return: 该成绩的日期
        """
        return Date(data[2])
