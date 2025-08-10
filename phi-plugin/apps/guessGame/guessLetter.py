"""
Phigros出字母猜曲名游戏
会随机抽选 n 首歌曲
每首曲目的名字只显示一部分，剩下的部分隐藏
通过给出的字母猜出相应的歌曲
玩家可以翻开所有曲目响应的字母获得更多线索
"""

import asyncio
import random
import re
import time
from typing import Any, TypedDict

import cn2an
from nonebot_plugin_uninfo import Uninfo
from pypinyin import Style, pinyin

from zhenxun.services.log import logger

from ...config import PluginConfig, cmdhead
from ...model.getdata import getdata
from ...model.getInfo import getInfo
from ...model.getPic import pic
from ...model.send import send

songsname = getInfo.songlist
songweights: dict[str, dict[str, float]] = {}
"""每首歌曲被抽取的权重"""
# 曲目初始洗牌
random.shuffle(songsname)

gamelist: dict[str, dict[int, str]] = {}
"""标准答案曲名"""
blurlist: dict[str, dict[int, str]] = {}
"""模糊后的曲名"""
alphalist: dict[str, str] = {}
"""翻开的字母"""
winnerlist: dict[str, dict[int, str]] = {}
"""猜对者的群昵称"""
lastGuessedTime: dict[str, float] = {}
"""群聊猜字母全局冷却时间"""
lastRevealedTime: dict[str, float] = {}
"""群聊翻字母全局冷却时间"""
lastTipTime: dict[str, float] = {}
"""群聊提示全局冷却时间"""
gameSelectList = {}
"""群聊游戏选择的游戏范围"""


class timeCountStruct(TypedDict):
    """群聊游戏计时器结构"""

    startTime: float
    newTime: float


timeCount: dict[str, timeCountStruct] = {}
"""群聊游戏计时器"""
isfuzzymatch = True
"""是否模糊匹配"""


def getRandomSong(group_id: str):
    """定义随机抽取曲目的函数"""
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


def encrypt_song_name(name: str) -> str:
    """加密曲目名称函数"""
    num = 0  # NOTE: 当前配置为不显示任何字符
    numset = [
        (lambda: random.randint(0, len(name) - 1))()
        for _ in range(num)
        if name[random.randint(0, len(name) - 1)] != " "
    ]

    encrypted = []
    for index, char in enumerate(name):
        if index in numset:
            encrypted.append(char)
        elif char in (" ", " "):
            encrypted.append(" ")
        else:
            encrypted.append("*")

    return "".join(encrypted)


def gameover(group_id: str, gameList: dict[str, dict[str, Any]]):
    """结束本群游戏，返回答案"""
    t = gamelist[group_id]
    winner = winnerlist[group_id]
    del alphalist[group_id]
    del gamelist[group_id]
    del gameList[group_id]
    del blurlist[group_id]
    del winnerlist[group_id]
    del timeCount[group_id]

    output = ["开字母已结束，答案如下："]
    for i, correct_name in t.items():
        output.append(f"\n【{i}】{correct_name}")
        if winner_card := winner.get(i):
            output.append(f" @{winner_card}")

    return output


def getRandCharacter(str: str, blur: str):
    """随机取字符"""
    # 寻找未打开的位置
    temlist = []  # 存放 * 的下标
    temlist.extend(i for i in range(len(str)) if blur[i] == "*")
    return str[random.choice(temlist)]


