"""
phigros趣味功能
"""

from datetime import datetime
import math
import random

from nonebot_plugin_alconna import Alconna, on_alconna
from nonebot_plugin_uninfo import Uninfo

from ..config import recmdhead
from ..model.fCompute import fCompute
from ..model.getFile import readFile
from ..model.getInfo import getInfo
from ..model.path import infoPath
from ..model.picmodle import picmodle
from ..model.send import send
from ..models import jrrpModel
from ..utils import can_be_call

jrrp = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(jrrp|今日人品)"),
    rule=can_be_call("jrrp"),
    priority=5,
    block=True,
)


@jrrp.handle()
async def _(session: Uninfo):
    jrrp_data: list = await jrrpModel.get_jrrp(session.user.id)
    sentence = await readFile.FileReader(infoPath / "sentences.json")
    if not jrrp_data:
        jrrp_data = [
            round(easeOutCubic(random.random() * 100)),
            math.floor(random.random() * len(sentence)),
        ]
        good = getInfo.word["good"]
        bad = getInfo.word["bad"]
        common = getInfo.word["common"]
        for _ in range(4):
            id_ = math.floor(random.random() * (len(good) + len(common)))
            if id_ < len(good):
                jrrp_data.append(good[id_])
                good.pop(id_)
            else:
                jrrp_data.append(common[id_ - len(good)])
                common.pop(id_ - len(good))
        for _ in range(4):
            id_ = math.floor(random.random() * (len(bad) + len(common)))
            if id_ < len(bad):
                jrrp_data.append(bad[id_])
                bad.pop(id_)
            else:
                jrrp_data.append(common[id_ - len(bad)])
                common.pop(id_ - len(bad))
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
                "bkg": await getInfo.getill("Shine After"),
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
