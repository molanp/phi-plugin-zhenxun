"""
phigros b19查询
"""

from functools import cmp_to_key
import math
import random
import re
from typing import Literal

from arclet.alconna import StrMulti
from nonebot_plugin_alconna import Alconna, Args, CommandMeta, Match, on_alconna
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger

from ..config import PluginConfig, cmdhead, recmdhead
from ..lib.PhigrosUser import PhigrosUser
from ..model.cls.LevelRecordInfo import LevelRecordInfo
from ..model.constNum import Level, LevelNum
from ..model.fCompute import fCompute
from ..model.getdata import getdata
from ..model.getInfo import getInfo
from ..model.getPic import pic
from ..model.picmodle import picmodle
from ..model.send import send
from ..utils import can_be_call, to_dict

ChallengeModeName = ["白", "绿", "蓝", "红", "金", "彩"]


b19 = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(b|rks|pgr|PGR|B|RKS)",
        Args["nnum?", int],
        meta=CommandMeta(compact=True),
    ),
    rule=can_be_call("b19"),
    block=True,
    priority=5,
)

p30 = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(p|P)",
        Args["nnum?", int],
        meta=CommandMeta(compact=True),
    ),
    rule=can_be_call("p30"),
    block=True,
    priority=5,
)

arcgrosB19 = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(a|arc|啊|阿|批|屁|劈)",
        Args["nnum?", str],
        meta=CommandMeta(compact=True),
    ),
    rule=can_be_call("arcgrosB19"),
    block=True,
    priority=5,
)

lmtAcc = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*lmtacc",
        Args["acc?", float],
        meta=CommandMeta(compact=True),
    ),
    rule=can_be_call("lmtAcc"),
    block=True,
    priority=5,
)

singlescore = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(score|单曲成绩)",
        Args["picversion?", Literal[1, 2]],
        Args["song?", str],
        meta=CommandMeta(compact=True),
    ),
    rule=can_be_call("singlescore"),
    block=True,
    priority=5,
)

suggest = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(suggest|推分(建议)?)",
        Args["input", StrMulti],
        meta=CommandMeta(compact=True),
    ),
    rule=can_be_call("suggest"),
    block=True,
    priority=5,
)

chap__ = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*chap",
        Args["song", StrMulti],
        meta=CommandMeta(compact=True),
    ),
    rule=can_be_call("chap"),
    block=True,
    priority=5,
)


@b19.handle()
async def _(session: Uninfo, nnum: Match[int]):
    save = await send.getsaveResult(session)
    if not save:
        return
    if err := await save.checkNoInfo():
        await send.sendWithAt("以下曲目无信息，可能导致b19显示错误\n" + "".join(err))
    num = nnum.result if nnum.available else 33
    num = max(num, 33)
    num = min(num, PluginConfig.get("B19MaxNum"))
    # NOTE: 因响应器限制，暂时无法实现匹配中间消息(bksong)(取消息不可预料)
    plugin_data = await getdata.getNotesData(session.user.id)
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(
            "正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", recallTime=5
        )
    save_b19 = await save.getB19(num)
    stats = save.getStats()
    money = getattr(save.gameProgress, "money", [0])
    gameuser = {
        "avatar": getdata.idgetavatar(save.gameuser.avatar),
        "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "rks": save.saveInfo.summary.rankingScore,
        "data": "".join(
            [
                f"{v}{u} "
                for v, u in zip(money, ["KiB", "MiB", "GiB", "TiB", "PiB"])
                if v
            ]
        ),
        "PlayerId": fCompute.convertRichText(save.saveInfo.PlayerId),
    }
    data = {
        "phi": save_b19["phi"],
        "b19_list": save_b19["b19_list"],
        "Date": save.saveInfo.summary.updatedAt,
        "background": await getInfo.getill(random.choice(getInfo.illlist)),
        "theme": plugin_data.plugin_data.theme,
        "gameuser": gameuser,
        "stats": stats,
    }
    res: list = [await picmodle.b19(to_dict(data))]
    if abs(save_b19.get("com_rks", 0) - save.saveInfo.summary.rankingScore) > 0.1:  # type: ignore
        res.append(
            f"请注意，当前版本可能更改了计算规则\n计算rks: {save_b19['com_rks']}\n"
            f"存档rks:{save.saveInfo.summary.rankingScore}"
        )
    await send.sendWithAt(res, True)


