"""phigros rks 排行榜"""

import contextlib
import random
import re

from nonebot_plugin_alconna import Alconna, Args, Match, on_alconna
from nonebot_plugin_uninfo import Uninfo

from zhenxun.configs.config import BotConfig
from zhenxun.services.log import logger

from ..config import PluginConfig, cmdhead
from ..lib.PhigrosUser import PhigrosUser
from ..model.cls.models import UserItem
from ..model.cls.saveHistory import Save, saveHistory
from ..model.fCompute import fCompute
from ..model.getInfo import getInfo
from ..model.getNotes import getNotes
from ..model.getRksRank import getRksRank
from ..model.getSave import getSave
from ..model.makeRequest import makeRequest
from ..model.makeRequestFnc import makeRequestFnc
from ..model.picmodle import picmodle
from ..model.send import send
from ..utils import can_be_call, to_dict

recmdhead = re.escape(cmdhead)

rankList = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(排行榜|ranklist)", Args["rank", int, 0]),
    rule=can_be_call("rankList"),
    priority=5,
    block=True,
)

rankfind = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(查询排名|rankfind)", Args["q?", float, 0]),
    rule=can_be_call("rankList"),
    priority=5,
    block=True,
)

godList = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(封神榜|godlist)"),
    rule=can_be_call("godList"),
    priority=5,
    block=True,
)


@rankList.handle()
async def _(session: Uninfo, rank: Match[int]):
    msg = rank.result if rank.available else 0
    data = {
        "Title": "RankingScore排行榜",
        "totDataNum": 0,
        "BotNick": BotConfig.self_nickname,
        "users": [],
        "me": {},
    }
    if PluginConfig.get("openPhiPluginApi"):
        try:
            if msg:
                api_ranklist = await makeRequest.getRanklistRank(request_rank=msg)
            else:
                api_ranklist = await makeRequest.getRanklistUser(
                    makeRequestFnc.makePlatform(session)
                )
            data["totDataNum"] = api_ranklist.totDataNum
            for item in api_ranklist.users:
                data["users"].append(
                    {
                        **await makeSmallLine(item),
                        "index": item.index,
                        "me": api_ranklist.me,
                    }
                )
            data["me"] = await makeLargeLine(
                await Save.constructor(**api_ranklist.me.save),
                saveHistory(api_ranklist.me.history),
            )
            await send.sendWithAt(
                [
                    f"总数据量：{data['totDataNum']}",
                    await picmodle.common("rankingList", data),
                ]
            )
            return
        except Exception as e:
            logger.error("API ERR", "phi-plugin:rankList", e=e)
    rankNum = 0
    data["totDataNum"] = await getRksRank.getAllRank()
    if msg:
        rankNum = max(min(msg, data["totDataNum"]), 1) - 1
    else:
        save = await send.getsaveResult(session)
        if not save:
            return
        sessionToken = save.getSessionToken()
        rankNum = await getRksRank.getUserRank(sessionToken)
    # 展示的用户数据
    if rankNum < 2:
        _list = await getRksRank.getRankUser(0, 5)
        myTk = _list[rankNum]
    else:
        _list = await getRksRank.getRankUser(rankNum - 2, rankNum + 3)
        myTk = _list[2]
    for index in range(max(5, len(_list))):
        if index >= len(_list):
            data["users"].append({"playerId": "无效用户", "index": index + rankNum - 2})
        sessionToken = _list[index]
        save = await getSave.getSaveBySessionToken(sessionToken)
        if not save:
            data["users"].append({"playerId": "无效用户", "index": index + rankNum - 2})
            await getRksRank.delUserRks(sessionToken)
        else:
            data["users"].append(
                {
                    **await makeSmallLine(save),
                    "index": max(index + rankNum - 1, index + 1),
                    "me": myTk == save.getSessionToken(),
                }
            )
        if myTk == sessionToken and save:
            history = await getSave.getHistoryBySessionToken(save.getSessionToken())
            data["me"] = await makeLargeLine(save, history)
    await send.sendWithAt(
        [f"总数据量：{data['totDataNum']}", await picmodle.common("rankingList", data)]
    )


