"""phigros屁股肉设置"""

from typing import Any

from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import Alconna, Args, CommandMeta, on_alconna

from ..config import recmdhead

set = on_alconna(
    Alconna(
        rf"re:{recmdhead}\s*(设置|set)",
        Args["name", str]["value", Any],
        meta=CommandMeta(compact=True),
    ),
    priority=5,
    block=True,
    permission=SUPERUSER,
)


@set.handle()
async def _():
    await set.finish("不支持")
