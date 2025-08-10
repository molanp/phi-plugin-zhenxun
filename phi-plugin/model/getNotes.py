from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from .constNum import LevelItem
from .getFile import readFile
from .path import pluginDataPath


class taskDataDetail(BaseModel):
    rank: LevelItem
    type: Literal["score", "acc"]
    value: float = 0.0


class taskData(BaseModel):
    song: str
    reward: int = 0
    finished: bool = False
    illustration: str | Path = ""
    request: taskDataDetail


class NotesDataDetail(BaseModel):
    money: int = 0
    sign_in: datetime = datetime.fromtimestamp(0)
    task_time: datetime = datetime.fromtimestamp(0)
    task: list[taskData] = []
    theme: str = "star"


class NotesData(BaseModel):
    plugin_data: NotesDataDetail = NotesDataDetail()


class getNotes:

    @staticmethod
    async def getNotesData(user_id: str, islock: bool = False) -> NotesData:
        """
        获取并初始化用户数据

        :param str user_id: 用户id
        :returns:
        """
        data = await readFile.FileReader(pluginDataPath / f"{user_id}_.json")
        if not data or not data.get("plugin_data"):
            return NotesData()
        else:
            return NotesData(**data.get("plugin_data"))

    @staticmethod
    async def putNotesData(user_id: str, data: dict[str, Any]) -> bool:
        """保存用户数据"""
        return await readFile.SetFile(pluginDataPath / f"{user_id}_.json", data)

    @staticmethod
    async def delNotesData(user_id: str) -> bool:
        return await readFile.DelFile(pluginDataPath / f"{user_id}_.json")
