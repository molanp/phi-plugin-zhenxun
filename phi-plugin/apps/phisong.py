"""phigros图鉴"""

import asyncio
import math
import random
import re
from typing import Any, Literal

from arclet.alconna import StrMulti
from nonebot_plugin_alconna import (
    Alconna,
    AlconnaQuery,
    Args,
    CommandMeta,
    Match,
    Option,
    Query,
    Target,
    on_alconna,
    store_true,
)
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_waiter import prompt

from zhenxun.utils.message import MessageUtils
from zhenxun.utils.rules import admin_check, ensure_group

from ..config import PluginConfig, Version, cmdhead, recmdhead
from ..model.cls.Chart import Chart
from ..model.cls.SongsInfo import SongsInfoObject
from ..model.constNum import Level, LevelNum
from ..model.fCompute import fCompute, match_request_return
from ..model.getChartTag import getChartTag
from ..model.getComment import getComment
from ..model.getdata import getdata
from ..model.getFile import readFile
from ..model.getInfo import getInfo
from ..model.getPic import pic
from ..model.getSave import getSave
from ..model.path import configPath
from ..model.picmodle import picmodle
from ..model.send import send
from ..utils import can_be_call, to_dict

wait_to_del_comment = {}

song = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(曲|song)",
        Args["songname?", str],
        Option("-comment", action=store_true),
        Option("-p", Args["_page?", int, 1]),
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("song"),
)
search = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(查找|检索|search)",
        Args["_input", StrMulti],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("search"),
)

setnick = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(设置别名|setnic(k?))",
        Args["_old_nick?", str]["_new_nick?", str],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=admin_check(5),
)

delnick = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(删除别名|delnic(k?))",
        Args["_nick", str],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=admin_check(5),
)

ill = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(曲绘|ill|Ill)",
        Args["songname?", str],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("ill"),
)
randClg = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*randclg",
        Args["_input", StrMulti],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("randClg"),
)
randmic = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(随机|rand(om)?)",
        Args["_input", StrMulti],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("randmic"),
)
alias = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*alias",
        Args["songname", str],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("alias"),
)
comrks = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(com|计算)",
        Args["_rks?", float]["_acc?", float],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("comrks"),
)
tips = on_alconna(
    Alconna(rf"re:{recmdhead}\s*tips"), block=True, priority=5, rule=can_be_call("tips")
)
newSong = on_alconna(
    Alconna(rf"re{recmdhead}\s*new"),
    block=True,
    priority=5,
    rule=can_be_call("newSong"),
)
table = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(定数表|table)",
        Args["_t?", int],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("table"),
)
comment = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(comment|cmt|评论|评价)",
        Args["content?", StrMulti],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("comment"),
)
recallComment = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*recmt", Args["objId?", int], meta=CommandMeta(compact=True)
    ),
    block=True,
    priority=5,
    rule=can_be_call("recallComment"),
)
myComment = on_alconna(
    Alconna(rf"re:{recmdhead}\s*mycmt"),
    block=True,
    priority=5,
    rule=can_be_call("myComment"),
)
chart = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*chart",
        Args["songname", str]["_rank", str],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("chart"),
)
addtag = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*addtag", Args["songname", str]["_rank", str]["_tag", str]
    ),
    block=True,
    priority=5,
    rule=can_be_call("addtag"),
)
subtag = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*subtag", Args["songname", str]["_rank", str]["_tag", str]
    ),
    block=True,
    priority=5,
    rule=can_be_call("subtag"),
)
retag = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*retag", Args["songname", str]["_rank", str]["_tag", str]
    ),
    block=True,
    priority=5,
    rule=can_be_call("retag"),
)


@song.handle()
async def _(
    songname: Match[str],
    _page: Match[int],
    comment: Query[bool] = AlconnaQuery("comment.value", False),
):
    """歌曲图鉴"""
    song = songname.result if songname.available else None
    page = _page.result if _page.available else 1
    addComment = comment.result if comment.available else False

    if not song:
        await send.sendWithAt(f"请指定曲名哦！\n格式：{cmdhead} song <曲名>")
        return
    songs = await getInfo.fuzzysongsnick(song)
    if songs:
        if len(songs) > 1:
            msgRes = f"找到了{len(songs)}首歌曲！"
            for i in songs:
                msgRes += f"\n{getInfo.SongGetId(i) or i}"
            msgRes += f"\n请发送 {cmdhead} song <曲目id> 来查看详细信息！"
        else:
            songs = songs[0]
            infoData = await getInfo.info(songs)
            assert infoData
            data = to_dict(infoData)
            if PluginConfig.get("allowComment") and (addComment or page):
                commentData = await getComment.getBySongId(infoData.id)
                for item in commentData:
                    save = await getSave.getSaveBySessionToken(item.sessionToken)
                    if not save:
                        await getComment.delete(item.commentId)
                        del commentData[commentData.index(item)]
                        continue
                    item.comment = fCompute.convertRichText(item.comment)
                commentsAPage: int = PluginConfig.get("commentsAPage")
                maxPage = math.ceil(len(commentData) / commentsAPage)
                page = max(min(page, maxPage), 1)
                data["comment"] = {
                    "command": (
                        f"当前共有{len(commentData)}条评论，第{page}页，共{maxPage}页，"
                        f"发送{cmdhead} cmt <曲名> <定级?>(换行)<内容> 进行评论，"
                        "-p <页码> 选择页数"
                    ),
                    "list": to_dict(
                        commentData[
                            commentsAPage * (page - 1) : commentsAPage * page - 1
                        ]
                    ),
                }
            msgRes = await picmodle.atlas(data)
        await send.sendWithAt(msgRes)
    else:
        await send.sendWithAt(
            f"未找到{song}的相关曲目信息QAQ\n如果想要提供别名的话请访问"
            f" {cmdhead}help 中的别名投稿链接嗷！",
            True,
        )


