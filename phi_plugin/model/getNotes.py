from typing import Any, Literal, TypedDict

from ..utils import to_dict
from .getFile import readFile
from .getSave import getSave
from .path import pluginDataPath, savePath


class pluginData(TypedDict):
    money: int
    sign_in: str
    task_time: str
    task: list
    theme: str


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
                **(await getNotes.getNotesData(user_id)),
                **(to_dict(await getSave.getHistory(user_id))),
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
    async def getNotesData(
        user_id: str, islock: bool = False
    ) -> dict[Literal["plugin_data"], pluginData]:
        """
        获取并初始化用户数据

        :param str user_id: 用户id
        :returns:
        """
        data = await readFile.FileReader(pluginDataPath / f"{user_id}_.json")
        if not data or not data.get("plugin_data"):
            data: dict[Literal["plugin_data"], pluginData] = {
                "plugin_data": {
                    "money": 0,
                    "sign_in": "Wed Apr 03 2024 23:03:52 GMT+0800 (中国标准时间)",
                    "task_time": "Wed Apr 03 2024 23:03:52 GMT+0800 (中国标准时间)",
                    "task": [],
                    "theme": "common",
                }
            }
        return data

    @staticmethod
    async def putNotesData(user_id: str, data: dict) -> bool:
        """保存用户数据"""
        return await readFile.SetFile(pluginDataPath / f"{user_id}_.json", data)

    @staticmethod
    async def delNotesData(user_id) -> bool:
        return await readFile.DelFile(pluginDataPath / f"{user_id}_.json")
