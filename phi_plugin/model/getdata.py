import math
from pathlib import Path
from typing import Any, Literal

from nonebot.adapters import Event

from zhenxun.services.log import logger
from zhenxun.utils.platform import PlatformUtils

from ..config import PluginConfig
from ..utils import Date, Event2session, to_dict
from .cls.LevelRecordInfo import LevelData
from .cls.Save import Save
from .cls.SongsInfo import SongsInfoObject
from .constNum import Level
from .getFile import _SUPPORTED_FORMATS, readFile
from .getInfo import getInfo
from .getNotes import getNotes
from .getPic import SongsIllAtlasData, pic
from .getSave import getSave
from .path import pluginDataPath
from .picmodle import picmodle
from .send import send


class _getdata:
    def __init__(self):
        self.Level = getInfo.Level
        """难度映射"""
        self.avatarid = getInfo.avatarid
        """头像id"""
        self.tips = getInfo.Tips
        """Tips"""
        self.ori_info = getInfo.ori_info
        """原版信息"""
        self.songsid = getInfo.songsid
        """通过id获取曲名"""
        self.idssong = getInfo.idssong
        """原曲名称获取id"""
        self.illlist = getInfo.illlist
        """含有曲绘的曲目列表，原曲名称"""
        self.songlist = getInfo.songlist
        """所有曲目曲名列表"""

    def fuzzysongsnick(self, mic: str, Distance: float = 0.85):
        """
        根据参数模糊匹配返回原曲名称

        :param mic: 别名
        :param Distance: 匹配阈值，猜词0.95
        :return: 原曲名称
        """
        return getInfo.fuzzysongsnick(mic, Distance)

    async def info(
        self, song: str | None = None, original: bool = False
    ) -> SongsInfoObject | dict[str, SongsInfoObject] | None:
        """
        :param song: 原曲曲名
        :param original: 是否仅使用原版曲库
        """
        if song:
            return await getInfo.info(song, original)
        return await getInfo.all_info(original)

    async def getData(
        self,
        fileName: str,
        fatherPath: str | Path,
        style: _SUPPORTED_FORMATS | None = None,
    ):
        """
        获取 chos 文件

        :param fileName: 文件名称 含后缀
        :param fatherPath: 路径
        :param style: 指定格式
        """
        return await readFile.FileReader(Path(fatherPath) / fileName, style)

    async def setData(
        self,
        fileName: str,
        data: Any,
        fatherPath: str | Path,
        style: _SUPPORTED_FORMATS | None = None,
    ):
        """
        修改 chos 文件为 data

        :param fileName: 文件名称 含后缀
        :param data: 覆写内容
        :param fatherPath: 父路径
        :param style: 文件类型
        """
        return await readFile.SetFile(Path(fatherPath) / fileName, data, style)

    async def delData(self, fileName: str, fatherPath: str | Path):
        """
        删除 chos.yaml 文件

        :param fileName: 文件名称 含后缀
        :param fatherPath: 路径
        """
        return await readFile.DelFile(Path(fatherPath) / fileName)

    async def getsave(self, id: str):
        """
        获取user_id对应的存档文件

        :param id: user_id
        """
        return await getSave.getSave(id)

    async def putsave(self, id: str, data: dict):
        """
        保存user_id对应的存档文件

        :param id: user_id
        """
        return await getSave.putSave(id, data)

    async def delsave(self, id: str):
        """
        删除user_id对应的存档文件

        :param id: user_id
        """
        return await getSave.delSave(id)

    async def delpluginData(self, id: str):
        """
        删除user_id对应的娱乐数据

        :param id: user_id
        """
        return self.delData(f"{id}.json", pluginDataPath)

    async def getpluginData(self, id: str):
        """
        获取user_id对应的娱乐数据

        :param id: user_id
        """
        return await getNotes.getPluginData(id)

    async def putpluginData(self, id: str, data: dict):
        """
        保存user_id对应的娱乐数据

        :param id: user_id
        :param data: 娱乐数据
        """
        return await getNotes.putPluginData(id, data)

    async def getNotesData(self, id: str, islock: bool = False):
        """
        获取并初始化 id 插件相关数据

        :param id: user_id
        :param islock:  是否锁定
        :return: 整个data对象
        """
        return await getNotes.getNotesData(id, islock)

    def getimg(self, img: str, style: str = "png"):
        """
        获取本地图片

        :param img: 文件名
        :param style: 文件格式，默认为png
        """
        return pic.getimg(img, style)

    async def getDan(self, id: str):
        """
        获取玩家 Dan 数据

        :param id: user_id
        """
        return await getSave.getDan(id)

    def songsnick(self, mic: str):
        """
        匹配歌曲名称，根据参数返回原曲名称

        :param mic: 别名
        :return: 原曲名称
        """
        return getInfo.songsnick(mic)

    async def setnick(self, mic: str, nick: str):
        """
        设置别名

        :param mic: 原名
        :param nick: 别名
        """
        return await getInfo.setnick(mic, nick)

    async def GetSongsInfoAtlas(self, name: str, data: Any):
        """
        获取歌曲图鉴，曲名为原名

        :param name: 曲名
        :param data: 自定义数据
        """
        return await pic.GetSongsInfoAtlas(name, data)

    async def GetSongsIllAtlas(self, name: str, data: SongsIllAtlasData | None = None):
        """
        通过曲目获取曲目图鉴

        :param name: 原曲名称
        :param data: 自定义数据
        """
        return await pic.GetSongsIllAtlas(name, data)

    async def buildingRecord(
        self, e: Event, User: PhigrosUser
    ) -> tuple[float, int] | Literal[False]:
        """
        更新存档

        :param User: User
        :return: [rks变化值，note变化值]，失败返回 false
        """
        session = await Event2session(e)
        old = await self.getsave(session.user.id)
        try:
            save_info = await User.getSaveInfo()
            if old and Date(old.saveInfo["modifiedAt"]["iso"]) == Date(
                save_info["modifiedAt"]["iso"]
            ):
                return (0, 0)
            err = await User.buildRecord()
            if err:
                await send.send_with_At(
                    e, "以下曲目无信息，可能导致b19显示错误\n" + err.join("\n")
                )
        except Exception as err:
            if not PlatformUtils.is_qbot(session):
                await send.send_with_At(e, f"更新失败！QAQ\n{err}")
            else:
                await send.send_with_At(e, "更新失败！QAQ\n请稍后重试")
            logger.error("更新失败！QAQ", "phi-plugin", e=err)
            return False
        try:
            await self.putsave(session.user.id, to_dict(User))
        except Exception as err:
            await send.send_with_At(e, f"保存存档失败!\n{err}")
            logger.error("保存存档失败", "phi-plugin", e=err)
            return False
        now = await Save().constructor(to_dict(User))
        if old and (old.session and old.session != User.session):
            await send.send_with_At(
                e,
                "检测到新的sessionToken，将自动更换绑定。如果需要删除统计"
                f"记录请 ⌈{PluginConfig.get('cmdhead')}"
                "unbind⌋ 进行解绑哦！",
            )
        # await now.init()
        # 更新
        history = await getSave.getHistory(session.user.id)
        history.update(now)
        await getSave.putHistory(session.user.id, to_dict(history))
        pluginData = await getNotes.getNotesData(session.user.id)
        # 修正
        # 移植不需要考虑
        # if pluginData.get("update") or pluginData.get("task_update"):
        #     pluginData.pop("update", None)
        #     pluginData.pop("task_update", None)
        # note数量变化
        add_money = 0
        task = pluginData.get("plugin_data", {}).get("task")
        if task:
            for id in now.gameRecord:
                for i, _ in enumerate(task):
                    if not task[i]:
                        continue
                    if (
                        not task[i]["finished"]
                        and getInfo.songsid.get(id) == task[i]["song"]
                    ):
                        level = Level[task[i]["request"]["rank"]]
                        if not now.gameRecord[id][level]:
                            continue
                        match task[i]["request"]["type"]:
                            case "acc":
                                if (
                                    now.gameRecord[id][level].acc
                                    >= task[i]["request"]["value"]
                                ):
                                    pluginData["plugin_data"]["task"][i]["finished"] = (
                                        True
                                    )
                                    pluginData["plugin_data"]["money"] += task[i][
                                        "reward"
                                    ]
                                    add_money += task[i]["reward"]
                            case "score":
                                if (
                                    now.gameRecord[id][level].score
                                    >= task[i]["request"]["value"]
                                ):
                                    pluginData["plugin_data"]["task"][i]["finished"] = (
                                        True
                                    )
                                    pluginData["plugin_data"]["money"] += task[i][
                                        "reward"
                                    ]
                                    add_money += task[i]["reward"]
        await self.putpluginData(session.user.id, pluginData)
        # rks变化
        add_rks = (
            now.saveInfo["summary"]["rankingScore"]
            - old.saveInfo["summary"]["rankingScore"]
            if old
            else 0
        )
        return (add_rks, add_money)

    async def getb19(self, data: dict):
        """获取best19图片"""
        return await picmodle.b19(data)

    async def getupdate(self, data: dict):
        """获取update图片"""
        return await picmodle.update(data)

    async def gettasks(self, data: dict):
        """获取任务列表图片"""
        return await picmodle.tasks(data)

    async def getuser_info(self, data: dict, kind: int):
        """获取个人信息图片"""
        return await picmodle.user_info(data, kind)

    async def getlvsco(self, data: dict):
        """获取定级区间成绩"""
        return await picmodle.lvsco(data)

    async def getsingle(self, data: dict):
        """获取单曲成绩"""
        return await picmodle.score(data)

    async def getillpicmodle(self, data: dict):
        """获取曲绘图鉴"""
        return await picmodle.ill(data)

    async def getguess(self, data: dict):
        """获取猜曲绘图片"""
        return await picmodle.guess(data)

    async def getrand(self, data: dict):
        """获取随机曲目图片"""
        return await picmodle.rand(data)

    async def getill(
        self, name: str, kind: Literal["common", "blur", "low"] = "common"
    ):
        """
        获取曲绘，返回地址

        :param  name: 原名
        :param kind: 清晰度
        :return: 网址或文件地址
        """
        return await getInfo.getill(name, kind)

    def idgetavatar(self, id: str):
        """
        通过id获得头像文件名称

        :param id: id
        :return: file name
        """
        return getInfo.idgetavatar(id)

    def idgetsong(self, id: str) -> str | None:
        """
        根据曲目id获取原名

        :param str id: 曲目id
        :return: 原名
        """
        return getInfo.idgetsong(id)

    def SongGetId(self, song: str) -> str | None:
        """
        通过原曲曲目获取曲目id

        :param str song: 原曲曲名
        :return: 曲目id
        """
        return getInfo.SongGetId(song)

    def getrks(self, acc: float, difficulty: int):
        """
        计算等效rks

        :param acc: 准确度
        :param difficulty: 原曲定数
        :return: 等效rks
        """
        if acc == 100:
            # 满分原曲定数即为有效rks
            return difficulty
        elif acc < 70:
            # 无效acc
            return 0
        else:
            # 非满分计算公式 [(((acc - 55) / 45) ^ 2) * 原曲定数]
            return difficulty * (((acc - 55) / 45) ** 2)

    def comsuggest(self, rks: float, difficulty: int, count: int | None = None):
        """
        计算所需acc

        :param rks: 目标rks
        :param difficulty: 原曲定数
        :param count: 保留位数
        :return: 建议acc
        """
        ans = 45 * math.sqrt(rks / difficulty) + 55
        if ans >= 100:
            return "无法推分"
        else:
            return f"{round(ans, count)}%" if count is not None else str(ans)


def add_new_score(
    pluginData: dict,
    level: Literal["EZ", "HD", "IN", "AT", "LEGACY"],
    nowRecord: LevelData,
) -> int:
    """
    处理新成绩

    :param pluginData: pluginData
    :param level: level
    :param nowRecord: 当前成绩
    """
    task = pluginData.get("plugin_data", {}).get("task")
    add_money = 0
    if task:
        for i, _ in enumerate(task):
            if not task[i]:
                continue
            if (
                not task[i]["finished"]
                and task[i].get("song") is None
                and task[i]["request"]["rank"] == level
            ):
                match task[i]["request"]["type"]:
                    case "acc":
                        if nowRecord["acc"] >= task[i]["request"]["value"]:
                            pluginData["plugin_data"]["task"][i]["finished"] = True
                            pluginData["plugin_data"]["money"] += task[i]["reward"]
                            add_money += task[i]["reward"]
                    case "score":
                        if nowRecord["score"] >= task[i]["request"]["value"]:
                            pluginData["plugin_data"]["task"][i]["finished"] = True
                            pluginData["plugin_data"]["money"] += task[i]["reward"]
                            add_money += task[i]["reward"]
    return add_money


getdata = _getdata()
