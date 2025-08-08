"""
phi-plugin更新
"""

import re

from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import Alconna, on_alconna

from zhenxun.utils.repo_utils.utils import check_git

from ..config import cmdhead
from ..model.send import send

recmdhead = re.escape(cmdhead)

update = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(强制|qz)?(更新|gx)"),
    priority=5,
    block=True,
    permission=SUPERUSER,
)

ill_update = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(下载|更新|gx|down|up)\s*(曲绘|ill)"),
    priority=5,
    block=True,
    permission=SUPERUSER,
)


@update.handle()
async def _():
    if not await check_git():
        await send.sendWithAt("当前环境中不存在Git，无法使用此命令", True)
        return
    await send.sendWithAt("未使用git安装本插件，不支持此功能", True)


@ill_update.handle()
async def _():
    if not await check_git():
        await send.sendWithAt("当前环境中不存在Git，无法使用此命令", True)
        return
    await send.sendWithAt("未使用git安装本插件，不支持此功能", True)
