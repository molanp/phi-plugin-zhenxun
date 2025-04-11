import os
import json
import math
import asyncio
from typing import Dict, Any, Optional, Union
from datetime import datetime

from zhenxun.services.log import logger  # 假设日志模块已存在
from .path import dataPath, pluginDataPath, _path, redisPath
from .class_saveHistory import saveHistory
from .class.SongsInfo import SongsInfo
from .class.Save import Save
from .class.PhigrosUser import PhigrosUser
from .getSave import getSave as getSaveModule
from .getNotes import getPluginData as getNotesPluginData
from .getPic import getimg as getPic_getimg
from .picmodle import b19, update, tasks, user_info, lvsco, score, ill, guess, rand
from .constNum import Level
from .getInfo import (
    getInfo,
    Level as LevelMapping,
    avatarid as avatar_id,
    tips as tips_data,
    ori_info,
    songsid,
    idssong,
    illlist,
    songlist,
    fuzzysongsnick,
    info as info_func,
    all_info as all_info_func,
    setnick as setnick_func,
    idgetsong as id_getsong,
    SongGetId as song_get_id,
    getill as get_ill,
    idgetavatar as id_get_avatar,
)

class GetData:
    def __init__(self):
        self.Level = LevelMapping  # 难度映射
        self.avatarid = avatar_id
        self.tips = tips_data
        self.ori_info = ori_info
        self.songsid = songsid
        self.idssong = idssong
        self.illlist = illlist
        self.songlist = songlist


    async def fuzzysongsnick(self, mic: str, distance: float = 0.85) -> list:
        return fuzzysongsnick(mic, distance)

    async def info(self, song: Optional[str] = None, original: bool = False) -> Union[SongsInfo, Dict[str, SongsInfo]]:
        return info_func(song, original) if song else all_info_func(original)


    async def getsave(self, user_id: str) -> Optional[Save]:
        return await getSaveModule.getSave(user_id)

    async def putsave(self, user_id: str, data: Any) -> bool:
        return await getSaveModule.putSave(user_id, data)

    async def delsave(self, user_id: str) -> bool:
        return await getSaveModule.delSave(user_id)

    async def delpluginData(self, user_id: str) -> bool:
        return await self.delData(f"{user_id}_.json", pluginDataPath)

    async def getpluginData(self, user_id: str) -> Any:
        return await getNotesPluginData(user_id)

    async def putpluginData(self, user_id: str, data: Any) -> bool:
        return await getNotesPluginData.putPluginData(user_id, data)

    async def getNotesData(
        self,
        user_id: str,
        islock: bool = False
    ) -> Any:
        return await getNotesPluginData.getNotesData(user_id, islock)

    def getimg(self, img: str, style: str = "png") -> str:
        return getPic_getimg(img, style)

    async def getDan(self, user_id: str) -> Any:
        return await getSaveModule.getDan(user_id)

    async def songsnick(self, mic: str) -> str:
        return getInfo.songsnick(mic)

    async def setnick(self, mic: str, nick: str) -> bool:
        return await setnick_func(mic, nick)

    async def GetSongsInfoAtlas(
        self,
        e: Any,
        name: str,
        data: Optional[Dict] = None
    ) -> Any:
        return await pic.GetSongsInfoAtlas(e, name, data)

    async def GetSongsIllAtlas(
        self,
        e: Any,
        name: str,
        data: Optional[Dict] = None
    ) -> Any:
        return await pic.GetSongsIllAtlas(e, name, data)

    async def buildingRecord(
        self,
        e: Any,
        user: PhigrosUser
    ) -> Union[list[int], bool]:
        user_id = e.user_id
        old = await self.getsave(user_id)
        if old and old.session:
            if old.session == user.session:
                pass
            else:
                await getSaveModule.add_user_token(user_id, user.session)
                old = await self.getsave(user_id)
        try:
            save_info = await user.getSaveInfo()
            if old and old.saveInfo.modifiedAt.iso == save_info.modifiedAt.iso:
                return [0, 0]
            err = await user.buildRecord()
            if err:
                e.send(f"以下曲目无信息，可能导致b19显示错误\n{chr(10).join(err)}", reply_to=True)
        except Exception as ex:
            error_msg = f"更新失败！QAQ\n{ex}"
            e.send(error_msg, reply_to=True)
            logger.error(str(ex))
            return False
        try:
            await self.putsave(user_id, user)
        except Exception as ex:
            e.send(f"保存存档失败！{ex}", reply_to=True)
            logger.error(str(ex))
            return False
        now = Save(user)
        history = await getSaveModule.getHistory(user_id)
        history.update(now)
        await getSaveModule.putHistory(user_id, history)
        plugin_data = await self.getNotesData(user_id)
        if hasattr(plugin_data, "update") or hasattr(plugin_data, "task_update"):
            del plugin_data.update
            del plugin_data.task_update
        add_money = 0
        if plugin_data?.plugin_data?.task:
            for song_id in now.gameRecord:
                song_name = self.id_getsong(song_id)
                for task in plugin_data.plugin_data.task.values():
                    if not task.finished and task.song == song_name:
                        level = Level.index(task.request.rank)
                        record = now.gameRecord[song_id].get(level, {})
                        if task.request.type == "acc":
                            if record.get("acc", 0) >= task.request.value:
                                task.finished = True
                                plugin_data.plugin_data.money += task.reward
                                add_money += task.reward
                        elif task.request.type == "score":
                            if record.get("score", 0) >= task.request.value:
                                task.finished = True
                                plugin_data.plugin_data.money += task.reward
                                add_money += task.reward
            await self.putpluginData(user_id, plugin_data)
        add_rks = now.saveInfo.summary.rankingScore - (old.saveInfo.summary.rankingScore if old else 0)
        return [add_rks, add_money]

    async def getb19(self, e: Any, data: Any) -> Any:
        return await b19(e, data)

    async def getupdate(self, e: Any, data: Any) -> Any:
        return await update(e, data)

    async def gettasks(self, e: Any, data: Any) -> Any:
        return await tasks(e, data)

    async def getuser_info(
        self,
        e: Any,
        data: Any,
        kind: str
    ) -> Any:
        return await user_info(e, data, kind)

    async def getlvsco(self, e: Any, data: Any) -> Any:
        return await lvsco(e, data)

    async def getsingle(self, e: Any, data: Any) -> Any:
        return await score(e, data)

    async def getillpicmodle(self, e: Any, data: Any) -> Any:
        return await ill(e, data)

    async def getguess(self, e: Any, data: Any) -> Any:
        return await guess(e, data)

    async def getrand(self, e: Any, data: Any) -> Any:
        return await rand(e, data)

    def getill(
        self,
        name: str,
        kind: str = "common"
    ) -> str:
        return get_ill(name, kind)

    def idgetavatar(self, avatar_id: str) -> str:
        return id_get_avatar(avatar_id)

    def idgetsong(self, song_id: str) -> str:
        return id_getsong(song_id)

    def SongGetId(self, song_name: str) -> str:
        return song_get_id(song_name)

    def getrks(self, acc: float, difficulty: float) -> float:
        if acc == 100:
            return difficulty
        elif acc < 70:
            return 0.0
        else:
            return difficulty * (( (acc - 55) / 45 ) ** 2)

    def comsuggest(
        self,
        rks: float,
        difficulty: float,
        count: Optional[int] = None
    ) -> Union[str, float]:
        ans = 45 * math.sqrt(rks / difficulty) + 55
        if ans >= 100:
            return "无法推分"
        else:
            return f"{ans:.{count}f}%" if count is not None else ans

# 初始化实例
get = GetData()