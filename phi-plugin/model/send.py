from typing import Any

from nonebot.matcher import current_bot
from nonebot_plugin_alconna import UniMessage
from nonebot_plugin_uninfo import Uninfo

from zhenxun.utils.withdraw_manage import WithdrawManager

from ..config import cmdhead
from ..utils import to_dict


class send:
    @classmethod
    async def sendWithAt(cls, msg: Any, quote=False, recallTime=0):
        """
        :param msg: UniMessage支持的消息内容
        :param quote: 是否引用回复
        :param recallTime: 撤回时间，0为不撤回 单位，秒
        """
        recepit = await UniMessage(msg).send(at_sender=True, reply_to=quote)
        if recallTime > 0:
            WithdrawManager.append(
                current_bot.get(),
                recepit.msg_ids[0]["message_id"],
                recallTime,
            )
        return recepit

    @classmethod
    async def getsaveResult(cls, session: Uninfo, ver: float | None = None, send=True):
        """
        检查存档部分

        :param ver int: 存档版本
        :param send bool: 是否发送提示
        :return: None | Save
        """
        from .cls.common import Save
        from .getSave import getSave
        from .getUpdateSave import getUpdateSave

        sessionToken = await getSave.get_user_token(session.user.id)

        if not sessionToken:
            if send:
                await cls.sendWithAt(
                    "请先绑定sessionToken哦！\n"
                    "如果不知道自己的sessionToken可以尝试扫码绑定嗷！\n"
                    f"获取二维码：{cmdhead} bind qrcode\n"
                    f"帮助：{cmdhead} tk help\n"
                    f"格式：{cmdhead} bind <sessionToken>",
                )
            return None

        user_save = (await getUpdateSave.getNewSaveFromLocal(session, sessionToken))[
            "save"
        ]

        if not user_save or (
            ver and (not user_save.Recordver or user_save.Recordver < ver)
        ):
            if send:
                await cls.sendWithAt(
                    f"请先更新数据哦！\n格式：{cmdhead} update",
                )
            return None

        return Save(**to_dict(user_save))
