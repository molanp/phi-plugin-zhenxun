from typing import Any

from .getFile import readFile
from .getSave import getSave
from .path import pluginDataPath, savePath


class getNotes:
    @classmethod
    async def getPluginData(cls, user_id: str) -> dict[str, Any] | None:
        """
        获取uid对应的娱乐数据

        :param str user_id: 用户id
        """
        session = await getSave.get_user_token(user_id)
        if session is not None:
            return {
                **(await cls.getNotesData(user_id)),
                **(await getSave.getHistory(user_id)),
            }
        return None

    @classmethod
    async def putPluginData(cls, user_id: str, data: dict) -> bool:
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

    @classmethod
    async def getNotesData(cls, user_id: str) -> dict[str, dict[str, Any]]:
        """
        获取并初始化用户数据

        :param str user_id: 用户id
        :returns:
        ```json
        {
            plugin_data: {
                money: number,
                sign_in: string,
                task_time: string,
                task: [dict...],
                theme: string
            }
        }
        """
        data = await readFile.FileReader(pluginDataPath / f"{user_id}_.json")
        if not data or not data.get("plugin_data"):
            data = {
                "plugin_data": {
                    "money": 0,
                    "sign_in": "Wed Apr 03 2024 23:03:52 GMT+0800 (中国标准时间)",
                    "task_time": "Wed Apr 03 2024 23:03:52 GMT+0800 (中国标准时间)",
                    "task": [],
                    "theme": "common",
                }
            }
        return data

    @classmethod
    async def putNotesData(cls, user_id: str, data: dict) -> bool:
        """保存用户数据"""
        return await readFile.SetFile(pluginDataPath / f"{user_id}_.json", data)

    @classmethod
    async def delNotesData(cls, user_id) -> bool:
        return await readFile.DelFile(pluginDataPath / f"{user_id}_.json")