@search.handle()
async def _(session: Uninfo, _input: Match):
    msg = _input.result if _input.available else ""
    msg = msg.lower()

    patterns: dict[Literal["bpm", "difficulty", "combo"], Any] = {
        "bpm": {
            "regex": re.compile(r"bpm[\s:：,，/|~是为]*([0-9]+(?:\s*-\s*[0-9]+)?)"),
            "predicate": lambda item, b, t: item.bpm and b <= item.bpm <= t,
        },
        "difficulty": {
            "regex": re.compile(
                r"(?:difficulty|dif|定数|难度|定级)[\s:：,，/|~是为]*([0-9.]+(?:\s*-\s*[0-9.]+)?)"
            ),
            "predicate": lambda item, b, t: item.chart
            and any(b <= level.difficulty <= t for level in item.chart.values()),
        },
        "combo": {
            "regex": re.compile(
                r"(?:combo|cmb|物量|连击)[\s:：,，/|~是为]*([0-9]+(?:\s*-\s*[0-9]+)?)"
            ),
            "predicate": lambda item, b, t: item.get("chart")
            and any(b <= level.combo <= t for level in item.chart.values()),
        },
    }
    remain = await getdata.info()
    result: dict[str, SongsInfoObject] = {}
    filters: dict[Literal["bpm", "difficulty", "combo"], tuple[float, float]] = {}

    # 处理每个模式
    for key, pattern in patterns.items():
        if match := pattern["regex"].search(msg):
            # 处理匹配结果
            match_str = match.group(1)
            match_str = re.sub(
                r"(?:bpm|difficulty|dif|难度|定级|定数|combo|cmb|物量|连击)[\s:：,，/|~是为]*",
                "",
                match_str,
            )

            # 解析范围
            if "-" in match_str:
                bottom, top = sorted(map(float, match_str.split("-")))
            else:
                bottom = top = float(match_str)

            if key == "difficulty" and ".0" not in match_str and top % 1 == 0:
                top += 0.9
            filters[key] = (bottom, top)
            for i, v in remain.items():
                if pattern["predicate"](v, bottom, top):
                    result[i] = v
            remain = result
            result = {}
    bpm_par = ""
    difficulty_par = ""
    combo_par = ""
    if v := filters.get("bpm"):
        bpm_par = f"BPM:{v[0]}"
        if v[1]:
            bpm_par += f"-{v[1]}"
    if v := filters.get("difficulty"):
        difficulty_par = f"定级:{v[0]}"
        if v[1]:
            difficulty_par += f"-{v[1]}"
    if v := filters.get("combo"):
        combo_par = f"物量:{v[0]}"
        if v[1]:
            combo_par += f"-{v[1]}"
    if PluginConfig.get("isGuild"):
        Resmsg = []
        tot = 0
        count = 0
        single = f"当前筛选：\n{bpm_par}\n{difficulty_par}\n{combo_par}"
        for i, song in remain.items():
            msg = f"\n{i} BPM:{song.bpm}" if count else f"{i} BPM:{song.bpm}"
            for level, c in song.chart.items():
                msg += f"<{level}> {c.difficulty} {c.combo}"
            single += msg
            tot += 1
            count += 1
            # 每条消息10行
            if count == 10:
                Resmsg.append(single)
                single = ""
                count = 0
        if count:
            Resmsg.append(single)
            count = 0
        if ensure_group(session):
            await send.sendWithAt(f"找到了{tot}个结果，自动转为私聊发送喵～", True)
            await MessageUtils.alc_forward_msg(
                Resmsg,
                session.user.id,
                str(session.user.name),
            ).send(target=Target(session.user.id, private=True))
        else:
            await MessageUtils.alc_forward_msg(
                Resmsg,
                session.user.id,
                str(session.user.name),
            ).send()
    else:
        Resmsg = [f"当前筛选：\n{bpm_par}\n{difficulty_par}\n{combo_par}"]
        for i, song in remain.items():
            msg = f"{i}\nBPM:{song.bpm}"
            for level, c in song.chart.items():
                msg += f"<{level}> {c.difficulty} {c.combo}"
            Resmsg.append(msg)
        await MessageUtils.alc_forward_msg(
            Resmsg,
            session.user.id,
            str(session.user.name),
        ).send()
        await send.sendWithAt(f"找到了{len(Resmsg) - 1}首曲目喵！")