# FIXME: 这个和b19就多了个spInfo，后续合并一下优化代码
@p30.handle()
async def _(session: Uninfo, nnum: Match[int]):
    save = await send.getsaveResult(session)
    if not save:
        return
    err = await save.checkNoInfo()
    if err:
        await send.sendWithAt("以下曲目无信息，可能导致b19显示错误\n" + "\n".join(err))
    num = nnum.result if nnum.available else 33
    num = max(num, 33)
    num = min(num, PluginConfig.get("B19MaxNum"))
    # NOTE: 因响应器限制，暂时无法实现匹配中间消息(bksong)(取消息不可预料)
    plugin_data = await getdata.getNotesData(session.user.id)
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(
            "正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", recallTime=5
        )
    try:
        await getdata.buildingRecord(p30, session, PhigrosUser(save.sessionToken))
    except Exception as e:
        logger.error("p30更新存档失败", "phi-plugin", session=session, e=e)
        await send.sendWithAt("p30生成失败了...", True)
        return
    save_b19 = await save.getBestWithLimit(num, [{"type": "acc", "value": [100, 100]}])
    stats = save.getStats()
    money = getattr(save.gameProgress, "money", [0])
    gameuser = {
        "avatar": getdata.idgetavatar(save.gameuser.avatar),
        "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "rks": save_b19["com_rks"],
        "data": "".join(
            [
                f"{v}{u} "
                for v, u in zip(money, ["KiB", "MiB", "GiB", "TiB", "PiB"])
                if v
            ]
        ),
        "PlayerId": fCompute.convertRichText(save.saveInfo.PlayerId),
    }
    data = {
        "phi": save_b19["phi"],
        "b19_list": save_b19["b19_list"],
        "Date": save.saveInfo.summary.updatedAt,
        "background": await getInfo.getill(random.choice(getInfo.illlist)),
        "theme": plugin_data.plugin_data.theme,
        "gameuser": gameuser,
        "stats": stats,
        "spInfo": "All Perfect Only Mode",
    }
    res: list = [await picmodle.b19(data)]
    if abs(save_b19.get("com_rks", 0) - save.saveInfo.summary.rankingScore) > 0.1:  # type: ignore
        res.append(
            f"计算rks: {save_b19['com_rks']}\n"
            f"存档rks:{save.saveInfo.summary.rankingScore}"
        )
    await send.sendWithAt(res, True)


# NOTE: arc版查分图
@arcgrosB19.handle()
async def _(session: Uninfo, nnum: Match[str]):
    save = await send.getsaveResult(session)
    if not save:
        return
    if err := await save.checkNoInfo():
        await send.sendWithAt("以下曲目无信息，可能导致b19显示错误\n" + "\n".join(err))
    num = nnum.result if nnum.available else "b32"

    # 提取数字
    if isinstance(num, str):
        match = re.search(r"\d+", num)  # 匹配字符串中的第一个数字序列
        num = int(match.group()) if match else 32
    else:
        num = int(num)  # 确保为整数
    num = max(num, 30)
    num = min(num, PluginConfig.get("B19MaxNum"))
    plugin_data = await getdata.getNotesData(session.user.id)
    save_b19 = await save.getB19(num)
    money = getattr(save.gameProgress, "money", [0])
    gameuser = {
        "avatar": getdata.idgetavatar(save.gameuser.avatar),
        "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "rks": save_b19["com_rks"],
        "data": "".join(
            [
                f"{v}{u} "
                for v, u in zip(money, ["KiB", "MiB", "GiB", "TiB", "PiB"])
                if v
            ]
        ),
        "backgroundUrl": await fCompute.getBackground(save.gameuser.background),
        "PlayerId": fCompute.convertRichText(save.saveInfo.PlayerId),
    }
    data = {
        "phi": save_b19["phi"],
        "b19_list": save_b19["b19_list"],
        "Date": save.saveInfo.summary.updatedAt,
        "background": await getInfo.getill(random.choice(getInfo.illlist)),
        "theme": plugin_data.plugin_data.theme,
        "gameuser": gameuser,
        "spInfo": "All Perfect Only Mode",
        "fCompute": fCompute,
    }
    await send.sendWithAt(await picmodle.arcgros_b19(data), True)