class guessLetter:
    @staticmethod
    async def start(
        session: Uninfo,
        song_name: str | None,
        gameList: dict[str, dict[str, Any]],
    ):
        """发起出字母猜歌"""
        group_id = session.scene.id
        # TODO 处理其他游戏曲库
        totNameList = []
        gameSelectList[group_id] = []
        if not song_name:
            totNameList = await getInfo.all_info()
            gameSelectList[group_id].append("phigros")
        else:
            for i in getInfo.DLC_Info.keys():
                if i in song_name:
                    totNameList.extend(getInfo.DLC_Info[i])
                    gameSelectList[group_id].append(i)
        if group_id in gamelist:
            await send.sendWithAt(
                "喂喂喂，已经有群友发起出字母猜歌啦，不要再重复发起了，赶快输入"
                f"'{cmdhead}第X个XXXX'来猜曲名或者'{cmdhead}出X'来揭开字母吧！"
                f"结束请发 {cmdhead} ans 嗷！",
                True,
            )
            return
        if len(songsname) < PluginConfig.get("LetterNum"):
            await send.sendWithAt(
                "曲库中曲目的数量小于开字母的条数哦！更改曲库后需要重启哦！"
            )
            return
        alphalist[group_id] = ""
        lastGuessedTime[group_id] = 0
        lastRevealedTime[group_id] = 0
        lastTipTime[group_id] = 0
        songweights[group_id] = songweights.get(group_id, {})
        # 将每一首曲目的权重初始化为1
        for song in songsname:
            songweights[group_id][song] = 1
        # 预开猜对者数组
        winnerlist[group_id] = {}
        # 存储单局抽到的曲目下标
        chose = []
        nowTime = time.time()
        for i in range(PluginConfig.get("LetterNum")):
            # 根据曲目权重随机返回一首曲目名称
            randsong = getRandomSong(group_id)
            # 防止抽到重复的曲目
            cnnt = 0
            songinfo = await getInfo.info(randsong)
            assert songinfo
            while randsong in chose or songinfo.can_t_be_letter:
                cnnt += 1
                if cnnt >= 50:
                    logger.error("抽取曲目失败，请检查曲库设置", "phi-plugin:letter")
                    await send.sendWithAt("抽取曲目失败，请检查曲库设置")
                    return
                randsong = getRandomSong(group_id)
            chose.append(songinfo)
            gamelist[group_id] = gamelist.get(group_id, {})
            blurlist[group_id] = blurlist.get(group_id, {})
            gamelist[group_id][i] = songinfo.song
            blurlist[group_id][i] = encrypt_song_name(songinfo.song)
            gameList[group_id] = {"gameType": "guessLetter"}
            timeCount[group_id] = {
                "startTime": nowTime,
                "newTime": nowTime + PluginConfig.get("LetterTimeLength"),
            }
        # 输出提示信息
        await send.sendWithAt(
            f"开字母开启成功！回复'nX.XXXX'命令猜歌，例如：n1.Reimei;"
            f"发送'open X'来揭开字母(不区分大小写，不需要指令头)，"
            f"如'open A';发送'{cmdhead} ans'结束并查看答案哦！",
        )
        # 延时1s
        await asyncio.sleep(1)
        output = "开字母进行中：\n"
        for i, n in blurlist[group_id].items():
            output += f"【{i}】{n}\n"
        await send.sendWithAt(output, True)
        # 如果过长时间没人回答则结束
        await asyncio.sleep(timeCount[group_id]["newTime"] - time.time())
        if group_id not in gameList or nowTime != timeCount[group_id]["startTime"]:
            return
        await send.sendWithAt("呜，怎么还没有人答对啊QAQ！只能说答案了喵……")
        await send.sendWithAt(gameover(group_id, gameList))

    @staticmethod
    async def reveal(
        session: Uninfo,
        msg: str,
        gameList: dict[str, dict[str, Any]],
    ):
        """翻开字母"""
        group_id = session.scene.id
        if group_id not in gamelist:
            await send.sendWithAt(
                f"现在还没有进行的开字母捏，赶快输入{cmdhead} ltr开始新的一局吧！",
            )
            return
        timeCount[group_id]["newTime"] = time.time() + PluginConfig.get(
            "LetterTimeLength"
        )
        _time = PluginConfig.get("LetterRevealCd")
        currentTime = time.time()
        timetik = currentTime - lastRevealedTime[group_id]
        timeleft = round(_time - timetik)
        if timetik < _time:
            await send.sendWithAt(
                f"翻字符的全局冷却时间还有${timeleft}s呐，先耐心等下哇QAQ",
                True,
            )
            return
        lastRevealedTime[group_id] = currentTime
        letter = msg.lower()
        if letter.upper() in alphalist[group_id]:
            await send.sendWithAt(
                f"字符[ {letter} ]已经被打开过了ww,不用需要再重复开啦！", True
            )
            return
        output = []
        included = False
        for i, songname in gamelist[group_id].items():
            blurname = blurlist[group_id][i]
            characters = ""
            letters = ""
            if re.search(r"[\u4e00-\u9fff]", songname):
                characters = "".join(re.findall(r"[\u4e00-\u9fff]", songname))
                letters = "".join(
                    [item[0] for item in pinyin(characters, style=Style.FIRST_LETTER)]
                )
            if letter not in songname.lower() and letter not in letters:
                continue
            included = True
            if i >= len(blurlist[group_id]):
                continue
            newBlurname = ""
            for index, char in enumerate(songname):
                # 中文字符处理
                if "\u4e00" <= char <= "\u9fff":
                    # 获取拼音首字母并比较
                    char_pinyin = pinyin(char, style=Style.FIRST_LETTER)[0][0]
                    if char_pinyin.lower() == letter.lower():
                        newBlurname += char
                    else:
                        try:
                            newBlurname += blurname[index]
                        except IndexError:
                            newBlurname += "*"
                # 英文字符处理
                elif char.lower() == letter.lower():
                    newBlurname += char
                else:
                    try:
                        newBlurname += blurname[index]
                    except IndexError:
                        newBlurname += "*"
            if "*" in newBlurname:
                blurlist[group_id][i] = newBlurname
        if included:
            alphalist[group_id] += (
                f"{letter.upper()} "
                if re.fullmatch(r"[A-Za-z]+", letter)
                else f"{letter} "
            )
            output.append(f"成功翻开字母[ {letter} ]\n")
        else:
            output.append(f"这几首曲目中不包含字母[ {letter} ]\n")
        output.append(f"当前所有翻开的字母[ {alphalist[group_id]}")
        isEmpty = group_id not in blurlist
        for m, song in gamelist[group_id].items():
            if not isEmpty and blurlist[group_id].get(m):
                output.append(f"\n【{m}】{blurlist[group_id][m]}")
            else:
                result = f"\n【${m}】${song}"
                if user := winnerlist[group_id].get(m):
                    result += f" @{user}"
                output.append(result)
        if isEmpty:
            output.insert(0, "\n所有字母已翻开，答案如下：\n")
            del alphalist[group_id]
            del blurlist[group_id]
            del gamelist[group_id]
            del gameList[group_id]
            del winnerlist[group_id]

        await send.sendWithAt(output, True)

    @staticmethod
    async def guess(
        session: Uninfo,
        msg: str,
        gameList: dict[str, dict[str, Any]],
    ):
        """猜测"""
        group_id, user_id = session.scene.id, session.user.id
        sender = getattr(session.member, "nick") or session.user.name or user_id
        timeCount[group_id]["newTime"] = time.time() + PluginConfig.get(
            "LetterTimeLength"
        )
        # 必须已经开始了一局
        if group_id in gamelist:
            _time = PluginConfig.get("LetterGuessCd")
            currentTime = time.time()
            timetik = currentTime - lastGuessedTime[group_id]
            timeleft = round(_time - timetik)
            # 上一轮猜测的Cd还没过
            if timetik < _time:
                await send.sendWithAt(
                    f"猜测的冷却时间还有{timeleft}s呐，先耐心等下哇QAQ", True
                )
                return
            # 上一轮Cd结束，更新新一轮的时间戳
            lastGuessedTime[group_id] = currentTime
            opened = f"\n所有翻开的字母[ {alphalist[group_id]}]\n"
            if result := re.match(
                r"^\s*[第n]\s*(\d+|[一二三四五六七八九十百]+)\s*[个首.]?(.*)$", msg
            ):
                num = (
                    result[1] if isinstance(result[1], int) else cn2an.cn2an(result[1])
                )
                assert isinstance(num, int)
                content = result[2]
                if num > PluginConfig.get("LetterNum"):
                    await send.sendWithAt(f"没有第{num}个啦！看清楚再回答啊喂！￣へ￣")
                    return
                songs = (
                    await getdata.fuzzysongsnick(content, 0.95)
                    if isfuzzymatch
                    else await getdata.songsnick(content)
                )
                standard_song = gamelist[group_id].get(num)
                if songs:
                    output = []
                    for song in songs:
                        if standard_song and standard_song == song:
                            # 已经猜完移除掉的曲目不能再猜
                            if not blurlist[group_id].get(num):
                                await send.sendWithAt(
                                    f"曲目[{standard_song}]已经猜过了，要不咱们换一个吧uwu",
                                )
                                return
                            del blurlist[group_id][num]
                            await send.sendWithAt(
                                f"恭喜你ww，答对啦喵，第{num}首答案是[{standard_song}]!"
                                "ヾ(≧▽≦*)o ",
                                True,
                            )
                            # 发送曲绘
                            if song_info := await getdata.info(standard_song):
                                if song_info.illustration:
                                    match PluginConfig.get("LetterIllustration"):
                                        case "水印版":
                                            await send.sendWithAt(
                                                await getdata.getillpicmodle(
                                                    {
                                                        "illustration": (
                                                            await getdata.getill(
                                                                standard_song
                                                            )
                                                        ),
                                                        "illustrator": (
                                                            song_info.illustrator
                                                        ),
                                                    }
                                                ),
                                            )
                                        case "原版":
                                            await send.sendWithAt(
                                                await pic.getIll(standard_song)
                                            )
                                        case _:
                                            pass
                            # 记录猜对者
                            winnerlist[group_id][num] = sender
                            isEmpty = not blurlist[group_id]
                            """是否全部猜完"""
                            if not isEmpty:
                                output.extend(("开字母进行中：", opened))
                                for i in gamelist[group_id].keys():
                                    if v := blurlist[group_id].get(i):
                                        output.append(f"\n【{i}】{v}")
                                    else:
                                        output.append(
                                            f"\n【{i}】{gamelist[group_id][i]}"
                                        )
                                        if w := winnerlist[group_id].get(i):
                                            output.append(f" @{w}")
                                await send.sendWithAt(output, True)
                            else:
                                del alphalist[group_id]
                                del blurlist[group_id]
                                output.append("开字母已结束，答案如下：\n")
                                for i, song in gamelist[group_id].items():
                                    output.append(f"\n【{i}】{song}")
                                    if w := winnerlist[group_id].get(i):
                                        output.append(f" @{w}")
                                output.append(opened)
                                del gamelist[group_id]
                                del gameList[group_id]
                                del winnerlist[group_id]
                                await send.sendWithAt(output)
                            return
                    if len(songs) > 1:
                        await send.sendWithAt(
                            f"第{num}首不是[{content}]www，要不再想想捏？如果实在不会可以"
                            f"悄悄发个[{cmdhead} tip]哦≧ ﹏ ≦",
                            True,
                        )
                    else:
                        await send.sendWithAt(
                            f"第{num}首不是[{songs[0]}]www，要不再想想捏？如果实在不会可以"
                            f"悄悄发个[{cmdhead} tip]哦≧ ﹏ ≦",
                            True,
                        )
                    return
                await send.sendWithAt(f"没有找到[{content}]的曲目信息呐QAQ", True)
                return
            # 格式匹配错误放过命令
            return
        # 未进行游戏放过命令
        return

    @staticmethod
    async def ans(
        session: Uninfo,
        gameList: dict[str, dict[str, Any]],
    ):
        """答案"""
        group_id = session.scene.id
        if group_id in gamelist:
            await send.sendWithAt(
                "好吧好吧，既然你执着要放弃，那就公布答案好啦。", True
            )
            await send.sendWithAt(gameover(group_id, gameList))
            return
        await send.sendWithAt(
            f"现在还没有进行的开字母捏，赶快输入'{cmdhead} letter'开始新的一局吧！",
            True,
        )

    @staticmethod
    async def getTip(
        session: Uninfo,
        gameList: dict[str, dict[str, Any]],
    ):
        """提示"""
        group_id = session.scene.id
        timeCount[group_id]["newTime"] = time.time() + PluginConfig.get(
            "LetterTimeLength"
        )
        if group_id not in gamelist:
            await send.sendWithAt(
                f"现在还没有进行的开字母捏，赶快输入'{cmdhead} letter'开始新的一局吧！",
                True,
            )
            return
        _time = PluginConfig.get("LetterTipCd")
        currentTime = time.time()
        timetik = currentTime - lastTipTime[group_id]
        timeleft = round(_time - timetik)
        if timetik < _time:
            await send.sendWithAt(
                f"使用提示的全局冷却时间还有{timeleft}s呐，还请先耐心等下哇QAQ",
                True,
            )
            return
        lastTipTime[group_id] = currentTime

        commonKeys = [i for i in gamelist[group_id] if i in blurlist[group_id]]
        randsymbol = None
        while randsymbol is None or randsymbol == "*":
            key = random.choice(commonKeys)
            songname = blurlist[group_id][key]
            randsymbol = getRandCharacter(songname, blurlist[group_id][key])
        for key, songname in gamelist[group_id].items():
            blurname = blurlist[group_id].get(key)
            if not blurname:
                continue
            newBlurname = ""
            for index, char in enumerate(songname):
                if "\u4e00" <= char <= "\u9fff":
                    if (
                        pinyin(char, style=Style.FIRST_LETTER)[0][0].lower()
                        == randsymbol.lower()
                    ):
                        newBlurname += char
                        continue
                    newBlurname += (
                        char if char.lower() == randsymbol.lower() else blurname[index]
                    )
            if "*" in newBlurname:
                blurlist[group_id][key] = newBlurname
        if re.fullmatch(r"[A-Za-z]+", randsymbol):
            alphalist[group_id] += randsymbol.upper()
        else:
            alphalist[group_id] += f"{randsymbol} "
        output = [
            f"已经帮你随机翻开一个字符[ {randsymbol} ]了捏 ♪（＾∀＾●）ﾉ\n",
            f"当前所有翻开的字符[ {alphalist[group_id]}]",
        ]
        isEmpty = group_id not in blurlist
        if not isEmpty:
            for key, song in gamelist[group_id].items():
                if v := blurlist[group_id].get(key):
                    output.append(f"\n【{key}】{v}")
                else:
                    output.append(f"\n【{key}】{song}")
                    if w := winnerlist[group_id].get(key):
                        output.append(f" @{w}")
        else:
            del alphalist[group_id]
            del blurlist[group_id]
            output.append("\n字母已被全部翻开，答案如下：")
            for key, song in gamelist[group_id].items():
                output.append(f"\n【{key}】{song}")
                if w := winnerlist[group_id].get(key):
                    output.append(f" @{w}")
            del gamelist[group_id]
            del gameList[group_id]
            del winnerlist[group_id]
        await send.sendWithAt(output, True)

    @staticmethod
    async def mix(session: Uninfo):
        """洗牌"""
        group_id = session.scene.id
        if group_id in gamelist:
            await send.sendWithAt(
                "当前有正在进行的游戏，请等待游戏结束再执行该指令", True
            )
            return
        random.shuffle(songsname)
        songweights[group_id] = songweights.get(group_id, {})
        # 将每一首曲目的权重初始化为1
        for song in songsname:
            songweights[group_id][song] = 1
        await send.sendWithAt("洗牌成功了www", True)

    @staticmethod
    async def checkLetterInSongs(group_id: str, letter: str) -> bool:
        """检查字母是否包含在曲目中"""
        for i, songname in gamelist[group_id].items():
            blurname = blurlist[group_id].get(i)
            characters = "".join(re.findall(r"[\u4e00-\u9fa5]", songname, re.UNICODE))
            letters = pinyin(characters, style=Style.FIRST_LETTER)[0][0]
            if (
                letter.lower() not in songname.lower()
                and letter.lower() not in letters.lower()
            ):
                continue
            if not blurname:
                continue
            newBlurname = ""
            for index, char in enumerate(songname):
                # 中文字符处理
                if "\u4e00" <= char <= "\u9fff":
                    # 获取拼音首字母并比较
                    char_pinyin = pinyin(char, style=Style.FIRST_LETTER)[0][0]
                    if char_pinyin.lower() == letter.lower():
                        newBlurname += char
                        continue
                newBlurname += (
                    char if char.lower() == letter.lower() else blurname[index]
                )
            if "*" in newBlurname:
                blurlist[group_id][i] = newBlurname
        return bool(blurlist[group_id])