@setnick.handle()
async def _(_old_nick: Match[str], _new_nick: Match[str]):
    """设置别名"""
    msg = (
        _old_nick.result if _old_nick.available else "",
        _new_nick.result if _new_nick.available else "",
    )
    if msg[1]:
        mic = await getdata.fuzzysongsnick(msg[0], 1)
        if mic:
            mic = mic[0]
        else:
            await send.sendWithAt(f"输入有误哦！没有找到“{msg[0]}”这首曲子呢！")
            return
        if mic in await getdata.fuzzysongsnick(msg[1], 1):
            # 已经添加过该别名
            await send.sendWithAt(f"{mic} 已经有 {msg[1]} 这个别名了哦！")
            return
        else:
            await getdata.setnick(mic, msg[1])
            await send.sendWithAt("设置完成！")
    else:
        await send.sendWithAt(
            "输入有误哦！请按照\n原名(或已有别名) 别名\n的格式发送哦！"
        )


@delnick.handle()
async def _(session: Uninfo, _nick: Match[str]):
    nick = _nick.result if _nick.available else ""
    anss: dict[str, list] = await readFile.FileReader(configPath / "nickconfig.yaml")
    if ans := anss.get(nick):
        if len(ans) == 1:
            del anss[nick]
            await readFile.SetFile(configPath / "nickconfig.yaml", anss)
            await send.sendWithAt("删除成功！")
        else:
            wait_to_del_list = ans
            wait_to_del_nick = nick
            Remsg = ["找到了多个别名！请发送 序号 进行选择！"]
            Remsg.extend(f"#{i}\n{wait_to_del_list[i]}" for i in wait_to_del_list)
            await MessageUtils.alc_forward_msg(
                Remsg, session.user.id, str(session.user.name)
            ).send()
            await send.sendWithAt("找到了多个结果！")
            r = await prompt("", timeout=30)
            if r is None:
                await send.sendWithAt("操作已取消", True)
                return
            await choosesdelnick(
                anss, wait_to_del_list, wait_to_del_nick, r.extract_plain_text().strip()
            )
    else:
        await send.sendWithAt(f"未找到 {nick} 所对应的别名哦！")


async def choosesdelnick(anss, wait_to_del_list, wait_to_del_nick, choose):
    if choose in wait_to_del_list:
        del wait_to_del_list[choose]
        anss[wait_to_del_nick] = wait_to_del_list
        await readFile.SetFile(configPath / "nickconfig.yaml", anss)
        await send.sendWithAt("删除成功！")
    else:
        await send.sendWithAt(f"未找到 {choose} 所对应的别名哦！")


@ill.handle()
async def _(session: Uninfo, songname: Match[str]):
    msg = songname.result if songname.available else None
    if not msg:
        await send.sendWithAt(f"请指定曲名哦！\n格式：{cmdhead} ill <曲名>")
        return
    songs = await getdata.fuzzysongsnick(msg)
    if songs:
        if len(songs) >= 1:
            msgRes = []
            for song in songs:
                msgRes.append(await getdata.GetSongsIllAtlas(song))
            await MessageUtils.alc_forward_msg(
                msgRes, session.user.id, str(session.user.name)
            ).send()
            await send.sendWithAt(f"找到了{len(songs)}首歌曲！")
        else:
            song = songs[0]
            await send.sendWithAt(await getdata.GetSongsIllAtlas(song))
    else:
        await send.sendWithAt(f"未找到{msg}的相关曲目信息QAQ", True)


