import math
import random
from typing import Literal

from arclet.alconna import StrMulti
from nonebot_plugin_alconna import Alconna, Args, CommandMeta, Match, on_alconna
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger

from ..config import PluginConfig, cmdhead, recmdhead
from ..model.cls.LevelRecordInfo import LevelRecordInfo
from ..model.constNum import Level, LevelItem
from ..model.fCompute import fCompute
from ..model.getdata import getdata
from ..model.getInfo import getInfo
from ..model.getNotes import getNotes
from ..model.getSave import getSave
from ..model.picmodle import picmodle
from ..model.send import send
from ..rule import can_be_call
from ..utils import Number, to_dict

data = on_alconna(
    Alconna(rf"re:{recmdhead}\s*data"), block=True, priority=5, rule=can_be_call("data")
)

info = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*info",
        Args["_kind?", Literal[1, 2]]["_bksong?", str],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("info"),
)

lvscore = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*((lvsco(re)?)|scolv)",
        Args["_input", StrMulti],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("lvscore"),
)

_list = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*list",
        Args["_input", StrMulti],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("list"),
)


@data.handle()
async def _(session: Uninfo):
    """查询data"""
    User = await getdata.getsave(session.user.id)
    if User:
        if User.gameProgress:
            _data = "".join(
                [
                    f"{v}{u} "
                    for v, u in zip(
                        User.gameProgress.money, ["KiB", "MiB", "GiB", "TiB", "PiB"]
                    )
                    if v
                ][::-1]
            )
            await send.sendWithAt(f"您的data数为：{_data}")
        else:
            await send.sendWithAt(f"请先更新数据哦！\n{cmdhead} update")
    else:
        await send.sendWithAt(
            f"请先绑定sessionToken哦！\n{cmdhead} bind <sessionToken>\n"
            f"如果不知道自己的Token可以通过扫码绑定哦！\n如果不知道命令可以用{cmdhead}help查看哦！"
        )


@info.handle()
async def _(session: Uninfo, _bksong: Match[str], _kind: Match[Literal[1, 2]]):
    # 背景
    bksong = _bksong.result if _bksong.available else None
    kind = _kind.result if _kind.available else 1
    if bksong:
        tem = getInfo.fuzzysongsnick(bksong)
        bksong = getInfo.getill(tem[0]) if tem else None
    if not bksong:
        bksong = getInfo.getill(random.choice(getInfo.illlist))

    save = await send.getsaveResult(session, 1.0)
    if not save:
        return

    stats = save.getStats()
    money = getattr(save.gameProgress, "money", [0])
    userbackground = fCompute.getBackground(save.gameuser.background)

    if not userbackground:
        await send.sendWithAt(f"ERROR: 未找到[{save.gameuser.background}]的有关信息！")
        logger.error(
            f"未找到[{save.gameuser.background}]对应的曲绘！", "phi-plugin:user:info"
        )
    dan = await getdata.getDan(session.user.id)
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
            ][::-1]
        ),
        "selfIntro": fCompute.convertRichText(save.gameuser.selfIntro),
        "backgroundurl": userbackground,
        "PlayerId": fCompute.convertRichText(save.saveInfo.PlayerId),
        "CLGMOD": dan.get("Dan"),
        "EX": dan.get("EX"),
    }
    user_data = await getSave.getHistory(session.user.id)
    result = user_data.getRksAndDataLine()

    (
        rks_history,
        data_history,
        rks_range,
        data_range,
        rks_date,
        data_date,
    ) = (
        result.rks_history,
        result.data_history,
        result.rks_range,
        result.data_range,
        result.rks_date,
        result.data_date,
    )
    # 统计在要求acc>=i的前提下，玩家的rks为多少
    # 存档
    acc_rksRecord = save.getRecord()
    # phi列表
    acc_rks_phi = save.findAccRecord(100)
    # 所有rks节点
    acc_rks_data = []
    # 转换成坐标的节点
    acc_rks_data_ = []
    # rks上下界
    acc_rks_range = [100.0, 0.0]
    # 预处理
    phi_rks = 0
    for i in range(3):
        if i < len(acc_rks_phi):
            phi_rks += acc_rks_phi[i].rks
        else:
            break
    # 原本b19中最小acc 要展示的acc序列
    acc_rks_AccRange = [100.0]
    for i in range(min(len(acc_rksRecord), 27)):
        acc_rks_AccRange[0] = min(acc_rks_AccRange[0], acc_rksRecord[i].acc)

    while acc_rks_AccRange[0] <= 100:
        sum_rks = 0
        if not acc_rks_AccRange[0]:
            break
        for j in range(len(acc_rksRecord)):
            if j >= 27:
                break
            if acc_rksRecord[j].acc < acc_rks_AccRange[0]:
                # 预处理展示的acc数字
                acc_rks_AccRange.append(acc_rks_AccRange[0])
            while acc_rksRecord[j].acc < acc_rks_AccRange[0]:
                del acc_rksRecord[j]
            sum_rks += acc_rksRecord[j].rks
        tem_rks = (sum_rks + phi_rks) / 30
        acc_rks_data.append([acc_rks_AccRange[0], tem_rks])
        acc_rks_range[0] = min(acc_rks_range[0], tem_rks)
        acc_rks_range[1] = max(acc_rks_range[1], tem_rks)

        acc_rks_AccRange[0] += 0.01

        if acc_rks_AccRange[-1] < 100:
            acc_rks_AccRange.append(100)
        for i in range(len(acc_rks_data)):
            if acc_rks_data_ and acc_rks_data[i - 1][1] == acc_rks_data[i][1]:
                acc_rks_data_[-1][2] = fCompute.range(
                    acc_rks_data[i][0], acc_rks_AccRange
                )
            else:
                acc_rks_data_.append(
                    [
                        fCompute.range(acc_rks_data[i - 1][0], acc_rks_AccRange),
                        fCompute.range(acc_rks_data[i - 1][1], acc_rks_range),
                        fCompute.range(acc_rks_data[i][0], acc_rks_AccRange),
                        fCompute.range(acc_rks_data[i][1], acc_rks_range),
                    ]
                )
        # 处理acc显示区间，防止横轴数字重叠
        if acc_rks_AccRange[0] == 100:
            acc_rks_AccRange[0] = 0

        acc_length = 100 - acc_rks_AccRange[0]
        min_acc = acc_rks_AccRange[0]
        while (100 - acc_rks_AccRange[-2]) < acc_length / 10:
            del acc_rks_AccRange[-2]

        acc_rks_AccRange_position = [[acc_rks_AccRange[0], 0]]
        for i in range(len(acc_rks_AccRange)):
            while (acc_rks_AccRange[i] - acc_rks_AccRange[-1]) < acc_length / 10:
                del acc_rks_AccRange[i]
            acc_rks_AccRange_position.append(
                [
                    acc_rks_AccRange[i],
                    (acc_rks_AccRange[i] - min_acc) / acc_length * 100,
                ]
            )
        data = {
            "gameuser": gameuser,
            "userstats": stats,
            "rks_history": rks_history,
            "data_history": data_history,
            "rks_range": rks_range,
            "data_range": data_range,
            "data_date": [
                fCompute.date_to_string(data_date[0]),
                fCompute.date_to_string(data_date[1]),
            ],
            "rks_date": [
                fCompute.date_to_string(rks_date[0]),
                fCompute.date_to_string(rks_date[1]),
            ],
            "acc_rks_data": acc_rks_data_,
            "acc_rks_range": acc_rks_range,
            "acc_rks_AccRange": acc_rks_AccRange_position,
            "background": bksong,
        }
        await send.sendWithAt(await getdata.getuser_info(data, kind))


