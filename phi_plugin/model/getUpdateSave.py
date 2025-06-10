from nonebot import require

from ..config import PluginConfig
from ..lib.PhigrosUser import PhigrosUser
from .getNotes import getNotes
from .getSave import getSave
from .getSaveFromApi import getSaveFromApi
from .makeRequest import makeRequest
from .makeRequestFnc import makeRequestFnc
from .models.Save import Save
from .send import send

require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import SupportScope
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger


class getUpdateSave:
    @classmethod
    async def getNewSaveFromApi(cls, e: Uninfo, token: str | None = None) -> dict:
        old = await getSaveFromApi.getSave(e.user.id)
        newSaveInfo = await makeRequest.getCloudSaveInfo(
            **{"token": token, **makeRequestFnc.makePlatform(e)}
        )
        if newSaveInfo["modifiedAt"]["iso"] == getattr(
            getattr(getattr(old, "saveInfo", None), "modifiedAt", None),
            "iso",
            None,
        ):
            return {"save": old, "added_rks_notes": [0, 0]}
        newSave = await makeRequest.getCloudSaves(
            **{"token": token, **makeRequestFnc.makePlatform(e)}
        )
        await getSaveFromApi.putSave(e.user.id, newSave)
        result = Save(newSave)
        await result.init()
        await getSaveFromApi.putSave(e.user.id, result)
        if token:
            await getSave.add_user_token(e.user.id, token)
        added_rks_notes = await cls.buildingRecord(old, newSave, e)
        return {"save": result, "added_rks_notes": added_rks_notes}

    @classmethod
    async def getNewSaveFromLocal(cls, e: Uninfo, token: str | None = None) -> dict:
        old = await getSave.getSave(e.user.id)
        token = token or old.session
        User = PhigrosUser(token)
        try:
            save_info = await User.getSaveInfo()
            if old and old.saveInfo.modifiedAt.iso == save_info.modifiedAt.iso:
                return {"save": old, "added_rks_notes": [0, 0]}
            await User.buildRecord()
        except Exception as err:
            if e.scope != SupportScope.qq_api:
                await send.send_with_At(f"更新失败！QAQ\n{err}")
            else:
                await send.send_with_At("更新失败！QAQ\n请稍后重试")
            logger.error("信息更新失败", "phi-plugin", e=err)
            raise err
        try:
            await getSave.putSave(e.user.id, User)
        except Exception as err:
            await send.send_with_At(f"保存存档失败!\n{err}")
            logger.error("保存存档失败", "phi-plugin", e=err)
            raise err
        now = Save(User.model_dump())  # TODO:在py里似乎需要转字典传入,使用model_dump?

        if old and (old.session and old.session != User.session):
            await send.send_with_At(
                "检测到新的sessionToken，将自动更换绑定。"
                "如果需要删除统计记录请"
                f"⌈{PluginConfig.get('cmdhead')} unbind⌋ 进行解绑哦！"
            )
            await getSave.add_user_token(e.user.id, User.session)
            old = await getSave.getSave(e.user.id)
        # await now.init()
        history = await getSave.getHistory(e.user.id)
        await history.update(now)
        await getSave.putHistory(e.user.id, history)
        added_rks_notes = await cls.buildingRecord(old, now, e)
        return {"save": now, "added_rks_notes": added_rks_notes}

    @classmethod
    async def buildingRecord(cls, old: Save, now: Save, e: Uninfo) -> list[int] | bool:
        """
        更新存档

        :return list[int, int] | False: [ks变化值，note变化值]，失败返回 false
        """
        notesData = await getNotes.getNotesData(e.user.id)
        # 修正
        if notesData.get("update") or notesData.get("task_update"):
            notesData.pop("update", None)
            notesData.pop("task_update", None)
        # note数量变化
        add_money = 0
        task = notesData.get("plugin_data", {}).get("task")
        add_money = 0

        if task:
            for song_id, record_levels in now.gameRecord.items():
                for i, task_info in enumerate(task):
                    if not task_info:  # 跳过空任务
                        continue
                    if task_info.get("finished"):  # 已完成的任务跳过
                        continue

                    song = task_info.get("song")
                    if song != song_id:
                        continue

                    level = task_info["request"].get("rank", None)
                    if level not in ["pst", "prs", "ftr", "byd"]:  # 根据实际等级设定
                        continue

                    level_index = {"pst": 0, "prs": 1, "ftr": 2, "byd": 3}.get(level, 0)
                    current_record = (
                        record_levels[level_index]
                        if isinstance(record_levels, list)
                        and len(record_levels) > level_index
                        else None
                    )

                    if not current_record:
                        continue

                    request_type = task_info["request"].get("type")
                    request_value = task_info["request"].get("value", 0)

                    if request_type == "acc":
                        if current_record.get("acc", 0) >= request_value:
                            task_info["finished"] = True
                            reward = task_info.get("reward", 0)
                            add_money += reward
                            notesData["plugin_data"]["money"] += reward
                    elif request_type == "score":
                        if current_record.get("score", 0) >= request_value:
                            task_info["finished"] = True
                            reward = task_info.get("reward", 0)
                            add_money += reward
                            notesData["plugin_data"]["money"] += reward

        await getNotes.putNotesData(e.user.id, notesData)

        # rks变化
        add_rks = (
            now.saveInfo.summary.rankingScore - old.saveInfo.summary.rankingScore
            if old
            else 0
        )
        return [add_rks, add_money]
