"""
phigros趣味功能
"""

from datetime import datetime
from functools import lru_cache
import math
import random

from nonebot_plugin_alconna import Alconna, on_alconna
from nonebot_plugin_uninfo import Uninfo

from ..config import recmdhead
from ..model.fCompute import fCompute
from ..model.getFile import FileManager
from ..model.getInfo import getInfo
from ..model.path import infoPath
from ..model.picmodle import picmodle
from ..model.send import send
from ..models import jrrpModel
from ..rule import can_be_call

sentence = []

jrrp = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(jrrp|今日人品)"),
    rule=can_be_call("jrrp"),
    priority=5,
    block=True,
)


@lru_cache(maxsize=1)
def get_sentences():
    import asyncio

    return asyncio.run(FileManager.ReadFile(infoPath / "sentences.json"))


@jrrp.handle()
async def _(session: Uninfo):
    jrrp_data: list = await jrrpModel.get_jrrp(session.user.id)
    sentence = get_sentences()
    if not jrrp_data:
        lucky = round(easeOutCubic(random.random() * 100))
        idx = math.floor(random.random() * len(sentence))
        good = getInfo.word["good"][:]
        bad = getInfo.word["bad"][:]
        common = getInfo.word["common"][:]
        good_list = random.sample(good + common, 4)
        for g in good_list:
            if g in good:
                good.remove(g)
            else:
                common.remove(g)
        bad_list = random.sample(bad + common, 4)
        jrrp_data = [lucky, idx, *good_list, *bad_list]
        await jrrpModel.set_jrrp(session.user.id, jrrp_data)
    if jrrp_data[0] == 100:
        luck_rank = 5
    elif jrrp_data[0] >= 80:
        luck_rank = 4
    elif jrrp_data[0] >= 60:
        luck_rank = 3
    elif jrrp_data[0] >= 40:
        luck_rank = 2
    elif jrrp_data[0] >= 20:
        luck_rank = 1
    else:
        luck_rank = 0
    await send.sendWithAt(
        await picmodle.common(
            "jrrp",
            {
                "bkg": getInfo.getill("Shine After"),
                "lucky": jrrp_data[0],
                "luckRank": luck_rank,
                "year": datetime.now().year,
                "month": fCompute.ped(datetime.now().month, 2),
                "day": fCompute.ped(datetime.now().day, 2),
                "sentence": sentence[jrrp_data[1]],
                "good": jrrp_data[2:6],
                "bad": jrrp_data[6:10],
            },
        ),
        True,
    )


def easeOutCubic(x: float):
    return 1 - pow(1 - x, 3)