@lvscore.handle()
async def _(session: Uninfo, _input: Match):
    save = await send.getsaveResult(session)
    if not save:
        return
    input = _input.result if _input.available else ""
    result = fCompute.match_request(input, getInfo.MAX_DIFFICULTY)
    _range, isask = result.range, result.isask
    _range[1] = min(_range[1], getInfo.MAX_DIFFICULTY)
    _range[0] = max(_range[0], 0)

    unlockcharts = 0
    totreal_score = 0
    totacc = 0
    totcharts = 0
    totcleared = 0
    totfc = 0
    totphi = 0
    tottot_score = 0
    tothighest = 0
    totlowest = 17
    totsongs = 0
    totRating: dict[
        Literal[
            "phi",
            "FC",
            "V",
            "S",
            "A",
            "B",
            "C",
            "F",
        ],
        int,
    ] = {
        "phi": 0,
        "FC": 0,
        "V": 0,
        "S": 0,
        "A": 0,
        "B": 0,
        "C": 0,
        "F": 0,
    }
    totRank: dict[LevelItem | str, int] = {
        "AT": 0,
        "IN": 0,
        "HD": 0,
        "EZ": 0,
    }
    unlockRank: dict[LevelItem, int] = {
        "AT": 0,
        "IN": 0,
        "HD": 0,
        "EZ": 0,
    }
    unlocksongs = 0

    Record = save.gameRecord

    for info in getInfo.ori_info.values():
        vis = False
        for lv in info.chart:
            difficulty = Number(info.chart[lv].difficulty)
            if (
                _range[0] <= difficulty
                and difficulty <= _range[1]
                and lv in Level
                and isask[Level.index(lv)]
            ):
                totcharts += 1
                totRank[lv] += 1
                if not vis:
                    totsongs += 1
                    vis = True

    for id in Record:
        info = getInfo.info(getInfo.idgetsong(id) or "")
        record = Record[id]
        vis = False
        for lv in Level:
            if not info or lv not in info.chart:
                continue
            difficulty = Number(info.chart[lv].difficulty)
            if (
                _range[0] < difficulty
                and difficulty <= _range[1]
                and isask[Level.index(lv)]
            ):
                if lv not in record or not record[lv]:
                    continue
                rlv = record[lv]
                assert rlv
                unlockcharts += 1
                unlockRank[lv] += 1
                if not vis:
                    unlocksongs += 1
                    vis = True
                if rlv.score >= 700000:
                    totcleared += 1
                if rlv.fc or rlv.score == 1000000:
                    totfc += 1
                if rlv.score == 1000000:
                    totphi += 1
                totRating[rlv.Rating] += 1
                totacc += rlv.acc
                totreal_score += rlv.score
                tottot_score += 1000000

                tothighest += max(rlv.rks, tothighest)
                totlowest += min(rlv.rks, totlowest)
    illustration = fCompute.getBackground(save.gameuser.background)
    if not illustration:
        await send.sendWithAt(
            f"ERROR: 未找到[{save.gameuser.background}]背景的有关信息！"
        )
        logger.error(
            f"未找到{save.gameuser.background}的曲绘！", "phi-plugin:user:lvscore"
        )

        data = {
            "tot": {
                "at": totRank["AT"],
                "in": totRank["IN"],
                "hd": totRank["HD"],
                "ez": totRank["EZ"],
                "songs": totsongs,
                "charts": totcharts,
                "score": tottot_score,
            },
            "real": {
                "at": unlockRank["AT"],
                "in": unlockRank["IN"],
                "hd": unlockRank["HD"],
                "ez": unlockRank["EZ"],
                "songs": unlocksongs,
                "charts": unlockcharts,
                "score": totreal_score,
            },
            "rating": {
                **totRating,
                "tot": fCompute.rate(totreal_score, tottot_score, totfc == totcharts),
            },
            "range": {
                "bottom": _range[0],
                "top": _range[1],
                "left": _range[0] / 16.9 * 100,
                "length": (_range[1] - _range[0]) / 16.9 * 100,
            },
            "illustration": illustration,
            "highest": tothighest,
            "lowest": totlowest,
            "tot_cleared": totcleared,
            "tot_fc": totfc,
            "tot_phi": totphi,
            "tot_acc": (totacc / totcharts),
            "date": fCompute.date_to_string(save.saveInfo.modifiedAt.iso),
            "progress_phi": round((totphi / totcharts * 100), 2),
            "progress_fc": round((totfc / totcharts * 100), 2),
            "avatar": getInfo.idgetavatar(save.gameuser.avatar),
            "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
            "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
            "rks": save.saveInfo.summary.rankingScore,
            "PlayerId": fCompute.convertRichText(save.saveInfo.PlayerId),
            "background": getInfo.getill(random.choice(getInfo.illlist), "blur"),
        }
        await send.sendWithAt(await getdata.getlvsco(data))


