"""phi-plugin货币系统"""

import asyncio
import math
import random
import time

from nonebot_plugin_alconna import Alconna, Args, At, CommandMeta, Match, on_alconna
from nonebot_plugin_uninfo import Uninfo

from zhenxun.utils.platform import PlatformUtils

from ..config import cmdhead, recmdhead
from ..model.cls.common import Save
from ..model.cls.LevelRecordInfo import LevelRecordInfo
from ..model.constNum import Level, LevelItem
from ..model.getdata import getdata
from ..model.getInfo import getInfo
from ..model.getNotes import getNotes, taskData
from ..model.send import send
from ..rule import can_be_call
from ..utils import Date, to_dict

theme_data = [
    {"id": "default", "src": "默认"},
    {"id": "snow", "src": "寒冬"},
    {"id": "star", "src": "使一颗心免于哀伤"},
]


sp_date_tips = [
    "渲...渲染失败QAQ！啊...什么！这里不是B30吗？！不...不管了！愚人节快乐！"
]


Level: list[LevelItem] = Level

sign = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(sign|sign in|签到|打卡)"),
    block=True,
    priority=5,
    rule=can_be_call("sign"),
)

tasks = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(task|我的任务)"),
    block=True,
    priority=5,
    rule=can_be_call("tasks"),
)

retask = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(retask|刷新任务)"),
    block=True,
    priority=5,
    rule=can_be_call("retask"),
)

give = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(send|送|转)",
        Args["_target?", At | int | str]["_money?", int],
        meta=CommandMeta(compact=True),
    ),
    block=True,
    priority=5,
    rule=can_be_call("send"),
)

theme = on_alconna(
    Alconna(
        rf"re:{recmdhead}\*theme", Args["_aim?", int], meta=CommandMeta(compact=True)
    ),
    block=True,
    priority=5,
    rule=can_be_call("theme"),
)


@sign.handle()
async def _(session: Uninfo):
    """签到"""
    data = await getNotes.getNotesData(session.user.id)
    last_sign = data.plugin_data.sign_in
    now_time = Date(time.time())
    request_time = now_time.replace(hour=0, minute=0, second=0)
    is_sp_date = now_time.month == 4 and now_time.day == 1
    if request_time > last_sign:
        getnum = random.randint(5, 20)
        if is_sp_date:
            getnum = random.choice([4, 1])
        data.plugin_data.money += getnum
        data.plugin_data.sign_in = now_time
        await getNotes.putNotesData(session.user.id, to_dict(data))
        # 判断时间段
        time1 = now_time.replace(hour=6, minute=0, second=0)
        time2 = now_time.replace(hour=11, minute=30, second=0)
        time3 = now_time.replace(hour=13, minute=0, second=0)
        time4 = now_time.replace(hour=18, minute=30, second=0)
        time5 = now_time.replace(hour=23, minute=0, second=0)

        str_time = now_time.strftime("%H:%M:%S")

        Remsg = []
        if now_time < time1:
            Remsg.append(
                f"签到成功！现在是{str_time}，夜深了，注意休息哦！(∪.∪ )...zzz\n"
            )
        elif now_time < time2:
            Remsg.append(f"签到成功！现在是{str_time}，早安呐！ヾ(≧▽≦*)o\n")
        elif now_time < time3:
            Remsg.append(f"签到成功！现在是{str_time}，午好嗷！(╹ڡ╹ )\n")
        elif now_time < time4:
            Remsg.append(f"签到成功！现在是{str_time}，下午好哇！(≧∀≦)ゞ\n")
        elif now_time < time5:
            Remsg.append(f"签到成功！现在是{str_time}，晚上好！( •̀ ω •́ )✧\n")
        else:
            Remsg.append(
                f"签到成功！现在是{str_time}，夜深了，注意休息哦！(∪.∪ )...zzz\n"
            )
        if is_sp_date:
            Remsg.append(
                f"{random.choice(sp_date_tips)}恭喜您获得了{getnum}个Note！"
                f"当前您所拥有的 Note 数量为：{data.plugin_data.money}"
            )
        else:
            Remsg.append(
                f"恭喜您获得了{getnum}个Note！"
                f"当前您所拥有的 Note 数量为：{data.plugin_data.money}\n"
                "祝您今日愉快呐！（￣︶￣）↗　"
            )
        save = await send.getsaveResult(session, send=False)
        if save:
            last_task = data.plugin_data.task_time

            if last_task < request_time:
                # 如果有存档并且没有刷新过任务自动刷新
                await _retask(session)
                Remsg.append("\n已自动为您刷新任务！您今日份的任务如下：")
            else:
                await _tasks(session)
                Remsg.append("\n您今日已经领取过任务了哦！您今日份的任务如下：")
        else:
            Remsg.append(
                "\n您当前没有绑定sessionToken呐！任务需要绑定sessionToken后才能获取哦！"
                f"\n{cmdhead} bind <sessionToken>"
            )
        await send.sendWithAt(Remsg)
    elif is_sp_date:
        await send.sendWithAt(
            f"{random.choice(sp_date_tips)}"
            f"你在今天{last_sign.strftime('%H:%M:%S')}的时候已经签过到了哦！\n"
            f"你现在的Note数量: {data.plugin_data.money}"
        )
    else:
        await send.sendWithAt(
            f"你在今天{last_sign.strftime('%H:%M:%S')}的时候已经签过到了哦！\n"
            f"你现在的Note数量: {data.plugin_data.money}"
        )