# NOTE: limit只对acc满分生效是正常的，符合原版js逻辑
# NOTE: 限制最低acc后的rks
@lmtAcc.handle()
async def _(session: Uninfo, acc: Match[float]):
    _acc = acc.result if acc.available else None
    if _acc is None or not isinstance(_acc, float) or _acc < 0 or _acc > 100:
        await send.sendWithAt(
            f"我听不懂 {_acc} 是多少喵！请指定一个0-100的数字喵！\n"
            f"格式：{cmdhead} lmtacc <0-100>",
        )
        return
    save = await send.getsaveResult(session)
    if not save:
        return
    if err := await save.checkNoInfo():
        await send.sendWithAt("以下曲目无信息，可能导致b19显示错误\n" + "\n".join(err))
    nnum = 33
    plugin_data = await getdata.getNotesData(session.user.id)
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(
            "正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", recallTime=5
        )
    save_b19 = await save.getBestWithLimit(
        nnum, [{"type": "acc", "value": [_acc, 100]}]
    )
    stats = save.getStats()
    money = getattr(save.gameProgress, "money", [0])
    gameuser = {
        "avatar": getdata.idgetavatar(save.gameuser.avatar),
        "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "rks": save.saveInfo.summary.rankingScore,
        "data": "".join(
            [
                f"{v}{u} "
                for v, u in zip(money, ["KiB", "MiB", "GiB", "TiB", "PiB"])
                if v
            ]
        ),
        "PlayerId": fCompute.convertRichText(save.saveInfo.PlayerId),
    }
    data = {
        "phi": save_b19["phi"],
        "b19_list": save_b19["b19_list"],
        "Date": save.saveInfo.summary.updatedAt,
        "background": await getInfo.getill(random.choice(getInfo.illlist)),
        "theme": plugin_data.plugin_data.theme,
        "gameuser": gameuser,
        "stats": stats,
        "spInfo": f"ACC is limited to {_acc}%",
    }
    res: list = [await picmodle.b19(to_dict(data))]
    if abs(save_b19["com_rks"] - save.saveInfo.summary.rankingScore) > 0.1:
        res.append(
            f"计算rks: {save_b19['com_rks']}\n"
            f"存档rks:{save.saveInfo.summary.rankingScore}"
        )
    await send.sendWithAt(res, True)


