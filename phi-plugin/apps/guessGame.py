"""
phi-plugin 猜曲游戏
"""

from nonebot import on_message
from nonebot.internal.rule import Rule
from nonebot_plugin_alconna import Alconna, Args, CommandMeta, Match, UniMsg, on_alconna
from nonebot_plugin_uninfo import Uninfo

from zhenxun.utils.rules import ensure_group

from ..config import cmdhead, recmdhead
from ..model.getBanGroup import getBanGroup
from ..model.send import send
from .guessGame.guessIll import guessIll
from .guessGame.guessLetter import guessLetter
from .guessGame.guessTips import guessTips

games = ["提示猜曲", "tipgame", "ltr", "letter", "开字母", "guess", "猜曲绘"]
gameList = {}


def is_started() -> Rule:
    """
    是否开始游戏

    返回:
        Rule: Rule
    """

    async def _rule(session: Uninfo) -> bool:
        return session.scene.id in gameList

    return Rule(_rule)


start = on_alconna(
    Alconna(
        rf"re:{recmdhead}",
        Args["gameType", games]["songname?", str, None],
        meta=CommandMeta(compact=True),
    ),
    priority=5,
    block=True,
)
guess = on_message(
    rule=is_started(),
    priority=5,
    block=True,
)
reveal = on_alconna(
    Alconna(
        r"re:(出|开|翻|揭|看|翻开|打开|揭开|open)",
        Args["content", r"re:[a-zA-Z\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\d\S]"],
        meta=CommandMeta(compact=True),
    ),
    rule=is_started(),
    priority=5,
    block=True,
)
getTip = on_alconna(
    Alconna(rf"re:{cmdhead}\s*(tip|提示)"), rule=is_started(), priority=5, block=True
)
ans = on_alconna(Alconna(rf"re:{cmdhead}\s*(ans|答案|结束)"), priority=5, block=True)


@start.handle()
async def _(session: Uninfo, gameType: Match[str], songname: Match[str]):
    if not ensure_group(session):
        await send.sendWithAt("请在群聊中使用这个功能嗷！")
        return
    if session.scene.id in gameList:
        await send.sendWithAt(
            "当前存在其他未结束的游戏嗷！"
            f"如果想要开启新游戏请 {cmdhead} ans 结束进行的游戏嗷！",
        )
        return
    _gameType = gameType.result if gameType.available else ""
    song = songname.result if songname.available else None
    match _gameType:
        case "tipgame" | "提示猜曲":
            if await getBanGroup.get(session, "tipgame"):
                await send.sendWithAt("这里被管理员禁止使用这个功能了呐QAQ！")
                return
            return await guessTips.start(session, gameList)
        case "letter" | "ltr" | "开字母":
            if await getBanGroup.get(session, "ltrgame"):
                await send.sendWithAt("这里被管理员禁止使用这个功能了呐QAQ！")
                return
            return await guessLetter.start(session, song, gameList)
        case "guess" | "猜曲绘":
            if await getBanGroup.get(session, "guessgame"):
                await send.sendWithAt("这里被管理员禁止使用这个功能了呐QAQ！")
                return
            return await guessIll.start(session, gameList)
        case _:
            pass


@reveal.handle()
async def _(session: Uninfo, content: Match[str | int]):
    match gameList[session.scene.id]["gameType"]:
        case "guessLetter":
            msg = str(content.result) if content.available else ""
            return await guessLetter.reveal(session, msg, gameList)
        case _:
            pass


@guess.handle()
async def _(session: Uninfo, msg: UniMsg):
    _msg = msg.extract_plain_text().strip()
    match gameList[session.scene.id]["gameType"]:
        case "guessTips":
            return await guessTips.guess(session, _msg, gameList)
        case "guessLetter":
            return await guessLetter.guess(session, _msg, gameList)
        case "guessIll":
            return await guessIll.guess(session, _msg, gameList)
        case _:
            pass


@getTip.handle()
async def _(session: Uninfo):
    match gameList[session.scene.id]["gameType"]:
        case "guessTips":
            return await guessTips.getTip(session, gameList)
        case "guessLetter":
            return await guessLetter.getTip(session, gameList)
        case _:
            pass


@ans.handle()
async def _(session: Uninfo):
    match gameList[session.scene.id]["gameType"]:
        case "guessTips":
            return await guessTips.ans(session, gameList)
        case "guessLetter":
            return await guessLetter.ans(session, gameList)
        case "guessIll":
            return await guessIll.ans(session, gameList)
        case _:
            await send.sendWithAt("当前没有进行中的游戏嗷！")
