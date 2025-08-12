import math
from pathlib import Path
from typing import Any, Literal, overload

from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger
from zhenxun.utils.platform import PlatformUtils

from ..config import cmdhead
from ..lib.PhigrosUser import PhigrosUser
from ..utils import to_dict
from .cls.common import Save
from .cls.models import LevelData
from .cls.SongsInfo import SongsInfoObject
from .constNum import Level, LevelItem
from .getFile import SUPPORTED_FORMATS, FileManager
from .getInfo import getInfo
from .getNotes import getNotes
from .getPic import SongsIllAtlasData, pic
from .getSave import getSave
from .picmodle import picmodle
from .send import send


class getdata:
    @staticmethod
    def fuzzysongsnick(mic: str, Distance: float = 0.85):
        """
        根据参数模糊匹配返回原曲名称

        :param mic: 别名
        :param Distance: 匹配阈值，猜词0.95
        :return: 原曲名称
        """
        return getInfo.fuzzysongsnick(mic, Distance)

    @staticmethod
    @overload
    def info(song: str) -> SongsInfoObject | None: ...
    @staticmethod
    @overload
    def info() -> dict[str, SongsInfoObject]: ...
    @staticmethod
    def info(
        song: str | None = None,
    ) -> SongsInfoObject | None | dict[str, SongsInfoObject]:
        """
        :param song: 原曲曲名
        :param original: 是否仅使用原版曲库
        """
        return getInfo.info(song) if song else getInfo.all_info()

    @staticmethod
    async def getData(
        fileName: str,
        fatherPath: str | Path,
        style: SUPPORTED_FORMATS | None = None,
    ):
        """
        获取 chos 文件

        :param fileName: 文件名称 含后缀
        :param fatherPath: 路径
        :param style: 指定格式
        """
        return await FileManager.ReadFile(Path(fatherPath) / fileName, style)

    @staticmethod
    def setData(
        fileName: str,
        data: Any,
        fatherPath: str | Path,
        style: SUPPORTED_FORMATS | None = None,
    ):
        """
        修改 chos 文件为 data

        :param fileName: 文件名称 含后缀
        :param data: 覆写内容
        :param fatherPath: 父路径
        :param style: 文件类型
        """
        return FileManager.SetFile(Path(fatherPath) / fileName, data, style)

    @staticmethod
    def delData(fileName: str, fatherPath: str | Path):
        """
        删除 chos.yaml 文件

        :param fileName: 文件名称 含后缀
        :param fatherPath: 路径
        """
        return FileManager.DelFile(Path(fatherPath) / fileName)

    @staticmethod
    async def getsave(id: str):
        """
        获取user_id对应的存档文件

        :param id: user_id
        """
        return await getSave.getSave(id)

    @staticmethod
    async def putsave(id: str, data: dict):
        """
        保存user_id对应的存档文件

        :param id: user_id
        """
        return await getSave.putSave(id, data)

    @staticmethod
    async def delsave(id: str):
        """
        删除user_id对应的存档文件

        :param id: user_id
        """
        return await getSave.delSave(id)

    @staticmethod
    def delNotesData(user_id: str):
        """
        删除user_id对应的娱乐数据

        :param user_id: user_id
        """
        return getNotes.delNotesData(user_id)

    @staticmethod
    def getNotesData(user_id: str, islock: bool = False):
        """
        获取user_id对应的娱乐数据

        :param user_id: user_id
        :param islock:  是否锁定
        :return: 娱乐数据
        """
        return getNotes.getNotesData(user_id, islock)

    @staticmethod
    def putNotesData(user_id: str, data: dict):
        """
        保存user_id对应的娱乐数据

        :param id: user_id
        :param data: 娱乐数据
        """
        return getNotes.putNotesData(user_id, data)

    @staticmethod
    def getimg(img: str, style: str = "png"):
        """
        获取本地图片

        :param img: 文件名
        :param style: 文件格式，默认为png
        """
        return pic.getimg(img, style)

    @staticmethod
    async def getDan(id: str):
        """
        获取玩家 Dan 数据

        :param id: user_id
        """
        return await getSave.getDan(id)

    @staticmethod
    def songsnick(mic: str):
        """
        匹配歌曲名称，根据参数返回原曲名称

        :param mic: 别名
        :return: 原曲名称
        """
        return getInfo.songsnick(mic)

    @staticmethod
    async def setnick(mic: str, nick: str):
        """
        设置别名

        :param mic: 原名
        :param nick: 别名
        """
        return await getInfo.setnick(mic, nick)

    @staticmethod
    async def GetSongsInfoAtlas(name: str, data: dict | None = None):
        """
        获取歌曲图鉴，曲名为原名

        :param name: 曲名
        :param data: 自定义数据
        """
        return await pic.GetSongsInfoAtlas(name, data)

    @staticmethod
    async def GetSongsIllAtlas(name: str, data: SongsIllAtlasData | None = None):
        """
        通过曲目获取曲目图鉴

        :param name: 原曲名称
        :param data: 自定义数据
        """
        return await pic.GetSongsIllAtlas(name, data)

    @staticmethod
    async def buildingRecord(
        matcher, session: Uninfo, User: PhigrosUser
    ) -> tuple[float, int] | Literal[False]:
        """
        更新存档

        :param User: User
        :return: [rks变化值，note变化值]，失败返回 false
        """
        old = await getdata.getsave(session.user.id)
        try:
            save_info = await User.getSaveInfo()
            if old and old.saveInfo.modifiedAt.iso == save_info.modifiedAt.iso:
                return (0, 0)
            await User.buildRecord()
            # if not err:
            #     await send.sendWithAt(
            #         matcher,
            #         "以下曲目无信息，可能导致b19显示错误\n",  # + err.join("\n")
            #     )
        except Exception as err:
            if not PlatformUtils.is_qbot(session):
                await send.sendWithAt(f"更新失败！QAQ\n{err}")
            else:
                await send.sendWithAt("更新失败！QAQ\n请稍后重试")
            logger.error("更新失败！QAQ", "phi-plugin", e=err)
            return False
        try:
            await getdata.putsave(session.user.id, to_dict(User))
        except Exception as err:
            await send.sendWithAt(f"保存存档失败!\n{err}")
            logger.error("保存存档失败", "phi-plugin", e=err)
            return False
        now = Save(**to_dict(User))
        if old and (old.sessionToken and old.sessionToken != User.sessionToken):
            await send.sendWithAt(
                "检测到新的sessionToken，将自动更换绑定。如果需要删除统计"
                f"记录请 ⌈{cmdhead}"
                "unbind⌋ 进行解绑哦！",
            )
        # await now.init()
        # 更新
        history = await getSave.getHistory(session.user.id)
        history.update(now)
        await getSave.putHistory(session.user.id, to_dict(history))
        pluginData = await getNotes.getNotesData(session.user.id)
        # note数量变化
        add_money = 0
        task = pluginData.plugin_data.task
        if task:
            for id in now.gameRecord:
                for t in task:
                    if not t.finished and getInfo.idgetsong(id) == t.song:
                        temp = now.gameRecord[id][Level.index(t.request.rank)]
                        if not temp:
                            continue
                        match t.request.type:
                            case "acc":
                                if temp.acc >= t.request.value:
                                    t.finished = True
                                    pluginData.plugin_data.money += t.reward
                                    add_money += t.reward
                            case "score":
                                if temp.score >= t.request.value:
                                    t.finished = True
                                    pluginData.plugin_data.money += t.reward
                                    add_money += t.reward
        await getNotes.putNotesData(session.user.id, to_dict(pluginData))
        # rks变化
        add_rks = (
            now.saveInfo.summary.rankingScore - old.saveInfo.summary.rankingScore
            if old
            else 0
        )
        return (add_rks, add_money)

    @staticmethod
    async def getb19(data: dict):
        """获取best19图片"""
        return await picmodle.b19(data)

    @staticmethod
    async def getupdate(data: dict):
        """获取update图片"""
        return await picmodle.update(data)

    @staticmethod
    async def gettasks(data: dict):
        """获取任务列表图片"""
        return await picmodle.tasks(data)

    @staticmethod
    async def getuser_info(data: dict, kind: Literal[1, 2]):
        """获取个人信息图片"""
        return await picmodle.user_info(data, kind)

    @staticmethod
    async def getlvsco(data: dict):
        """获取定级区间成绩"""
        return await picmodle.lvsco(data)

    @staticmethod
    async def getsingle(data: dict):
        """获取单曲成绩"""
        return await picmodle.score(data)

    @staticmethod
    async def getillpicmodle(data: dict):
        """获取曲绘图鉴"""
        return await picmodle.ill(data)

    @staticmethod
    async def getguess(data: dict):
        """获取猜曲绘图片"""
        return await picmodle.guess(data)

    @staticmethod
    async def getrand(data: dict):
        """获取随机曲目图片"""
        return await picmodle.rand(data)

    @staticmethod
    def getill(name: str, kind: Literal["common", "blur", "low"] = "common"):
        """
        获取曲绘，返回地址

        :param  name: 原名
        :param kind: 清晰度
        :return: 网址或文件地址
        """
        return getInfo.getill(name, kind)

    @staticmethod
    def idgetavatar(id: str):
        """
        通过id获得头像文件名称

        :param id: id
        :return: file name
        """
        return getInfo.idgetavatar(id)

    @staticmethod
    def idgetsong(id: str) -> str | None:
        """
        根据曲目id获取原名

        :param str id: 曲目id
        :return: 原名
        """
        return getInfo.idgetsong(id)

    @staticmethod
    def SongGetId(song: str) -> str | None:
        """
        通过原曲曲目获取曲目id

        :param str song: 原曲曲名
        :return: 曲目id
        """
        return getInfo.SongGetId(song)

    @staticmethod
    def getrks(acc: float, difficulty: float):
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

    @staticmethod
    def comsuggest(rks: float, difficulty: float, count: int | None = None):
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
    level: LevelItem,
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
                        if nowRecord.acc >= task[i]["request"]["value"]:
                            pluginData["plugin_data"]["task"][i]["finished"] = True
                            pluginData["plugin_data"]["money"] += task[i]["reward"]
                            add_money += task[i]["reward"]
                    case "score":
                        if nowRecord.score >= task[i]["request"]["value"]:
                            pluginData["plugin_data"]["task"][i]["finished"] = True
                            pluginData["plugin_data"]["money"] += task[i]["reward"]
                            add_money += task[i]["reward"]
    return add_money