@singlescore.handle()
async def _(session: Uninfo, picversion: Match[int], song: Match[str]):
    _picversion = picversion.result if picversion.available else 1
    _song = song.result if song.available else None
    if not _song:
        await send.sendWithAt(f"请指定曲名哦！\n格式：{cmdhead} score <曲名>")
        return
    __song = await getdata.fuzzysongsnick(_song)
    if not __song:
        await send.sendWithAt(
            f"未找到 {_song} 的有关信息哦！",
        )
        return
    save = await send.getsaveResult(session)
    if not save:
        return
    _song = __song[0]
    Record = save.gameRecord
    songId = getInfo.SongGetId(_song)
    ans = Record.get(songId) if songId else None
    if not ans:
        await send.sendWithAt(
            f"我不知道你关于[{_song}]的成绩哦！"
            f"可以试试更新成绩哦！\n格式：{cmdhead} update",
        )
        return
    dan = await getdata.getDan(session.user.id)
    data = {
        "songName": _song,
        "PlayerId": save.saveInfo.PlayerId,
        "avatar": getdata.idgetavatar(session.user.id),
        "Rks": round(save.saveInfo.summary.rankingScore, 4),
        "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "scoreData": {},
        "CLGMOD": dan.get("Dan") if dan else None,
        "EX": dan.get("EX") if dan else None,
    }
    data["illustration"] = await getInfo.getill(_song)
    songsinfo = await getInfo.info(_song, True)
    assert songsinfo
    match _picversion:
        case 2:
            for level, a in ans.items():
                if a:
                    a.acc = round(a.acc, 4)
                    a.rks = round(a.rks, 4)
                    data[level] = {
                        **to_dict(a),
                        "suggest": save.getSuggest(
                            songId,
                            level,
                            4,
                            songsinfo.chart[level].difficulty,
                        ),
                    }
                else:
                    data[level] = {"Rating": "NEW"}
            await send.sendWithAt(await picmodle.score(data, 2))
        case _:
            for level in Level:
                if level not in songsinfo.chart:
                    break
                data["scoreData"][level] = {
                    "difficulty": songsinfo.chart[level].difficulty
                }
            for level, a in ans.items():
                if a:
                    a.acc = round(a.acc, 4)
                    a.rks = round(a.rks, 4)
                    data[level] = {
                        **to_dict(a),
                        "suggest": save.getSuggest(
                            songId,
                            level,
                            4,
                            songsinfo.chart[level].difficulty,
                        ),
                    }
                else:
                    data[level] = {"Rating": "NEW"}
            await send.sendWithAt(await picmodle.score(data, 1), True)


# NOTE: 推分建议，建议的是RKS+0.01的所需值
@suggest.handle()
async def _(session: Uninfo, input: Match):
    save = await send.getsaveResult(session)
    if not save:
        return
    input_ = input.result if input.available else ""
    # 处理范围请求
    req = fCompute.match_request(input_)
    range_ = req.range
    isask = req.isask
    scoreAsk = req.scoreAsk
    # 取出信息
    Record = save.gameRecord
    # 计算
    data = []
    for id in Record:
        song = getdata.idgetsong(id)
        if not song:
            logger.warning(f"曲目无信息: {id}", "phi-plugin")
            continue
        info = await getdata.info(song, True)
        assert info
        record = Record[id]
        for lv in range(4):
            if not info.chart.get(Level[lv]):
                continue
            difficulty = info.chart[Level[lv]].difficulty
            assert isinstance(difficulty, float)
            if range_[0] <= difficulty and difficulty <= range_[1] and isask[lv]:
                level = LevelNum[lv]
                rlv = record[level]
                if not rlv and not scoreAsk.NEW:
                    continue
                if rlv and not getattr(scoreAsk, rlv.Rating.upper()):
                    continue
                if not rlv:
                    rlv = LevelRecordInfo()
                rlv.suggest = save.getSuggest(id, level, 4, difficulty)
                if "无" in rlv.suggest:
                    continue
                data.append(
                    {
                        **to_dict(rlv),
                        **to_dict(info),
                        "illustration": await getdata.getill(song, "low"),
                        "difficulty": difficulty,
                        "rank": Level[lv],
                    }
                )
    limitnum = PluginConfig.get("listScoreMaxNum")
    if len(data) > limitnum:
        await send.sendWithAt(
            f"谱面数量过多({len(data)})大于设置的最大值({limitnum})，只显示前{limitnum}条！",
        )
    data = data[:limitnum]
    data = sorted(data, key=cmp_to_key(cmpsugg))
    plugin_data = await getdata.getNotesData(session.user.id)
    await send.sendWithAt(
        await picmodle.list(
            {
                "head_title": "推分建议",
                "song": data,
                "background": await getdata.getill(random.choice(getInfo.illlist)),
                "theme": plugin_data.plugin_data.theme,
                "PlayerId": save.saveInfo.PlayerId,
                "Rks": round(save.saveInfo.summary.rankingScore, 4),
                "Date": save.saveInfo.summary.updatedAt,
                "ChallengeMode": math.floor(
                    save.saveInfo.summary.challengeModeRank / 100
                ),
                "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
                "dan": await getdata.getDan(session.user.id),
            }
        ),
        True,
    )


