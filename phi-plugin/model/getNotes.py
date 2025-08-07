from typing import Any

from pydantic import BaseModel

from ..utils import to_dict
from .getFile import readFile
from .getSave import getSave
from .path import pluginDataPath, savePath


class pluginDataDetail(BaseModel):
    money: int = 0
    sign_in: str = ""
    task_time: str = ""
    task: list = []
    theme: str = "star"


class pluginData(BaseModel):
    plugin_data: pluginDataDetail = pluginDataDetail()


class getNotes:
    @staticmethod
    async def getPluginData(user_id: str) -> dict[str, Any]:
        """
        获取uid对应的娱乐数据

        :param str user_id: 用户id
        """
        session = await getSave.get_user_token(user_id)
        if session is not None:
            return {
                **to_dict(await getNotes.getNotesData(user_id)),
                **to_dict(await getSave.getHistory(user_id)),
            }
        return {}

    @staticmethod
    async def putPluginData(user_id: str, data: dict) -> bool:
        """保存 user_id 对应的娱乐数据"""
        session = await getSave.get_user_token(user_id)
        if data.get("rks") is not None:
            assert session is not None
            # 分流
            history = {
                "data": data.get("data"),
                "rks": data.get("rks"),
                "scoreHistory": data.get("scoreHistory"),
                "dan": data.get("plugin_data", {}).get("CLGMOD"),
                "version": data.get("version"),
            }
            return await readFile.SetFile(savePath / session / "history.json", history)
        return await readFile.SetFile(pluginDataPath / f"{user_id}_.json", data)

    @staticmethod
    async def getNotesData(user_id: str, islock: bool = False) -> pluginData:
        """
        获取并初始化用户数据

        :param str user_id: 用户id
        :returns:
        """
        data = await readFile.FileReader(pluginDataPath / f"{user_id}_.json")
        if not data or not data.get("plugin_data"):
            return pluginData()
        else:
            return pluginData(**data.get("plugin_data"))

    @staticmethod
    async def putNotesData(user_id: str, data: dict) -> bool:
        """保存用户数据"""
        return await readFile.SetFile(pluginDataPath / f"{user_id}_.json", data)

    @staticmethod
    async def delNotesData(user_id: str) -> bool:
        return await readFile.DelFile(pluginDataPath / f"{user_id}_.json")
