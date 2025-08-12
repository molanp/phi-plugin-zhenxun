from typing import Literal

from nonebot_plugin_uninfo import Uninfo

from .getSave import getSave
from .send import send


class getBanGroup:
    @staticmethod
    async def redis(
        group_id: str,
        func: Literal[
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
        ],
    ) -> bool:
        from ..models import banGroup

        return await banGroup.getStatus(group_id, func)

    @staticmethod
    async def get(
        session: Uninfo,
        func: Literal[
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
    ) -> bool:
        group_id = session.scene.id
        if not group_id:
            return False
        sessionToken = await getSave.get_user_token(session.user.id)
        if sessionToken and await getSave.isBanSessionToken(sessionToken):
            await send.sendWithAt("当前账户被加入黑名单，详情请联系管理员(2)。")
            return True
        match func:
            case "help" | "tkhelp":
                return await getBanGroup.redis(group_id, "help")
            case "bind" | "unbind":
                return await getBanGroup.redis(group_id, "bind")
            case (
                "b19"
                | "p30"
                | "lmtAcc"
                | "arcgrosB19"
                | "update"
                | "info"
                | "list"
                | "singlescore"
                | "lvscore"
                | "chap"
                | "suggest"
            ):
                return await getBanGroup.redis(group_id, "b19")
            case "data":
                return await getBanGroup.redis(group_id, "wb19")
            case (
                "song"
                | "ill"
                | "chart"
                | "addtag"
                | "search"
                | "alias"
                | "randmic"
                | "randClg"
                | "table"
                | "comment"
                | "recallComment"
                | "myComment"
            ):
                return await getBanGroup.redis(group_id, "song")
            case "rankList" | "godList":
                return await getBanGroup.redis(group_id, "ranklist")
            case "comrks" | "tips" | "newSong":
                return await getBanGroup.redis(group_id, "fnc")
            case "tipgame":
                return await getBanGroup.redis(group_id, "tipgame")
            case "guessgame":
                return await getBanGroup.redis(group_id, "guessgame")
            case "ltrgame":
                return await getBanGroup.redis(group_id, "ltrgame")
            case "sign" | "send" | "tasks" | "retask" | "jrrp":
                return await getBanGroup.redis(group_id, "sign")
            case "theme":
                return await getBanGroup.redis(group_id, "setting")
            case "dan" | "danupdate":
                return await getBanGroup.redis(group_id, "dan")
