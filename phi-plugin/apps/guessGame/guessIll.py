import asyncio
import contextlib
import random
from typing import Any

from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger

from ...config import PluginConfig, cmdhead
from ...model.cls.SongsInfo import SongsInfoObject
from ...model.getdata import getdata
from ...model.getInfo import getInfo
from ...model.send import send

songsname = getInfo.illlist
songweights: dict[str, dict[str, float]] = {}
"""存储每首歌曲被抽取的权重"""
# 曲目初始洗牌
random.shuffle(songsname)

gamelist: dict[str, str] = {}


def getRandomSong(session: Uninfo):
    """定义随机抽取曲目的函数"""
    group_id = session.scene.id

    # 计算曲目的总权重
    total_weight = sum(songweights[group_id].values())

    random_weight = random.uniform(0, total_weight)

    accumulated_weight = 0
    for song, weight in songweights[group_id].items():
        accumulated_weight += weight
        if accumulated_weight >= random_weight:
            # 权重每次衰减60%
            songweights[group_id][song] *= 0.4
            return song

    # 如果由于浮点数精度问题未能正确选择歌曲，则随机返回一首
    return random.choice(songsname)


async def gameover(matcher, data: dict):
    """游戏结束，发送相应位置"""
    data["ans"] = data["illustration"]
    data["style"] = 1
    await send.sendWithAt(matcher, await getdata.getguess(data))


def area_increase(size: int, data: dict, fnc: list[int]):
    """
    区域扩增

    :param int size: 增加的像素值
    :param dict data:
    :param list fnc:
    """
    if data["height"] < 1080:
        if data["height"] + size > 1080:
            data["height"] = 1080
            data["y"] = 0
        else:
            data["height"] += size
            data["y"] = min(max(0, data["y"] - size / 2), 1080 - data["height"])
    if data["width"] < 2048:
        if data["width"] + size > 2048:
            data["width"] = 2048
            data["x"] = 0
            with contextlib.suppress(ValueError):
                fnc.remove(0)
        else:
            data["width"] += size
            data["x"] = min(max(0, data["x"] - size / 2), 2048 - data["width"])


def blur_down(size: int, data: dict, fnc: list[int]):
    """
    降低模糊度

    :param int size: 降低值
    """
    data["blur"] = max(0, data["blur"] - size)
    if not data["blur"]:
        with contextlib.suppress(ValueError):
            fnc.remove(1)


def gave_a_tip(
    known_info: dict,
    remain_info: list[str],
    songs_info: SongsInfoObject,
    fnc: list[int],
):
    """获得一个歌曲信息的提示"""
    if remain_info:
        aim = random.choice(remain_info)
        remain_info.remove(aim)
        known_info[aim] = getattr(songs_info, aim)
        if not remain_info:
            with contextlib.suppress(ValueError):
                fnc.remove(2)
        if aim == "chart":
            t1 = random.choice(list(songs_info.chart.keys()))
            known_info["chart"] = f"\n该曲目的 {t1} 谱面的"
            match random.randint(0, 2):
                case 0:
                    """定数"""
                    known_info["chart"] = f"定数为 {songs_info.chart[t1].difficulty}"
                case 1:
                    """物量"""
                    known_info["chart"] = f"物量为 {songs_info.chart[t1].combo}"
                case 2:
                    """谱师"""
                    known_info["chart"] = f"谱师为 {songs_info.chart[t1].charter}"
    else:
        logger.error("Error: remaining info is empty", "phi-plugin:guessill")


