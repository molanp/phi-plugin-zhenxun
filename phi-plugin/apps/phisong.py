"""phigros图鉴"""

import contextlib
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
    Image,
    Match,
    Option,
    Query,
    Target,
    UniMsg,
    on_alconna,
    store_true,
)
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_waiter import prompt

from zhenxun.services.log import logger
from zhenxun.utils._image_template import ImageTemplate
from zhenxun.utils.http_utils import AsyncHttpx
from zhenxun.utils.message import MessageUtils
from zhenxun.utils.rules import admin_check, ensure_group

from ..config import PluginConfig, Version, cmdhead, recmdhead
from ..model.cls.Chart import Chart
from ..model.cls.SongsInfo import SongsInfoObject
from ..model.constNum import Level, LevelNum
from ..model.fCompute import fCompute, match_request_return
from ..model.getChartTag import getChartTag
from ..model.getComment import CommentDict, getComment
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
com = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(com|计算)",
        Args["_difficulty?", float]["_acc?", float],
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
        Args["_t?", float],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("table"),
)
comment = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(comment|cmt|评论|评价)",
        Args["songname?", str]["rank?", str]["content?", StrMulti],
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
        rf"re:{recmdhead}\s*(addtag|subtag|retag)",
        Args["songname", str]["_rank", str]["_tag?", str],
    ),
    block=True,
    priority=5,
    rule=can_be_call("addtag"),
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


@com.handle()
async def _(_difficulty: Match[float], _acc: Match[float]):
    """计算等效rks"""
    difficulty = _difficulty.result if _difficulty.available else None
    acc = _acc.result if _acc.available else None
    if (
        difficulty
        and acc
        and difficulty > 0
        and difficulty <= 18
        and acc > 0
        and acc <= 100
    ):
        result = fCompute.rks(acc, difficulty)
        await send.sendWithAt(f"dif: {difficulty} acc: {acc}\n计算结果：{result}", True)
    else:
        await send.sendWithAt(f"格式错误QAQ！\n格式：{cmdhead} com <定数> <acc>")


@tips.handle()
async def _():
    """随机tips"""
    await send.sendWithAt(random.choice(getInfo.Tips))


@randClg.handle()
async def _(session: Uninfo, _input: Match):
    arg = _input.result if _input.available else ""
    songReq = ""
    if m := re.compile(r"[\(（].*?[\)）]").search(arg):
        songReq = re.sub(r"[\(\)（）]", "", m[0])
        arg = arg.replace(m[0], "", 1)
    songAsk = fCompute.match_request(songReq)
    tmp = fCompute.match_request(arg, 48)
    isask, range = tmp.isask, tmp.range
    NumList: list[float] = []
    while range[0] <= range[1]:
        NumList.append(range[0])
        range[0] += 1
    chartList: dict[float, list[Chart]] = {}
    for dif, charts in getInfo.info_by_difficulty.items():
        if dif < range[1]:
            for chart in charts:
                difficulty = chart.difficulty
                if (
                    chart.rank
                    and isask[Level.index(chart.rank)]
                    and chartMatchReq(songAsk, chart)
                ):
                    if difficulty in chartList:
                        chartList[difficulty].append(chart)
                    else:
                        chartList[difficulty] = [chart]
    random.shuffle(NumList)
    res = __randClg(NumList.pop(0), chartList)
    while not res and len(NumList):
        res = __randClg(NumList.pop(0), chartList)
    if res:
        songs = []
        plugin_data = await getdata.getNotesData(session.user.id)
        for r in res:
            info = await getInfo.info(getInfo.idgetsong(r.id) or "")
            assert info
            songs.append(
                {
                    "id": info.id,
                    "song": info.song,
                    "rank": r.rank,
                    "difficulty": r.difficulty,
                    "illustration": await getInfo.getill(info.song),
                    **to_dict(info.chart[r.rank]),
                }
            )
        await send.sendWithAt(
            await picmodle.common(
                "clg",
                {
                    "songs": songs,
                    "tot_clg": math.floor(res[0].difficulty)
                    + math.floor(res[1].difficulty)
                    + math.floor(res[2].difficulty),
                    "background": await getInfo.getill(
                        random.choice(getInfo.illlist), "blur"
                    ),
                    "theme": plugin_data.plugin_data.theme,
                },
            )
        )
    else:
        await send.sendWithAt("未找到符合条件的谱面QAQ！")