@randmic.handle()
async def _(_input: Match):
    """随机定级范围内曲目"""
    msg = _input.result if _input.available else ""
    msg = msg.upper()
    isask = [False, False, False, False]
    if "EZ" in msg:
        msg.replace("EZ", "")
        isask[0] = True
    if "HD" in msg:
        msg.replace("HD", "")
        isask[1] = True
    if "IN" in msg:
        msg.replace("IN", "")
        isask[2] = True
    if "AT" in msg:
        msg.replace("AT", "")
        isask[3] = True
    if rank := msg.strip().split("-"):
        if "+" in rank[0]:
            if len(rank) > 1:
                await send.sendWithAt(
                    f"含有 '+' 的难度不支持指定范围哦！\n{cmdhead} "
                    "rand <定数>+ <难度(可多选)>",
                    True,
                )
                return
            else:
                rank[0] = Number(rank[0].replace("+", ""))  # type: ignore
                if rank[0] == float("NaN"):
                    await send.sendWithAt(
                        f"{rank[0]} 不是一个定级哦\n{cmdhead} "
                        "rand <定数>- <难度(可多选)>",
                        True,
                    )
                    return
                bottom: float = rank[0]  # type: ignore
                top = 100
        elif "-" in rank[0] and len(rank) == 1:
            rank[0] = Number(rank[0].replace("-", ""))  # type: ignore
            if rank[0] == float("NaN"):
                await send.sendWithAt(
                    f"{rank[0]} 不是一个定级哦\n{cmdhead} rand <定数>- <难度(可多选)>",
                    True,
                )
                return
            else:
                bottom = 0
                top = rank[0]
        else:
            rank[0] = Number(rank[0])  # type: ignore
            if len(rank) > 1:
                rank[1] = Number(rank[1])  # type: ignore
                if rank[0] == float("NaN") or rank[1] == float("NaN"):
                    await send.sendWithAt(
                        f"{rank[0]} - {rank[1]} 不是一个定级范围哦\n"
                        f"{cmdhead} rand <定数1> - <定数2> <难度(可多选)>",
                        True,
                    )
                    return
                top = max(rank[0], rank[1])
                bottom = min(rank[0], rank[1])  # type: ignore
            elif rank[0] == float("NaN"):
                await send.sendWithAt(
                    f"{rank[0]} 不是一个定级哦\n{cmdhead} rand <定数> <难度(可多选)>",
                    True,
                )
                return
            else:
                top = bottom = rank[0]  # type: ignore
    else:
        top = 100
        bottom = 0

    if top % 1 == 0 and ".0" in msg:
        top += 0.9  # type: ignore
    songsname = []
    for i, obj in getInfo.ori_info.items():
        for level, lv in LevelNum.items():
            if level < len(isask) and isask[level] and lv in obj.chart:
                difficulty = obj.chart[lv].difficulty
                if difficulty >= bottom and difficulty <= top:  # type: ignore
                    songsname.append(
                        {
                            **to_dict(obj.chart[lv]),
                            "rank": lv,
                            "illustration": await getdata.getill(i),
                            "song": obj.song,
                            "illustrator": obj.illustrator,
                            "composer": obj.composer,
                        }
                    )
    if not songsname:
        await send.sendWithAt(
            f"未找到 {bottom} - {top} 的 "
            f"{Level[0] if isask[0] else ''}{Level[1] if isask[1] else ''}"
            f"{Level[2] if isask[2] else ''}{Level[3] if isask[3] else ''}谱面QAQ!"
        )
        return
    result = random.choice(songsname)
    await send.sendWithAt(await getdata.getrand(result))


@alias.handle()
async def _(songname: Match[str]):
    """查询歌曲别名"""
    msg = songname.result if songname.available else ""
    song = getInfo.idgetsong(msg) or await getInfo.fuzzysongsnick(msg)
    if song:
        if isinstance(song, list):
            song = song[0]
        info = await getInfo.info(song)
        assert info
        nick = "======================\n已有别名：\n"
        anss: dict[str, list] = await readFile.FileReader(
            configPath / "nickconfig.yaml"
        )
        if usernick := anss.get(song):
            nick += "\n".join(usernick) + "\n"
        if v := getInfo.nicklist.get(info.song):
            nick += "\n".join(v)
        await send.sendWithAt(
            [f"\nname: {song[0]}\nid: {info.id}\n", await pic.getIll(song[0]), nick]
        )
    else:
        await send.sendWithAt(
            f"未找到{msg}的相关曲目信息QAQ！如果想要提供别名的话请访问"
            f" {cmdhead}help 中的别名投稿链接嗷！",
            True,
        )


#     /**计算等效rks */
#     async comrks(e) {

#         if (await getBanGroup.get(e, 'comrks')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let msg = e.msg.replace(/^[#/].*(com|计算)\s*/, '')
#         let data = msg.split(' ')
#         data[0] = Number(data[0])
#         data[1] = Number(data[1])
#         if (data && data[1] && data[0] > 0 && data[0] <= 18 && data[1] > 0 && data[1] <= 100) {
#             send.send_with_At(e, `dif: ${data[0]} acc: ${data[1]}\n计算结果：${fCompute.rks(Number(data[1]), Number(data[0]))}`, true)
#             return true
#         } else {
#             send.send_with_At(e, `格式错误QAQ！\n格式：${Config.getUserCfg('config', 'cmdhead')} com <定数> <acc>`)
#             return false
#         }
#     }

#     /**随机tips */
#     async tips(e) {

#         if (await getBanGroup.get(e, 'tips')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         send.send_with_At(e, getInfo.tips[fCompute.randBetween(0, getInfo.tips.length - 1)])
#     }

#     async randClg(e) {
#         if (await getBanGroup.get(e, 'randclg')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let songReg = /[\(（].*[\)）]/
#         let songReq = ""
#         let arg = e.msg.replace(/^.*randclg\s*/, '')
#         // console.info(arg.match(songReg))
#         if (arg.match(songReg)) {
#             songReq = arg.match(songReg)[0].replace(/[\(\)（）]/g, "")
#             arg = arg.replace(arg.match(songReg)[0], "")
#         }

#         let songAsk = fCompute.match_request(songReq)

#         // console.info(songAsk, songReq)

#         let { isask, range } = fCompute.match_request(arg, 48)

#         let NumList = []
#         for (let i = range[0]; i <= range[1]; i++) {
#             NumList.push(i)
#         }

#         let chartList = {}
#         for (let dif in getInfo.info_by_difficulty) {
#             if (Number(dif) < range[1]) {
#                 for (let i in getInfo.info_by_difficulty[dif]) {
#                     let chart = getInfo.info_by_difficulty[dif][i]
#                     let difficulty = Math.floor(chart.difficulty)
#                     if (isask[LevelNum[chart.rank]] && chartMatchReq(songAsk, chart)) {
#                         if (chartList[difficulty]) {
#                             chartList[difficulty].push(chart)
#                         } else {
#                             chartList[difficulty] = [chart]
#                         }
#                     }
#                 }
#             }
#         }