@_list.handle()
async def _(session: Uninfo, _input: Match):
    save = await send.getsaveResult(session)
    if not save:
        return
    input = _input.result if _input.available else ""
    result = fCompute.match_request(input, getInfo.MAX_DIFFICULTY)
    _range, isask, scoreAsk = result.range, result.isask, result.scoreAsk

    Record = save.gameRecord

    data = []

    for id in Record:
        song = getInfo.idgetsong(id)
        if not song:
            logger.warning(f"{id} 曲目无信息", "phi-plugin:user:list")
            continue
        info = getInfo.info(song)
        record = Record[id]
        for lv in Level:
            if not info or lv not in info.chart:
                continue
            difficulty = Number(info.chart[lv].difficulty)
            if (
                _range[0] < difficulty
                and difficulty <= _range[1]
                and isask[Level.index(lv)]
            ):
                if (lv not in record or not record[lv]) and not scoreAsk.NEW:
                    continue
                if (
                    lv in record
                    and record[lv]
                    and not getattr(scoreAsk, record[lv].Rating.upper())  # pyright: ignore[reportOptionalMemberAccess]
                ):
                    continue
                if lv not in record:
                    setattr(record, lv, LevelRecordInfo())
                record[Level.index(lv)].suggest = save.getSuggest(id, lv, 4, difficulty)  # pyright: ignore[reportOptionalMemberAccess]
                data.append(
                    {
                        **to_dict(record[Level.index(lv)]),
                        **to_dict(info),
                        "illustration": getInfo.getill(
                            getInfo.idgetsong(id) or "", "low"
                        ),
                        "difficulty": difficulty,
                        "rank": lv,
                    }
                )
    if len(data) > PluginConfig.get("listScoreMaxNum"):
        await send.sendWithAt(
            f"谱面数量过多({len(data)})大于设置的最大值({PluginConfig.get('listScoreMaxNum')})，请缩小搜索范围QAQ！"
        )
        return

    data.sort(key=lambda x: x.get("difficulty", 0), reverse=True)

    plugin_data = await getNotes.getNotesData(session.user.id)

    await send.sendWithAt(
        await picmodle.list(
            {
                "head_title": "成绩筛选",
                "song": data,
                "background": getInfo.getill(random.choice(getInfo.illlist)),
                "theme": plugin_data.plugin_data.theme,
                "PlayerId": save.saveInfo.PlayerId,
                "Rks": round(save.saveInfo.summary.rankingScore, 4),
                "Date": save.saveInfo.summary.updatedAt,
                "ChallengeMode": math.floor(
                    save.saveInfo.summary.challengeModeRank / 100
                ),
                "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
                "dan": await getdata.getDan(session.user.id),
                "request": f"{_range[0]} - {_range[1]}",
            }
        )
    )