@newSong.handle()
async def _():
    ans = ""
    with contextlib.suppress(Exception):
        info = (await AsyncHttpx.get(PluginConfig.get("phigrousUpdateUrl"))).json()
        data = info["data"]["list"][0]
        version_label = data["version_label"]
        whatsnew = (
            data["whatsnew"]["text"]
            .replace("<div>", "")
            .replace("</div>", "")
            .replace("<br/>", "\n")
        )
        ans += f"最新版本：{version_label}\n更新信息：\n{whatsnew}"
    ans += f"信息文件版本：{Version['phigros']}\n"
    ans += "新曲速递：\n"
    for song in getInfo.updatedSong:
        info = await getInfo.info(song)
        assert info
        ans += f"{info.song}\n"
        for j, c in info.chart.items():
            ans += f"  {j} {c.difficulty} {c.combo}\n"
    ans += "\n定数&谱面修改：\n"
    for song, v in getInfo.updatedChart.items():
        ans += f"{song}\n"
        for level, chart in v.items():
            ans += f"  {level}:\n"
            chart = to_dict(chart)
            if chart["isNew"]:
                for key, value in chart.items():
                    ans += f"    {key}: {value[0]}\n"
            else:
                for key, value in chart.items():
                    ans += f"    {key}: {value[0]} -> {value[1]}\n"

    if len(ans) > 500:
        await send.sendWithAt("新曲速递内容过长，请试图查阅其他途径！", True)
    else:
        await send.sendWithAt(ans)


@table.handle()
async def _(_t: Match[float]):
    dif = _t.result if _t.available else None
    if not dif:
        await send.sendWithAt(
            f"请输入定数嗷！\n格式：{cmdhead} table <定数>",
            True,
        )
        return
    await send.sendWithAt(Image(url=getInfo.getTableImg(dif)))


@comment.handle()
async def _(session: Uninfo, songname: Match[str], rank: Match[str], content: Match):
    if not PluginConfig.get("allowComment"):
        await send.sendWithAt("这里被管理员禁止使用这个功能了呐QAQ！")
        return
    save = await send.getsaveResult(session)
    if not save:
        return
    nickname = songname.result if songname.available else None
    if not nickname:
        await send.sendWithAt(
            f"请指定曲名哦！\n格式：\n{cmdhead} cmt <曲名> <难度?> <内容>"
        )
        return
    rankKind = rank.result.upper() if rank.available else "IN"
    match rankKind:
        case "EZ":
            rankNum = 0
        case "HD":
            rankNum = 1
        case "IN":
            rankNum = 2
        case "AT":
            rankNum = 3
        case "LGC" | "LEGACY":
            rankNum = 4
        case _:
            rankNum = -1
    song = await getInfo.fuzzysongsnick(nickname)
    if not song:
        await send.sendWithAt(
            f"未找到{nickname}的相关曲目信息QAQ\n如果想要提供别名的话请访问"
            f" {cmdhead}help 中的别名投稿链接嗷！",
            True,
        )
        return
    songInfo = await getInfo.info(song[0])
    assert songInfo
    if songInfo.sp_vis:
        rankKind = "IN"
    elif rankNum == -1:
        await send.sendWithAt(f"{rankKind} 不是一个难度QAQ！")
        return
    elif rankKind not in songInfo.chart:
        await send.sendWithAt(f"{song[0]} 没有 {rankKind} 这个难度QAQ！")
        return
    comment = content.result if content.available else ""
    comment = re.sub(r"[\x00-\x09\x0b-\x1f\x7f-\x9f]", "", comment)
    if not comment:
        await send.sendWithAt("不可发送空白内容w(ﾟДﾟ)w！")
        return
    if len(comment) > 1000:
        await send.sendWithAt("太长了吧！你想干嘛w(ﾟДﾟ)w！")
        return
    songId = songInfo.id
    cmtobj: CommentDict = {
        "sessionToken": save.sessionToken,
        "ObjectId": save.saveInfo.objectId,
        "rks": save.saveInfo.summary.rankingScore,
        "rank": rankKind,
        "score": 0,
        "acc": 0,
        "fc": False,
        "challenge": save.saveInfo.summary.challengeModeRank,
        "comment": comment,
        "spInfo": "",
        "PlayerId": save.saveInfo.PlayerId,
        "avatar": save.saveInfo.avatar,
    }
    songRecord = save.getSongsRecord(songId)
    if not songInfo.sp_vis and rankKind in songRecord:
        r = await save.getB19(27)
        phi = r["phi"]
        b19_list = r["b19_list"]
        spInfo = ""
        for i, r in enumerate(phi):
            if r and r.id == songId and r.rank == rankKind:
                spInfo = f"Perfect {i + 1}"
                break
        if not spInfo and getattr(songRecord[rankKind], "score", 0) == 1000000:
            spInfo = "All Perfect"
        for i, r in enumerate(b19_list):
            if r.id == songId and r.rank == rankKind:
                if spInfo:
                    spInfo += f" & Best {i + 1}"
                else:
                    spInfo = f"Best {i + 1}"
                break
        cmtobj["score"] = getattr(songRecord[rankKind], "score", 0)
        cmtobj["acc"] = getattr(songRecord[rankKind], "acc", 0)
        cmtobj["fc"] = getattr(songRecord[rankKind], "fc", False)
        cmtobj["spInfo"] = spInfo
    if await getComment.add(songId, cmtobj):
        await send.sendWithAt("评论成功！φ(゜▽゜*)♪")
    else:
        await send.sendWithAt("遇到未知错误QAQ！")