#         NumList = fCompute.randArray(NumList)


#         let res = randClg(NumList.shift(), { ...chartList })
#         while (!res && NumList.length) {
#             res = randClg(NumList.shift(), { ...chartList })
#         }
#         // console.info(res)
#         if (res) {

#             let songs = []

#             let plugin_data = await get.getpluginData(e.user_id)

#             for (let i in res) {
#                 let info = getInfo.info(getInfo.idgetsong(res[i].id))
#                 songs.push({
#                     id: info.id,
#                     song: info.song,
#                     rank: res[i].rank,
#                     difficulty: res[i].difficulty,
#                     illustration: getInfo.getill(info.song),
#                     ...info.chart[res[i].rank]
#                 })
#             }

#             send.send_with_At(e, await picmodle.common(e, 'clg', {
#                 songs,
#                 tot_clg: Math.floor(res[0].difficulty) + Math.floor(res[1].difficulty) + Math.floor(res[2].difficulty),
#                 background: getInfo.getill(getInfo.illlist[Number((Math.random() * (getInfo.illlist.length - 1)).toFixed(0))], 'blur'),
#                 theme: plugin_data?.plugin_data?.theme || 'star',
#             }))

#             // ans += `${getInfo.idgetsong(res[0].id)} ${res[0].rank} ${res[0].difficulty}\n`
#             // ans += `${getInfo.idgetsong(res[1].id)} ${res[1].rank} ${res[1].difficulty}\n`
#             // ans += `${getInfo.idgetsong(res[2].id)} ${res[2].rank} ${res[2].difficulty}\n`
#             // ans += `difficulty: ${Math.floor(res[0].difficulty) + Math.floor(res[1].difficulty) + Math.floor(res[2].difficulty)}`
#         } else {
#             send.send_with_At(e, `未找到符合条件的谱面QAQ！`)
#         }

#         return true;
#     }

#     async newSong(e) {

#         if (await getBanGroup.get(e, 'newSong')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }
#         let ans = ''
#         try {
#             let info = await (await fetch(Config.getUserCfg('config', 'phigrousUpdateUrl'))).json()
#             ans += `最新版本：${info?.data?.list?.[0]?.version_label}\n更新信息：\n${info?.data?.list?.[0]?.whatsnew?.text?.replace(/<\/?div>/g, '')?.replace(/<br\/>/g, '\n')}\n`
#         } catch (e) { }
#         ans += `信息文件版本：${Version.phigros}\n`
#         ans += '新曲速递：\n'
#         for (let i in getInfo.updatedSong) {
#             let info = getInfo.info(getInfo.updatedSong[i])
#             ans += `${info.song}\n`
#             for (let j in info.chart) {
#                 ans += `  ${j} ${info.chart[j].difficulty} ${info.chart[j].combo}\n`
#             }
#         }

#         ans += '\n定数&谱面修改：\n'
#         for (let song in getInfo.updatedChart) {
#             let tem = getInfo.updatedChart[song]
#             ans += song + '\n'
#             for (let level in tem) {
#                 ans += `  ${level}:\n`
#                 if (tem[level].isNew) {
#                     delete tem[level].isNew
#                     for (let obj in tem[level]) {
#                         ans += `    ${obj}: ${tem[level][obj][0]}\n`
#                     }
#                 } else {
#                     for (let obj in tem[level]) {
#                         ans += `    ${obj}: ${tem[level][obj][0]} -> ${tem[level][obj][1]}\n`
#                     }
#                 }
#             }
#         }

#         // getFile.SetFile('updatedSong.txt', ans, 'TXT')

#         if (ans.length > 500) {
#             send.send_with_At(e, '新曲速递内容过长，请试图查阅其他途径！', true)
#             return false
#         }

#         send.send_with_At(e, ans)
#     }

#     async table(e) {

#         if (await getBanGroup.get(e, 'table')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let dif = Number(e.msg.match(/[0-9]+/)?.[0])

#         if (!dif) {
#             send.send_with_At(e, `请输入定数嗷！\n/格式：${Config.getUserCfg('config', 'cmdhead')} table <定数>`, true)
#             return false
#         }


#         send.send_with_At(e, segment.image(getInfo.getTableImg(dif)))

#     }

#     async comment(e) {

#         if (await getBanGroup.get(e, 'comment') || !(await Config.getUserCfg('config', 'allowComment'))) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let save = await send.getsave_result(e);

#         if (!save) {
#             return true
#         }

#         let msg = e.msg.replace(/[#/](.*?)(comment|cmt|评论|评价)(\s*)/, "");
#         if (!msg) {
#             send.send_with_At(e, `请指定曲名哦！\n格式：\n/${Config.getUserCfg('config', 'cmdhead')} cmt <曲名> <难度?>(换行)\n<内容>`)
#             return true
#         }

