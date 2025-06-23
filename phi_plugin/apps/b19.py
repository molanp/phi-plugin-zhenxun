from functools import cmp_to_key
import math
import random
import re
from typing import Literal

from nonebot_plugin_alconna import (
    Alconna,
    Args,
    Arparma,
    CommandMeta,
    MultiVar,
    on_alconna,
)
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger

from ..config import PluginConfig
from ..lib.PhigrosUser import PhigrosUser
from ..model.cls.LevelRecordInfo import LevelRecordInfo
from ..model.fCompute import fCompute
from ..model.getBanGroup import getBanGroup
from ..model.getdata import getdata
from ..model.getInfo import getInfo
from ..model.getNotes import getNotes
from ..model.getPic import pic
from ..model.picmodle import picmodle
from ..model.send import send
from ..utils import to_dict

ChallengeModeName = ["白", "绿", "蓝", "红", "金", "彩"]

Level: list = ["EZ", "HD", "IN", "AT", None]  # 存档的难度映射
cmdhead = re.escape(PluginConfig.get("cmdhead", "/phi"))

b19 = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*(b|rks|pgr|PGR|B|RKS)",
        Args["nnum", int, 33],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
)

p30 = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*(p|P)", Args["nnum", int, 33], meta=CommandMeta(compact=True)
    ),
    block=True,
    priority=5,
)

arcgrosB19 = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*(a|arc|啊|阿|批|屁|劈)",
        Args["nnum", str, "b32"],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
)

lmtAcc = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*lmtacc",
        Args["acc", float, None],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
)

singlescore = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*(score|单曲成绩)",
        Args["picversion", Literal[1, 2], 1],
        Args["song", str, None],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
)

suggest = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(suggest|推分(建议)?)", Args["input", MultiVar]),
    block=True,
    priority=5,
)

chap = on_alconna(
    Alconna(rf"re:{cmdhead}\s*chap", Args["song", MultiVar, "help"]),
    block=True,
    priority=5,
)


