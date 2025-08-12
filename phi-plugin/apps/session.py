"""
sessionToken获取
"""

import asyncio
import random
import re
import time

from nonebot_plugin_alconna import Alconna, Args, CommandMeta, Match, on_alconna
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_waiter import prompt

from zhenxun.services.log import logger
from zhenxun.utils.platform import PlatformUtils
from zhenxun.utils.rules import ensure_group
from zhenxun.utils.withdraw_manage import WithdrawManager

from ..config import PluginConfig, cmdhead, recmdhead
from ..lib.getQRcode import getQRcode
from ..model.cls.common import Save
from ..model.cls.saveHistory import saveHistory
from ..model.cls.scoreHistory import scoreHistory
from ..model.fCompute import fCompute
from ..model.getdata import getdata
from ..model.getInfo import getInfo
from ..model.getNotes import getNotes
from ..model.getSave import getSave
from ..model.getUpdateSave import UpdateSaveResult, getUpdateSave
from ..model.send import send
from ..models import qrCode
from ..rule import can_be_call
from ..utils import Date, to_dict

bind = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(绑定|bind)",
        Args["sstk?", str],
        meta=CommandMeta(compact=True),
    ),
    rule=can_be_call("bind"),
    block=True,
    priority=5,
)
update = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(更新|update)"),
    rule=can_be_call("update"),
    block=True,
    priority=5,
)
unbind = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(解绑|unbind)"),
    rule=can_be_call("unbind"),
    block=True,
    priority=5,
)
clean = on_alconna(
    Alconna(rf"re:{recmdhead}\s*clean"),
    block=True,
    priority=5,
)
getSstk = on_alconna(
    Alconna(rf"re:{recmdhead}\s*sessionToken"),
    block=True,
    priority=5,
)


@bind.handle()
async def _(bot, session: Uninfo, sstk: Match[str]):
    """这里逻辑太复杂了，得谨慎点"""
    param = sstk.result if sstk.available else ""
    sessionToken = re.compile(r"[0-9a-zA-Z]{25}|qrcode", re.IGNORECASE).search(param)
    localPhigrosToken = await getSave.get_user_token(session.user.id)
    sessionToken = sessionToken[0] if sessionToken else localPhigrosToken
    if localPhigrosToken:
        await send.sendWithAt("不要重复绑定啊喂!")
        return
    if not sessionToken:
        await send.sendWithAt(
            "喂喂喂！你还没输入sessionToken呐！\n"
            f"扫码绑定：{cmdhead} bind qrcode\n"
            f"普通绑定：{cmdhead} bind <sessionToken>",
        )
        return
    if sessionToken == "qrcode":
        # 用户若已经触发且未绑定，则发送原来的二维码
        qrcode, QRCodetimeout, request = await qrCode.get_qrcode(session.user.id)
        if qrcode:
            recallTime = QRCodetimeout
            if QRCodetimeout >= 60:
                recallTime = 60
            if PluginConfig.get("TapTapLoginQRcode"):
                qrCodeMsg = await send.sendWithAt(
                    [
                        "请识别二维码并按照提示进行登录嗷！请勿错扫他人二维码。"
                        "请注意，登录TapTap可能造成账号及财产损失，"
                        "请在信任Bot来源的情况下扫码登录。\n"
                        f"二维码剩余时间:{QRCodetimeout}",
                        await getQRcode.getQRcode(qrcode),
                    ],
                    False,
                    recallTime,
                )
            else:
                qrCodeMsg = await send.sendWithAt(
                    "请点击链接进行登录嗷！请勿使用他人的链接。请注意，"
                    "登录TapTap可能造成账号及财产损失，请在信任Bot来源的情况下扫码登录。\n"
                    f"链接剩余时间:{QRCodetimeout}\n{qrcode}",
                    recallTime=recallTime,
                )
        else:
            request = await getQRcode.getRequest()
            if PluginConfig.get("TapTapLoginQRcode"):
                qrCodeMsg = await send.sendWithAt(
                    [
                        "请识别二维码并按照提示进行登录嗷！请勿错扫他人二维码。"
                        "请注意，登录TapTap可能造成账号及财产损失，请在信任Bot来源的情况下扫码登录。",
                        await getQRcode.getQRcode(request["data"]["qrcode_url"]),
                    ],
                    recallTime=60,
                )
            else:
                qrCodeMsg = await send.sendWithAt(
                    "请点击链接进行登录嗷！请勿使用他人的链接。"
                    "请注意，登录TapTap可能造成账号及财产损失，请在信任Bot来源的情况下扫码登录。\n"
                    f"{request['data']['qrcode_url']}",
                    recallTime=60,
                )
        recall_id = WithdrawManager._index - 1
        QRCodetimeout = request["data"]["expires_in"]
        # 判断adapter是否为QQBot
        # 如果是并且超时时间大于270秒则将超时时间改为270秒，以免被动消息回复超时
        if PlatformUtils.is_qbot(session) and QRCodetimeout > 270:
            QRCodetimeout = 270
        await qrCode.set_qrcode(
            session.user.id, request["data"]["qrcode_url"], request, QRCodetimeout
        )
        result = await asyncio.create_task(
            waitResponse(bot, QRCodetimeout, request, recall_id, qrCodeMsg)
        )
        await qrCode.del_qecode(session.user.id)
        if not result.get("success"):
            await send.sendWithAt("操作超时，请重试QAQ！")
            return
        try:
            sessionToken = await getQRcode.getSessionToken(result)
        except Exception as e:
            logger.error("获取sessionToken失败", "phi-plugin", e=e, session=session)
            await send.sendWithAt(
                "获取sessionToken失败QAQ！请确认您的Phigros已登录TapTap账号并同步！"
                f"\n错误信息：{type(e)}: {e}",
            )
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt("正在绑定，请稍等一下哦！\n >_<", recallTime=5)
    await send.sendWithAt(
        "请注意保护好自己的sessionToken呐！如果需要获取已绑定的sessionToken可以私聊发送"
        f"{cmdhead} sessionToken 哦！",
        recallTime=10,
    )
    updateData = await getUpdateSave.getNewSaveFromLocal(session, sessionToken)
    history = await getSave.getHistory(session.user.id)
    await build(session, updateData, history)