@recallComment.handle()
async def _(bot, session: Uninfo, objId: Match[int]):
    if not PluginConfig.get("allowComment"):
        await send.sendWithAt("这里被管理员禁止使用这个功能了呐QAQ！")
        return
    if session.user.id not in bot.config.superusers:
        save = await send.getsaveResult(session)
        if not save:
            return

    commentId = objId.result if objId.available else None
    if not commentId:
        await send.sendWithAt(f"请输入评论ID嗷！\n格式：{cmdhead} recmt <评论ID>")
        return

    comment = await getComment.getByCommentId(commentId)
    if not comment:
        await send.sendWithAt(f"没有找到ID为 {commentId} 的评论QAQ！")
        return
    if (
        session.user.id not in bot.config.superusers
        and comment.sessionToken == save.sessionToken  # pyright: ignore[reportPossiblyUnboundVariable]
        and comment.ObjectId == save.saveInfo.objectId  # pyright: ignore[reportPossiblyUnboundVariable]
    ):
        await send.sendWithAt("您没有权限操作这条评论捏(。﹏。)")
        return
    if await getComment.delete(commentId):
        await send.sendWithAt("删除成功！")
    else:
        await send.sendWithAt("删除失败QAQ！")


@myComment.handle()
async def _(session: Uninfo):
    save = await send.getsaveResult(session)
    if not save:
        return
    comments = await getComment.getBySstkAndObjectId(
        save.sessionToken, save.saveInfo.objectId
    )
    if comments:
        data_list = [
            [
                comment.commentId,
                comment.songId,
                comment.rank,
                comment.comment,
                fCompute.date_to_string(comment.created_at),
            ]
            for comment in comments
        ]
        await send.sendWithAt(
            Image(
                raw=(
                    await ImageTemplate.table_page(
                        "您的评论列表",
                        None,
                        ["ID", "曲目", "难度", "内容", "时间"],
                        data_list,
                    )
                ).pic2bytes()
            )
        )
    else:
        await send.sendWithAt("您还没有评论哦！")