@b19.handle()
async def _(session: Uninfo, params: Arparma):
    if await getBanGroup.get(b19, session, "b19"):
        await send.sendWithAt(b19, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    save = await send.getsaveResult(b19, session)
    if not save:
        return
    if err := await save.checkNoInfo():
        await send.sendWithAt(
            b19, "以下曲目无信息，可能导致b19显示错误\n" + "".join(err)
        )
    nnum = params.query("nnum") or 33
    nnum = max(nnum, 33)
    nnum = min(nnum, PluginConfig.get("B19MaxNum"))
    # NOTE: 因响应器限制，暂时无法实现匹配中间消息(bksong)(取消息不可预料)
    plugin_data = await getNotes.getNotesData(session.user.id)
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(
            b19, "正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", recallTime=5
        )
    save_b19 = await save.getB19(nnum)
    stats = await save.getStats()
    money = save.gameProgress.money
    gameuser = {
        "avatar": await getdata.idgetsong(save.gameuser.avatar) or "Introduction",
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
    await send.sendWithAt(b19, res)


# FIXME: 这个和b19就多了个spInfo，后续合并一下优化代码
@p30.handle()
async def _(session: Uninfo, params: Arparma):
    if await getBanGroup.get(p30, session, "p30"):
        await send.sendWithAt(p30, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    save = await send.getsaveResult(p30, session)
    if not save:
        return
    err = await save.checkNoInfo()
    if err:
        await send.sendWithAt(
            p30, "以下曲目无信息，可能导致b19显示错误\n" + "\n".join(err)
        )
    nnum = params.query("nnum") or 33
    nnum = max(nnum, 33)
    nnum = min(nnum, PluginConfig.get("B19MaxNum"))
    # NOTE: 因响应器限制，暂时无法实现匹配中间消息(bksong)(取消息不可预料)
    plugin_data = await getNotes.getNotesData(session.user.id)
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(
            p30, "正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", recallTime=5
        )
    try:
        await getdata.buildingRecord(p30, session, PhigrosUser(save.sessionToken))
    except Exception as e:
        logger.error("p30更新存档失败", "phi-plugin", session=session, e=e)
        await send.sendWithAt(p30, "p30生成失败了...")
        return
    save_b19 = await save.getBestWithLimit(nnum, [{"type": "acc", "value": [100, 100]}])
    stats = await save.getStats()
    money = save.gameProgress.money
    gameuser = {
        "avatar": await getdata.idgetsong(save.gameuser.avatar) or "Introduction",
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
    await send.sendWithAt(p30, res)


# NOTE: arc版查分图
@arcgrosB19.handle()
async def _(session: Uninfo, params: Arparma):
    if await getBanGroup.get(arcgrosB19, session, "arcgrosB19"):
        await send.sendWithAt(arcgrosB19, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    save = await send.getsaveResult(arcgrosB19, session)
    if not save:
        return
    if err := await save.checkNoInfo():
        await send.sendWithAt(
            arcgrosB19, "以下曲目无信息，可能导致b19显示错误\n" + "\n".join(err)
        )
    nnum = params.query("nnum") or "b32"

    # 提取数字
    if isinstance(nnum, str):
        match = re.search(r"\d+", nnum)  # 匹配字符串中的第一个数字序列
        nnum = int(match.group()) if match else 32
    else:
        nnum = int(nnum)  # 确保为整数
    nnum = max(nnum, 30)
    nnum = min(nnum, PluginConfig.get("B19MaxNum"))
    plugin_data = await getNotes.getNotesData(session.user.id)
    save_b19 = await save.getB19(nnum)
    money = save.gameProgress.money
    gameuser = {
        "avatar": await getdata.idgetsong(save.gameuser.avatar) or "Introduction",
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
    await send.sendWithAt(arcgrosB19, await picmodle.arcgros_b19(data))


# NOTE: limit只对acc满分生效是正常的，符合原版js逻辑
# NOTE: 限制最低acc后的rks
@lmtAcc.handle()
async def _(session: Uninfo, params: Arparma):
    if await getBanGroup.get(lmtAcc, session, "lmtAcc"):
        await send.sendWithAt(lmtAcc, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    acc = params.query("acc") or None
    if acc is None or not isinstance(acc, float) or acc < 0 or acc > 100:
        await send.sendWithAt(
            lmtAcc,
            f"我听不懂 {acc} 是多少喵！请指定一个0-100的数字喵！\n"
            f"格式：{cmdhead} lmtacc <0-100>",
        )
        return
    save = await send.getsaveResult(lmtAcc, session)
    if not save:
        return
    if err := await save.checkNoInfo():
        await send.sendWithAt(
            arcgrosB19, "以下曲目无信息，可能导致b19显示错误\n" + "\n".join(err)
        )
    nnum = 33
    plugin_data = await getdata.getpluginData(session.user.id)
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(
            lmtAcc, "正在生成图片，请稍等一下哦！\n//·/w\\·\\\\", recallTime=5
        )
    save_b19 = await save.getBestWithLimit(nnum, [{"type": "acc", "value": [acc, 100]}])
    stats = await save.getStats()
    money = save.gameProgress.money
    gameuser = {
        "avatar": await getdata.idgetsong(save.gameuser.avatar) or "Introduction",
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
        "theme": plugin_data.get("plugin_data", {}).get("theme", "star"),
        "gameuser": gameuser,
        "stats": stats,
        "spInfo": f"ACC is limited to {acc}%",
    }
    res: list = [await picmodle.b19(to_dict(data))]
    if abs(save_b19.get("com_rks", 0) - save.saveInfo.summary.rankingScore) > 0.1:  # type: ignore
        res.append(
            f"计算rks: {save_b19['com_rks']}\n"
            f"存档rks:{save.saveInfo.summary.rankingScore}"
        )
    await send.sendWithAt(lmtAcc, res)


@singlescore.handle()
async def _(session: Uninfo, params: Arparma):
    if await getBanGroup.get(singlescore, session, "singlescore"):
        await send.sendWithAt(singlescore, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    picversion = params.query("picversion")
    song = params.query("song")
    if not song:
        await send.sendWithAt(
            singlescore, f"请指定曲名哦！\n格式：{cmdhead} score <曲名>"
        )
        return
    song = await getdata.fuzzysongsnick(song)
    if not song:
        await send.sendWithAt(
            singlescore,
            f"未找到 {song} 的有关信息哦！",
        )
        return
    save = await send.getsaveResult(singlescore, session)
    if not save:
        return
    song = song[0]
    Record = save.gameRecord
    songId = await getInfo.SongGetId(song)
    ans = Record.get(songId) if songId else None
    if not ans:
        await send.sendWithAt(
            singlescore,
            f"我不知道你关于[{song}]的成绩哦！"
            f"可以试试更新成绩哦！\n格式：{cmdhead} update",
        )
        return
    dan = await getdata.getDan(session.user.id)
    assert isinstance(dan, dict)
    data = {
        "songName": song,
        "PlayerId": save.saveInfo.PlayerId,
        "avatar": await getdata.idgetavatar(session.user.id),
        "Rks": round(save.saveInfo.summary.rankingScore, 4),
        "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "scoreData": {},
        "CLGMOD": dan.get("Dan") if dan else None,
        "EX": dan.get("EX") if dan else None,
    }
    data["illustration"] = await getInfo.getill(song)
    songsinfo = await getInfo.info(song, True)
    assert songsinfo is not None
    match picversion:
        case 2:
            for i, a in enumerate(ans):
                if a:
                    a.acc = round(a.acc, 4)
                    a.rks = round(a.rks, 4)
                    data[Level[i]] = {
                        **to_dict(ans[i]),
                        "suggest": save.getSuggest(
                            songId,
                            i,
                            4,
                            songsinfo.chart[Level[i]].difficulty,  # type: ignore # NOTE: 这里类型一定是flloat
                        ),
                    }
                else:
                    data[Level[i]] = {"Rating": "NEW"}
            await send.sendWithAt(singlescore, await picmodle.score(data, 2))
        case _:
            for i, _ in enumerate(Level):
                if not songsinfo.chart.get(Level[i]):
                    break
                data["scoreData"][Level[i]] = {
                    "difficulty": songsinfo.chart[Level[i]].difficulty
                }
            for i, a in enumerate(ans):
                if a:
                    a.acc = round(a.acc, 4)
                    a.rks = round(a.rks, 4)
                    data[Level[i]] = {
                        **to_dict(ans[i]),
                        "suggest": save.getSuggest(
                            songId,
                            i,
                            4,
                            songsinfo.chart[Level[i]].difficulty,  # type: ignore # NOTE: 这里类型一定是flloat
                        ),
                    }
                else:
                    data[Level[i]] = {"Rating": "NEW"}
            await send.sendWithAt(singlescore, await picmodle.score(data, 1))


# NOTE: 推分建议，建议的是RKS+0.01的所需值
@suggest.handle()
async def _(session: Uninfo, param: Arparma):
    if await getBanGroup.get(suggest, session, "suggest"):
        await send.sendWithAt(suggest, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    save = await send.getsaveResult(suggest, session)
    if not save:
        return
    input_ = param.query("input")
    assert input_ is not None
    # 处理范围请求
    req = fCompute.match_request(input_)
    range_ = req["range"]
    isask = req["isask"]
    scoreAsk = req["scoreAsk"]
    # 取出信息
    Record = save.gameRecord
    # 计算
    data = []
    for id in Record:
        song = await getdata.idgetsong(id)
        if not song:
            logger.warning(f"曲目无信息: {id}", "phi-plugin")
            continue
        info = await getdata.info(song, True)
        assert info is not None
        record = Record[id]
        for lv in range(4):
            if not info.chart.get(Level[lv]):
                continue
            difficulty = info.chart[Level[lv]].difficulty
            assert isinstance(difficulty, float)
            if range_[0] <= difficulty and difficulty <= range_[1] and isask[lv]:
                rlv = record[lv]
                if not rlv and not scoreAsk["NEW"]:
                    continue
                if rlv and not scoreAsk[rlv.Rating.upper()]:
                    continue
                if not rlv:
                    rlv = LevelRecordInfo()
                rlv.suggest = save.getSuggest(id, lv, 4, difficulty)
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
            suggest,
            f"谱面数量过多({len(data)})大于设置的最大值({limitnum})，只显示前{limitnum}条！",
        )
    data = data[:limitnum]
    data = sorted(data, key=cmp_to_key(cmpsugg))
    plugin_data = await getdata.getpluginData(session.user.id)
    await send.sendWithAt(
        suggest,
        await picmodle.list(
            {
                "head_title": "推分建议",
                "song": data,
                "background": await getdata.getill(random.choice(getInfo.illlist)),
                "theme": plugin_data.get("plugin_data", {}).get("theme", "star"),
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
    )


#
@chap.handle()
async def _(session: Uninfo, params: Arparma):
    if await getBanGroup.get(chap, session, "chap"):
        await send.sendWithAt(chap, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    msg = params.query("song") or ""
    if msg.upper() == "HELP" or not msg:
        await send.sendWithAt(chap, pic.getimg("chapHelp"))
        return
    chap = await fCompute.fuzzySearch(msg, getInfo.chapNick)
    chap = chap[0].get("value") if chap else ""
    if not chap and msg != "ALL":
        await send.sendWithAt(
            chap,
            f"未找到{msg}章节QAQ！可以使用 {cmdhead} chap help 来查询支持的名称嗷！",
        )
        return
    save = await send.getsaveResult(chap, session.user.id)
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
    rankAcc = {"EZ": 0, "HD": 0, "IN": 0, "AT": 0}

#         for (let song in getInfo.ori_info) {
#             if (getInfo.ori_info[song].chapter == chap || msg == 'ALL') {
#                 song_box[song] = { illustration: getInfo.getill(song, 'low'), chart: {} }
#                 let id = getInfo.idssong[song]
#                 /**曲目成绩对象 */
#                 let songRecord = save.getSongsRecord(id)
#                 let info = getInfo.info(song, true)
#                 for (let level in info.chart) {
#                     let i = LevelNum[level]
#                     /**跳过旧谱 */
#                     if (!level) continue
#                     let Record = songRecord[i]
#                     song_box[song].chart[level] = {
#                         difficulty: info.chart[level].difficulty,
#                         Rating: Record?.Rating || 'NEW',
#                         suggest: save.getSuggest(id, i, 4, info.chart[level].difficulty)
#                     }
#                     if (Record) {
#                         song_box[song].chart[level].score = Record.score
#                         song_box[song].chart[level].acc = Record.acc.toFixed(4)
#                         song_box[song].chart[level].rks = Record.rks.toFixed(4)
#                         song_box[song].chart[level].fc = Record.fc
#                     }
#                     ++count.tot
#                     if (Record?.Rating) {
#                         ++count[Record.Rating]
#                         rankAcc[level] += Number(Record.acc || 0)
#                     } else {
#                         ++count.NEW
#                     }
#                     ++rank[level]
#                 }
#             }
#         }

#         let progress = {}
#         for (let level in rank) {
#             if (rank[level]) {
#                 progress[level] = rankAcc[level] / rank[level]
#             }
#         }

#         send.send_with_At(e, await altas.chap(e, {
#             player: { id: save.saveInfo.PlayerId },
#             count,
#             song_box,
#             progress,
#             num: rank.EZ,
#             chapName: msg == 'ALL' ? 'AllSong' : chap,
#             chapIll: getInfo.getChapIll(msg == 'ALL' ? 'AllSong' : chap),
#         }))

#     }
# }


def cmpsugg(a, b):
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
