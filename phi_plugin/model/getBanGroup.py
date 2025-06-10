from ..models import banGroup


class getBanGroup:
    @classmethod
    async def getStatus(cls, group_id: str, func: str) -> bool:
        return await banGroup.getStatus(group_id, func)

    @classmethod
    async def get(cls, group: str | None, func: str) -> bool:
        if not group:
            return False

        match func:
            case "help" | "tkhelp":
                return await cls.getStatus(group, "help")
            case "bind" | "unbind":
                return await cls.getStatus(group, "bind")
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
                return await cls.getStatus(group, "b19")
            case "bestn" | "data":
                return await cls.getStatus(group, "wb19")
            case (
                "song"
                | "ill"
                | "chart"
                | "addtag"
                | "retag"
                | "search"
                | "alias"
                | "randmic"
                | "randClg"
                | "table"
                | "comment"
                | "recallComment"
            ):
                return await cls.getStatus(group, "song")
            case "rankList" | "godList":
                return await cls.getStatus(group, "ranklist")
            case "comrks" | "tips" | "newSong":
                return await cls.getStatus(group, "fnc")
            case "tipgame":
                return await cls.getStatus(group, "tipgame")
            case "guessgame":
                return await cls.getStatus(group, "guessgame")
            case "ltrgame":
                return await cls.getStatus(group, "ltrgame")
            case "sign" | "send" | "tasks" | "retask" | "jrrp":
                return await cls.getStatus(group, "sign")
            case "theme":
                return await cls.getStatus(group, "setting")
            case "dan" | "danupdate":
                return await cls.getStatus(group, "dan")
            case _:
                return False
