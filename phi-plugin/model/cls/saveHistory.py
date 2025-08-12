from datetime import datetime
import math
from typing import Any

from ...utils import Date, to_dict
from ..constNum import MAX_DIFFICULTY, Level, LevelItem
from ..fCompute import fCompute
from .common import Save
from .LevelRecordInfo import LevelRecordInfo
from .models import HistoryModel, RecordModel, dataLine, rksLine, rksLineWithdataLine


def merge(m: list, n: list) -> list:
    """
    数组合并按照 date 排序并去重

    :param m: 第一个数组
    :param n: 第二个数组
    :return: 合并后的数组
    """
    t = m + n
    # 按照 date 排序
    t.sort(key=lambda x: x["date"])

    i = 1
    while i < len(t) - 1:
        # 因绘制折线图需要，需要保留同一值两端
        if checkValue(t[i]["value"], t[i - 1]["value"]) and checkValue(
            t[i]["value"], t[i + 1]["value"]
        ):
            del t[i]
        else:
            i += 1
    return t


def createHistory(
    acc: float, score: int, date: datetime, fc: bool
) -> tuple[float, int, datetime, bool]:
    """
    创建历史记录

    :param acc: 准确度
    :param score: 分数
    :param date: 日期
    :param fc: 是否全连
    :return: 历史记录列表
    """
    return (round(acc, 4), score, date, fc)


def openHistory(data: list | tuple) -> HistoryModel:
    """
    展开信息

    :param data:历史成绩
    """
    return HistoryModel(
        **{
            "acc": data[0],
            "score": data[1],
            "date": Date(data[2]),
            "fc": data[3],
        }
    )


def checkValue(a: Any, b: Any):
    """
    比较两个数组

    :param a: 第一个值
    :param b: 第二个值
    :return: bool
    """
    if not isinstance(a, list):
        return a == b

    if a is None or b is None:
        return False

    return all(a[i] == b[i] for i in range(len(a)))


