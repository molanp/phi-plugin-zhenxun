import copy
from datetime import datetime
import math

from zhenxun.services.log import logger

from ..fCompute import fCompute
from ..getInfo import getInfo
from ..getRksRank import getRksRank
from ..makeRequest import OriSave
from .LevelRecordInfo import LevelRecordInfo


class Save:
    session: str
    apiId: str
    saveInfo: dict
    saveUrl: str
    Recordvr: str
    gameProgress: dict | None
    gameuser: dict | None
    gameRecord: dict[str, list["LevelRecordInfo | None"]]
    sortedRecord: list["LevelRecordInfo"] | None = None
    B19List: dict[str, list["LevelRecordInfo"] | float]
    b19_rks: float | None = None

    async def constructor(self, data: OriSave, ignore: bool = False) -> "Save":
        """
        :param data: 原始数据
        :param ignore: 跳过存档检查
        """
        self.session = data["session"]
        self.apiId = data["apiId"]
        self.saveInfo = {
            # 账户创建时间 2022-09-03T10:21:48.613Z
            "createdAt": data["saveInfo"]["createdAt"],
            "gameFile": {
                # 文件类型
                "__type": data["saveInfo"]["gameFile"]["__type"],
                # 存档bucket
                "bucket": data["saveInfo"]["gameFile"]["bucket"],
                # 存档创建时间 2023-10-05T07:41:24.503Z
                "createdAt": data["saveInfo"]["gameFile"]["createdAt"],
                # gamesaves/{32}/.save
                "key": data["saveInfo"]["gameFile"]["key"],
                # metaData
                "metaData": data["saveInfo"]["gameFile"]["metaData"],
                # mime_type
                "mime_type": data["saveInfo"]["gameFile"]["mime_type"],
                # .save
                "name": data["saveInfo"]["gameFile"]["name"],
                # 存档id {24}
                "objectId": data["saveInfo"]["gameFile"]["objectId"],
                # provider
                "provider": data["saveInfo"]["gameFile"]["provider"],
                # 存档更新时间 2023-10-05T07:41:24.503Z
                "updatedAt": data["saveInfo"]["gameFile"]["updatedAt"],
                # https:rak3ffdi.tds1.tapfiles.cn/gamesaves/{32}/.save
                "url": data["saveInfo"]["gameFile"]["url"],
            },
            # 存档上传时间 {__type："Date", "iso": "2023-10-06T03:46:33.000Z"}
            "modifiedAt": {
                "__type": "Date",
                # 存档上传时间 "2023-10-06T03:46:33.000Z"
                "iso": datetime.fromisoformat(
                    data["saveInfo"]["modifiedAt"]["iso"].replace("Z", "+00:00")
                ),
            },
            # 用户id {24} 与 gameFile 中的不同
            "objectId": data["saveInfo"].objectId,
            "summary": {
                # 插件获取存档时间 2023 Oct.06 11:46:33
                "updatedAt": data["saveInfo"]["summary"]["updatedAt"],
                # 存档版本
                "saveVersion": data["saveInfo"]["summary"]["saveVersion"],
                # 课题分
                "challengeModeRank": data["saveInfo"]["summary"]["challengeModeRank"],
                # rks
                "rankingScore": float(data["saveInfo"]["summary"]["rankingScore"]),
                # 客户端版本号
                "gameVersion": data["saveInfo"]["summary"]["gameVersion"],
                # 头像
                "avatar": data["saveInfo"]["summary"]["avatar"],
                # 完成曲目数量
                "cleared": data["saveInfo"]["summary"]["cleared"],
                # FC曲目数量
                "fullCombo": data["saveInfo"]["summary"]["fullCombo"],
                # AP曲目数量
                "phi": data["saveInfo"]["summary"]["phi"],
            },
            # ACL
            "ACL": data["saveInfo"]["ACL"],
            # authData
            "authData": data["saveInfo"]["authData"],
            # 头像
            "avatar": data["saveInfo"]["avatar"],
            # 邮箱验证
            "emailVerified": data["saveInfo"]["emailVerified"],
            # 手机验证
            "mobilePhoneVerified": data["saveInfo"]["mobilePhoneVerified"],
            # 昵称
            "nickname": data["saveInfo"]["nickname"],
            # sessionToken
            "sessionToken": data["saveInfo"]["sessionToken"],
            # 短id
            "shortId": data["saveInfo"]["shortId"],
            # 用户名
            "username": data["saveInfo"]["username"],
            # 存档上传时间 2023 Oct.06 11:46:33
            "updatedAt": data["saveInfo"]["updatedAt"],
            # 用户信息
            "user": data["saveInfo"]["user"],
            # 用户名
            "PlayerId": data["saveInfo"]["PlayerId"],
        }
        self.saveUrl = data["saveUrl"]
        # 官方存档版本号
        self.Recordvr = data["Recordvr"]
        self.gameProgress = (
            {
                # 首次运行
                "isFirstRun": data["gameProgress"]["isFirstRun"],
                # 过去的章节已完成
                "legacyChapterFinished": data["gameProgress"]["legacyChapterFinished"],
                # 已展示收藏品Tip
                "alreadyShowCollectionTip": data["gameProgress"][
                    "alreadyShowCollectionTip"
                ],
                # 已展示自动解锁IN Tip
                "alreadyShowAutoUnlockINTip": data["gameProgress"][
                    "alreadyShowAutoUnlockINTip"
                ],
                # 剧情完成(显示全部歌曲和课题模式入口)
                "completed": data["gameProgress"]["completed"],
                # ？？？
                "songUpdateInfo": data["gameProgress"]["songUpdateInfo"],
                # 课题分
                "challengeModeRank": data["gameProgress"]["challengeModeRank"],
                # data货币
                "money": data["gameProgress"]["money"],
                # 痉挛解锁
                "unlockFlagOfSpasmodic": data["gameProgress"]["unlockFlagOfSpasmodic"],
                # Igallta解锁
                "unlockFlagOfIgallta": data["gameProgress"]["unlockFlagOfIgallta"],
                # Rrhar'il解锁
                "unlockFlagOfRrharil": data["gameProgress"]["unlockFlagOfRrharil"],
                # IN达到S
                # (+倒霉蛋,船,Shadow,心之所向,inferior,DESTRUCTION 3,2,1,Distorted Fate)
                "flagOfSongRecordKey": data["gameProgress"]["flagOfSongRecordKey"],
                # Random切片解锁
                "randomVersionUnlocked": data["gameProgress"]["randomVersionUnlocked"],
                # 第八章入场
                "chapter8UnlockBegin": data["gameProgress"]["chapter8UnlockBegin"],
                # 第八章第二阶段
                "chapter8UnlockSecondPhase": data["gameProgress"][
                    "chapter8UnlockSecondPhase"
                ],
                # 第八章通过
                "chapter8Passed": data["gameProgress"]["chapter8Passed"],
                # 第八章各曲目解锁
                "chapter8SongUnlocked": data["gameProgress"]["chapter8SongUnlocked"],
            }
            if data.get("gameProgress")
            else None
        )
        self.gameuser = (
            {
                # user
                "name": data["gameuser"]["name"],
                # 版本
                "version": data["gameuser"]["version"],
                # 是否展示Id
                "showPlayerId": data["gameuser"]["showPlayerId"],
                # 简介
                "selfIntro": data["gameuser"]["selfIntro"],
                # 头像
                "avatar": data["gameuser"]["avatar"],
                # 背景
                "background": data["gameuser"]["background"],
            }
            if data.get("gameuser")
            else None
        )
        if self.checkIg():
            await getRksRank.delUserRks(self.session)
            logger.warning(f"封禁tk {self.session}", "phi-plugin")
            raise ValueError(
                "您的存档rks异常，该 token 已禁用，如有异议请联系机器人管理员。\n"
                f"{self.session}"
            )
        self.gameRecord = {}
        for id in data.get("gameRecord", {}):
            self.gameRecord[id] = []
            for i in data["gameRecord"][id]:
                level = int(i)
                record = data["gameRecord"][id][i]
                if not record:
                    # 保持和 JS 一致，直接赋值到指定下标
                    while len(self.gameRecord[id]) <= level:
                        self.gameRecord[id].append(None)
                    self.gameRecord[id][level] = None
                    continue

                if not ignore:
                    if record["acc"] > 100 or record["acc"] < 0:
                        logger.error(f"acc > 100 封禁tk {self.session}", "phi-plugin")
                        await getRksRank.delUserRks(self.session)
                        raise ValueError(
                            "您的存档 acc 异常，该 token 已禁用"
                            f"，如有异议请联系机器人管理员。\n{self.session}"
                        )
                    if record["score"] > 1000000 or record["score"] < 0:
                        logger.error(
                            f"score > 1000000 封禁tk {self.session}", "phi-plugin"
                        )
                        await getRksRank.delUserRks(self.session)
                        raise ValueError(
                            "您的存档 score 异常，该 token 已禁用，"
                            f"如有异议请联系机器人管理员。\n{self.session}"
                        )
                # 保持和 JS 一致，直接赋值到指定下标
                while len(self.gameRecord[id]) <= level:
                    self.gameRecord[id].append(None)
                self.gameRecord[id][level] = await LevelRecordInfo().init(
                    record, id, level
                )
        return self

    async def init(self):
        # for id in self.gameRecord:
        #     for i in self.gameRecord[id]:
        #         level = int(i)
        #         if not self.gameRecord[id].get(level):
        #             continue
        pass

    def checkNoInfo(self) -> list[str]:
        """
        检查 gameRecord 中的歌曲 ID 是否有效。
        返回无效 ID 列表。
        """

        err = []
        err.extend(
            song_id for song_id in self.gameRecord if not getInfo.idgetsong(song_id)
        )
        return err

    def getRecord(self) -> list[LevelRecordInfo]:
        """
        获取存档

        :return: 按照 rks 降序排序的数组
        """
        if self.sortedRecord is not None:
            return self.sortedRecord
        sortedRecord: list[LevelRecordInfo] = []
        for song_id, record_list in self.gameRecord.items():
            for level_idx, tem in enumerate(record_list):
                if level_idx == 4:
                    break
                if not tem or not getattr(tem, "score", None):
                    continue
                sortedRecord.append(tem)
        sortedRecord.sort(key=lambda x: -x.rks)
        self.sortedRecord = sortedRecord
        return sortedRecord

    def findAccRecord(self, acc: float, same: bool = False) -> list[LevelRecordInfo]:
        """
        筛选满足 ACC 条件的成绩。

        :param acc: 最低 ACC 值（包含）
        :param same: 是否只保留最高 rks 的连续项
        :return: 按 rks 降序排列的成绩列表
        """
        record = []
        for song_id, record_list in self.gameRecord.items():
            for level_idx, tem in enumerate(record_list):
                if level_idx == 4:
                    break
                if not tem:
                    continue
                if tem.acc >= acc:
                    record.append(tem)

        # 按 rks 降序排序
        record.sort(key=lambda x: -x.rks)

        if same:
            for i in range(len(record) - 1):
                if i + 1 < len(record) and record[i].rks != record[i + 1].rks:
                    return record[: i + 1]

        return record

    def minUpRks(self) -> float:
        """计算rks+0.01的最低所需要提升的rks"""
        # 考虑屁股肉四舍五入原则
        ranking_score: float = self.saveInfo["summary"]["rankingScore"]
        minuprks = (math.floor(ranking_score * 100) / 100) + 0.005 - ranking_score
        return minuprks + 0.01 if minuprks < 0 else minuprks

    def check_record(self) -> str:
        """
        检查存档中的成绩是否存在问题。
        :return: 错误信息字符串
        """
        error = ""
        Level = ["EZ", "HD", "IN", "AT", "LEGACY"]

        for song_id, records in self.gameRecord.items():
            for level_idx, score in enumerate(records):
                if not score:
                    continue

                acc = score.acc
                score_val = score.score or 0
                fc = score.fc
                if acc < 0 or acc > 100 or score_val < 0 or score_val > 1000000:
                    error += f"\n{song_id} {Level[level_idx]} {fc} {acc:.2f} {score_val} 非法的成绩"  # noqa: E501
                if not fc and (score_val >= 1000000 or acc >= 100):
                    error += f"\n{song_id} {Level[level_idx]} {fc} {acc:.2f} {score_val} 不符合预期的值"  # noqa: E501
                if (score_val >= 1000000 and acc < 100) or (
                    score_val < 1000000 and acc >= 100
                ):
                    error += f"\n{song_id} {Level[level_idx]} {fc} {acc:.2f} {score_val} 成绩不自洽"  # noqa: E501

        return error

    def getSongsRecord(self, id: str) -> dict[str, LevelRecordInfo | None]:
        """
        :param str id: 曲目id
        """
        if record_list := self.gameRecord.get(id):
            return {str(i): item for i, item in enumerate(record_list)}
        else:
            return {}

    async def getB19(self, num: int) -> dict[str, list[LevelRecordInfo] | float]:
        """
        :param num: B几
        :return:
        ```
        {
            "phi": list[LevelRecordInfo],
            "b19_list": list[LevelRecordInfo],
            "com_rks": float,
        }
        """
        if self.B19List:
            return self.B19List
        # 计算得到的rks，仅作为测试使用
        sum_rks: float = 0
        # 满分且 rks 最高的成绩数组
        philist = self.findAccRecord(100)
        # p3
        phi = [philist.pop(0) for _ in range(min(3, len(philist)))]
        # logger.info(phi, "pgi-plugin")
        # 处理数据
        for i in range(3):
            if i >= len(phi):
                phi[i] = False  # type: ignore
                continue

            record = phi[i]
            if record.rks:
                phi[i] = copy.deepcopy(record)
                sum_rks += float(phi[i].rks)  # 计算 rks
                phi[i].illustration = await getInfo.getill(phi[i].song)
                phi[i].suggest = "无法推分"
        # 所有成绩
        rkslist = self.getRecord()
        # 真实 rks
        userrks = self.saveInfo["summary"]["rankingScore"]
        # 考虑屁股肉四舍五入原则的最小上升rks
        minuprks = math.floor(userrks * 100) / 100 + 0.005 - userrks
        if minuprks < 0:
            minuprks += 0.01
        # bestN 列表
        b19_list: list[LevelRecordInfo] = []
        for i in range(min(num, len(rkslist))):
            record = rkslist[i]
            # 计算 rks
            if i < 27:
                sum_rks += float(record.rks)
            # 是 Best 几
            record.num = i + 1
            # 推分建议
            if record.rks < 100:
                base_rks = (
                    record.rks if i < 26 else rkslist[min(26, len(rkslist) - 1)].rks
                )
                suggest = fCompute.suggest(
                    base_rks + minuprks * 30, record.difficulty, 2
                )
                if (
                    "无" in suggest
                    and (not phi or (record.rks > phi[-1].rks))
                    and record.rks < 100
                ):
                    suggest = "100.00%"
                record.suggest = suggest
            else:
                record.suggest = "无法推分"

            # 曲绘
            record.illustration = await getInfo.getill(record.song, "common")

            # b19列表
            b19_list.append(record)
        com_rks = sum_rks / 30
        self.B19List = {
            "phi": phi,
            "b19_list": b19_list,
        }
        self.b19_rks = b19_list[min(len(b19_list) - 1, 26)].rks
        return {
            "phi": phi,
            "b19_list": b19_list,
            "com_rks": com_rks,
        }

    async def getBestWithLimit(
        self, num: int, limit: dict[str, dict[str, str | list[float]]]
    ) -> dict[str, list[LevelRecordInfo] | float]:
        """
        :param num: B几
        :param limit: 条件
        :return:
        ```
        {
            "phi": list[LevelRecordInfo],
            "b19_list": list[LevelRecordInfo],
            "com_rks": float,
        }
        """
        # 计算得到的rks，仅作为测试使用
        sum_rks: float = 0
        # 满分且 rks 最高的成绩数组
        philist = self.findAccRecord(100)
        # 处理条件
        i = len(philist) - 1
        while i >= 0:
            if not checkLimit(philist[i], limit):
                philist.pop(i)
            i -= 1
        # p3
        phi = [philist.pop(0) for _ in range(min(3, len(philist)))]
        # logger.info(phi, "pgi-plugin")
        # 处理数据
        for i in range(3):
            if i >= len(phi):
                phi[i] = False  # type: ignore
                continue
            if phi[i].rks:
                phi[i] = copy.deepcopy(phi[i])
                sum_rks += float(phi[i].rks)  # 计算 rks
                phi[i].illustration = await getInfo.getill(phi[i].song)
                phi[i].suggest = "无法推分"
        # 所有成绩
        rkslist = self.getRecord()
        # 真实 rks
        userrks = self.saveInfo["summary"]["rankingScore"]
        # 考虑屁股肉四舍五入原则的最小上升rks
        minuprks = math.floor(userrks * 100) / 100 + 0.005 - userrks
        if minuprks < 0:
            minuprks += 0.01
        # bestN 列表
        b19_list: list[LevelRecordInfo] = []
        for i in range(min(num, len(rkslist))):
            record = rkslist[i]
            # 计算 rks
            if i < 27:
                sum_rks += float(record.rks)
            # 是 Best 几
            record.num = i + 1
            # 推分建议
            if record.rks < 100:
                base_rks = (
                    record.rks if i < 26 else rkslist[min(26, len(rkslist) - 1)].rks
                )
                suggest = fCompute.suggest(
                    base_rks + minuprks * 30, record.difficulty, 2
                )
                if (
                    "无" in suggest
                    and (not phi or (record.rks > phi[-1].rks))
                    and record.rks < 100
                ):
                    suggest = "100.00%"
                record.suggest = suggest
            else:
                record.suggest = "无法推分"

            # 曲绘
            record.illustration = await getInfo.getill(record.song, "common")

            # b19列表
            b19_list.append(record)
        com_rks = sum_rks / 30
        self.B19List = {
            "phi": phi,
            "b19_list": b19_list,
        }
        self.b19_rks = b19_list[min(len(b19_list) - 1, 26)].rks
        return {
            "phi": phi,
            "b19_list": b19_list,
            "com_rks": com_rks,
        }

    def getSuggest(self, id: str, lv: int, count: int, difficulty: int) -> str:
        """
        :param id: id
        :param lv: lv
        :param count: 保留位数
        :param difficulty: difficulty
        :return: 推分建议
        """
        if not self.b19_rks:
            record = self.getRecord()
            self.b19_rks = record[26].rks if len(record) > 26 else 0
            acc_record = self.findAccRecord(100, True)
            self.b0_rks = acc_record[0].rks if acc_record else None
        suggest = (
            fCompute.suggest(
                max(self.b19_rks, 0) + self.minUpRks() * 30, difficulty, count
            )
            if not self.gameRecord.get(id)
            or lv >= len(self.gameRecord[id])
            or getattr(self.gameRecord[id][lv], "rks", False)
            else fCompute.suggest(
                max(self.b19_rks, getattr(self.gameRecord[id][lv], "rks", 0))
                + self.minUpRks() * 30,
                difficulty,
                count,
            )
        )
        if "无" in suggest and difficulty > (self.b0_rks or 0) + self.minUpRks() * 30:
            return f"{100:.{count}f}%"
        return suggest

    def getRks(self) -> float:
        """
        获取存档RKS

        :return: 存档RKS
        """
        return self.saveInfo["summary"]["rankingScore"]

    def getSessionToken(self) -> str:
        """
        获取存档sessionToken

        :return: 存档sessionToken
        """
        return self.session

    async def getStats(self) -> list[dict[str, str | float]]:
        """获取存档成绩总览"""
        #'EZ', 'HD', 'IN', 'AT'
        tot = [0, 0, 0, 0]
        Record = self.gameRecord
        Level = getInfo.Level
        stats_ = {
            "title": "",
            "Rating": "",
            "unlock": 0,
            "tot": 0,
            "cleared": 0,
            "fc": 0,
            "phi": 0,
            "real_score": 0,
            "tot_score": 0,
            "highest": 0,
            "lowest": 18,
        }
        stats = [dict(stats_) for _ in range(4)]
        for song in getInfo.ori_info:
            info = getInfo.ori_info[song]
            if info.chart.get("At") and info.chart["At"].difficulty:
                tot[3] += 1
            if info.chart.get("IN") and info.chart["IN"].difficulty:
                tot[2] += 1
            if info.chart.get("HD") and info.chart["HD"].difficulty:
                tot[1] += 1
            if info.chart.get("EZ") and info.chart["EZ"].difficulty:
                tot[0] += 1
        stats[0]["tot"] = tot[0]
        stats[0]["title"] = Level[0]

        stats[1]["tot"] = tot[1]
        stats[1]["title"] = Level[1]

        stats[2]["tot"] = tot[2]
        stats[2]["title"] = Level[2]

        stats[3]["tot"] = tot[3]
        stats[3]["title"] = Level[3]

        for id in Record:
            if not getInfo.idgetsong(id):
                continue
            record = Record[id]
            for lv in [0, 1, 2, 3]:
                if lv >= len(record) or not record[lv]:
                    continue
                stats[lv]["unlock"] += 1
                rlv = record[lv]
                assert rlv is not None
                if (rlv.score or 0) > 700000:
                    stats[lv]["cleared"] += 1
                if rlv.fc or (rlv.score or 0) == 1000000:
                    stats[lv]["fc"] += 1
                if (rlv.score or 0) == 1000000:
                    stats[lv]["phi"] += 1

                stats[lv]["real_score"] += rlv.score or 0
                stats[lv]["tot_score"] += 1000000

                stats[lv]["highest"] = max(rlv.rks, stats[lv]["highest"])
                stats[lv]["lowest"] = min(rlv.rks, stats[lv]["lowest"])
        for lv in [0, 1, 2, 3]:
            stats[lv]["Rating"] = fCompute.rate(
                stats[lv]["real_score"],
                stats[lv]["tot_score"],
                stats[lv]["fc"] == stats[lv]["unlock"],
            )
            if stats[lv]["lowest"] == 18:
                stats[lv]["lowest"] = 0
        return stats

    def checkIg(self) -> bool:
        ranking_score = self.saveInfo["summary"]["rankingScore"]
        challenge_rank = self.saveInfo["summary"]["challengeModeRank"]

        # 检查 rankingScore 是否非法（非 0 却为假值）
        if not ranking_score and ranking_score != 0:
            return True

        # 检查 challengeModeRank 的各种非法情况
        if challenge_rank is None:
            return True
        if challenge_rank % 100 > 51:
            return True
        if challenge_rank < 0:
            return True
        if challenge_rank % 100 == 0 and challenge_rank != 0:
            return True
        return challenge_rank % 1 != 0


def checkLimit(record: LevelRecordInfo, limit: dict[str, dict[str, str | list[float]]]):
    for lim in limit.values():
        value = lim.get("value")
        assert isinstance(value, list), (
            f"Expected 'value' to be a list, got {type(value)}"
        )
        assert len(value) == 2, f"Expected 'value' to have 2 elements, got {len(value)}"
        assert all(isinstance(x, int | float) for x in value), (
            f"Expected all elements of 'value' to be numbers, got {value}"
        )

        match lim.get("type"):
            case "acc":
                if record.acc < value[0] or record.acc > value[1]:
                    return False
            case "score":
                if record.score is not None and (
                    record.score < value[0] or record.score > value[1]
                ):
                    return False
            case "rks":
                if record.rks < value[0] or record.rks > value[1]:
                    return False
    return True