@chap__.handle()
async def _(session: Uninfo, song: Match):
    msg = song.result if song.available else ""
    if msg.upper() == "HELP" or not msg:
        await send.sendWithAt(pic.getimg("chapHelp"))
        return
    chap = fCompute.fuzzySearch(msg, getInfo.chapNick)
    chap = chap[0].get("value") if chap else ""
    if not chap and msg != "ALL":
        await send.sendWithAt(
            f"未找到{msg}章节QAQ！可以使用 {cmdhead} chap help 来查询支持的名称嗷！",
            True,
        )
        return
    save = await send.getsaveResult(session)
    if not save:
        return
    song_box = {}
    # 统计各评分出现次数
    count = {
        "tot": 0,
        "phi": 0,
        "FC": 0,
        "V": 0,
        "S": 0,
        "A": 0,
        "B": 0,
        "C": 0,
        "F": 0,
        "NEW": 0,
    }
    # 统计各难度出现次数
    rank = {"EZ": 0, "HD": 0, "IN": 0, "AT": 0}
    # 统计各难度ACC和
    rankAcc = {"EZ": 0.0, "HD": 0.0, "IN": 0.0, "AT": 0.0}
    for _song in getInfo.ori_info:
        if getInfo.ori_info[_song].chapter == chap or msg == "ALL":
            song_box[_song] = {
                "illustration": await getInfo.getill(_song, "low"),
                "chart": {},
            }
            id = getInfo.idssong[_song]
            # 曲目成绩对象
            songRecord = save.getSongsRecord(id)
            info = await getInfo.info(_song, True)
            assert info
            for level in info.chart:
                # 跳过旧谱
                if not level:
                    continue
                Record = None if level not in songRecord else songRecord[level]
                song_box[_song]["chart"][level] = {
                    "difficulty": info.chart[level].difficulty,
                    "Rating": getattr(Record, "Rating", "NEW"),
                    "suggest": save.getSuggest(
                        id,
                        level,
                        4,
                        info.chart[level].difficulty,  # type: ignore
                    ),
                }
                if Record:
                    song_box[_song]["chart"][level]["score"] = Record.score
                    song_box[_song]["chart"][level]["acc"] = round(Record.acc, 4)
                    song_box[_song]["chart"][level]["rks"] = round(Record.rks, 4)
                    song_box[_song]["chart"][level]["fc"] = Record.fc
                count["tot"] += 1
                if getattr(Record, "Rating", None):
                    assert Record
                    count[Record.Rating] += 1
                    rankAcc[level] += Record.acc
                else:
                    count["NEW"] += 1
                rank[level] += 1
    progress = {
        level: rankAcc[level] / rank[level] for level in rank if rank.get(level)
    }
    await send.sendWithAt(
        await picmodle.chap(
            {
                "player": {"id": save.saveInfo.PlayerId},
                "count": count,
                "song_box": song_box,
                "progress": progress,
                "num": rank["EZ"],
                "chapName": "AllSong" if msg == "ALL" else chap,
                "chapIll": getInfo.getChapIll("AllSong" if msg == "ALL" else chap),
            }
        ),
        True,
    )


def cmpsugg(a: dict, b: dict):
    def com(difficulty, suggest):
        # 计算核心公式
        return difficulty + (min(suggest - 98, 1) ** 2) * difficulty * 0.089

    # 提取并处理数据
    s_a = float(a["suggest"].replace("%", ""))
    s_b = float(b["suggest"].replace("%", ""))

    # 计算比较值
    com_a = com(a["difficulty"], s_a)
    com_b = com(b["difficulty"], s_b)

    # 返回比较结果（正数表示a应排在b之后）
    return com_a - com_b