class saveHistory:
    scoreHistory: dict[
        str,
        dict[
            LevelItem,
            list[tuple[float, int, datetime, bool]],
        ],
    ]
    """
    歌曲成绩记录
    ```
    {
        "songId": { - 曲目id
            "dif": [ - diff 难度 ["EZ", "HD", "IN", "AT", "LEGACY"]
                [acc:round(float, 4), score: int, date: datetime, fc: bool],
                [acc, score, date, fc],
                ...
            ]
        }
    }
    """
    data: list[RecordModel]
    """data货币变更记录"""
    rks: list[RecordModel]
    """rks变更记录"""
    challengeModeRank: list[RecordModel]
    """课题模式成绩"""
    version: float | None
    """
    历史记录版本号

    - v1.0,取消对当次更新内容的存储，取消对task的记录，更正scoreHistory
    - v1.1,更正scoreHistory
    - v2,由于曲名错误，删除所有记录，曲名使用id记录
    - v3,添加课题模式历史记录
    """
    dan: list[dict[str, Any]]
    """民间考核"""

    def __init__(self, data: dict[str, Any]):
        self.scoreHistory = data.get("scoreHistory") or {}
        self.data = [RecordModel(**i) for i in data.get("data") or []]
        self.rks = [RecordModel(**i) for i in data.get("rks") or []]
        self.challengeModeRank = [
            RecordModel(**i) for i in data.get("challengeModeRank") or []
        ]
        self.version = data.get("version") or None
        self.dan = data.get("dan") or []

        # 检查版本
        if not self.version or self.version < 2:
            if self.scoreHistory:
                for i in self.scoreHistory:
                    if ".0" not in i:
                        self.scoreHistory = {}
                    break
            self.version = 2
        if self.version < 3:
            self.challengeModeRank = []
            self.version = 3

    def add(self, data: "saveHistory") -> "saveHistory":
        """
        合并记录

        :param saveHistory data: 另一个 History 存档
        """
        self.data = merge(self.data, data.data)
        self.rks = merge(self.rks, data.rks)
        self.challengeModeRank = merge(self.challengeModeRank, data.challengeModeRank)
        for song in data.scoreHistory:
            if not self.scoreHistory.get(song):
                self.scoreHistory[song] = {}
            for dif in data.scoreHistory.get(song, {}):
                if self.scoreHistory[song] and self.scoreHistory[song].get(dif):
                    self.scoreHistory[song][dif] = (
                        self.scoreHistory[song][dif] + data.scoreHistory[song][dif]
                    )
                    self.scoreHistory[song][dif].sort(key=lambda x: openHistory(x).date)
                else:
                    self.scoreHistory[song][dif] = data.scoreHistory[song][dif]
                i = 1
                while i < len(self.scoreHistory[song][dif]):
                    last = openHistory(self.scoreHistory[song][dif][i - 1])
                    now = openHistory(self.scoreHistory[song][dif][i])
                    if (
                        last.score == now.score
                        and last.acc == now.acc
                        and last.fc == now.fc
                    ):
                        del self.scoreHistory[song][dif][i]
                    else:
                        i += 1
        return self

    def update(self, save: Save):
        """
        检查新存档中的变更并记录

        :param Save save: 新存档
        """
        # 更新单曲成绩
        for id in save.gameRecord:
            if self.scoreHistory.get(id) is None:
                self.scoreHistory[id] = {}
                for lv, record in enumerate(save.gameRecord.get(id, [])):
                    # 提取成绩
                    now = record
                    if not now:
                        continue
                    now.date = save.saveInfo.modifiedAt.iso
                    level = Level[lv]
                    # 本地无记录
                    if level not in self.scoreHistory[id]:
                        self.scoreHistory[id][level] = [
                            createHistory(
                                now.acc,
                                now.score,
                                save.saveInfo.modifiedAt.iso,
                                now.fc,
                            )
                        ]
                        continue
                    # 本地记录日期为递增
                    for i in range(len(self.scoreHistory[id][level]) - 1, -1, -1):
                        # 第 i 项记录
                        old = openHistory(self.scoreHistory[id][level][i])
                        # 日期完全相同则认为已存储
                        if (
                            old.score == now.score
                            and old.acc == now.acc
                            and old.fc == now.fc
                        ):
                            # 标记已处理
                            now = None
                            break
                        # 找到第一个日期小于新成绩的日期
                        if old.date < now.date and (
                            old.acc != round(now.acc, 4)
                            or old.score != now.score
                            or old.fc != now.fc
                        ):
                            self.scoreHistory[id][level].insert(
                                i,
                                createHistory(
                                    now.acc,
                                    now.score,
                                    save.saveInfo.modifiedAt.iso,
                                    now.fc,
                                ),
                            )
                            # 标记已处理
                            now = None
                            break
                    # 未被处理，有该难度记录，说明日期早于本地记录
                    if now:
                        self.scoreHistory[id][level].insert(
                            0,
                            createHistory(
                                now.acc,
                                now.score,
                                save.saveInfo.modifiedAt.iso,
                                now.fc,
                            ),
                        )
                    # 查重
                    j = 1
                    while j < len(self.scoreHistory[id][level]):
                        last = openHistory(self.scoreHistory[id][level][j - 1])
                        now = openHistory(self.scoreHistory[id][level][j])
                        if (
                            last.score == now.score
                            and last.acc == now.acc
                            and last.fc == now.fc
                        ):
                            del self.scoreHistory[id][level][j]
                        else:
                            j += 1
        # 更新rks记录
        for i in range(len(self.rks) - 1, -1, -1):
            if save.saveInfo.modifiedAt.iso > self.rks[i].date:
                if (
                    i + 1 >= len(self.rks)
                    or self.rks[i].value != save.saveInfo.summary.rankingScore
                    or self.rks[i + 1].value != save.saveInfo.summary.rankingScore
                ):
                    self.rks.insert(
                        i + 1,
                        RecordModel(
                            **{
                                "date": save.saveInfo.modifiedAt.iso,
                                "value": save.saveInfo.summary.rankingScore,
                            }
                        ),
                    )
                break
        if not self.rks:
            self.rks.append(
                RecordModel(
                    **{
                        "date": save.saveInfo.modifiedAt.iso,
                        "value": save.saveInfo.summary.rankingScore,
                    }
                )
            )
        # 更新data记录
        for i in range(len(self.data) - 1, -1, -1):
            if save.saveInfo.modifiedAt.iso > self.data[i].date:
                if i + 1 >= len(self.data) or (
                    checkValue(
                        self.data[i].value, getattr(save.gameProgress, "money", [0])
                    )
                    and checkValue(
                        self.data[i + 1].value if i + 1 < len(self.data) else None,
                        getattr(save.gameProgress, "money", [0]),
                    )
                ):
                    self.data.insert(
                        i + 1,
                        RecordModel(
                            **{
                                "date": save.saveInfo.modifiedAt.iso,
                                "value": getattr(save.gameProgress, "money", [0]),
                            }
                        ),
                    )
                break
        if not self.data:
            self.data.append(
                RecordModel(
                    **{
                        "date": save.saveInfo.modifiedAt.iso,
                        "value": getattr(save.gameProgress, "money", [0]),
                    }
                )
            )
        # 更新课题模式记录
        for i in range(len(self.challengeModeRank) - 1, -1, -1):
            if save.saveInfo.modifiedAt.iso > self.challengeModeRank[i].date:
                clg = save.saveInfo.summary.challengeModeRank
                if clg != self.challengeModeRank[i].value and (
                    i + 1 > len(self.challengeModeRank)
                    or self.challengeModeRank[i + 1].value != clg
                ):
                    self.challengeModeRank.insert(
                        i + 1,
                        RecordModel(
                            **{
                                "date": save.saveInfo.modifiedAt.iso,
                                "value": save.saveInfo.summary.challengeModeRank,
                            }
                        ),
                    )
                break
        if not self.challengeModeRank:
            self.challengeModeRank.append(
                RecordModel(
                    **{
                        "date": save.saveInfo.modifiedAt.iso,
                        "value": save.saveInfo.summary.challengeModeRank,
                    }
                )
            )

    def getSongsLastRecord(
        self, id: str
    ) -> dict[str, list[tuple[float, int, datetime, bool]]]:
        """
        获取歌曲最新的历史记录

        :param str id: 曲目id
        """
        t = {**self.scoreHistory.get(id, {})}
        for level in t:
            if records := t[level]:
                # 获取最新的一条记录并展开信息
                last_record = openHistory(records[-1])
                # 创建 LevelRecordInfo 实例
                level_info = LevelRecordInfo.init(
                    to_dict(last_record), id=id, rank=level
                )
                # 保留原始日期
                level_info.date = last_record.date
                t[level] = [level_info.to_tuple()]
            else:
                t[level] = []
        return t

    def getRksAndDataLine(self) -> rksLineWithdataLine:
        """折线图数据"""
        rks = self.getRksLine()
        data = self.getDataLine()
        return rksLineWithdataLine.from_models(rks, data)

    def getRksLine(self) -> rksLine:
        rks_range: list[float] = [MAX_DIFFICULTY, 0]
        rks_date: list[int] = []
        rks_history: list[list[float]] = []
        if user_rks_data := self.rks:
            rks_date = [int(user_rks_data[0].date.timestamp() * 1000), 0]
            rks_history_: list[RecordModel] = []
            for i, _ in enumerate(user_rks_data):
                user_rks_data[i].date = user_rks_data[i].date
                if (
                    i <= 1
                    or user_rks_data[i].value
                    != rks_history_[len(rks_history_) - 2].value
                ):
                    rks_history_.append(user_rks_data[i])
                    rks_range[0] = min(rks_range[0], user_rks_data[i].value)
                    rks_range[1] = max(rks_range[1], user_rks_data[i].value)
                else:
                    rks_history_[-1].date = user_rks_data[i].date
                rks_date[1] = int(user_rks_data[i].date.timestamp() * 1000)
            for i, _ in enumerate(rks_history_):
                if i + 1 >= len(rks_history_):
                    break
                x1 = fCompute.range(
                    int(rks_history_[i].date.timestamp() * 1000), rks_date
                )
                y1 = fCompute.range(rks_history_[i].value, rks_range)
                x2 = fCompute.range(
                    int(rks_history_[i + 1].date.timestamp() * 1000), rks_date
                )
                y2 = fCompute.range(rks_history_[i + 1].value, rks_range)
                rks_history.append([x1, y1, x2, y2])
            if not rks_history:
                rks_history.append([0, 50, 100, 50])
        return rksLine(
            **{
                "rks_history": rks_history,
                "rks_range": rks_range,
                "rks_date": rks_date,
            }
        )

    def getDataLine(self) -> dataLine:  # sourcery skip: extract-method
        data_range: list[float | str] = [1e9, 0]
        data_date: list[int] = []
        data_history: list[list[float]] = []
        if user_data_data := self.data:
            data_date = [int(user_data_data[0].date.timestamp() * 1000), 0]
            data_history_: list[RecordModel] = []
            for i, _ in enumerate(user_data_data):
                value = user_data_data[i].value
                assert isinstance(value, tuple)
                user_data_data[i].value = (
                    ((value[4] * 1024 + value[3]) * 1024 + value[2]) * 1024 + value[1]
                ) * 1024 + value[0]
                user_data_data[i].date = user_data_data[i].date
                if (
                    i <= 1
                    or len(data_history_) < 2
                    or user_data_data[i].value
                    != data_history_[len(data_history_) - 2].value
                ):
                    data_history_.append(user_data_data[i])
                    data_range[0] = min(data_range[0], user_data_data[i].value)
                    data_range[1] = max(data_range[1], user_data_data[i].value)
                else:
                    data_history_[len(user_data_data) - 1].date = user_data_data[i].date
                data_date[1] = int(user_data_data[i].date.timestamp() * 1000)
            for i, _ in enumerate(data_history_):
                if i + 1 >= len(data_history_):
                    break
                x1 = fCompute.range(data_history_[i].date.timestamp() * 1000, data_date)
                y1 = fCompute.range(data_history_[i].value, data_range)
                x2 = fCompute.range(
                    data_history_[i + 1].date.timestamp() * 1000, data_date
                )
                y2 = fCompute.range(data_history_[i + 1].value, data_range)
                data_history.append([x1, y1, x2, y2])
            unit = ["KiB", "MiB", "GiB", "TiB", "Pib"]
            for i in range(1, 5):
                assert isinstance(data_range[0], int)
                if math.floor(data_range[0] / (math.pow(1024, i))) < 1024:
                    data_range[0] = (
                        f"{math.floor(data_range[0] / (math.pow(1024, i)))}{unit[i]}"
                    )
            for i in range(1, 5):
                assert isinstance(data_range[1], int)
                if math.floor(data_range[1] / (math.pow(1024, i))) < 1024:
                    data_range[1] = (
                        f"{math.floor(data_range[1] / (math.pow(1024, i)))}{unit[i]}"
                    )
        return dataLine(
            **{
                "data_history": data_history,
                "data_range": data_range,
                "data_date": data_date,
            }
        )
