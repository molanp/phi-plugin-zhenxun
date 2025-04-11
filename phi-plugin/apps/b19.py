ChallengeModeName = ["白", "绿", "蓝", "红", "金", "彩"]
# 存档的难度映射
Level = ["EZ", "HD", "IN", "AT", None]

chap = {
    "S": "单曲精选集",
    "单曲": "单曲精选集",
    "单曲精选集": "单曲精选集",
    "C0": "Chapter Legacy 过去的章节",
    "旧章": "Chapter Legacy 过去的章节",
    "LEGACY": "Chapter Legacy 过去的章节",
    "C5": "Chapter 5 霓虹灯牌",
    "霓虹灯牌": "Chapter 5 霓虹灯牌",
    "C6": "Chapter 6 方舟蜃景",
    "方舟蜃景": "Chapter 6 方舟蜃景",
    "C7": "Chapter 7 时钟链接",
    "时钟链接": "Chapter 7 时钟链接",
    "C8": "Chapter 8 凌日潮汐",
    "凌日潮汐": "Chapter 8 凌日潮汐",
    "S1": "Side Story 1 忘忧宫",
    "忘忧宫": "Side Story 1 忘忧宫",
    "S2": "Side Story 2 弭刻日",
    "弭刻日": "Side Story 2 弭刻日",
    "S3": "Side Story 3 盗乐行",
    "盗乐行": "Side Story 3 盗乐行",
    "S4": "Side Story 4 无相乡",
    "无相乡": "Side Story 4 无相乡",
    "EXS": "Extra Story Chapter 极星卫",
    "极星卫": "Extra Story Chapter 极星卫",
    "黑皇帝": "Chapter EX-Rising Sun Traxx 精选集",
    "HYUN": "Chapter EX-HyuN 精选集",
    "GOOD": "Chapter EX-GOOD 精选集",
    "WAVEAT": "Chapter EX-WAVEAT 精选集",
    "喵斯": "Chapter EX-Muse Dash 精选集",
    "MUSE": "Chapter EX-Muse Dash 精选集",
    "KALPA": "Chapter EX-KALPA 精选集",
    "LANOTA": "Chapter EX-Lanota 精选集",
    "盘子": "Chapter EX-Lanota 精选集",
    "江米条": "Chapter EX-姜米條 精选集",
    "姜米條": "Chapter EX-姜米條 精选集",
    "茶鸣": "Chapter EX-茶鸣拾贰律 精选集",
    "茶鸣拾贰律": "Chapter EX-茶鸣拾贰律 精选集",
    "茶鸣十二律": "Chapter EX-茶鸣拾贰律 精选集",
    "OVERRAPID": "Chapter EX-OverRapid 精选集",
    "OR": "Chapter EX-OverRapid 精选集",
    "ROTAENO": "Chapter EX-Rotaeno 精选集",
    "方向盘": "Chapter EX-Rotaeno 精选集",
    "CHUNITHM": "Chapter EX-CHUNITHM 精选集",
    "中二": "Chapter EX-CHUNITHM 精选集",
    "范式": "Chapter EX-Paradigm：Reboot 精选集",
    "SHINOBI": "Chapter EX-SHINOBI SLASH 精选集",
    "千恋万花": "Chapter EX-SHINOBI SLASH 精选集",
    "TAKUMI": "Chapter EX-TAKUMI³精选集",
    "塔库米": "Chapter EX-TAKUMI³精选集",
    "三次方": "Chapter EX-TAKUMI³精选集",
    "节奏大师": "Chapter EX-节奏大师精选集",
    "齐秦太帅": "Chapter EX-节奏大师精选集",
    "JZDS": "Chapter EX-节奏大师精选集",
    "EGTS": "Chapter EX-EGTS 精选集",
}

from typing import Any
from nonebot_plugin_alconna import (
    Alconna,
    Arparma,
    Args,
    CommandMeta,
    Text,
    Field,
    At,
    UniMessage,
    UniMsg,
    on_alconna,
)
from nonebot_plugin_uninfo import Uninfo

b19 = on_alconna(
    Alconna(
        "re:(?i)phi\s*(b\d+|pgr|rks)",
        Args["nnum?", int, 33]
    ),
    priority=5,
    block=True,
)

# @b19.handle()
# async def _b19(session: Uninfo, nnum: int):
    