@retask.handle()
async def _retask(session: Uninfo):
    """刷新任务并发送图片"""
    save = await getdata.getsave(session.user.id)
    if not save:
        await send.sendWithAt(
            f"该功能需要绑定后才能使用哦！\n格式：{cmdhead} bind <sessionToken>"
        )
        return
    data = await getNotes.getNotesData(session.user.id)
    last_task = data.plugin_data.task_time
    now_time = Date(time.time())
    request_time = now_time.replace(hour=0, minute=0, second=0)
    oldtask = []

    # note变化
    change_note = 0

    if request_time <= last_task:
        # 花费20Notes刷新
        if data.plugin_data.money >= 20:
            data.plugin_data.money -= 20
            change_note -= 20
            oldtask = data.plugin_data.task
        else:
            await send.sendWithAt(
                "刷新任务需要 20 Notes，咱没有那么多Note哇QAQ！\n"
                f"你当前的 Note 数目为：{data.plugin_data.money}"
            )
            return
    data.plugin_data.task_time = now_time
    data.plugin_data.task = randtask(save, oldtask)
    vis = bool(data.plugin_data.task)
    if not vis:
        await send.sendWithAt(
            "哇塞，您已经把所有曲目全部满分了呢！没有办法为您布置任务了呢！敬请期待其他玩法哦！"
        )
        return

    await getNotes.putNotesData(session.user.id, to_dict(data))

    str_time = now_time.strftime("%H:%M:%S")

    # 判断时间段
    time1 = now_time.replace(hour=6, minute=0, second=0)
    time2 = now_time.replace(hour=11, minute=30, second=0)
    time3 = now_time.replace(hour=13, minute=0, second=0)
    time4 = now_time.replace(hour=18, minute=30, second=0)
    time5 = now_time.replace(hour=23, minute=0, second=0)

    if now_time < time1:
        Remsg = f"现在是{str_time}，夜深了，注意休息哦！"
        Remsg1 = "(∪.∪ )...zzz"
    elif now_time < time2:
        Remsg = f"现在是{str_time}，早安呐！"
        Remsg1 = "ヾ(≧▽≦*)o"
    elif now_time < time3:
        Remsg = f"现在是{str_time}，午好嗷！"
        Remsg1 = "(╹ڡ╹ )"
    elif now_time < time4:
        Remsg = f"现在是{str_time}，下午好哇！"
        Remsg1 = "(≧∀≦)ゞ"
    elif now_time < time5:
        Remsg = f"现在是{str_time}，晚上好！"
        Remsg1 = "( •̀ ω •́ )✧"
    else:
        Remsg = f"现在是{str_time}，夜深了，注意休息哦！"
        Remsg1 = "(∪.∪ )...zzz"

    # 添加曲绘
    if data.plugin_data.task:
        for t in data.plugin_data.task:
            t.illustration = getInfo.getill(t.song)
    picdata = {
        "PlayerId": save.saveInfo.PlayerId,
        "Rks": round(save.saveInfo.summary.rankingScore, 4),
        "Date": now_time.strftime("%H:%M:%S %b.%d %Y"),
        "ChallengeMode": math.floor(save.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": save.saveInfo.summary.challengeModeRank % 100,
        "background": getInfo.getill(random.choice(getInfo.illlist)),
        "task": data.plugin_data.task,
        "task_ans": Remsg,
        "task_ans1": Remsg1,
        "Notes": data.plugin_data.money,
        "tips": random.choice(getInfo.Tips),
        "change_notes": change_note or "",
        "theme": data.plugin_data.theme,
    }
    is_sp_date = now_time.month == 4 and now_time.day == 1
    if is_sp_date:
        picdata["tips"] = random.choice(sp_date_tips)
    await send.sendWithAt(await getdata.gettasks(to_dict(picdata)))


@tasks.handle()
async def _tasks(session: Uninfo):
    now = await send.getsaveResult(session)
    if not now:
        return
    now_time = Date(time.time())

    str_time = now_time.strftime("%H:%M:%S")

    # 判断时间段
    time1 = now_time.replace(hour=6, minute=0, second=0)
    time2 = now_time.replace(hour=11, minute=30, second=0)
    time3 = now_time.replace(hour=13, minute=0, second=0)
    time4 = now_time.replace(hour=18, minute=30, second=0)
    time5 = now_time.replace(hour=23, minute=0, second=0)

    if now_time < time1:
        Remsg = f"现在是{str_time}，夜深了，注意休息哦！"
        Remsg1 = "(∪.∪ )...zzz"
    elif now_time < time2:
        Remsg = f"现在是{str_time}，早安呐！"
        Remsg1 = "ヾ(≧▽≦*)o"
    elif now_time < time3:
        Remsg = f"现在是{str_time}，午好嗷！"
        Remsg1 = "(╹ڡ╹ )"
    elif now_time < time4:
        Remsg = f"现在是{str_time}，下午好哇！"
        Remsg1 = "(≧∀≦)ゞ"
    elif now_time < time5:
        Remsg = f"现在是{str_time}，晚上好！"
        Remsg1 = "( •̀ ω •́ )✧"
    else:
        Remsg = f"现在是{str_time}，夜深了，注意休息哦！"
        Remsg1 = "(∪.∪ )...zzz"

    data = await getNotes.getNotesData(session.user.id)
    # 添加曲绘
    if data.plugin_data.task:
        for t in data.plugin_data.task:
            t.illustration = getInfo.getill(t.song)
    picdata = {
        "PlayerId": now.saveInfo.PlayerId,
        "Rks": round(now.saveInfo.summary.rankingScore, 4),
        "Date": now_time.strftime("%H:%M:%S %b.%d %Y"),
        "ChallengeMode": math.floor(now.saveInfo.summary.challengeModeRank / 100),
        "ChallengeModeRank": now.saveInfo.summary.challengeModeRank % 100,
        "background": getInfo.getill(random.choice(getInfo.illlist)),
        "task": data.plugin_data.task,
        "task_ans": Remsg,
        "task_ans1": Remsg1,
        "Notes": data.plugin_data.money,
        "tips": random.choice(getInfo.Tips),
        "dan": await getdata.getDan(session.user.id),
        "theme": data.plugin_data.theme,
    }
    is_sp_date = now_time.month == 4 and now_time.day == 1
    if is_sp_date:
        picdata["tips"] = random.choice(sp_date_tips)

    await send.sendWithAt(await getdata.gettasks(to_dict(picdata)))


@give.handle()
async def _(bot, session: Uninfo, _target: Match[At | int | str], _money: Match[int]):
    """转账"""
    target = _target.result if _target.available else None
    money = _money.result if _money.available else None
    if target is None or money is None:
        await send.sendWithAt(
            f"格式错误！请指定目标\n格式：{cmdhead} send <@ or id> <数量>", True
        )
        return
    if isinstance(target, At):
        target = target.target
    if isinstance(target, int):
        target = str(target)
    target_info = await PlatformUtils.get_user(bot, target, session.scene.id)
    if not target_info:
        await send.sendWithAt("这个用户……好像没有见过呢……")
        return
    sender_data = await getNotes.getNotesData(session.user.id)
    if target == session.user.id:
        await send.sendWithAt("转账成……欸？这个目标……在拿我寻开心嘛！")
        await asyncio.sleep(1)
        await send.sendWithAt("转账失败！扣除 20 Notes！")
        if sender_data.plugin_data.money < 20:
            await send.sendWithAt("a，你怎么连20 Note都没有哇")
            await send.sendWithAt("www，算了，我今天心情好，不和你计较了，哼！")
        else:
            sender_data.plugin_data.money -= 20
        await getNotes.putNotesData(session.user.id, to_dict(sender_data))
        return

    if sender_data.plugin_data.money < money:
        await send.sendWithAt(
            f"你当前的Note数量不够哦！\n当前Note: {sender_data.plugin_data.money}"
        )
        return
    target_data = await getNotes.getNotesData(target)
    sender_old = sender_data.plugin_data.money
    target_old = target_data.plugin_data.money
    sender_data.plugin_data.money -= money
    await getNotes.putNotesData(session.user.id, to_dict(sender_data))
    target_data.plugin_data.money += math.ceil(money * 0.8)
    await getNotes.putNotesData(target, to_dict(target_data))

    target_name = (
        target_info.card
        if target_info.card is not None and target_info.card != ""
        else target_info.name
    )
    await send.sendWithAt(
        f"转账成功！\n你当前的Note: {sender_old} -{money} = "
        f"{sender_data.plugin_data.money}\n{target_name}的Note: "
        f"{target_old} + {math.ceil(money * 0.8)} = {target_data.plugin_data.money}"
    )


@theme.handle()
async def _(session: Uninfo, _aim: Match[int]):
    """主题相关"""
    aim = _aim.result if _aim.available else None
    if aim is None or aim < 0 or aim > 2:
        await send.sendWithAt(f"请输入主题数字嗷！\n格式{cmdhead} theme 0-2")
        return
    plugin_data = await getNotes.getNotesData(session.user.id)
    plugin_data.plugin_data.theme = theme_data[aim]["id"]
    await getNotes.putNotesData(session.user.id, to_dict(plugin_data))

    await send.sendWithAt(f"设置成功！\n你当前的主题是: 「{theme_data[aim]['src']}」")


def randtask(save: Save, task: list[taskData] | None = None):
    if task is None:
        task = []
    rks = save.saveInfo.summary.rankingScore
    gameRecord: dict[str, list[LevelRecordInfo | None]] = {}
    for song in save.gameRecord:
        if s := getInfo.idgetsong(song):
            gameRecord[s] = save.gameRecord[song]
    info = getInfo.ori_info
    # 任务难度分级后的曲目列表
    ranked_songs: list[list[dict]] = [[], [], [], [], []]
    # 割分歌曲的临界定数
    rank_line = []
    while len(task) < len(ranked_songs):
        task.append(None)  # pyright: ignore[reportArgumentType] # 填充占位符

    if rks < 15:
        rank_line.extend((rks - 1, rks - 0.5, rks + 0, rks + 1))
    elif rks < 16:
        rank_line.extend((rks - 1.5, rks - 0.3, rks + 0, rks + 0.5))
    else:
        rank_line.extend((rks - 2, rks - 1, rks - 0.5, rks + 0))
    rank_line.append(18)

    # 将曲目分级并处理
    for id in info:
        if id == "テリトリーバトル.ツユ":
            continue
        for level in Level:
            if c := info[id].chart.get(level):
                if (
                    id not in gameRecord
                    or level not in gameRecord[id]
                    or getattr(gameRecord[id][level], "acc", 0) != 100
                ):
                    dif = c.difficulty
                    for i, v in enumerate(rank_line):
                        if dif < v:
                            ranked_songs[i].append({"song": id, "level": level})
                            break

    reward = [10, 15, 30, 60, 80, 100]
    for i, v in enumerate(ranked_songs):
        if i < len(task) and task[i].finished:
            continue
        aim = random.choice(ranked_songs[i])
        if not aim:
            continue
        song = aim["song"]
        level = Level.index(aim["level"])
        _type = random.randint(0, 1)  # 0: acc, 1: score
        old_acc = 0
        old_score = 0
        if (
            song in gameRecord
            and level < len(gameRecord[song])
            and gameRecord[song][level]
        ):
            old_acc = gameRecord[song][level].acc  # pyright: ignore[reportOptionalMemberAccess]
            old_score = gameRecord[song][level].score  # pyright: ignore[reportOptionalMemberAccess]
        if _type:
            base = min(old_score + 1, 1e6)
            change = 1e6 - base
            value = -change * math.cos(random.random() * math.pi / 2) + change + base
            value = min(round(value), 1e6)
        else:
            base = min(old_acc + 0.01, 100)
            change = 100 - base
            value = -change * math.cos(random.random() * math.pi / 2) + change + base
            value = min(round(value, 2), 100)
        task[i] = taskData(
            **{
                "song": song,
                "reward": random.choice(reward),
                "finished": False,
                "request": {
                    "rank": level,
                    "type": "score" if _type else "acc",
                    "value": value,
                },
            }
        )
    return task
