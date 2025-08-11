"""
phigros屁股肉帮助
"""

import random

from nonebot_plugin_alconna import Alconna, on_alconna
from nonebot_plugin_uninfo import Uninfo

from ..config import cmdhead, recmdhead
from ..model.getdata import getdata
from ..model.getFile import readFile
from ..model.getInfo import getInfo
from ..model.path import infoPath
from ..model.picmodle import picmodle
from ..model.send import send
from ..utils import can_be_call

help = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(命令|帮助|菜单|help|说明|功能|指令|使用说明)",
    ),
    rule=can_be_call("help"),
    priority=5,
    block=True,
)
tkhelp = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*tok(?:en)?(命令|帮助|菜单|help|说明|功能|指令|使用说明)",
    ),
    rule=can_be_call("tkhelp"),
    priority=5,
    block=True,
)


@help.handle()
async def _(bot, session: Uninfo):
    pluginData = await getdata.getNotesData(session.user.id)
    helpGroup = await readFile.FileReader(infoPath / "help.json")
    await send.sendWithAt(
        await picmodle.help(
            {
                "helpGroup": helpGroup,
                "cmdHead": cmdhead,
                "isMaster": session.user.id in bot.config.superusers,
                "background": await getdata.getill(random.choice(getInfo.illlist)),
                "theme": pluginData.plugin_data.theme,
            }
        ),
    )


@tkhelp.handle()
async def _():
    await send.sendWithAt(
        (
            "sessionToken有关帮助：\n【推荐】：扫码登录TapTap获取token\n"
            f"指令：{cmdhead} bind qrcode\n"
            "【基础方法】https://www.kdocs.cn/l/catqcMM9UR5Y\n绑定sessionToken指令：\n"
            f"{cmdhead} bind <sessionToken>"
        ),
    )
