import shutil

from ..models import SstkData
from .cls.Save import Save
from .cls.saveHistory import saveHistory
from .getFile import readFile
from .getRksRank import getRksRank
from .path import savePath


class getSave:
    @classmethod
    async def add_user_token(cls, user_id: str, sstk: str):
        """添加 user_id 号对应的 Token"""
        return await SstkData.add_sstk(user_id, sstk)

    @classmethod
    async def get_user_token(cls, user_id: str):
        """获取 user_id 号对应的 Token"""
        return await SstkData.get_sstk(user_id)

    @classmethod
    async def del_user_token(cls, user_id: str):
        """移除 user_id 对应的 Token"""
        return await SstkData.delete_sstk(user_id)

    @classmethod
    async def getSave(cls, user_id: str) -> Save | None:
        """
        获取 user_id 对应的存档文件

        :param str user_id: user_id
        :return: Save
        """
        sstk = await SstkData.get_sstk(user_id)
        if sstk is None:
            return None
        if await cls.isBanSessionToken(sstk):
            raise ValueError(f"{sstk} 已被禁用")

        result = await readFile.FileReader(savePath / sstk / "save.json")
        if not result:
            return None
        tem = await Save().constructor(result)
        if tem.saveInfo:
            await tem.init()
        else:
            return None
        return tem

    @classmethod
    async def getSaveBySessionToken(cls, sstk: str | None) -> Save | None:
        """
        获取 sessionToken 对应的存档文件

        :param str | None sstk: sessionToken
        :return: Save
        """
        if sstk is None:
            return
        if await cls.isBanSessionToken(sstk):
            raise ValueError(f"{sstk} 已被禁用")

        result = await readFile.FileReader(savePath / sstk / "save.json")
        if not result:
            return None
        tem = await Save().constructor(result)
        if tem.saveInfo:
            await tem.init()
        else:
            return None
        return tem

    @classmethod
    async def putSave(cls, user_id: str, data: dict):
        """
        保存 user_id 对应的存档文件

        :param str user_id: user_id
        :param dict data: data
        """
        sstk = data.get("sessionToken")
        if await cls.isBanSessionToken(sstk):
            raise ValueError(f"{sstk} 已被禁用")
        assert sstk is not None
        await cls.add_user_token(user_id, sstk)
        return await readFile.SetFile(savePath / sstk / "save.json", data)

    @classmethod
    async def getHistory(cls, user_id: str) -> "saveHistory":
        """
        获取 user_id 对应的历史记录

        :param str user_id: user_id
        :return: saveHistory
        """
        sstk = await SstkData.get_sstk(user_id)
        if sstk is None:
            return None
        if await cls.isBanSessionToken(sstk):
            raise ValueError(f"{sstk} 已被禁用")
        result = await readFile.FileReader(savePath / sstk / "history.json")
        return saveHistory(result)

    @classmethod
    async def getHistoryBySessionToken(cls, sstk: str) -> "saveHistory":
        if await cls.isBanSessionToken(sstk):
            raise ValueError(f"{sstk} 已被禁用")
        result = await readFile.FileReader(savePath / sstk / "history.json")
        return saveHistory(result)

    @classmethod
    async def putHistory(cls, user_id: str, data: dict):
        """
        保存 user_id 对应的历史记录

        :param str user_id: user_id
        :param dict data: saveHistory
        """
        sstk = await SstkData.get_sstk(user_id)
        if sstk is None:
            return None
        return await readFile.SetFile(savePath / (sstk) / "history.json", data)

    @classmethod
    async def getDan(cls, user_id: str, all=False):
        """
        获取玩家 Dan 数据

        :param str user_id: QQ号
        :param bool all: 是否返回所有数据
        :return: Dan数据
        """
        history = await cls.getHistory(user_id)

        dan = history.get("dan")

        if dan and not isinstance(dan, list):
            dan = [dan]
        if all is True:
            return dan
        return dan[0] if dan else None

    @classmethod
    async def delSave(cls, user_id: str):
        """
        删除 user_id 对应的存档文件

        :param str user_id: user_id
        """
        sstk = await SstkData.get_sstk(user_id)
        if sstk is None:
            return False
        fPath = savePath / sstk
        await readFile.DelFile(fPath / "save.json")
        await readFile.DelFile(fPath / "history.json")
        await getRksRank.delUserRks(sstk)
        shutil.rmtree(fPath, ignore_errors=True)
        await cls.del_user_token(user_id)
        return True

    @classmethod
    async def delSaveBySessionToken(cls, sstk: str):
        """
        删除 sessionToken 对应的存档文件

        :param str sstk: sessionToken
        """
        if sstk is None:
            return False
        fPath = savePath / sstk
        await readFile.DelFile(fPath / "save.json")
        await readFile.DelFile(fPath / "history.json")
        await getRksRank.delUserRks(sstk)
        shutil.rmtree(fPath, ignore_errors=True)
        return True

    @classmethod
    async def banSessionToken(cls, token: str):
        """
        禁用 sessionToken
        :param str token: sessionToken
        """
        return await SstkData.ban_sstk(token)

    @classmethod
    async def allowSessionToken(cls, token: str):
        """
        解禁 sessionToken
        :param str token: sessionToken
        """
        return await SstkData.unban_sstk(token)

    @classmethod
    async def isBanSessionToken(cls, token: str | None):
        """
        检查 sessionToken 是否被禁用
        :param str|None token: sessionToken
        """
        return False if token is None else await SstkData.is_ban_sessionToken(token)

    @classmethod
    async def getGod(cls):
        """
        获取所有被禁用的 sessionToken
        """
        return await SstkData.get_ban_sstk()
