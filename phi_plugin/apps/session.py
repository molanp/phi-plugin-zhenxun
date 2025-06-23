import asyncio
import random
import re
import time
from typing import Any

from nonebot_plugin_alconna import Alconna, Args, Arparma, on_alconna
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_waiter import prompt

from zhenxun.services.log import logger
from zhenxun.utils.platform import PlatformUtils
from zhenxun.utils.rules import ensure_group
from zhenxun.utils.withdraw_manage import WithdrawManager

from ..config import PluginConfig
from ..lib.getQRcode import getQRcode
from ..model.cls.common import Save
from ..model.cls.saveHistory import saveHistory
from ..model.cls.scoreHistory import scoreHistory
from ..model.fCompute import fCompute
from ..model.getBanGroup import getBanGroup
from ..model.getdata import getdata
from ..model.getInfo import getInfo
from ..model.getNotes import getNotes
from ..model.getSave import getSave
from ..model.getSaveFromApi import getSaveFromApi
from ..model.getUpdateSave import getUpdateSave
from ..model.makeRequest import makeRequest
from ..model.makeRequestFnc import makeRequestFnc
from ..model.send import send
from ..models import qrCode
from ..utils import Date, to_dict

cmdhead = re.escape(PluginConfig.get("cmdhead", "/phi"))
apiMsg = (
    "\n请注意，您尚未设置API Token！\n指令格式：\n"
    f"{cmdhead} setApiToken <apiToken>\n更多帮助：{cmdhead} apihelp"
)

bind = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(绑定|bind)", Args["sessionToken?", str | int, "None"]),
    block=True,
    priority=5,
)
update = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(更新|update)"),
    block=True,
    priority=5,
)
unbind = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(解绑|unbind)"),
    block=True,
    priority=5,
)
clean = on_alconna(
    Alconna(rf"re:{cmdhead}\s*clean"),
    block=True,
    priority=5,
)
getSstk = on_alconna(
    Alconna(rf"re:{cmdhead}\s*sessionToken"),
    block=True,
    priority=5,
)


