from .class.Save import getSave
from .getSave import getSave

from nonebot import get_bot
from nonebot_plugin_alconna import Image, Text, UniMessage
from nonebot_plugin_uninfo import Uninfo

from zhenxun.services.log import logger
from zhenxun.utils.message import MessageUtils
from zhenxun.utils.platform import PlatformUtils

from ..config import PluginConfig


class send:
    @classmethod
    async def send_with_At(cls, msg: list[Text | Image] | Text | str, quote=True):
        """
        私聊省略@

        :param list[Text | Image] | Text msg: 消息内容
        :param bool quote: 是否引用回复
        """
        if isinstance(msg, str):
            msg = [Text(msg)]
        await UniMessage(msg).send(at_sender=True, reply=quote)

    @classmethod
    async def getsave_result(cls, session: Uninfo, ver) -> bool | Save:
        """
        检查存档部分

        :param session: 会话对象
        :param ver: 存档版本
        :return: bool 是否成功
        * v1.0,取消对当次更新内容的存储，取消对task的记录，更正scoreHistory
        * v1.1,更正scoreHistory
        * v1.2,由于曲名错误，删除所有记录，曲名使用id记录
        """
        sessionToken = await getSave.get_user_token(session.user.id)

        user_save = await getSave.getSave(session.user.id)

        if not sessionToken:
            await cls.send_with_At(
                "请先绑定sessionToken哦！\n"
                "如果不知道自己的sessionToken可以尝试扫码绑定嗷！\n"
                f"获取二维码：{PluginConfig.get('cmdhead')} bind qrcode\n"
                f"帮助：{PluginConfig.get('cmdhead')} tk help\n"
                f"格式：{PluginConfig.get('cmdhead')} bind <sessionToken>"
            )
            return False

        if not user_save or (
            ver and (not user_save.Recordver or user_save.Recordver < ver)
        ):
            await cls.send_with_At(
                f"请先更新数据哦！\n格式：{PluginConfig.get('cmdhead')} update"
            )
            return False

        return user_save

    @classmethod
    async def pick_send(cls, session: Uninfo, msg: list[Text | Image]):
        """
        转发到私聊

        :param session: 会话对象
        :param list[Text | Image] | Text msg: 消息内容
        """
        user = await PlatformUtils.get_user(get_bot(session.self_id), session.user.id)
        try:
            await cls.send_with_At(
                MessageUtils.alc_forward_msg(
                    msg,
                    session.self_id,
                    user.name if user else session.user.id,
                )
            )
        except Exception as e:
            logger.error("消息转发失败", "phi-plugin", e=e)
            await cls.send_with_At("转发失败QAQ！请尝试在私聊触发命令！")

