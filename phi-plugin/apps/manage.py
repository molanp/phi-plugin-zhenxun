"""
phigros屁股肉管理
"""

from pathlib import Path
from typing import Literal

from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import Alconna, Args, CommandMeta, Match, on_alconna
from nonebot_plugin_htmlrender import shutdown_browser, start_browser
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_waiter import prompt

from zhenxun.services.log import logger
from zhenxun.utils.rules import admin_check, ensure_group

from ..config import recmdhead
from ..model.getBackup import getBackup
from ..model.getRksRank import getRksRank
from ..model.getSave import getSave
from ..model.path import backupPath
from ..model.send import send
from ..models import banGroup

banSetting: list[
    Literal[
        "help",
        "bind",
        "b19",
        "wb19",
        "song",
        "ranklist",
        "fnc",
        "tipgame",
        "guessgame",
        "ltrgame",
        "sign",
        "setting",
        "dan",
    ]
] = [
    "help",
    "bind",
    "b19",
    "wb19",
    "song",
    "ranklist",
    "fnc",
    "tipgame",
    "guessgame",
    "ltrgame",
    "sign",
    "setting",
    "dan",
]


restartpu = on_alconna(
    Alconna(rf"re:{recmdhead}\s*repu"), priority=5, block=True, permission=SUPERUSER
)

backup = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*backup",
        Args["extra?", str, ""],
        meta=CommandMeta(compact=True),
    ),
    priority=5,
    block=True,
    permission=SUPERUSER,
)

restore = on_alconna(
    Alconna(rf"re:{recmdhead}\s*restore"), priority=5, block=True, permission=SUPERUSER
)

get = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*get", Args["rank", int], meta=CommandMeta(compact=True)
    ),
    priority=5,
    block=True,
    permission=SUPERUSER,
)

delete = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*del", Args["sstk", str], meta=CommandMeta(compact=True)
    ),
    priority=5,
    block=True,
    permission=SUPERUSER,
)

allow = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*allow", Args["sstk", str], meta=CommandMeta(compact=True)
    ),
    priority=5,
    block=True,
    permission=SUPERUSER,
)

ban = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*ban", Args["func", str], meta=CommandMeta(compact=True)
    ),
    priority=5,
    block=True,
    rule=admin_check(5),
)

unban = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*unban", Args["func", str], meta=CommandMeta(compact=True)
    ),
    priority=5,
    block=True,
    rule=admin_check(5),
)


@restartpu.handle()
async def _():
    try:
        await shutdown_browser()
        await start_browser()
    except Exception as e:
        logger.error("重启浏览器失败", "phi-plugin:restartpu", e=e)
        await send.sendWithAt(str(e), True)
    else:
        await send.sendWithAt("成功", True)


@backup.handle()
async def _(extra: Match[str]):
    back = extra.result if extra.available else ""
    back = back.lower() == "back"
    await send.sendWithAt("开始备份，请稍等...")
    try:
        await getBackup.backup(back)
    except Exception as e:
        logger.error("备份失败", "phi-plugin:backup", e=e)
        await send.sendWithAt(str(e), True)


@restore.handle()
async def _():
    msg = "请选择要恢复的备份：\n"
    file_list: dict[int, Path] = {}
    try:
        for i, path in enumerate(backupPath.iterdir()):
            msg += f"[{i}]{path}\n"
            file_list[i] = path
        r = await prompt(msg, timeout=30)
        if r is None:
            await send.sendWithAt("操作已取消", True)
            return
        await doRestore(file_list, r.extract_plain_text().strip())
    except Exception as e:
        logger.error("获取备份失败", "phi-plugin:restore", e=e)
        await send.sendWithAt(str(e), True)
        return


async def doRestore(file_list: dict[int, Path], r: str):
    try:
        filePath = file_list[int(r)]
        await getBackup.restore(filePath)
        await send.sendWithAt(f"[{r}] {filePath} 恢复成功")
    except Exception as e:
        logger.error("备份恢复失败", "phi-plugin:restore", e=e)
        await send.sendWithAt([f"第[{r}]项不存在QAQ！", str(e)], True)


@get.handle()
async def _(rank: Match[int]):
    r = rank.result if rank.available else None
    if not r:
        await send.sendWithAt("输入错误: 序号不存在!")
        return
    token = await getRksRank.getRankUser(r - 1, r)
    await send.sendWithAt(str(token), True)


@delete.handle()
async def _(sstk: Match[str]):
    s = sstk.result if sstk.available else None
    if not s:
        await send.sendWithAt("输入错误: 未输入任何内容!")
        return
    await getSave.delSaveBySessionToken(s)
    await getSave.banSessionToken(s)
    await send.sendWithAt("成功", True)


@allow.handle()
async def _(sstk: Match[str]):
    s = sstk.result if sstk.available else None
    if not s:
        await send.sendWithAt("输入错误: 未输入任何内容!")
        return
    await getSave.allowSessionToken(s)
    await send.sendWithAt("成功", True)


@ban.handle()
async def _(session: Uninfo, func: Match[str]):
    if not ensure_group(session):
        await send.sendWithAt("请在群聊中使用呐！")
        return
    f = func.result if func.available else None
    if not f:
        await send.sendWithAt("输入错误: 未输入任何内容!")
        return
    group_id = session.scene.id
    match f:
        case "all":
            for i in banSetting:
                await banGroup.add(group_id, i)
        case _:
            if f in banSetting:
                await banGroup.add(
                    group_id,
                    f,
                )
    await send.sendWithAt(
        f"当前: {group_id}\n已禁用:\n\t- {{}}".format(
            "\n\t- ".join(await banGroup.show(group_id))
        )
    )


@unban.handle()
async def _(session: Uninfo, func: Match[str]):
    if not ensure_group(session):
        await send.sendWithAt("请在群聊中使用呐！")
        return
    f = func.result if func.available else None
    if not f:
        await send.sendWithAt("输入错误: 未输入任何内容!")
        return
    group_id = session.scene.id
    match f:
        case "all":
            for i in banSetting:
                await banGroup.remove(
                    group_id,
                    i,
                )
        case _:
            if f in banSetting:
                return await banGroup.remove(
                    group_id,
                    f,
                )
    await send.sendWithAt(
        f"当前: {group_id}\n已禁用:\n\t- {{}}".format(
            "\n\t- ".join(await banGroup.show(group_id))
        )
    )