@update.handle()
async def _(session: Uninfo):
    sessionToken = await getSave.get_user_token(session.user.id)
    if not sessionToken:
        await send.sendWithAt(
            "没有找到你的存档哦！请先绑定sessionToken！\n"
            f"帮助：{cmdhead} tk help\n"
            f"格式：{cmdhead} bind <sessionToken>",
        )
        return
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt("正在生成，请稍等一下哦！\n >_<", recallTime=5)
    try:
        updateData = await getUpdateSave.getNewSaveFromLocal(session, sessionToken)
        history = await getSave.getHistory(session.user.id)
        await build(session, updateData, history)
    except Exception as e:
        logger.error("更新信息失败", "phi-plugin", e=e)
        await send.sendWithAt(
            f"更新失败，请检查你的sessionToken是否正确QAQ！\n错误信息：{type(e)}: {e}",
        )


@unbind.handle()
async def _(session: Uninfo):
    if not await getSave.get_user_token(session.user.id):
        await send.sendWithAt("没有找到你的存档信息嗷！")
        return
    ensure = await prompt(
        "解绑会导致历史数据全部清空呐QAQ！真的要这么做吗?(确认/取消)", timeout=30
    )
    if ensure and ensure.extract_plain_text().strip() == "确认":
        flag = True
        try:
            await getSave.delSave(session.user.id)
            await getNotes.delNotesData(session.user.id)
        except Exception as e:
            await send.sendWithAt(f"解绑失败QAQ！\n错误信息：{type(e)}: {e}")
            logger.error("用户解绑失败", "phi-plugin", session=session, e=e)
            flag = False
        if flag:
            await send.sendWithAt("解绑成功")
    else:
        await send.sendWithAt("已取消操作")


@clean.handle()
async def _(session: Uninfo):
    ensure = await prompt(
        "请注意，本操作将会删除Phi-Plugin关于您的所有信息QAQ！真的要这么做吗?(确认/取消)",
        timeout=30,
    )
    if ensure and ensure.extract_plain_text().strip() == "确认":
        flag = True
        try:
            await getSave.delSave(session.user.id)
            await getNotes.delNotesData(session.user.id)
        except Exception as e:
            await send.sendWithAt(f"删除失败QAQ！\n错误信息：{type(e)}: {e}")
            flag = False
        if flag:
            await send.sendWithAt("清除数据成功")
    else:
        await send.sendWithAt("已取消操作")


@getSstk.handle()
async def _(session: Uninfo):
    if ensure_group(session):
        await send.sendWithAt("请私聊使用嗷")
        return
    save = await send.getsaveResult(session, -1, False)
    if save is None:
        await send.sendWithAt("未绑定存档，请先绑定存档嗷！")
        return
    await send.sendWithAt(
        f"PlayerId: {fCompute.convertRichText(save.saveInfo.PlayerId, True)}\n"
        f"sessionToken: {save.sessionToken}\nObjectId: {save.saveInfo.objectId}\n"
        f"QQId: {session.user.id}",
    )


def toHex(num: int) -> str:
    """定义一个函数，接受一个整数参数，返回它的十六进制形式"""
    return f"{num:02x}"


def getRandomBgColor() -> str:
    """定义一个函数，不接受参数，返回一个随机的背景色"""
    red = random.randint(0, 200)
    green = random.randint(0, 200)
    blue = random.randint(0, 200)

    return f"#{toHex(red)}{toHex(green)}{toHex(blue)}"


def comWidth(num: int):
    """计算/update宽度"""
    return num * 125 + 20 * num - 20