@rankfind.handle()
async def _(q: Match[float]):
    rks = q.result if q.available else 0
    if not rks:
        await send.sendWithAt(f"请输入要查询的 rks！\n格式： {cmdhead} rankfind <rks>")
        return
    if PluginConfig.get("openPhiPluginApi"):
        try:
            res = await makeRequest.getRanklistRks(rks)
            await send.sendWithAt(
                f"当前服务器记录中一共有 {res.rksRank}"
                f"/{res.totNum} 位玩家的 rks 大于 {rks}！"
            )
            return
        except Exception as e:
            logger.error("API ERR", "phi-plugin:rankList", e=e)
    totDataNum = await getRksRank.getAllRank()
    rank = await getRksRank.getRankByRks(rks)
    await send.sendWithAt(
        f"当前服务器记录中一共有 {rank}/{totDataNum} 位玩家的 rks 大于 {rks}！"
    )


@godList.handle()
async def _(session: Uninfo):
    _list = await getSave.getGod()
    plugin_data = await getNotes.getNotesData(session.user.id)
    data = {
        "Title": "封神榜",
        "totDataNum": 0,
        "BotNick": BotConfig.self_nickname,
        "users": [],
        "background": getInfo.getill(random.choice(getInfo.illlist), "blur"),
        "theme": plugin_data.plugin_data.theme,
    }
    if not _list:
        data["totDataNum"] = 0
        await send.sendWithAt(await picmodle.common("rankingList", data))
        return
    data["totDataNum"] = len(_list)
    for index, item in enumerate(_list):
        with contextlib.suppress(Exception):
            godRecord = PhigrosUser(item)
            await godRecord.buildRecord()
            record = to_dict(godRecord)
            god = await Save().constructor(record, True)
            await god.init()
            data["users"].append(await makeLargeLine(god, saveHistory(record)))
            data["users"][len(data["users"])]["index"] = index
    await send.sendWithAt(await picmodle.common("rankingList", data))


async def makeLargeLine(save: Save, history: saveHistory):
    """创建一个详细对象"""
    if not save:
        return {"playerId": "无效用户"}
    lineData = history.getRksAndDataLine()
    for index, item in enumerate(lineData.rks_date):
        item = fCompute.formatDateToNow(item)
        lineData.rks_date[index] = item  # pyright: ignore[reportArgumentType, reportCallIssue]
    clgHistory = []
    clgHistory.extend(
        {
            "ChallengeMode": round(item.value / 100),
            "ChallengeModeRank": item.value % 100,
            "date": fCompute.formatDateToNow(item.date),
        }
        for index, item in enumerate(history.challengeModeRank)
        if item.value != history.challengeModeRank[index - 1].value
    )
    b30Data = await save.getB19(33)
    b30list = {
        "P3": {"title": "Perfect 3", "list": b30Data["phi"]},
        "B3": {"title": "Best 3", "list": b30Data["b19_list"][3]},
        "F3": {"title": "Floor 3", "list": b30Data["b19_list"][24:27]},
        "L3": {"title": "Overflow 3", "list": b30Data["b19_list"][27:30]},
    }
    return {
        "backgroundurl": await getInfo.getBackground(save.gameuser.background),
        "avatar": await getInfo.idgetavatar(save.saveInfo.summary.avatar)
        or "Introduction",
        "playerId": fCompute.convertRichText(save.saveInfo.PlayerId),
        "rks": save.saveInfo.summary.rankingScore,
        "ChallengeMode": round(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "updated": fCompute.formatDate(save.saveInfo.modifiedAt.iso),
        "selfIntro": fCompute.convertRichText(save.gameuser.selfIntro),
        "rks_history": lineData.rks_history,
        "rks_range": lineData.rks_range,
        "rks_date": lineData.rks_date,
        "b30list": b30list,
        "clg_list": clgHistory,
    }


async def makeSmallLine(save: UserItem | Save):
    """创建一个简略对象"""
    if not save:
        return {"playerId": "无效用户"}
    return {
        "backgroundurl": await getInfo.getBackground(save.gameuser.background),
        "avatar": await getInfo.idgetavatar(save.saveInfo.summary.avatar)
        or "Introduction",
        "playerId": fCompute.convertRichText(save.saveInfo.PlayerId),
        "rks": save.saveInfo.summary.rankingScore,
        "ChallengeMode": round(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
    }
