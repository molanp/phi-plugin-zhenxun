import random
import time
from typing import Any

from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger

from ...config import PluginConfig, cmdhead
from ...model.fCompute import fCompute
from ...model.getInfo import getInfo
from ...model.getPic import pic
from ...model.picmodle import picmodle
from ...model.send import send


class guessTips:
    @staticmethod
    async def start(
        session: Uninfo,
        gameList: dict[str, dict[str, Any]],
    ):
        group_id = session.scene.id
        if group_id in gameList:
            await send.sendWithAt("请不要重复发起哦！")
            return
        # 提取原名，要求有曲绘
        songList = []
        totInfo = getInfo.ori_info
        for i in totInfo:
            if not await getInfo.getill(i):
                continue
            songList.append(i)
        if not songList:
            logger.error("猜曲绘无有效曲目", "phi-plugin")
            await send.sendWithAt(
                "当前曲库暂无有曲绘的曲目哦！更改曲库后需要重启哦！", False
            )
            return
        # 选中的歌曲原名
        song = songList[fCompute.randBetween(0, len(songList) - 1)]
        info = totInfo[song]
        # 文字提示
        tip: list[str] = [
            f"这首曲目隶属于 {info.chapter}",
            f"这首曲目的⌈BPM⌋值为 {info.bpm}",
            f"这首曲目的⌈作曲者⌋ 为 {info.composer}",
            f"这首曲目的⌈时长⌋为 {info.length}",
            f"这首曲目的⌈画师⌋为 {info.illustrator}",
        ]
        for level in info.chart:
            tip.extend(
                (
                    f"这首曲目的⌈{level}⌋难度⌈定数⌋为 {info.chart[level].difficulty}",
                    f"这首曲目的⌈{level}⌋难度⌈物量⌋为 {info.chart[level].combo}",
                    f"这首曲目的⌈{level}⌋难度⌈谱师⌋为 {info.chart[level].charter}",
                )
            )
        random.shuffle(tip)
        tip = tip[: PluginConfig.get("GuessTipsTipNum")]
        # 曲绘区域
        # width
        w_ = fCompute.randBetween(100, 150)
        # height
        h_ = fCompute.randBetween(100, 150)
        x_ = fCompute.randBetween(0, 2048 - w_)
        y_ = fCompute.randBetween(0, 1080 - h_)
        id_ = fCompute.randBetween(0, 1000000000)
        gameList[group_id] = {
            "gameType": "guessTips",
            "id": id_,
            "song": song,
            "startTime": time.time(),
            "tipTime": time.time(),
            "tips": tip,
            "tipNum": 1,  # 已发送提示的数量
            "ill": {
                "illustration": await getInfo.getill(song),
                "ans": await getInfo.getill(song),
                "width": w_,
                "height": h_,
                "x": x_,
                "y": y_,
            },
        }
        await send.sendWithAt(
            "下面开始进行猜曲绘哦！可以直接发送曲名进行回答哦！"
            f"每过{PluginConfig.get('GuessTipsTipCD')}秒后可以请求下一条提示，"
            f"共有{PluginConfig.get('GuessTipsTipNum') + 1}条提示嗷！"
            f"所有提示发送完毕{PluginConfig.get('GuessTipsAnsTime')}秒后会自动结束游戏嗷！"
            f"发送 {cmdhead} ans 也可以提前结束游戏呐！`)",
        )
        reMsg = "".join(
            f"{i + 1}.{gameList[group_id]['tips'][i]}\n"
            for i in range(PluginConfig.get("GuessTipsTipNum"))
        )
        await send.sendWithAt(reMsg)

        async def checkresult(group_id, id_, gameList):
            if group_id in gameList and gameList[group_id]["id"] == id_:
                await send.sendWithAt(
                    [
                        f"呜……很遗憾，没有人答对喵！正确答案是：{gameList[group_id]['song']}",
                        await picmodle.guess(
                            {
                                **gameList[group_id]["ill"],
                                "blur": 0,
                                "style": 1,
                            }
                        )
                        if gameList[group_id]["tipNum"]
                        > len(gameList[group_id]["tips"])
                        else "",
                    ],
                )

        scheduler.add_job(
            checkresult,
            "date",
            run_date=time.time() + PluginConfig.get("GuessTipsTimeout"),
            kwargs={"group_id": group_id, "id_": id_, "gameList": gameList},
        )

    @staticmethod
    async def getTip(
        session: Uninfo,
        gameList: dict[str, dict[str, Any]],
    ):
        group_id = session.scene.id
        if group_id not in gameList:
            return
        nowTime = time.time()
        gameData = gameList[group_id]
        if nowTime - gameData["tipTime"] < PluginConfig.get("GuessTipsTipCD"):
            await send.sendWithAt(
                f"提示的冷却时间还有{round(nowTime - gameData['tipTime'])}秒哦！",
            )
            return
        if gameData["tipNum"] > len(gameData["tips"]):
            await send.sendWithAt(
                "已经没有提示了呐，再仔细想想吧！",
            )
            return
        rev = []
        if gameData["tipNum"] == len(gameData["tips"]):

            async def checkresult(group_id, id_, gameList):
                if group_id in gameList and gameList[group_id]["id"] == id_:
                    del gameList[group_id]
                    await send.sendWithAt(
                        [
                            f"呜……很遗憾，没有人答对喵！正确答案是：{gameData['song']}",
                            await picmodle.guess(
                                {
                                    **gameData["ill"],
                                    "blur": 0,
                                    "style": 1,
                                }
                            ),
                        ],
                    )

            scheduler.add_job(
                checkresult,
                "date",
                run_date=time.time() + PluginConfig.get("GuessTipsAnsTime"),
                kwargs={
                    "group_id": group_id,
                    "id_": gameData["id"],
                    "gameList": gameList,
                },
            )
            await send.sendWithAt(
                f"接下来是曲绘提示哦！如果在{PluginConfig.get('GuessTipsAnsTime')}秒内没有回答正确的话，将会自动公布答案哦！",
            )
            rev.append(await picmodle.guess({**gameData["ill"], "blur": 0, "style": 0}))
        else:
            gameData["tipNum"] += 1
        resMsg = ""
        for i in range(gameList[group_id]["tipNum"]):
            resMsg += f"{i + 1}.{gameList[group_id]['tips'][i]}\n"
        rev.insert(0, resMsg)
        await send.sendWithAt(rev)

    @staticmethod
    async def guess(
        session: Uninfo,
        msg: str,
        gameList: dict[str, dict[str, Any]],
    ):
        group_id = session.scene.id
        if group_id not in gameList:
            return
        group_id = group_id
        song = await getInfo.fuzzysongsnick(msg, 0.95)
        if song and song[0]:
            for i in song:
                if gameList[group_id]["song"] == i:
                    gameData = gameList[group_id]
                    del gameList[group_id]
                    await send.sendWithAt("恭喜你，答对啦喵！ヾ(≧▽≦*)o", True)
                    if gameData["tipNum"] == gameData["tips"].length + 1:
                        await send.sendWithAt(
                            await picmodle.guess(
                                {
                                    **gameData["ill"],
                                    "blur": 0,
                                    "style": 0,
                                }
                            ),
                        )
                    await send.sendWithAt(await pic.GetSongsInfoAtlas(gameData["song"]))
                    return
            if len(song) > 1 and song[1]:
                await send.sendWithAt(f"不是 {msg} 哦喵！≧ ﹏ ≦", True, 5)
            else:
                await send.sendWithAt(f"不是 {song[0]} 哦喵！≧ ﹏ ≦", True, 5)

    @staticmethod
    async def ans(
        session: Uninfo,
        gameList: dict[str, dict[str, Any]],
    ):
        group_id = session.scene.id
        if group_id not in gameList:
            return
        gameData = gameList[group_id]
        del gameList[group_id]
        await send.sendWithAt(
            [
                f"好吧，下面开始公布答案。正确答案是：{gameData['song']}",
                await picmodle.guess(
                    {
                        **gameData["ill"],
                        "blur": 0,
                        "style": 1,
                    }
                )
                if gameData["tipNum"] > len(gameData["tips"])
                else "",
            ],
        )
        await send.sendWithAt(await pic.GetSongsInfoAtlas(gameData["song"]))
