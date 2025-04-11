import math
from typing import Any

from ..constNum import MAX_DIFFICULTY
from ..fCompute import fCompute
from .getInfo import getInfo
from .getRksRank import getRksRank
from .LevelRecordInfo import LevelRecordInfo


class Save:
    def __init__(self, data: dict, ignore: bool = False):
        self.session = data.get("session")
        self.saveInfo = {
            "createdAt": data["saveInfo"]["createdAt"],
            "gameFile": {
                "__type": data["saveInfo"]["gameFile"]["__type"],
                "bucket": data["saveInfo"]["gameFile"]["bucket"],
                "createdAt": data["saveInfo"]["gameFile"]["createdAt"],
                "key": data["saveInfo"]["gameFile"]["key"],
                "metaData": data["saveInfo"]["gameFile"]["metaData"],
                "mime_type": data["saveInfo"]["gameFile"]["mime_type"],
                "name": data["saveInfo"]["gameFile"]["name"],
                "objectId": data["saveInfo"]["gameFile"]["objectId"],
                "provider": data["saveInfo"]["gameFile"]["provider"],
                "updatedAt": data["saveInfo"]["gameFile"]["updatedAt"],
                "url": data["saveInfo"]["gameFile"]["url"],
            },
            "modifiedAt": {
                "__type": "Date",
                "iso": data["saveInfo"]["modifiedAt"]["iso"],
            },
            "objectId": data["saveInfo"]["objectId"],
            "summary": {
                "updatedAt": data["saveInfo"]["summary"]["updatedAt"],
                "saveVersion": data["saveInfo"]["summary"]["saveVersion"],
                "challengeModeRank": data["saveInfo"]["summary"]["challengeModeRank"],
                "rankingScore": float(data["saveInfo"]["summary"]["rankingScore"]),
                "gameVersion": data["saveInfo"]["summary"]["gameVersion"],
                "avatar": data["saveInfo"]["summary"]["avatar"],
                "cleared": data["saveInfo"]["summary"]["cleared"],
                "fullCombo": data["saveInfo"]["summary"]["fullCombo"],
                "phi": data["saveInfo"]["summary"]["phi"],
            },
            "ACL": data["saveInfo"]["ACL"],
            "authData": data["saveInfo"]["authData"],
            "avatar": data["saveInfo"]["avatar"],
            "emailVerified": data["saveInfo"]["emailVerified"],
            "mobilePhoneVerified": data["saveInfo"]["mobilePhoneVerified"],
            "nickname": data["saveInfo"]["nickname"],
            "sessionToken": data["saveInfo"]["sessionToken"],
            "shortId": data["saveInfo"]["shortId"],
            "username": data["saveInfo"]["username"],
            "updatedAt": data["saveInfo"]["updatedAt"],
            "user": data["saveInfo"]["user"],
            "PlayerId": data["saveInfo"]["PlayerId"],
        }
        self.saveUrl = data["saveUrl"]
        self.Recordver = data["Recordver"]
        self.gameProgress = data.get("gameProgress")
        if self.gameProgress:
            self.gameProgress = {
                "isFirstRun": self.gameProgress["isFirstRun"],
                "legacyChapterFinished": self.gameProgress["legacyChapterFinished"],
                "alreadyShowCollectionTip": self.gameProgress[
                    "alreadyShowCollectionTip"
                ],
                "alreadyShowAutoUnlockINTip": self.gameProgress[
                    "alreadyShowAutoUnlockINTip"
                ],
                "completed": self.gameProgress["completed"],
                "songUpdateInfo": self.gameProgress["songUpdateInfo"],
                "challengeModeRank": self.gameProgress["challengeModeRank"],
                "money": self.gameProgress["money"],
                "unlockFlagOfSpasmodic": self.gameProgress["unlockFlagOfSpasmodic"],
                "unlockFlagOfIgallta": self.gameProgress["unlockFlagOfIgallta"],
                "unlockFlagOfRrharil": self.gameProgress["unlockFlagOfRrharil"],
                "flagOfSongRecordKey": self.gameProgress["flagOfSongRecordKey"],
                "randomVersionUnlocked": self.gameProgress["randomVersionUnlocked"],
                "chapter8UnlockBegin": self.gameProgress["chapter8UnlockBegin"],
                "chapter8UnlockSecondPhase": self.gameProgress[
                    "chapter8UnlockSecondPhase"
                ],
                "chapter8Passed": self.gameProgress["chapter8Passed"],
                "chapter8SongUnlocked": self.gameProgress["chapter8SongUnlocked"],
            }
        self.gameuser = data.get("gameuser")
        if self.gameuser:
            self.gameuser = {
                "name": self.gameuser["name"],
                "version": self.gameuser["version"],
                "showPlayerId": self.gameuser["showPlayerId"],
                "selfIntro": self.gameuser["selfIntro"],
                "avatar": self.gameuser["avatar"],
                "background": self.gameuser["background"],
            }
        if checkIg(self):
            getRksRank.delUserRks(self.session)
            raise ValueError(f"存档异常，token {self.session} 已封禁")
        self.gameRecord = {}
        for song_id in data["gameRecord"]:
            self.gameRecord[song_id] = {}
            for level_str in data["gameRecord"][song_id]:
                level = int(level_str)
                level_data = data["gameRecord"][song_id][level_str]
                if not level_data:
                    self.gameRecord[song_id][level] = None
                    continue
                self.gameRecord[song_id][level] = {
                    "id": song_id,
                    "level": level,
                    "fc": level_data["fc"],
                    "score": level_data["score"],
                    "acc": level_data["acc"],
                }
                if not ignore:
                    if level_data["acc"] > 100 or level_data["acc"] < 0:
                        raise ValueError(f"acc异常，token {self.session} 已封禁")
                    if level_data["score"] > 1_000_000 or level_data["score"] < 0:
                        raise ValueError(f"score异常，token {self.session} 已封禁")

    async def init(self):
        for song_id in self.gameRecord:
            for level in self.gameRecord[song_id]:
                if self.gameRecord[song_id][level]:
                    record_data = self.gameRecord[song_id][level]
                    self.gameRecord[song_id][level] = LevelRecordInfo(
                        record_data, record_data["id"], record_data["level"]
                    )

    def getRecord(self) -> list:
        if hasattr(self, "sortedRecord"):
            return self.sortedRecord
        sortedRecord = []
        for song_id in self.gameRecord:
            for level in self.gameRecord[song_id]:
                if level == 4:
                    continue
                record = self.gameRecord[song_id][level]
                if not record or not record.get("score"):
                    continue
                sortedRecord.append(record)
        sortedRecord.sort(key=lambda x: -x["rks"])
        self.sortedRecord = sortedRecord
        return sortedRecord

    def findAccRecord(self, acc: float, same: bool = False) -> list:
        record = []
        for song_id in self.gameRecord:
            for level in self.gameRecord[song_id]:
                if level == 4:
                    continue
                current = self.gameRecord[song_id][level]
                if current and current["acc"] >= acc:
                    record.append(current)
        record.sort(key=lambda x: -x["rks"])

        if same and record:
            i = 0
            while i < len(record) - 1 and record[i]["rks"] == record[i + 1]["rks"]:
                i += 1
            record = record[: i + 1]

        return record

    def minUpRks(self) -> float:
        current_rks = self.saveInfo["summary"]["rankingScore"]
        minuprks = math.floor(current_rks * 100) / 100 + 0.005 - current_rks
        return minuprks + 0.01 if minuprks < 0 else minuprks

    def checkRecord(self) -> str:
        error = ""
        levels = ["EZ", "HD", "IN", "AT", "LEGACY"]
        for song_id in self.gameRecord:
            for level, record in self.gameRecord[song_id].items():
                if not record:
                    continue
                if (
                    record["acc"] > 100
                    or record["acc"] < 0
                    or record["score"] > 1_000_000
                    or record["score"] < 0
                ):
                    error += (
                        f"\n{song_id} {levels[level]} {record['fc']} "
                        f"{record['acc']} {record['score']} 非法的成绩"
                    )
                if (record["score"] >= 1_000_000 and record["acc"] < 100) or (
                    record["score"] < 1_000_000 and record["acc"] >= 100
                ):
                    error += (
                        f"\n{song_id} {levels[level]} {record['fc']} "
                        f"{record['acc']} {record['score']} 成绩不自洽"
                    )
        return error

    def getSongsRecord(self, id_: str) -> dict:
        return self.gameRecord.get(id_, {})

    async def getB19(self, num: int) -> dict:
        if hasattr(self, "B19List"):
            return self.B19List
        philist = self.findAccRecord(100)
        phi = philist[:3] if len(philist) >= 3 else philist
        # sum_rks = sum(r["rks"] for r in phi[:3])
        for i in range(3):
            if phi[i]:
                phi[i]["illustration"] = getInfo.getill(phi[i]["song"])
                phi[i]["suggest"] = "无法推分"
        rkslist = self.getRecord()
        # current_rks = self.saveInfo["summary"]["rankingScore"]
        min_up_rks = self.minUpRks()
        b19_list = []
        for i in range(min(num, len(rkslist))):
            entry = rkslist[i]
            entry["num"] = i + 1
            if i >= 26 and len(rkslist) > 26:
                base_rks = rkslist[26]["rks"]
            else:
                base_rks = entry["rks"]
            if entry["rks"] < 100:
                base_rks = rkslist[26]["rks"] if i >= 26 else entry["rks"]
                suggest = fCompute.suggest(
                    base_rks + min_up_rks * 30, entry["difficulty"], 2
                )
                if "无" in suggest and (not phi or entry["rks"] > phi[-1]["rks"]):
                    suggest = "100.00%"
            else:
                suggest = "无法推分"
            entry["suggest"] = suggest
            entry["illustration"] = getInfo.getill(entry["song"], "common")
            b19_list.append(entry)
        avg_rks = sum(r["rks"] for r in rkslist[:27]) / 30 if rkslist else 0
        if b19_list:
            index = min(26, len(b19_list) - 1)
            self.b19_rks = b19_list[index]["rks"]
        else:
            self.b19_rks = 0
        self.B19List = {"phi": phi, "b19_list": b19_list}
        self.b19_rks = b19_list[26]["rks"] if len(b19_list) > 26 else 0
        return {"phi": phi, "b19_list": b19_list, "com_rks": avg_rks}

    async def getBestWithLimit(self, num: int, limit: list[dict]) -> dict:
        philist = self.findAccRecord(100)
        # 过滤 philist
        i = len(philist) - 1
        while i >= 0:
            if not checkLimit(philist[i], limit):
                del philist[i]
            i -= 1
        phi = philist[:3]
        # sum_rks = sum(r["rks"] for r in phi[:3])
        for i in range(3):
            if phi[i]:
                phi[i]["illustration"] = getInfo.getill(phi[i]["song"])
                phi[i]["suggest"] = "无法推分"
        rkslist = self.getRecord()
        # 过滤 rkslist
        i = len(rkslist) - 1
        while i >= 0:
            if not checkLimit(rkslist[i], limit):
                del rkslist[i]
            i -= 1
        b19_list = []
        # current_rks = self.saveInfo["summary"]["rankingScore"]
        min_up_rks = self.minUpRks()
        for i in range(min(num, len(rkslist))):
            entry = rkslist[i]
            entry["num"] = i + 1
            base_rks = rkslist[26]["rks"] if i >= 26 else entry["rks"]
            suggest = fCompute.suggest(
                base_rks + min_up_rks * 30, entry["difficulty"], 2
            )
            if "无" in suggest and (not phi or entry["rks"] > phi[-1]["rks"]):
                suggest = "100.00%"
            else:
                suggest = "无法推分" if entry["rks"] >= 100 else suggest
            entry["suggest"] = suggest
            entry["illustration"] = getInfo.getill(entry["song"], "common")
            b19_list.append(entry)
        avg_rks = sum(r["rks"] for r in rkslist[:27]) / 30 if rkslist else 0
        return {"phi": phi, "b19_list": b19_list, "com_rks": avg_rks}

    def getSuggest(self, id_: str, lv: int, count: int, difficulty: float) -> str:
        # 确保 b19_rks 和 b0_rks 已定义
        if not hasattr(self, "b19_rks"):
            record = self.getRecord()
            self.b19_rks = record[26]["rks"] if len(record) > 26 else 0

        if not hasattr(self, "b0_rks"):
            # 获取最高rks的满分成绩（same=True）
            highest_phi = self.findAccRecord(100, same=True)
            self.b0_rks = highest_phi[0]["rks"] if highest_phi else 0

        # 获取当前成绩
        current = self.gameRecord.get(id_, {}).get(lv, {})
        current_rks = current.get("rks", 0) if current else 0

        # 计算基础rks
        base_rks = max(self.b19_rks, current_rks) if current else self.b19_rks

        # 调用 fCompute.suggest
        suggest = fCompute.suggest(base_rks + self.minUpRks() * 30, difficulty, count)

        if "无" in suggest:
            # 判断是否超过条件
            if (
                difficulty > (self.b0_rks + self.minUpRks() * 30)
            ) and current_rks < 100:
                return f"{100:.{count}f}%"
            else:
                return suggest
        else:
            return suggest

    def getRks(self) -> float:
        return float(self.saveInfo["summary"]["rankingScore"])

    def getSessionToken(self) -> Any:
        return self.session

    async def getStats(self) -> list[dict]:
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
        stats = [stats_.copy() for _ in range(4)]
        levels = ["EZ", "HD", "IN", "AT"]
        for song in getInfo.ori_info.values():
            for level in ["AT", "IN", "HD", "EZ"]:
                idx = levels.index(level)
                if song["chart"].get(level, {}).get("difficulty", 0):
                    stats[idx]["tot"] += 1
        for song_id in self.gameRecord:
            song_name = getInfo.idgetsong(song_id)
            if not song_name:
                continue
            for lv in range(4):
                record = self.gameRecord[song_id].get(lv, None)
                if not record:
                    continue
                stats[lv]["unlock"] += 1
                if record["score"] >= 700000:
                    stats[lv]["cleared"] += 1
                if record["fc"] or record["score"] == 1_000_000:
                    stats[lv]["fc"] += 1
                if record["score"] == 1_000_000:
                    stats[lv]["phi"] += 1
                stats[lv]["real_score"] += record["score"]
                stats[lv]["tot_score"] += 1_000_000
                stats[lv]["highest"] = max(stats[lv]["highest"], record["rks"])
                stats[lv]["lowest"] = min(stats[lv]["lowest"], record["rks"])
        for lv in range(4):
            stats[lv]["Rating"] = fCompute.rate(
                stats[lv]["real_score"],
                stats[lv]["tot_score"],
                stats[lv]["fc"] == stats[lv]["unlock"],
            )
            if stats[lv]["lowest"] == 18:
                stats[lv]["lowest"] = 0
        return stats


def checkLimit(record: dict, limits: list[dict]) -> bool:
    for limit in limits:
        val = limit["value"]
        if limit["type"] == "acc":
            if not (val[0] <= record["acc"] <= val[1]):
                return False
        elif limit["type"] == "score":
            if not (val[0] <= record["score"] <= val[1]):
                return False
        elif limit["type"] == "rks":
            if not (val[0] <= record["rks"] <= val[1]):
                return False
    return True


def checkIg(save: Save) -> bool:
    summary = save.saveInfo["summary"]
    if summary["rankingScore"] > MAX_DIFFICULTY:
        return True
    if not summary["rankingScore"] and summary["rankingScore"] != 0:
        return True
    cmr = summary["challengeModeRank"]
    if cmr % 100 > 51 or cmr < 0:
        return True
    if cmr % 100 == 0 and cmr != 0:
        return True
    return True if (cmr // 100) == 0 and cmr != 0 else cmr % 1 != 0