#         /**
#          * @type {allLevelKind}
#          */
#         let rankKind = msg.match(/ (EZ|HD|IN|AT|LEGACY)\s*\n/i)?.[1] || ''
#         rankKind = rankKind.toUpperCase()
#         let rankNum = 0;
#         switch (rankKind) {
#             case 'EZ':
#                 rankNum = 0;
#                 break;
#             case 'HD':
#                 rankNum = 1;
#                 break;
#             case 'IN':
#                 rankNum = 2;
#                 break;
#             case 'AT':
#                 rankNum = 3;
#                 break;
#             case 'LGC':
#             case 'LEGACY':
#                 rankNum = 4;
#                 break;
#             default:
#                 rankNum = -1;
#         }

#         let nickname = msg.replace(/( (EZ|HD|IN|AT|LEGACY))?\s*\n[\s\S]*?$/i, '')

#         let song = getInfo.fuzzysongsnick(nickname)?.[0]

#         if (!song) {
#             send.send_with_At(e, `未找到${nickname}的相关曲目信息QAQ\n如果想要提供别名的话请访问 /phihelp 中的别名投稿链接嗷！`, true)
#             return true;
#         }
#         let songInfo = getInfo.info(song)
#         if (!songInfo.sp_vis) {
#             if (!rankKind) {
#                 rankKind = 'IN';
#                 rankNum = 2;
#             } else if (rankNum == -1) {
#                 send.send_with_At(e, `${rankKind} 不是一个难度QAQ！`);
#                 return true;
#             } else if (!songInfo.chart[rankKind]) {
#                 send.send_with_At(e, `${song} 没有 ${rankKind} 这个难度QAQ！`);
#                 return true;
#             }
#         } else {
#             rankKind = 'IN';
#         }
#         /** @type {string} */
#         let comment = msg.match(/\n([\s\S]*)/)?.[1];
#         if (!comment) {
#             send.send_with_At(e, `不可发送空白内容w(ﾟДﾟ)w！`)
#             return true
#         }
#         if (comment.length > 1000) {
#             send.send_with_At(e, `太长了吧！你想干嘛w(ﾟДﾟ)w！`)
#             return true
#         }

#         let songId = songInfo.id;

#         if (Config.getUserCfg('config', 'openPhiPluginApi')) {
#             try {
#                 /**@type {commentObject} */
#                 let cmtobj = {
#                     songId: songInfo.id,
#                     rank: rankKind,
#                     apiUserId: save.apiId,
#                     rks: save.saveInfo.summary.rankingScore,
#                     score: 0,
#                     acc: 0,
#                     fc: 0,
#                     challenge: save.saveInfo.summary.challengeModeRank,
#                     time: new Date(),
#                     comment: comment
#                 };
#                 let songRecord = save.getSongsRecord(songId);
#                 if (!songInfo.sp_vis && songRecord?.[rankNum]) {
#                     let { phi, b19_list } = await save.getB19(27)
#                     let spInfo = '';

#                     for (let i = 0; i < phi.length; ++i) {
#                         if (phi[i].id == songId && phi[i].rank == rankKind) {
#                             spInfo = `Perfect ${i + 1}`;
#                             break;
#                         }
#                     }
#                     if (!spInfo && songRecord[rankNum].score == 1000000) {
#                         spInfo = 'All Perfect';
#                     }
#                     for (let i = 0; i < b19_list.length; ++i) {
#                         if (b19_list[i].id == songId && b19_list[i].rank == rankKind) {
#                             spInfo = spInfo ? spInfo + ` & Best ${i + 1}` : `Best ${i + 1}`;
#                             break;
#                         }
#                     }
#                     cmtobj = {
#                         ...cmtobj,
#                         score: songRecord[rankNum].score,
#                         acc: songRecord[rankNum].acc,
#                         fc: songRecord[rankNum].fc,
#                         spInfo,
#                     }
#                 };
#                 await makeRequest.addComment({
#                     ...makeRequestFnc.makePlatform(e),
#                     comment: cmtobj
#                 });
#                 send.send_with_At(e, `在线评论成功！φ(゜▽゜*)♪`);
#                 return true;
#             } catch (error) {
#                 logger.warn(`[phi-plugin] API评论失败`, error)
#             }
#         }

#         if (!save.session && !(await getSave.get_user_token(e.user_id))) {
#             send.send_with_At(e, `暂不支持通过API绑定的用户进行评论哦！`)
#             return true
#         }

#         let cmtobj = {
#             sessionToken: save.session,
#             userObjectId: save.saveInfo.objectId,
#             rks: save.saveInfo.summary.rankingScore,
#             rank: rankKind,
#             score: 0,
#             acc: 0,
#             fc: false,
#             challenge: save.saveInfo.summary.challengeModeRank,
#             comment: comment
#         };
#         let songRecord = save.getSongsRecord(songId);
#         if (!songInfo.sp_vis && songRecord?.[rankNum]) {
#             let { phi, b19_list } = await save.getB19(27)
#             let spInfo = '';

