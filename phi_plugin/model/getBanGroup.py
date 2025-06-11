from ..models import banGroup


class getBanGroup:
    @staticmethod
    async def getStatus(group_id: str, func: str) -> bool:
        return await banGroup.getStatus(group_id, func)

    @staticmethod
    async def get(group: str | None, func: str) -> bool:
        if not group:
            return False

        match func:
            case "help" | "tkhelp":
                return await getBanGroup.getStatus(group, "help")
            case "bind" | "unbind":
                return await getBanGroup.getStatus(group, "bind")
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
                return await getBanGroup.getStatus(group, "b19")
            case "bestn" | "data":
                return await getBanGroup.getStatus(group, "wb19")
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
                return await getBanGroup.getStatus(group, "song")
            case "rankList" | "godList":
                return await getBanGroup.getStatus(group, "ranklist")
            case "comrks" | "tips" | "newSong":
                return await getBanGroup.getStatus(group, "fnc")
            case "tipgame":
                return await getBanGroup.getStatus(group, "tipgame")
            case "guessgame":
                return await getBanGroup.getStatus(group, "guessgame")
            case "ltrgame":
                return await getBanGroup.getStatus(group, "ltrgame")
            case "sign" | "send" | "tasks" | "retask" | "jrrp":
                return await getBanGroup.getStatus(group, "sign")
            case "theme":
                return await getBanGroup.getStatus(group, "setting")
            case "dan" | "danupdate":
                return await getBanGroup.getStatus(group, "dan")
            case _:
                return False