@bind.handle()
async def _(bot, session: Uninfo, params: Arparma):
    """这里逻辑太复杂了，得谨慎点"""
    if await getBanGroup.get(bind, session, "bind"):
        await send.sendWithAt(bind, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    param: Any = params.query("sessionToken")
    sessionToken = re.compile(r"[0-9a-zA-Z]{25}|qrcode", re.IGNORECASE).search(param)
    localPhigrosToken = await getSave.get_user_token(session.user.id)
    sessionToken = sessionToken[0] if sessionToken else localPhigrosToken
    if localPhigrosToken:
        await send.sendWithAt(bind, "不要重复绑定啊喂!")
        return
    if not sessionToken:
        apiId = re.compile(r"[0-9]{10}", re.IGNORECASE).search(param)
        apiId = apiId[0] if apiId else None
        if PluginConfig.get("openPhiPluginApi"):
            result = await makeRequest.bind(
                {
                    **makeRequestFnc.makePlatform(session),
                    "api_user_id": apiId,
                }
            )
            if result.data.internal_id:
                resMsg = (
                    f"绑定成功！您的查分ID为：{result.data.internal_id}，请妥善保管嗷！"
                )
                if not result.data.have_api_token:
                    resMsg += apiMsg
                await send.sendWithAt(bind, resMsg)
                updateData = await getUpdateSave.getNewSaveFromApi(
                    session, sessionToken
                )
                history = await getSaveFromApi.getHistory(
                    session, ["data", "rks", "scoreHistory"]
                )
                await build(bind, session, updateData, history)
                return
            if result.message == "用户 未找到":
                await send.sendWithAt(
                    bind,
                    "喂喂喂！你还没输入sessionToken呐！\n"
                    f"扫码绑定：{cmdhead} bind qrcode\n"
                    f"普通绑定：{cmdhead} bind <sessionToken>",
                )
            else:
                await send.sendWithAt(bind, result.message)
                logger.error("API错误", "phi-plugin", session=session)
                logger.error(result.message, "phi-plugin", session=session)
        elif apiId:
            await send.sendWithAt(
                bind, "这里没有连接查分平台哦！请使用sessionToken进行绑定！"
            )
        else:
            await send.sendWithAt(
                bind,
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
                    bind,
                    [
                        "请识别二维码并按照提示进行登录嗷！请勿错扫他人二维码。"
                        "请注意，登录TapTap可能造成账号及财产损失，"
                        "请在信任Bot来源的情况下扫码登录。\n"
                        f"二维码剩余时间:{QRCodetimeout}",
                        await getQRcode.getQRcode(qrcode),
                    ],
                    False,
                    recallTime
                )
            else:
                qrCodeMsg = await send.sendWithAt(
                    bind,
                    "请点击链接进行登录嗷！请勿使用他人的链接。请注意，"
                    "登录TapTap可能造成账号及财产损失，请在信任Bot来源的情况下扫码登录。\n"
                    f"链接剩余时间:{QRCodetimeout}\n{qrcode}",
                    recallTime=recallTime
                )
        else:
            request = await getQRcode.getRequest()
            if PluginConfig.get("TapTapLoginQRcode"):
                qrCodeMsg = await send.sendWithAt(
                    bind,
                    [
                        "请识别二维码并按照提示进行登录嗷！请勿错扫他人二维码。"
                        "请注意，登录TapTap可能造成账号及财产损失，请在信任Bot来源的情况下扫码登录。",
                        await getQRcode.getQRcode(request["data"]["qrcode_url"]),
                    ],
                    recallTime=60
                )
            else:
                qrCodeMsg = await send.sendWithAt(
                    bind,
                    "请点击链接进行登录嗷！请勿使用他人的链接。"
                    "请注意，登录TapTap可能造成账号及财产损失，请在信任Bot来源的情况下扫码登录。\n"
                    f"{request['data']['qrcode_url']}",
                    recallTime=60
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
            await send.sendWithAt(bind, "操作超时，请重试QAQ！")
            return
        try:
            sessionToken = await getQRcode.getSessionToken(result)
        except Exception as e:
            logger.error("获取sessionToken失败", "phi-plugin", e=e, session=session)
            await send.sendWithAt(
                bind,
                "获取sessionToken失败QAQ！请确认您的Phigros已登录TapTap账号并同步！"
                f"\n错误信息：{type(e)}: {e}",
            )
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(bind, "正在绑定，请稍等一下哦！\n >_<", recallTime=5)
    if PluginConfig.get("openPhiPluginApi"):
        try:
            result = await makeRequest.bind(
                {**makeRequestFnc.makePlatform(session), "token": sessionToken}
            )
            if result.data.internal_id:
                resMsg = (
                    f"绑定成功！您的查分ID为：{result.data.internal_id}，请妥善保管嗷！"
                )
                if not result.data.have_api_token:
                    resMsg += apiMsg
                await send.sendWithAt(bind, resMsg)
                updateData = await getUpdateSave.getNewSaveFromApi(
                    session, sessionToken
                )
                history = await getSaveFromApi.getHistory(
                    session, ["data", "rks", "scoreHistory"]
                )
                await build(bind, session, updateData, history)
        except Exception as e:
            await send.sendWithAt(
                bind, f"{e}\n从API获取存档失败，本次绑定将不上传至查分平台QAQ！"
            )
            logger.error("API错误", "phi-plugin", e=e)
        return
    await send.sendWithAt(
        bind,
        "请注意保护好自己的sessionToken呐！如果需要获取已绑定的sessionToken可以私聊发送"
        f"{cmdhead} sessionToken 哦！",
        recallTime=10
    )
    # with contextlib.suppress(Exception):
    updateData = await getUpdateSave.getNewSaveFromLocal(bind, session, sessionToken)
    history = await getSave.getHistory(session.user.id)
    await build(bind, session, updateData, history)


@update.handle()
async def _(session: Uninfo):
    if await getBanGroup.get(update, session, "update"):
        await send.sendWithAt(update, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    if PluginConfig.get("openPhiPluginApi"):
        try:
            updateData = await getUpdateSave.getNewSaveFromApi(session)
            history = await getSaveFromApi.getHistory(
                session, ["data", "rks", "scoreHistory"]
            )
            await build(update, session, updateData, history)
            return
        except Exception as e:
            await send.sendWithAt(
                update,
                f"{e}\n从API获取存档失败，本次更新将使用本地数据QAQ！",
            )
            logger.error("API错误", "phi-plugin", e=e)
    sessionToken = await getSave.get_user_token(session.user.id)
    if not sessionToken:
        await send.sendWithAt(
            update,
            "没有找到你的存档哦！请先绑定sessionToken！\n"
            f"帮助：{cmdhead} tk help\n"
            f"格式：{cmdhead} bind <sessionToken>",
        )
        return
    if not PluginConfig.get("isGuild"):
        await send.sendWithAt(bind, "正在生成，请稍等一下哦！\n >_<", recallTime=5)
    try:
        updateData = await getUpdateSave.getNewSaveFromLocal(
            update, session, sessionToken
        )
        history = await getSave.getHistory(session.user.id)
        await build(update, session, updateData, history)
    except Exception as e:
        logger.error("更新信息失败", "phi-plugin", e=e)
        await send.sendWithAt(
            update,
            f"更新失败，请检查你的sessionToken是否正确QAQ！\n错误信息：{type(e)}: {e}",
        )


@unbind.handle()
async def _(session: Uninfo):
    if await getBanGroup.get(unbind, session, "unbind"):
        await send.sendWithAt(unbind, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    if not await getSave.get_user_token(
        session.user.id
    ) and not await getSaveFromApi.get_user_apiId(session.user.id):
        await send.sendWithAt(unbind, "没有找到你的存档信息嗷！")
        return
    ensure = await prompt(
        "解绑会导致历史数据全部清空呐QAQ！真的要这么做吗?(确认/取消)", timeout=30
    )
    if str(ensure).strip() == "确认":
        flag = True
        try:
            await getSave.delSave(session.user.id)
            if PluginConfig.get("openPhiPluginApi"):
                await getSaveFromApi.delSave(session)
            await getNotes.delNotesData(session.user.id)
        except Exception as e:
            await send.sendWithAt(unbind, f"解绑失败QAQ！\n错误信息：{type(e)}: {e}")
            logger.error("用户解绑失败", "phi-plugin", session=session, e=e)
            flag = False
        if flag:
            await send.sendWithAt(unbind, "解绑成功")
    else:
        await send.sendWithAt(unbind, "已取消操作")


@clean.handle()
async def _(session: Uninfo):
    ensure = await prompt(
        "请注意，本操作将会删除Phi-Plugin关于您的所有信息QAQ！真的要这么做吗?(确认/取消)",
        timeout=30,
    )
    if str(ensure).strip() == "确认":
        flag = True
        try:
            await getSave.delSave(session.user.id)
            await getNotes.delNotesData(session.user.id)
        except Exception as e:
            await send.sendWithAt(clean, f"删除失败QAQ！\n错误信息：{type(e)}: {e}")
            flag = False
        if flag:
            await send.sendWithAt(clean, "清除数据成功")
    else:
        await send.sendWithAt(unbind, "已取消操作")


@getSstk.handle()
async def _(session: Uninfo):
    if ensure_group(session):
        await send.sendWithAt(getSstk, "请私聊使用嗷")
        return
    save = await send.getsaveResult(getSstk, session, -1, False)
    if save is None:
        await send.sendWithAt(getSstk, "未绑定存档，请先绑定存档嗷！")
        return
    await send.sendWithAt(
        getSstk,
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


async def waitResponse(bot, QRCodetimeout, request, recall_id, qrCodeMsg):
    start_time = time.time()
    # 是否发送过已扫描提示
    flag = False
    result = {}
    while time.time() - start_time < QRCodetimeout:
        result = await getQRcode.checkQRCodeResult(request)
        if result.get("success"):
            break
        if result["data"].get("error") == "authorization_waiting" and not flag:
            await send.sendWithAt(bind, "二维码已扫描，请确认登录", recallTime=10)
            WithdrawManager.remove(recall_id)
            WithdrawManager.append(
                bot,
                qrCodeMsg.msg_ids[0]["message_id"],
                1,
            )
            flag = True
        await asyncio.sleep(2)
    return result


async def build(matcher, session: Uninfo, updateData: dict, history: saveHistory):
    """
    保存PhigrosUser

    js版本怎么跑起来的

    :param matcher: matcher
    :param updateData: {save:Save, added_rks_notes: [number, number]}
    :param history: saveHistory
    :return: Promise<void>
    """
    updateData = to_dict(updateData)
    added_rks_notes = updateData.get("added_rks_notes", [0, 0])
    save = updateData.get("save", {})
    if added_rks_notes[0]:
        value = added_rks_notes[0]
        sign = "+" if value > 0 else ""
        formatted = f"{value:.4f}" if value >= 1e-4 else ""
        added_rks_notes[0] = f"{sign}{formatted}"

    if added_rks_notes[1]:
        value = added_rks_notes[1]
        sign = "+" if value > 0 else ""
        added_rks_notes[1] = f"{sign}{value}"
    # 标记数据中含有的时间
    time_vis: dict[str, int] = {}
    # 总信息
    tot_update: list[dict] = []

    now = await Save().constructor(save)
    pluginData = await getNotes.getNotesData(session.user.id)
    for song in history.scoreHistory:
        tem = history.scoreHistory[song]
        for level in tem:
            _history = tem[level]
            for i, _ in enumerate(_history):
                score_date = fCompute.date_to_string(scoreHistory.date(_history[i]))
                score_info = await scoreHistory.extend(
                    song, level, _history[i], _history[i - 1]
                )
                if time_vis.get(score_date) is None:
                    time_vis[score_date] = len(tot_update)
                    tot_update.append(
                        {
                            "date": score_date,
                            "color": getRandomBgColor(),
                            "update_num": 0,
                            "song": [],
                        }
                    )
                tot_update[time_vis[score_date]]["update_num"] += 1
                tot_update[time_vis[score_date]]["song"].append(score_info)
    tot_update = sorted(tot_update, key=lambda x: Date(x["date"]), reverse=True)
    # 实际显示的数量
    show = 0
    # 每日显示上限
    DayNum = max(PluginConfig.get("HistoryDayNum"), 2)
    # 显示日期上限
    DateNum = PluginConfig.get("HistoryScoreDate")
    # 总显示上限
    TotNum = PluginConfig.get("HistoryScoreNum")
    for date, _ in enumerate(tot_update):
        # 天数上限
        if date > DateNum or TotNum <= show + min(
            DayNum, tot_update[date]["update_num"]
        ):
            tot_update = tot_update[:date]
            break
        # 预处理每日显示上限
        tot_update[date]["song"] = sorted(
            tot_update[date]["song"], key=lambda x: x.get("rks_new", 0), reverse=True
        )
        tot_update[date]["song"] = tot_update[date]["song"][
            : min(DayNum, TotNum - show)
        ]
        # 总上限
        show += len(tot_update[date]["song"])
    # 预分行
    box_line = []
    # 循环中当前行的数量
    line_num = 5
    flag = False
    while tot_update:
        if line_num == 5:
            if flag:
                box_line.append(
                    [
                        {
                            "color": tot_update[0]["color"],
                            "song": tot_update[0]["song"][:5],
                        }
                    ]
                )
            else:
                box_line.append(
                    [
                        {
                            "date": tot_update[0]["date"],
                            "color": tot_update[0]["color"],
                            "song": tot_update[0]["song"][:5],
                        }
                    ]
                )
            line_num = len(box_line[-1][-1]["song"])
        elif flag:
            box_line[-1].append(
                {
                    "color": tot_update[0]["color"],
                    "song": tot_update[0]["song"][: 5 - line_num],
                }
            )
        else:
            box_line[-1].append(
                {
                    "date": tot_update[0]["date"],
                    "color": tot_update[0]["color"],
                    "song": tot_update[0]["song"][: 5 - line_num],
                }
            )
        box_line[-1][-1]["width"] = comWidth(len(box_line[-1][-1]["song"]))
        flag = True
        if not tot_update[0].get("song"):
            box_line[-1][-1]["update_num"] = tot_update[0]["update_num"]
            tot_update.pop(0)
            flag = False
        tot_update.pop(0)
    # 添加任务信息
    task_data = pluginData.plugin_data.task
    task_time = fCompute.date_to_string(pluginData.plugin_data.task_time)
    # 添加曲绘
    if task_data:
        for i, _ in enumerate(task_data):
            if task_data[i]:
                task_data[i]["illustration"] = await getdata.getill(
                    task_data[i]["song"]
                )
                if task_data[i]["request"]["type"] == "acc":
                    task_data[i]["request"]["value"] = (
                        round(task_data[i]["request"]["value"], 4) + "%"
                    )
                    if len(task_data[i]["request"]["value"]) < 6:
                        task_data[i]["request"]["value"] = (
                            "0" + task_data[i]["request"]["value"]
                        )
    d_ = history.getRksLine()
    rks_history = d_.rks_history
    rks_range = d_.rks_range
    rks_date = d_.rks_date
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
        "background": await getdata.getill(random.choice(getInfo.illlist)),
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
        matcher,
        [
            f"PlayerId: {fCompute.convertRichText(now.saveInfo.PlayerId, True)}",
            await getdata.getupdate(data),
        ],
    )