async def waitResponse(bot, QRCodetimeout: int, request, recall_id, qrCodeMsg):
    start_time = time.time()
    # 是否发送过已扫描提示
    flag = False
    result = {}
    while time.time() - start_time < QRCodetimeout:
        result = await getQRcode.checkQRCodeResult(request)
        if result.get("success"):
            break
        if result["data"].get("error") == "authorization_waiting" and not flag:
            await send.sendWithAt("二维码已扫描，请确认登录", recallTime=10)
            WithdrawManager.remove(recall_id)
            WithdrawManager.append(
                bot,
                qrCodeMsg.msg_ids[0]["message_id"],
                1,
            )
            flag = True
        await asyncio.sleep(2)
    return result


async def build(
    session: Uninfo,
    _updateData: UpdateSaveResult,
    history: saveHistory,
):
    updateData = to_dict(_updateData)
    added_rks_notes = updateData.get("added_rks_notes", [0, 0])
    save = updateData.get("save", {})
    if added_rks_notes[0]:
        value = added_rks_notes[0]
        sign = "+" if value > 0 else ""
        formatted = f"{value:.4f}" if abs(value) >= 1e-4 else ""
        added_rks_notes[0] = f"{sign}{formatted}"
    if added_rks_notes[1]:
        value = added_rks_notes[1]
        sign = "+" if value > 0 else ""
        added_rks_notes[1] = f"{sign}{value}"

    now = Save(**save)
    pluginData = await getNotes.getNotesData(session.user.id)

    # 1. 聚合历史分数
    time_vis = {}
    tot_update = []
    for song, levels in history.scoreHistory.items():
        for level, records in levels.items():
            prev = None
            for record in records:
                score_date = fCompute.date_to_string(scoreHistory.date(record))
                score_info = scoreHistory.extend(song, level, record, prev)
                prev = record
                idx = time_vis.setdefault(score_date, len(tot_update))
                if idx == len(tot_update):
                    tot_update.append(
                        {
                            "date": score_date,
                            "color": getRandomBgColor(),
                            "update_num": 0,
                            "song": [],
                        }
                    )
                tot_update[idx]["update_num"] += 1
                tot_update[idx]["song"].append(score_info)
                await asyncio.sleep(0)
            await asyncio.sleep(0)
        await asyncio.sleep(0)

    tot_update.sort(key=lambda x: Date(x["date"]), reverse=True)

    # 2. 日期和数量裁剪
    show = 0
    DayNum = max(PluginConfig.get("HistoryDayNum"), 2)
    DateNum = PluginConfig.get("HistoryScoreDate")
    TotNum = PluginConfig.get("HistoryScoreNum")
    filtered_update = []
    for date_idx, day in enumerate(tot_update):
        if date_idx > DateNum or TotNum <= show + min(DayNum, day["update_num"]):
            break
        day["song"].sort(key=lambda x: x.get("rks_new", 0), reverse=True)
        day["song"] = day["song"][: min(DayNum, TotNum - show)]
        show += len(day["song"])
        filtered_update.append(day)
    tot_update = filtered_update

    # 3. 分行处理
    box_line = []
    for day in tot_update:
        songs = day["song"]
        for i in range(0, len(songs), 5):
            line = {
                "color": day["color"],
                "song": songs[i : i + 5],
                "width": comWidth(len(songs[i : i + 5])),
            }
            if i == 0:
                line["date"] = day["date"]
            if i + 5 >= len(songs):
                line["update_num"] = day["update_num"]
            if not box_line or "date" in line:
                box_line.append([line])
            else:
                box_line[-1].append(line)

    # 4. 任务信息和曲绘
    task_data = pluginData.plugin_data.task
    task_time = fCompute.date_to_string(pluginData.plugin_data.task_time)
    if task_data:
        for task in task_data:
            task.illustration = getdata.getill(task.song)

    # 5. rks历史
    d_ = history.getRksLine()
    rks_history = d_.rks_history
    rks_range = d_.rks_range
    rks_date = d_.rks_date

    # 6. 汇总数据
    data = {
        "PlayerId": fCompute.convertRichText(now.saveInfo.PlayerId),
        "Rks": round(now.saveInfo.summary.rankingScore, 4),
        "Date": now.saveInfo.summary.updatedAt,
        "ChallengeMode": int(
            (
                now.saveInfo.summary.challengeModeRank
                - (now.saveInfo.summary.challengeModeRank % 1000)
            )
            / 100
        ),
        "ChallengeModeRank": now.saveInfo.summary.challengeModeRank % 100,
        "background": getdata.getill(random.choice(getInfo.illlist)),
        "box_line": box_line,
        "Notes": pluginData.plugin_data.money,
        "tips": random.choice(getInfo.Tips),
        "task_data": task_data,
        "task_time": task_time,
        "dan": await getdata.getDan(session.user.id),
        "added_rks_notes": added_rks_notes,
        "theme": pluginData.plugin_data.theme,
        "rks_date": [
            fCompute.date_to_string(rks_date[0]),
            fCompute.date_to_string(rks_date[1]),
        ],
        "rks_history": rks_history,
        "rks_range": rks_range,
    }
    await send.sendWithAt(
        [
            f"PlayerId: {fCompute.convertRichText(now.saveInfo.PlayerId, True)}",
            await getdata.getupdate(data),
        ],
    )
