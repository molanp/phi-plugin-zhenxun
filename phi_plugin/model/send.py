from typing import Any

from nonebot.internal.matcher import Matcher
from nonebot_plugin_alconna import Image, Text, UniMessage
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils

from ..config import PluginConfig
from .cls.Save import Save
from .getSave import getSave
from .getUpdateSave import getUpdateSave


class send:
    @classmethod
    async def send_with_At(
        cls, e: Matcher, msg: Any, quote=True
    ):
        """
        :param e: 响应器对象
        :param msg: 消息内容
        :param quote: 是否引用回复
        """
        await e.send(UniMessage(msg), at_sender=True, reply_to=quote)  # type: ignore

    @classmethod
    async def getsave_result(
        cls, e: Matcher, session: Uninfo, ver, send=True
    ) -> bool | Save:
        """
        检查存档部分

        :param session: 会话对象
        :param ver int: 存档版本
        :param send bool: 是否发送提示
        :return: bool 是否成功
        """
        user_save = None

        if PluginConfig.get("openPhiPluginApi"):
            try:
                user_save = await getUpdateSave.getNewSaveFromApi(session)
                return user_save["save"]
            except Exception as err:
                if str(err) == "Phigros token is required":
                    try:
                        sessionToken = await getSave.get_user_token(session.user.id)
                        if not sessionToken:
                            if send:
                                await cls.send_with_At(
                                    e,
                                    "请先绑定sessionToken哦！\n"
                                    "如果不知道自己的sessionToken可以尝试扫码绑定嗷！\n"
                                    f"获取二维码：{PluginConfig.get('cmdhead')}"
                                    " bind qrcode\n"
                                    f"帮助：{PluginConfig.get('cmdhead')} tk help\n"
                                    f"格式：{PluginConfig.get('cmdhead')} bind"
                                    " <sessionToken>",
                                )
                            return False
                        user_save = await getUpdateSave.getNewSaveFromApi(
                            session, sessionToken
                        )
                        return user_save["save"]
                    except Exception as err:
                        logger.warning("[phi-plugin] API ERR", e=err)

        sessionToken = await getSave.get_user_token(session.user.id)

        if not sessionToken:
            if send:
                await cls.send_with_At(
                    e,
                    "请先绑定sessionToken哦！\n"
                    "如果不知道自己的sessionToken可以尝试扫码绑定嗷！\n"
                    f"获取二维码：{PluginConfig.get('cmdhead')} bind qrcode\n"
                    f"帮助：{PluginConfig.get('cmdhead')} tk help\n"
                    f"格式：{PluginConfig.get('cmdhead')} bind <sessionToken>",
                )
            return False

        user_save = (await getUpdateSave.getNewSaveFromLocal(e, session, sessionToken))[
            "save"
        ]

        if not user_save or (
            ver and (not user_save.Recordver or user_save.Recordver < ver)
        ):
            if send:
                await cls.send_with_At(
                    e, f"请先更新数据哦！\n格式：{PluginConfig.get('cmdhead')} update"
                )
            return False

        return user_save

    @classmethod
    async def pick_send(cls, e: Matcher, msg: list[Text | Image]):
        """
        转发到私聊

        :param session: 会话对象
        :param list[Text | Image] | Text msg: 消息内容
        """
        try:
            await e.send(
                MessageUtils.alc_forward_msg(
                    msg,
                    "80000000",
                    "匿名消息",
                )  # type: ignore
            )
        except Exception as err:
            logger.error("消息转发失败", "phi-plugin", e=err)
            await cls.send_with_At(e, "转发失败QAQ！请尝试在私聊触发命令！")
