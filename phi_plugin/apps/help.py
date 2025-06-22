import random
import re

from nonebot_plugin_alconna import Alconna, on_alconna
from nonebot_plugin_uninfo import Uninfo

from ..config import PluginConfig
from ..model.fCompute import fCompute
from ..model.getBanGroup import getBanGroup
from ..model.getdata import getdata
from ..model.getFile import readFile
from ..model.getInfo import getInfo
from ..model.path import infoPath
from ..model.picmodle import picmodle
from ..model.send import send

cmdhead = re.escape(PluginConfig.get("cmdhead", "/phi"))

help = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*(命令|帮助|菜单|help|说明|功能|指令|使用说明)",
    ),
    priority=5,
    block=True,
)
tkhelp = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*tok(?:en)?(命令|帮助|菜单|help|说明|功能|指令|使用说明)",
    ),
    priority=5,
    block=True,
)
apihelp = on_alconna(
    Alconna(
        rf"re:{cmdhead}\s*api(命令|帮助|菜单|help|说明|功能|指令|使用说明)",
    ),
    priority=5,
    block=True,
)


@help.handle()
async def _(session: Uninfo):
    if await getBanGroup.get(help, session, "help"):
        await send.sendWithAt(help, "这里被管理员禁止使用这个功能了呐QAQ！")
        return

    pluginData = await getdata.getpluginData(session.user.id)
    helpGroup = await readFile.FileReader(infoPath / "help.json")
    await send.sendWithAt(
        help,
        await picmodle.help(
            {
                "helpGroup": helpGroup,
                "cmdHead": cmdhead,
                "isMaster": await fCompute.is_superuser(session),
                "background": await getdata.getill(random.choice(getInfo.illlist)),
                "theme": pluginData.get("plugin_data", {}).get("theme") or "star",
            }
        ),
    )


@tkhelp.handle()
async def _(session: Uninfo):
    if await getBanGroup.get(tkhelp, session, "tkhelp"):
        await send.sendWithAt(tkhelp, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    await send.sendWithAt(
        tkhelp,
        (
            "sessionToken有关帮助：\n【推荐】：扫码登录TapTap获取token\n"
            f"指令：{cmdhead} bind qrcode\n"
            "【基础方法】https://www.kdocs.cn/l/catqcMM9UR5Y\n绑定sessionToken指令：\n"
            f"{cmdhead} bind <sessionToken>"
        ),
    )


@apihelp.handle()
async def _(session: Uninfo):
    if await getBanGroup.get(tkhelp, session, "apihelp"):
        await send.sendWithAt(tkhelp, "这里被管理员禁止使用这个功能了呐QAQ！")
        return
    if not PluginConfig.get("openPhiPluginApi"):
        await send.sendWithAt(apihelp, "这里没有连接查分平台哦！")
        return
    pluginData = await getdata.getpluginData(session.user.id)
    apiHelp = await readFile.FileReader(infoPath / "help" / "api.json")
    await send.sendWithAt(
        help,
        await picmodle.help(
            {
                "helpGroup": apiHelp,
                "cmdHead": cmdhead,
                "isMaster": await fCompute.is_superuser(session),
                "background": await getdata.getill(random.choice(getInfo.illlist)),
                "theme": pluginData.get("plugin_data", {}).get("theme") or "star",
            }
        ),
    )