@chart.handle()
async def _(songanme: Match[str], _rank: Match[str]):
    rank = _rank.result.upper() if _rank.available else None
    msg = songanme.result if songanme.available else ""
    song = await getInfo.fuzzysongsnick(msg)
    if not song:
        await send.sendWithAt(
            f"未找到{msg}的相关曲目信息QAQ！如果想要提供别名的话请访问"
            f" {cmdhead}help 中的别名投稿链接嗷！",
            True,
        )
        return
    info = await getInfo.info(song[0], True)
    assert info
    if rank not in info.chart:
        await send.sendWithAt(f"{song[0]} 没有 {rank} 这个难度QAQ！")
        return
    chart = info.chart[rank]
    allowChartTag = PluginConfig.get("allowChartTag")
    data = {
        "illustration": info.illustration,
        "song": info.song,
        "length": info.length,
        "rank": rank,
        "difficulty": chart.difficulty,
        "charter": chart.charter,
        "tap": chart.tap,
        "drag": chart.drag,
        "hold": chart.hold,
        "flick": chart.flick,
        "combo": chart.combo,
        "distribution": chart.distribution,
        "tip": f"发送 {cmdhead} addtag <曲名> <难度> <tag> 来添加标签哦！"
        if allowChartTag
        else "标签词云功能暂时被管理员禁用了哦！快去联系BOT主开启吧！",
        "chartLength": f"{math.floor(chart.maxTime / 60)}:"
        f"{fCompute.ped(math.floor(chart.maxTime % 60), 2)}",
        "words": await getChartTag.get(info.id, rank) if allowChartTag else "",
    }
    await send.sendWithAt(await picmodle.common("chartInfo", data))


@addtag.handle()
async def _(
    session: Uninfo,
    msg: UniMsg,
    songname: Match[str],
    _rank: Match[str],
    _tag: Match[str],
):
    if not PluginConfig.get("allowChartTag"):
        await send.sendWithAt("这里被管理员禁止使用这个功能了呐QAQ！")
        return
    m = re.search(r"(addtag|subtag|retag)", msg.extract_plain_text())
    assert m
    op = m[1]
    rank = _rank.result.upper() if _rank.available else None
    tag = _tag.result if _tag.available else None

    if not tag:
        await send.sendWithAt(
            f"请输入标签哦！\n格式：{cmdhead} {op} <曲名> <rank> <tag>"
        )
        return
    if len(tag) > 6:
        await send.sendWithAt(f"{tag} 太长了呐QAQ！请限制在6个字符以内嗷！")
        return
    name = songname.result if songname.available else ""
    song = await getInfo.fuzzysongsnick(name)
    if not song:
        await send.sendWithAt(
            f"未找到{name}的相关曲目信息QAQ！如果想要提供别名的话请访问"
            f" {cmdhead}help 中的别名投稿链接嗷！",
            True,
        )
        return
    info = await getInfo.info(song[0], True)
    assert info
    if rank not in info.chart:
        await send.sendWithAt(f"{song[0]} 没有 {rank} 这个难度QAQ！")
        return
    callback = False
    match op:
        case "addtag":
            callback = await getChartTag.add(info.id, tag, rank, True, session.user.id)
        case "subtag":
            callback = await getChartTag.add(info.id, tag, rank, False, session.user.id)
        case "retag":
            callback = await getChartTag.cancel(info.id, tag, rank, session.user.id)
    if callback:
        await send.sendWithAt("操作成功！")
    else:
        await send.sendWithAt("操作失败QAQ！")


def __randClg(clgNum: float, chartList: dict[float, list[Chart]]):
    difList: list[float] = []
    rand1: list[int] = []
    rand2: list[int] = []
    i = 1
    while i < min(getInfo.MAX_DIFFICULTY, clgNum - 2):
        if i in chartList:
            rand1.append(i)
            rand2.append(i)
        i += 1
    random.shuffle(rand1)
    random.shuffle(rand2)

    for a in rand1:
        for b in rand2:
            if a + b >= clgNum:
                continue
            c = clgNum - a - b
            tem: dict[float, int] = {a: 1}
            if b in tem:
                tem[b] += 1
            else:
                tem[b] = 1
            if c in tem:
                tem[c] += 1
            else:
                tem[c] = 1
            flag = any(
                i not in chartList or v > len(chartList[i]) for i, v in tem.items()
            )
            if flag:
                continue
            difList = [a, b, c]
            break
        if difList:
            break
    if not difList:
        return
    ans: list[Chart] = []
    for i in difList:
        if i not in chartList:
            logger.error(f"未意料的情况, {i} {chartList}", "phi-plugin:randClg")
        ans.append(chartList[i].pop(random.randint(0, len(chartList[i]) - 1)))
    return ans


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
