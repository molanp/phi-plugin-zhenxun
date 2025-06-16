from nonebot_plugin_uninfo import Uninfo

from ..models import userApiId
from ..utils import to_dict
from .cls.Save import Save
from .cls.saveHistory import saveHistory
from .getFile import readFile
from .makeRequest import makeRequest
from .makeRequestFnc import makeRequestFnc
from .path import apiSavePath


class getSaveFromApi:
    @classmethod
    async def add_user_apiId(cls, user_id: str, apiId: str):
        """添加 user_id 号对应的 apiId"""
        return await userApiId.add_user_apiId(user_id, apiId)

    @classmethod
    async def get_user_apiId(cls, user_id: str):
        """#获取 user_id 号对应的 apiId"""
        return await userApiId.get_user_apiId(user_id)

    @classmethod
    async def del_user_apiId(cls, user_id: str):
        """移除 user_id 对应的 apiId"""
        return await userApiId.del_user_apiId(user_id)

    @classmethod
    async def getSave(cls, user_id: str) -> Save | None:
        """
        获取 user_id 对应的存档文件

        :param  user_id: 用户id
        """
        apiId = await cls.get_user_apiId(user_id)
        result = (
            await readFile.FileReader(apiSavePath / apiId / "save.json")
            if apiId
            else None
        )
        if not result:
            return None
        tem = await Save().constructor(result)
        if tem.saveInfo:
            await tem.init()
        else:
            return None
        return tem

    @classmethod
    async def getSaveByApiId(cls, apiId: str) -> Save | None:
        """
        获取 apiId 对应的存档文件

        :param  apiId: apiId
        """
        result = (
            await readFile.FileReader(apiSavePath / apiId / "save.json")
            if apiId
            else None
        )
        if not result:
            return None
        tem = await Save().constructor(result)
        if tem.saveInfo:
            await tem.init()
        else:
            return None
        return tem

    @classmethod
    async def getSaveFromApi(cls, session: Uninfo) -> bool | Save:
        """
        从 API 获取存档

        :param  session: session
        """
        result = await Save().constructor(
            await makeRequest.getCloudSaves(makeRequestFnc.makePlatform(session))
        )
        await result.init()
        return result

    @classmethod
    async def putSave(cls, user_id: str, data: dict) -> bool:
        """
        保存 user_id 对应的存档文件

        :param  user_id: 用户id
        :param  dict data: 存档数据
        """
        apiId = data.get("apiId")
        if not apiId:
            raise ValueError("apiId is required")
        await cls.add_user_apiId(user_id, apiId)
        return await readFile.SetFile(apiSavePath / apiId / "save.json", data)

    @classmethod
    async def getHistory(cls, session: Uninfo, request: list) -> saveHistory:
        """
        获取 user_id 对应的历史记录

        :param session: 用户会话信息
        :param request: 请求的字段列表
        :return: saveHistory 实例
        """
        apiId = await cls.get_user_apiId(session.user.id)
        if not apiId:
            raise ValueError("apiId is undefined")

        params = makeRequestFnc.makePlatform(session)
        params["request"] = request
        result = await makeRequest.getHistory(params)
        return saveHistory(to_dict(result))

    @classmethod
    async def getSongHistory(
        cls, session: Uninfo, song_id: str | None = None, difficulty: str | None = None
    ):
        """
        获取指定曲目的历史记录

        :param session: 用户会话信息
        :param song_id: 曲目 ID
        :param difficulty: 难度等级
        :return: 历史记录数据
        """
        apiId = await cls.get_user_apiId(session.user.id)
        if not apiId:
            raise ValueError("apiId is undefined")

        params = makeRequestFnc.makePlatform(session)
        if song_id is not None:
            params["song_id"] = song_id
        if difficulty is not None:
            params["difficulty"] = difficulty

        return await makeRequest.getHistoryRecord(params)  # type: ignore

    @classmethod
    async def delSave(cls, session: Uninfo) -> bool:
        """删除 user_id 对应的存档文件"""
        apiId = await cls.get_user_apiId(session.user.id)
        if not apiId:
            return False
        fPath = apiSavePath / apiId
        await readFile.DelFile(fPath / "save.json")
        await readFile.DelDir(fPath / apiId)
        await cls.del_user_apiId(session.user.id)
        await makeRequest.unbind({**makeRequestFnc.makePlatform(session)})
        return True