#             for (let i = 0; i < phi.length; ++i) {
#                 if (phi[i].id == songId && phi[i].rank == rankKind) {
#                     spInfo = `Perfect ${i + 1}`;
#                     break;
#                 }
#             }
#             if (!spInfo && songRecord[rankNum].score == 1000000) {
#                 spInfo = 'All Perfect';
#             }
#             for (let i = 0; i < b19_list.length; ++i) {
#                 if (b19_list[i].id == songId && b19_list[i].rank == rankKind) {
#                     spInfo = spInfo ? spInfo + ` & Best ${i + 1}` : `Best ${i + 1}`;
#                     break;
#                 }
#             }
#             cmtobj = {
#                 ...cmtobj,
#                 score: songRecord[rankNum].score,
#                 acc: songRecord[rankNum].acc,
#                 fc: songRecord[rankNum].fc,
#                 spInfo,
#             }
#         };
#         if (getComment.add(songId, cmtobj)) {
#             send.send_with_At(e, `评论成功！φ(゜▽゜*)♪`);
#         } else {
#             send.send_with_At(e, `遇到未知错误QAQ！`);
#         }

#         return true;
#     }

#     async recallComment(e) {
#         if (await getBanGroup.get(e, 'recallComment') || !(await Config.getUserCfg('config', 'allowComment'))) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }
#         let save;
#         if (!e.isMaster) {
#             save = await send.getsave_result(e);
#             if (!save) {
#                 return true;
#             }
#         }

#         let commentId = e.msg.match(/[0-9]+/)?.[0];

#         if (!commentId) {
#             send.send_with_At(e, `请输入评论ID嗷！\n格式：/${Config.getUserCfg('config', 'cmdhead')} recmt <评论ID>`);
#             return true;
#         }

#         let comment = getComment.getByCommentId(commentId)
#         if (!comment) {
#             if (Config.getUserCfg('config', 'openPhiPluginApi')) {
#                 try {
#                     await makeRequest.delComment({ ...makeRequestFnc.makePlatform(e), comment_id: commentId });
#                     send.send_with_At(e, `删除在线评论成功！φ(゜▽゜*)♪`);
#                     return true;
#                 } catch (error) {
#                     logger.warn(`[phi-plugin] API删除评论失败`, error)
#                 }
#             }
#             send.send_with_At(e, `没有找到ID为${commentId}的评论QAQ！`);
#             return true;
#         }

#         if (!e.isMaster && !(comment.sessionToken == save.session || comment.userObjectId == save.saveInfo.objectId)) {
#             send.send_with_At(e, `您没有权限操作这条评论捏(。﹏。)`);
#             return true;
#         }

#         getComment.del(commentId) ?
#             send.send_with_At(e, `删除成功！`) :
#             send.send_with_At(e, `删除失败QAQ！`);
#     }

#     async myComment(e) {
#         if (await getBanGroup.get(e, 'myComment')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let save = await send.getsave_result(e);

#         if (!save) {
#             return true
#         }

#         if (Config.getUserCfg('config', 'openPhiPluginApi') && (save.session || save.apiId)) {
#             try {
#                 const comments = await makeRequest.getCommentsByUserId(makeRequestFnc.makePlatform(e));

#                 if (comments && comments.length > 0) {
#                     let msg = `您的评论列表：\nID | 曲目 | 难度 | 内容 | 时间\n`;
#                     for (let comment of comments) {
#                         msg += `${comment.id} | ${comment.songId} | ${comment.rank} | ${comment.comment} | ${fCompute.date_to_string(comment.time)}\n`
#                     }
#                     send.send_with_At(e, msg);
#                 } else {
#                     send.send_with_At(e, `您还没有评论哦！`);
#                 }
#                 return true;
#             } catch (error) {
#                 logger.warn(`[phi-plugin] 获取用户评论失败`, error)
#             }
#         }
#         return false;
#     }

#     async chart(e) {
#         if (await getBanGroup.get(e, 'chart')) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         let msg = e.msg.replace(/[#/](.*?)(chart)(\s*)/, "")

#         /** @type {levelKind} */
#         let rank = msg.match(/\s+(EZ|HD|IN|AT)/i)?.[1] || 'IN'
#         rank = rank.toUpperCase()
#         msg = msg.replace(/\s+(EZ|HD|IN|AT)/i, '')

#         let song = getInfo.fuzzysongsnick(msg)?.[0]
#         if (!song) {
#             send.send_with_At(e, `未找到${msg}的相关曲目信息QAQ！如果想要提供别名的话请访问 /phihelp 中的别名投稿链接嗷！`, true)
#             return true
#         }
#         let info = getInfo.info(song, true)
#         if (!info.chart[rank]) {
#             send.send_with_At(e, `${song} 没有 ${rank} 这个难度QAQ！`)
#             return true
#         }

#         let chart = info.chart[rank]

#         let allowChartTag = await Config.getUserCfg('config', 'allowChartTag')

#         let data = {
#             illustration: info.illustration,
#             song: info.song,
#             length: info.length,
#             rank: rank,
#             difficulty: chart.difficulty,
#             charter: chart.charter,
#             tap: chart.tap,
#             drag: chart.drag,
#             hold: chart.hold,
#             flick: chart.flick,
#             combo: chart.combo,
#             distribution: chart.distribution,
#             tip: allowChartTag ? `发送 /${Config.getUserCfg('config', 'cmdhead')} addtag <曲名> <难度> <tag> 来添加标签哦！` : `标签词云功能暂时被管理员禁用了哦！快去联系BOT主开启吧！`,
#             chartLength: `${Math.floor(chart.maxTime / 60)}:${Math.floor(chart.maxTime % 60).toString().padStart(2, '0')}`,
#             words: allowChartTag ? getChartTag.get(info.id, rank) : '',
#         }
#         e.reply(await picmodle.common(e, 'chartInfo', data))
#     }

