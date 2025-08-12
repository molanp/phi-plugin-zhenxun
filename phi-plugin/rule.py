from typing import Literal

from nonebot.internal.rule import Rule
from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_uninfo import Uninfo

from .model.getBanGroup import getBanGroup


def can_be_call(
    key: Literal[
        "bind",
        "unbind",
        "b19",
        "p30",
        "lmtAcc",
        "arcgrosB19",
        "update",
        "info",
        "list",
        "singlescore",
        "lvscore",
        "data",
        "chap",
        "suggest",
        "help",
        "tkhelp",
        "song",
        "ill",
        "chart",
        "addtag",
        "search",
        "alias",
        "randmic",
        "randClg",
        "table",
        "comment",
        "recallComment",
        "myComment",
        "rankList",
        "godList",
        "comrks",
        "tips",
        "newSong",
        "tipgame",
        "guessgame",
        "ltrgame",
        "sign",
        "send",
        "tasks",
        "retask",
        "jrrp",
        "theme",
        "dan",
        "danupdate",
    ],
) -> Rule:
    """
    功能是否能被调用

    参数:
        key: 功能名称

    返回:
        Rule: Rule
    """

    async def _rule(bot, session: Uninfo) -> bool:
        if session.user.id in bot.config.superusers:
            return True

        if await getBanGroup.get(session, key):
            await UniMessage("这里被管理员禁止使用这个功能了呐QAQ！").send(
                reply_to=True
            )
            return False
        return True

    return Rule(_rule)