class guessIll:
    @staticmethod
    async def start(matcher, session: Uninfo, gameList: dict[str, dict[str, Any]]):
        """猜曲绘"""
        group_id = session.scene.id
        if gamelist.get(group_id):
            await send.sendWithAt(matcher, "请不要重复发起哦！")
            return
        if len(songsname) == 0:
            await send.sendWithAt(
                matcher, "当前曲库暂无有曲绘的曲目哦！更改曲库后需要重启哦！"
            )
            return
        if not songweights.get(group_id):
            songweights[group_id] = {}
            # 将每一首曲目的权重初始化为1
            for song in songsname:
                songweights[group_id][song] = 1
        song = getRandomSong(session)
        songs_info = await getInfo.info(song)
        cnnt = 0
        while songs_info and songs_info.can_t_be_guessill:
            cnnt += 1
            if cnnt > 50:
                logger.error("抽取曲目失败，请检查曲库设置", "phi-plugin:guess")
                await send.sendWithAt(
                    matcher, "[phi guess]抽取曲目失败，请检查曲库设置"
                )
                return
            song = getRandomSong(session)
            songs_info = await getInfo.info(song)
        if songs_info is None:
            await send.sendWithAt(matcher, f"无法获取歌曲 {song} 的信息")
            return
        gamelist[group_id] = songs_info.song
        gameList[group_id] = {"gameType": "guessIll"}
        w_ = random.randint(100, 140)
        h_ = random.randint(100, 140)
        x_ = random.randint(0, 2048 - w_)
        y_ = random.randint(0, 1080 - h_)
        blur_ = random.randint(9, 14)
        data = {
            "illustration": await getInfo.getill(songs_info.song),
            "width": w_,
            "height": h_,
            "x": x_,
            "y": y_,
            "blur": blur_,
            "style": 0,
        }
        known_info = {}
        remain_info = ["chapter", "bpm", "composer", "length", "illustrator", "chart"]
        """
        随机给出提示
        0: 区域扩大
        1: 模糊度减小
        2: 给出一条文字信息
        3: 显示区域位置
        """
        fnc = [0, 1, 2, 3]
        await send.sendWithAt(
            matcher,
            "下面开始进行猜曲绘哦！回答可以直接发送哦！每过"
            f"{PluginConfig.get('GuessTipCd')}秒后将会给出进一步提示。发送 {cmdhead}"
            "ans 结束游戏",
            False,
        )
        await send.sendWithAt(
            matcher,
            await getdata.getguess(data),
            False,
            PluginConfig.get("GuessTipCd") if PluginConfig.get("GuessTipRecall") else 0,
        )
        # NOTE: 单局时间不超过4分半
        time = PluginConfig.get("GuessTipCd")
        for _ in range(int(270 / time)):
            for _ in range(time):
                await asyncio.sleep(1)
                if gamelist.get(group_id):
                    if gamelist[group_id] != songs_info.song:
                        await gameover(matcher, data)
                else:
                    await gameover(matcher, data)
            tipmsg = ""
            """这次干了什么"""
            match random.choice(fnc):
                case 0:
                    area_increase(100, data, fnc)
                    tipmsg = "[区域扩增!]"
                case 1:
                    blur_down(2, data, fnc)
                    tipmsg = "[清晰度上升!]"
                case 2:
                    gave_a_tip(known_info, remain_info, songs_info, fnc)
                    tipmsg = "[追加提示!]"
                case 3:
                    data["style"] = 1
                    fnc.remove(3)
                    tipmsg = "[全局视野!]"
            if known_info.get("chapter"):
                tipmsg += f"\n该曲目隶属于 {known_info['chapter']}"
            if known_info.get("bpm"):
                tipmsg += f"\n该曲目的 BPM 值为 {known_info['bpm']}"
            if known_info.get("composer"):
                tipmsg += f"\n该曲目的作者为 {known_info['composer']}"
            if known_info.get("length"):
                tipmsg += f"\n该曲目的时长为 {known_info['length']}"
            if known_info.get("illustrator"):
                tipmsg += f"\n该曲目曲绘的作者为 {known_info['illustrator']}"
            if known_info.get("chart"):
                tipmsg += known_info["chart"]
            """回复内容"""
            remsg = [tipmsg, await getdata.getguess(data)]
            if gamelist.get(group_id):
                if gamelist[group_id] != songs_info.song:
                    await gameover(matcher, data)
            else:
                await gameover(matcher, data)
            await send.sendWithAt(
                matcher,
                remsg,
                False,
                recallTime=(PluginConfig.get("GuessTipCd") + 1)
                if PluginConfig.get("GuessTipRecall")
                else 0,
            )
        for _ in range(time):
            await asyncio.sleep(1)
            if gamelist.get(group_id):
                if gamelist[group_id] != songs_info.song:
                    await gameover(matcher, data)
            else:
                await gameover(matcher, data)
        t = gamelist[group_id]
        del gamelist[group_id]
        del gameList[group_id]
        await send.sendWithAt(
            matcher, "呜，怎么还没有人答对啊QAQ！只能说答案了喵……", False
        )
        await send.sendWithAt(matcher, await getdata.GetSongsInfoAtlas(t), False)
        await gameover(matcher, data)

    @staticmethod
    async def guess(
        matcher, session: Uninfo, msg: str, gameList: dict[str, dict[str, Any]]
    ):
        """玩家猜测"""
        group_id = session.scene.id
        if gamelist.get(group_id):
            song = await getdata.fuzzysongsnick(msg, 0.95)
            if song and song[0]:
                for i in song:
                    if gamelist[group_id] == i:
                        t = gamelist[group_id]
                        del gamelist[group_id]
                        del gameList[group_id]
                        await send.sendWithAt(
                            matcher, "恭喜你，答对啦喵！ヾ(≧▽≦*)o", True
                        )
                        await send.sendWithAt(
                            matcher, await getdata.GetSongsInfoAtlas(t)
                        )
                        return
                if len(song) > 1 and song[1]:
                    await send.sendWithAt(matcher, f"不是 {msg} 哦喵！≧ ﹏ ≦", True, 5)
                else:
                    await send.sendWithAt(
                        matcher, f"不是 {song[0]} 哦喵！≧ ﹏ ≦", True, 5
                    )

    @staticmethod
    async def ans(matcher, session: Uninfo, gameList: dict[str, dict[str, Any]]):
        group_id = session.scene.id
        if gamelist.get(group_id):
            t = gamelist[group_id]
            del gamelist[group_id]
            del gameList[group_id]
            await send.sendWithAt(matcher, "好吧，下面开始公布答案。")
            await send.sendWithAt(matcher, await getdata.GetSongsInfoAtlas(t))

    @staticmethod
    async def mix(matcher, session: Uninfo):
        """洗牌"""
        group_id = session.scene.id
        if gamelist.get(group_id):
            await send.sendWithAt(
                matcher, "当前有正在进行的游戏，请等待游戏结束再执行该指令"
            )
            return
        # 曲目初始洗牌
        random.shuffle(songsname)
        songweights[group_id] = songweights.get(group_id, {})

        # 将每一首曲目的权重初始化为1
        for song in songsname:
            songweights[group_id][song] = 1
        await send.sendWithAt(matcher, "洗牌成功了www")