#     async addtag(e) {
#         if (await getBanGroup.get(e, 'addtag') || !(await Config.getUserCfg('config', 'allowChartTag'))) {
#             send.send_with_At(e, '这里被管理员禁止使用这个功能了呐QAQ！')
#             return false
#         }

#         /** @type {'addtag'|'subtag'|'retag'} */
#         let op = e.msg.match(/(addtag|subtag|retag)/i)?.[1]

#         let msg = e.msg.replace(/[#/](.*?)(addtag|subtag|retag)(\s*)/, "")

#         /** @type {levelKind} */
#         let rank = msg.match(/\s+(EZ|HD|IN|AT)\s+/i)?.[1] || 'IN'
#         rank = rank.toUpperCase()
#         msg = msg.replace(/\s+(EZ|HD|IN|AT)/i, '')

#         let tag = msg.match(/(?<=\s)[^\s]+$/)?.[0]
#         if (!tag) {
#             send.send_with_At(e, `请输入标签哦！\n格式：/${Config.getUserCfg('config', 'cmdhead')} ${op} <曲名> <rank> <tag>`)
#             return true
#         }
#         if (tag.length > 6) {
#             send.send_with_At(e, `${tag} 太长了呐QAQ！请限制在6个字符以内嗷！`)
#             return true
#         }
#         msg = msg.replace(tag, '')
#         let song = getInfo.fuzzysongsnick(msg)?.[0]
#         if (!song) {
#             send.send_with_At(e, `未找到${msg}的相关曲目信息QAQ！如果想要提供别名的话请访问 /phihelp 中的别名投稿链接嗷！`, true)
#             return true
#         }
#         let info = getInfo.info(song, true)
#         if (!info.chart[rank]) {
#             send.send_with_At(e, `${song} 没有 ${rank} 这个难度QAQ！`)
#             return true
#         }
#         if (!tag) {
#             send.send_with_At(e, `请输入标签哦！\n格式：/${Config.getUserCfg('config', 'cmdhead')} ${op} <曲名> <rank> <tag>`)
#             return true
#         }
#         let callback = false;
#         switch (op) {
#             case 'addtag':
#                 callback = getChartTag.add(info.id, tag, rank, true, e.user_id)
#                 break;
#             case 'subtag':
#                 callback = getChartTag.add(info.id, tag, rank, false, e.user_id)
#                 break;
#             case 'retag':
#                 callback = getChartTag.cancel(info.id, tag, rank, e.user_id)
#                 break;
#         }
#         if (callback) {
#             send.send_with_At(e, `操作成功！`)
#         } else {
#             send.send_with_At(e, `操作失败QAQ！`)
#         }
#     }

# }


# function randClg(clgNum, chartList) {
#     let difList = null;
#     let rand1 = [], rand2 = []
#     // console.info(getInfo.MAX_DIFFICULTY)
#     for (let i = 1; i <= Math.min(getInfo.MAX_DIFFICULTY, clgNum - 2); i++) {
#         // console.info(i, chartList[i])
#         if (chartList[i]) {
#             rand1.push(i)
#             rand2.push(i)
#         }
#     }
#     rand1 = fCompute.randArray(rand1);
#     rand2 = fCompute.randArray(rand2);
#     // console.info(clgNum, rand1, rand2)
#     for (let i in rand1) {
#         // console.info(rand1[i])
#         for (let j in rand2) {
#             let a = rand1[i]
#             let b = rand2[j]
#             if (a + b >= clgNum) continue
#             let c = clgNum - a - b
#             let tem = {}
#             tem[a] = 1
#             tem[b] ? ++tem[b] : tem[b] = 1
#             tem[c] ? ++tem[c] : tem[c] = 1
#             let flag = false
#             for (let i in tem) {
#                 if (!chartList[i] || tem[i] > chartList[i].length) {
#                     flag = true
#                     break
#                 }
#             }
#             if (flag) continue
#             difList = [a, b, c]
#             break;
#         }
#         if (difList) break;
#     }
#     if (!difList) {
#         return;
#     }
#     // console.info(difList)
#     let ans = []
#     for (let i in difList) {
#         if (!chartList[difList[i]]) {
#             logger.error(difList[i], chartList)
#         }
#         let tem = chartList[difList[i]].splice(fCompute.randBetween(0, chartList[difList[i]].length - 1), 1)[0]
#         ans.push(tem)
#     }
#     // console.info(clgNum, ans)
#     return ans;
# }
def chartMatchReq(ask: match_request_return, chart: Chart):
    r = chart.rank
    return bool(
        r in ask.isask
        and (
            ask.isask[Level.index(r)]
            and (chart.difficulty >= ask.range[0] and chart.difficulty <= ask.range[1])
        )
    )


def Number(x: Any):
    try:
        return float(x)
    except ValueError:
        return float("NaN")
