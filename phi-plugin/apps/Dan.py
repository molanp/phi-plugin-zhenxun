"""
phigros屁股肉段位
"""

from nonebot_plugin_alconna import Alconna, Args, Image, Match, on_alconna
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger

from ..config import cmdhead, recmdhead
from ..model.getdata import getdata
from ..model.getSave import getSave
from ..model.send import send
from ..model.Vika import Vika
from ..utils import can_be_call, to_dict

read = "https://www.bilibili.com/read/cv27354116"
sheet = "https://f.kdocs.cn/g/fxsg4EM2/"
word = getdata.getimg("dan_code")
cancanneed = bool(Vika.PhigrosDan)

if not cancanneed:
    logger.info("未填写 Vika Token ，将禁用段位认证。", "phi-plugin:Dan")


async def is_enable() -> bool:
    return cancanneed


danupdate = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(Dan|dan)\s*update"),
    block=True,
    priority=5,
    rule=is_enable & can_be_call("danupdate"),
)

dan = on_alconna(
    Alconna(rf"re:{recmdhead}\s*(Dan|dan)", Args["name?", str]),
    block=True,
    priority=5,
    rule=is_enable & can_be_call("dan"),
)


@dan.handle()
async def _(session: Uninfo, name: Match[str]):
    _name = name.result if name.available else None
    if not _name:
        dan = await getSave.getDan(session.user.id, True)
        if dan:
            resmsg: list = ["你的认证段位为"]
            for i in dan:
                resmsg.extend(
                    (
                        f"\n{i['Dan'].replace('/', ' ')} {'EX' if i.get('EX') else ''}",
                        Image(
                            url=i["img"]
                        ),  # BUG: 这里不知道vika表内此字段具体的图片资源是用什么表示的
                    )
                )
            await send.sendWithAt(resmsg, True)
        else:
            await send.sendWithAt(
                [
                    "唔，本地没有你的认证记录哦！如果提交过审核的话，可以试试更新一下嗷！"
                    f"\n格式：{cmdhead} dan update",
                    word,
                ],
                True,
            )
    else:
        try:
            dan = await Vika.GetUserDanByName(_name)
            if not dan:
                await send.sendWithAt(
                    [
                        f"唔，暂时没有在审核通过列表里找到{name}哦！如果提交过审核的话，请耐心等待审核通过哦！",
                        word,
                    ]
                )
                return
            resmsg: list = [f"{_name}的认证段位为"]
            for i in dan:
                resmsg.extend(
                    (
                        f"\n{i['Dan'].replace('/', ' ')} {'EX' if i.get('EX') else ''}",
                        Image(
                            url=i["img"]
                        ),  # BUG: 这里不知道vika表内此字段具体的图片资源是用什么表示的
                    )
                )
            await send.sendWithAt(resmsg, True)
        except Exception as err:
            logger.error("Dan查询出错", "phi-plugin:Dan", e=err)
            await send.sendWithAt("当前服务忙，请稍后重试QAQ！", True)


@danupdate.handle()
async def _(session: Uninfo):
    # 检查是否绑定并提示
    save = await send.getsaveResult(session)
    if not save:
        return
    try:
        dan = await Vika.GetUserDanBySstk(save.sessionToken)
    except Exception as err:
        logger.error("Dan更新出错", "phi-plugin:DanUpdate", e=err)
        await send.sendWithAt("当前服务忙，请稍后重试QAQ！", True)
        return
    if not dan:
        await send.sendWithAt(
            [
                "唔，暂时没有在审核通过列表里找到你哦！如果提交过审核的话，请耐心等待审核通过哦！",
                word,
            ],
            True,
        )
        return
    history = await getSave.getHistory(session.user.id)
    history.dan = dan
    await getSave.putHistory(session.user.id, to_dict(history))
    resmsg: list = ["更新成功！你的认证段位为\n"]
    for i in dan:
        resmsg.extend(
            (
                f"\n{i['Dan'].replace('/', ' ')} {'EX' if i.get('EX') else ''}",
                Image(
                    url=i["img"]
                ),  # BUG: 这里不知道vika表内此字段具体的图片资源是用什么表示的
            )
        )
    await send.sendWithAt(resmsg, True)
