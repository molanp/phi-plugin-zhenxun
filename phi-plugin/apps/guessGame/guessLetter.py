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

import cn2an
from nonebot_plugin_uninfo import Uninfo
from pypinyin import Style, pinyin

from zhenxun.services.log import logger

# NOTE
"""
js pinyin
a = pinyin(characters, { pattern: 'first', toneType: 'none', type: 'string' })
等价于
a = "".join([item[0] for item in pinyin(characters, style=Style.FIRST_LETTER)])
"""
from typing import Any, TypedDict

from ...config import PluginConfig, cmdhead
from ...model.getdata import getdata
from ...model.getInfo import getInfo
from ...model.getPic import pic
from ...model.send import send

songsname = getInfo.songlist
songweights = {}
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


def gameover(group_id, gameList):
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
    for i, correct_name in enumerate(t):
        output.append(f"\n【{i}】{correct_name}")
        if winner_card := winner.get(i):
            output.append(f" @{winner_card}")

    return output


class guessLetter:
    @staticmethod
    async def start(
        matcher, session: Uninfo, msg: str | None, gameList: dict[str, dict[str, Any]]
    ):
        """发起出字母猜歌"""
        group_id = session.scene.id
        # TODO 处理其他游戏曲库
        totNameList = []
        gameSelectList[group_id] = []
        if not msg:
            totNameList = await getInfo.all_info()
            gameSelectList[group_id].append("phigros")
        else:
            for i in getInfo.DLC_Info.keys():
                if i in msg:
                    totNameList.extend(getInfo.DLC_Info[i])
                    gameSelectList[group_id].append(i)
        if group_id in gamelist:
            await send.sendWithAt(
                matcher,
                "喂喂喂，已经有群友发起出字母猜歌啦，不要再重复发起了，赶快输入"
                f"'{cmdhead}第X个XXXX'来猜曲名或者'{cmdhead}出X'来揭开字母吧！"
                f"结束请发 {cmdhead} ans 嗷！",
                True,
            )
            return
        if len(songsname) < PluginConfig.get("LetterNum"):
            await send.sendWithAt(
                matcher, "曲库中曲目的数量小于开字母的条数哦！更改曲库后需要重启哦！"
            )
            return
        alphalist[group_id] = ""
        lastGuessedTime[group_id] = 0
        lastRevealedTime[group_id] = 0
        if not songweights.get(group_id):
            songweights[group_id] = {}
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
            randsong = getRandomSong(session)
            # 防止抽到重复的曲目
            cnnt = 0
            songinfo = await getInfo.info(randsong)
            assert songinfo is not None
            while randsong in chose or songinfo.can_t_be_letter:
                cnnt += 1
                if cnnt >= 50:
                    logger.error("抽取曲目失败，请检查曲库设置", "phi-plugin:letter")
                    await send.sendWithAt(matcher, "抽取曲目失败，请检查曲库设置")
                    return
                randsong = getRandomSong(session)
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
            matcher,
            f"开字母开启成功！回复'nX.XXXX'命令猜歌，例如：n1.Reimei;"
            f"发送'open X'来揭开字母(不区分大小写，不需要指令头)，"
            f"如'open A';发送'{cmdhead} ans'结束并查看答案哦！",
        )
        # 延时1s
        await asyncio.sleep(1)
        output = "开字母进行中：\n"
        for i, n in enumerate(blurlist[group_id]):
            output += f"【{i}】{n}\n"
        await send.sendWithAt(matcher, output, True)
        # 如果过长时间没人回答则结束
        await asyncio.sleep(timeCount[group_id]["newTime"] - time.time())
        if group_id not in gameList or nowTime != timeCount[group_id]["startTime"]:
            return
        await send.sendWithAt(matcher, "呜，怎么还没有人答对啊QAQ！只能说答案了喵……")
        await send.sendWithAt(matcher, gameover(group_id, gameList))

    @staticmethod
    async def reveal(
        matcher, session: Uninfo, msg: str, gameList: dict[str, dict[str, Any]]
    ):
        """翻开字母"""
        group_id = session.scene.id
        if group_id not in gamelist:
            await send.sendWithAt(
                matcher,
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
                matcher,
                f"翻字符的全局冷却时间还有${timeleft}s呐，先耐心等下哇QAQ",
                True,
            )
            return
        lastRevealedTime[group_id] = currentTime
        letter = msg.lower()
        if letter.upper() in alphalist[group_id]:
            await send.sendWithAt(
                matcher, f"字符[ {letter} ]已经被打开过了ww,不用需要再重复开啦！", True
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
        for m, song in enumerate(gamelist[group_id]):
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

        await send.sendWithAt(matcher, output, True)

    @staticmethod
    async def guess(
        matcher, session: Uninfo, msg: str, gameList: dict[str, dict[str, Any]]
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
                    matcher, f"猜测的冷却时间还有{timeleft}s呐，先耐心等下哇QAQ", True
                )
                return
            # 上一轮Cd结束，更新新一轮的时间戳
            lastGuessedTime[group_id] = currentTime
            opened = f"\n所有翻开的字母[ {alphalist[group_id]}]\n"
            if result := re.match(
                r"^\s*[第n]\s*(\d+|[一二三四五六七八九十百]+)\s*[个首.]?(.*)$", msg
            ):
                output = []
                num = (
                    result[1] if isinstance(result[1], int) else cn2an.cn2an(result[1])
                )
                assert isinstance(num, int)
                content = result[2]
                if num > PluginConfig.get("LetterNum"):
                    await send.sendWithAt(
                        matcher, f"没有第${num}个啦！看清楚再回答啊喂！￣へ￣"
                    )
                    return
                songs = (
                    await getdata.fuzzysongsnick(content, 0.95)
                    if isfuzzymatch
                    else await getdata.songsnick(content)
                )
                standard_song = gamelist[group_id].get(num)
                if songs:
                    for song in songs:
                        if standard_song and standard_song == song:
                            # 已经猜完移除掉的曲目不能再猜
                            if not blurlist[group_id].get(num):
                                await send.sendWithAt(
                                    matcher,
                                    f"曲目[{standard_song}]已经猜过了，要不咱们换一个吧uwu",
                                )
                                return
                            del blurlist[group_id][num]
                            await send.sendWithAt(
                                matcher,
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
                                                matcher,
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
                                                matcher, await pic.getIll(standard_song)
                                            )
                                        case _:
                                            pass
                            # 记录猜对者
                            winnerlist[group_id][num] = sender
                            isEmpty = not blurlist[group_id]
                            """是否全部猜完"""
                            if not isEmpty:
                                output.extend(["开字母进行中：", opened])
                                for i in gamelist[group_id].keys():
                                    if v := blurlist[group_id].get(i):
                                        output.append(f"\n【{i}】{v}")
                                    else:
                                        output.append(
                                            f"\n【{i}】{gamelist[group_id][i]}"
                                        )
                                        if w := winnerlist[group_id].get(i):
                                            output.append(f" @{w}")
                                await send.sendWithAt(matcher, output, True)
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
                                await send.sendWithAt(matcher, output)
                            return
                    if len(songs) > 1:
                        await send.sendWithAt(
                            matcher,
                            f"第{num}首不是[{content}]www，要不再想想捏？如果实在不会可以"
                            f"悄悄发个[{cmdhead} tip]哦≧ ﹏ ≦",
                            True,
                        )
                    else:
                        await send.sendWithAt(
                            matcher,
                            f"第{num}首不是[{songs[0]}]www，要不再想想捏？如果实在不会可以"
                            f"悄悄发个[{cmdhead} tip]哦≧ ﹏ ≦",
                            True,
                        )
                    return
                await send.sendWithAt(
                    matcher, f"没有找到[{content}]的曲目信息呐QAQ", True
                )
                return
            # 格式匹配错误放过命令
            return
        # 未进行游戏放过命令
        return


# export default new class guessLetter {


#     /** 答案 **/
#     async ans(e, gameList) {
#         const { group_id } = e//使用对象解构提取group_id

#         if (gamelist[group_id]) {
#             await e.reply('好吧好吧，既然你执着要放弃，那就公布答案好啦。', true)

#             e.reply(gameover(group_id, gameList))
#             return true
#         }

#         e.reply(`现在还没有进行的开字母捏，赶快输入'/${Config.getUserCfg('config', 'cmdhead')} letter'开始新的一局吧！`, true)
#         return false
#     }

#     /** 提示 **/
#     async getTip(e, gameList) {
#         const { group_id } = e
#         timeCount[group_id].newTime = Date.now() + (1000 * Config.getUserCfg('config', 'LetterTimeLength'))

#         if (!gamelist[group_id]) {
#             e.reply(`现在还没有进行的开字母捏，赶快输入'/${Config.getUserCfg('config', 'cmdhead')} letter'开始新的一局吧！`, true)
#             return false
#         }

#         const time = Config.getUserCfg('config', 'LetterTipCd')
#         const currentTime = Date.now()
#         const timetik = currentTime - lastTipTime[group_id]
#         const timeleft = Math.floor((1000 * time - timetik) / 1000)

#         if (timetik < 1000 * time) {
#             e.reply(`使用提示的全局冷却时间还有${timeleft}s呐，还请先耐心等下哇QAQ`, true)
#             return false
#         }

#         lastTipTime[group_id] = currentTime

#         const commonKeys = Object.keys(gamelist[group_id]).filter(key => key in blurlist[group_id])

#         let randsymbol
#         while (typeof randsymbol === 'undefined' || randsymbol === '*') {
#             const key = commonKeys[randint(0, commonKeys.length - 1)]
#             const songname = gamelist[group_id][key]
#             randsymbol = getRandCharacter(songname, blurlist[group_id][key])
#         }

#         const output = []

#         for (const key of Object.keys(gamelist[group_id])) {
#             const songname = gamelist[group_id][key]
#             let blurname = blurlist[group_id][key]

#             if (!blurname) {
#                 continue
#             }

#             let newBlurname = ''
#             for (let i = 0; i < songname.length; i++) {
#                 if (/^[\u4E00-\u9FFF]$/.test(songname[i]) && pinyin(songname[i], { pattern: 'first', toneType: 'none', type: 'string' }) == randsymbol.toLowerCase()) {
#                     newBlurname += songname[i]
#                     continue
#                 }

#                 if (songname[i].toLowerCase() == randsymbol.toLowerCase()) {
#                     newBlurname += songname[i]
#                 } else {
#                     newBlurname += blurname[i]
#                 }
#             }

#             blurlist[group_id][key] = newBlurname
#             if (!newBlurname.includes('*')) {
#                 delete blurlist[group_id][key]
#             }
#         }

#         alphalist[group_id] = alphalist[group_id] || {}

#         const reg = /^[A-Za-z]+$/g
#         if (reg.test(randsymbol)) {
#             alphalist[group_id] += randsymbol.toUpperCase() + ' '
#         } else {
#             alphalist[group_id] += randsymbol + ' '
#         }

#         output.push(`已经帮你随机翻开一个字符[ ${randsymbol} ]了捏 ♪（＾∀＾●）ﾉ\n`)

#         const opened = '当前所有翻开的字符[ ' + alphalist[group_id].replace(/\[object Object\]/g, '') + ']'

#         output.push(opened)

#         const isEmpty = Object.getOwnPropertyNames(blurlist[group_id]).length === 0
#         if (!isEmpty) {
#             for (const key of Object.keys(gamelist[group_id])) {
#                 if (blurlist[group_id][key]) {
#                     output.push(`\n【${key}】${blurlist[group_id][key]}`)
#                 } else {
#                     output.push(`\n【${key}】${gamelist[group_id][key]}`)
#                     if (winnerlist[group_id][key]) {
#                         output.push(` @${winnerlist[group_id][key]}`)
#                     }
#                 }
#             }
#         } else {
#             delete (alphalist[group_id])
#             delete (blurlist[group_id])
#             output.push('\n字母已被全部翻开，答案如下：')
#             for (let key in gamelist[group_id]) {
#                 output.push(`\n【${key}】${gamelist[group_id][key]}`)
#                 if (winnerlist[group_id][key]) {
#                     output.push(` @${winnerlist[group_id][key]}`)
#                 }
#             }
#             delete gameList[group_id]
#             delete (winnerlist[group_id])
#         }

#         e.reply(output, true)
#         return true
#     }

#     /** 洗牌 **/
#     async mix(e) {
#         const { group_id } = e

#         if (gamelist[group_id]) {
#             await e.reply(`当前有正在进行的游戏，请等待游戏结束再执行该指令`, true)
#             return false
#         }

#         // 曲目初始洗牌
#         shuffleArray(songsname)

#         songweights[group_id] = songweights[group_id] || {}

#         // 将权重归1
#         songsname.forEach(song => {
#             songweights[group_id][song] = 1
#         })

#         await e.reply(`洗牌成功了www`, true)
#         return true
#     }

#     // 检查字母是否包含在曲目中
#     checkLetterInSongs(group_id, letter) {

#         for (const i of Object.keys(gamelist[group_id])) {
#             const songname = gamelist[group_id][i]
#             const blurname = blurlist[group_id][i]
#             const characters = (songname.match(/[\u4e00-\u9fa5]/g) || []).join("")
#             const letters = pinyin(characters, { pattern: 'first', toneType: 'none', type: 'string' })

#             if (!(songname.toLowerCase().includes(letter.toLowerCase())) && !letters.includes(letter.toLowerCase())) {
#                 continue
#             }

#             if (!(blurname)) {
#                 continue
#             }

#             let newBlurname = ''
#             for (let ii = 0; ii < songname.length; ii++) {
#                 if (/^[\u4E00-\u9FFF]$/.test(songname[ii])) {
#                     if (pinyin(songname[ii], { pattern: 'first', toneType: 'none', type: 'string' }) === letter.toLowerCase()) {
#                         newBlurname += songname[ii]
#                         continue
#                     }
#                 }

#                 if (songname[ii].toLowerCase() === letter.toLowerCase()) {
#                     newBlurname += songname[ii]
#                 } else {
#                     newBlurname += blurname[ii]
#                 }
#             }
#             blurlist[group_id][i] = newBlurname
#             if (!newBlurname.includes('*')) {
#                 delete blurlist[group_id][i]
#             }
#         }

#         return Object.keys(blurlist[group_id]).length > 0
#     }

# }()

# /**
#  * RandBetween
#  * @param {number} top 随机值上界
#  */
# function randbt(top, bottom = 0) {
#     return Number((Math.random() * (top - bottom)).toFixed(0)) + bottom
# }

# //定义生成指定区间整数随机数的函数
# function randint(min, max) {
#     const range = max - min + 1
#     const randomOffset = Math.floor(Math.random() * range)
#     return (randomOffset + min) % range + min
# }

# //定义生成指定区间带有指定小数位数随机数的函数
# function randfloat(min, max, precision = 0) {
#     let range = max - min
#     let randomOffset = Math.random() * range
#     let randomNumber = randomOffset + min + range * 10 ** -precision

#     return precision === 0 ? Math.floor(randomNumber) : randomNumber.toFixed(precision)
# }


# //将中文数字转为阿拉伯数字
# function NumberToArabic(digit) {
#     //只处理到千，再高也根本用不上的www(十位数都用不上的说)
#     const numberMap = { 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9 }
#     const unitMap = { 十: 10, 百: 100, 千: 1000 }

#     const total = digit.split('').reduce((acc, character) => {
#         const { [character]: numberValue } = numberMap
#         const { [character]: unitValue } = unitMap

#         if (numberValue !== undefined) {
#             acc.currentUnit = numberValue
#         } else if (unitValue !== undefined) {
#             acc.currentUnit *= unitValue
#             acc.total += acc.currentUnit
#             acc.currentUnit = 0
#         }

#         return acc
#     }, { total: 0, currentUnit: 1 })

#     return total.total + total.currentUnit
# }

# //随机取字符
# function getRandCharacter(str, blur) {
#     // 寻找未打开的位置
#     const temlist = [] // 存放*的下标
#     for (let i = 0; i < blur.length; i++) {
#         if (blur[i] === '*') {
#             temlist.push(i)
#         }
#     }

#     // 生成随机索引
#     const randomIndex = randint(0, temlist.length - 1)

#     // 返回随机字符
#     return str.charAt(temlist[randomIndex]);
# }
