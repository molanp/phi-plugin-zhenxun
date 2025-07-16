from typing import Any

from nonebot.matcher import current_bot
from nonebot_plugin_alconna import Image, Text, UniMessage
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils
from zhenxun.utils.withdraw_manage import WithdrawManager

from ..config import PluginConfig
from ..utils import to_dict
from .cls.common import Save
from .getSave import getSave
from .getUpdateSave import getUpdateSave


class send:
    @classmethod
    async def sendWithAt(
        cls, matcher, msg: Any, quote=True, recallTime=0
    ):
        """
        :param e: 响应器对象
        :param msg: UniMessage支持的消息内容
        :param quote: 是否引用回复
        """
        recepit = await matcher.send(UniMessage(msg), at_sender=True, reply_to=quote) # type: ignore
        if recallTime > 0:  # 删除消息
            WithdrawManager.append(
                current_bot.get(),
                recepit.msg_ids[0]["message_id"],
                recallTime,
            )
        return recepit

    @classmethod
    async def getsaveResult(
        cls, matcher, session: Uninfo, ver: int | None = None, send=True
    ) -> None | Save:
        """
        检查存档部分

        :param matcher: 响应器对象
        :param ver int: 存档版本
        :param send bool: 是否发送提示
        :return: bool 是否成功
        """

        if PluginConfig.get("openPhiPluginApi"):
            try:
                user_save = await getUpdateSave.getNewSaveFromApi(session)
                return await Save().constructor(user_save["save"])
            except Exception as err:
                if str(err) == "Phigros token is required":
                    try:
                        sessionToken = await getSave.get_user_token(session.user.id)
                        if not sessionToken:
                            if send:
                                await cls.sendWithAt(
                                    matcher,
                                    "请先绑定sessionToken哦！\n"
                                    "如果不知道自己的sessionToken可以尝试扫码绑定嗷！\n"
                                    f"获取二维码：{PluginConfig.get('cmdhead')}"
                                    " bind qrcode\n"
                                    f"帮助：{PluginConfig.get('cmdhead')} tk help\n"
                                    f"格式：{PluginConfig.get('cmdhead')} bind"
                                    " <sessionToken>",
                                )
                            return None
                        user_save = await getUpdateSave.getNewSaveFromApi(
                            session, sessionToken
                        )
                        return await Save().constructor(user_save["save"])
                    except Exception as err:
                        logger.warning("[phi-plugin] API ERR", e=err)

        sessionToken = await getSave.get_user_token(session.user.id)

        if not sessionToken:
            if send:
                await cls.sendWithAt(
                    matcher,
                    "请先绑定sessionToken哦！\n"
                    "如果不知道自己的sessionToken可以尝试扫码绑定嗷！\n"
                    f"获取二维码：{PluginConfig.get('cmdhead')} bind qrcode\n"
                    f"帮助：{PluginConfig.get('cmdhead')} tk help\n"
                    f"格式：{PluginConfig.get('cmdhead')} bind <sessionToken>",
                )
            return None

        user_save = (
            await getUpdateSave.getNewSaveFromLocal(matcher, session, sessionToken)
        )["save"]

        if not user_save or (
            ver and (not user_save.Recordver or user_save.Recordver < ver)
        ):
            if send:
                await cls.sendWithAt(
                    matcher,
                    f"请先更新数据哦！\n格式：{PluginConfig.get('cmdhead')} update",
                )
            return None

        return await Save().constructor(to_dict(user_save))

    @classmethod
    async def pickSend(cls, matcher, msg: list[Text | Image]):
        """
        转发到私聊

        :param session: 会话对象
        :param list[Text | Image] | Text msg: 消息内容
        """
        try:
            await matcher.send(
                MessageUtils.alc_forward_msg(
                    msg,
                    "80000000",
                    "匿名消息",
                )
            )
        except Exception as err:
            logger.error("消息转发失败", "phi-plugin", e=err)
            await cls.sendWithAt(matcher, "转发失败QAQ！请尝试在私聊触发命令！")
