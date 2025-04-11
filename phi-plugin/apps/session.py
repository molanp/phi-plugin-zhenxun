import asyncio
from io import BytesIO
import re
import time

from nonebot_plugin_alconna import Alconna, Args, Image, UniMessage, on_alconna
from nonebot_plugin_uninfo import Uninfo
import qrcode

from zhenxun.plugins.zhenxun_plugin_phigros.phigros.model import PhigrosUserData
from zhenxun.services.log import logger

from ..lib.TapTap.LCHelper import LCHelper
from ..lib.TapTap.TapTapHelper import TapTapHelper

bind = on_alconna(
    Alconna(
        "re:(?i)phi\s*(绑定|bind)",
        Args["sessionToken?", str, None],
    ),
    priority=5,
    block=True,
)

update = on_alconna(
    Alconna(
        "re:(?i)phi\s*(更新|update)",
    ),
    priority=5,
    block=True,
)

unbind = on_alconna(
    Alconna(
        "re:(?i)phi\s*(解绑|unbind)",
    ),
    priority=5,
    block=True,
)

clean = on_alconna(
    Alconna(
        "re:(?i)phi\s*clean",
    ),
    priority=5,
    block=True,
)

getSstk = on_alconna(
    Alconna(
        "re:(?i)phi\s*sessionToken",
    ),
    priority=5,
    block=True,
)


@bind.handle()
async def _(session: Uninfo, sessionToken: str | None):
    """绑定sessionToken"""
    if sessionToken is None:
        await bind.send(
            "喂喂喂！你还没输入sessionToken呐！\n扫码绑定：phi bind <sessionToken>"
        )
    elif sessionToken == "qrcode":
        try:
            # 获取二维码请求
            request = await TapTapHelper.request_login_qr_code()
            qr_url = request["data"]["qrcode_url"]
            expires_in = request["data"]["expires_in"]

            # 生成二维码图片
            img = qrcode.make(qr_url)
            bio = BytesIO()
            img.save(bio)
            qr_image = Image(raw=bio.getvalue())

            # 发送二维码
            qr = await UniMessage(
                [
                    "请使用 TapTap 扫描二维码登录：",
                    qr_image,
                    f"二维码有效期：{expires_in // 60} 分钟",
                ]
            ).send(
                reply=True,
            )

            # 定期检查扫描状态
            start_time = time.time()
            while time.time() - start_time < expires_in:
                result = await TapTapHelper.check_qr_code_result(request)
                if result.get("success"):
                    # 获取 sessionToken
                    profile = await TapTapHelper.get_profile(result["data"])
                    session_token = await LCHelper.login_with_auth_data(
                        {**profile["data"], **result["data"]}
                    )

                    # 保存 sessionToken
                    await PhigrosUserData.set_session_token(
                        session.user.id, session_token
                    )
                    await bind.send("绑定成功！", reply=True)
                    return
                await asyncio.sleep(2)
            await qr.recall(index=0)
            await bind.send("二维码已过期，请重新绑定！", reply=True)

        except Exception as e:
            logger.error("绑定失败", session=session, e=e)
            await bind.send(f"绑定失败：{e!s}", reply=True)
    else:
        if len(sessionToken) != 25 or not re.match(r"^[a-zA-Z0-9]+$", sessionToken):
            await bind.send("无效的 sessionToken 格式！", reply=True)
            return
        try:
            # 保存 sessionToken
            await PhigrosUserData.set_session_token(session.user.id, sessionToken)
            await bind.send("绑定成功！", reply=True)
        except Exception as e:
            logger.error("绑定失败", session=session, e=e)
            await bind.send(f"绑定失败：{e!s}", reply=True)


@update.handle()
async def _(session: Uninfo):
    """更新存档"""
    session_token = await PhigrosUserData.get_session_token(session.user.id)
    if session_token is None:
        await update.send("未绑定 sessionToken，请先绑定！", reply=True)
        return

    try:
        user = PhigrosUser(session_token.decode())
        await build_profile(event, user)
        await send_with_at(event, "更新成功！")
    except Exception as e:
        logger.error(f"更新失败: {str(e)}")
        await send_with_at(event, f"更新失败：{str(e)}")


async def build_profile(event: Uninfo, user: PhigrosUser):
    """构建用户档案"""
    # 实现存档处理逻辑（需根据业务逻辑补充）
    pass


@unbind_cmd.handle()
async def handle_unbind(event: Uninfo, command: str):
    """解绑确认"""
    if command not in ["解绑", "unbind"]:
        return

    await send_with_at(event, "解绑将清除所有数据，确认吗？(确认/取消)", at=True)


@unbind_cmd.got("confirm")
async def confirm_unbind(event: Uninfo, confirm: str):
    if confirm == "确认":
        await redis_client.delete(f"session_token:{event.user_id}")
        await send_with_at(event, "解绑成功！")
    else:
        await send_with_at(event, "已取消解绑")


@clean_cmd.handle()
async def handle_clean(event: Uninfo, command: str):
    """清除所有数据"""
    if command != "clean":
        return

    await send_with_at(event, "将删除所有数据，确认吗？(确认/取消)", at=True)


@clean_cmd.got("confirm")
async def confirm_clean(event: Uninfo, confirm: str):
    if confirm == "确认":
        await redis_client.delete(f"session_token:{event.user_id}")
        await send_with_at(event, "数据已清除！")
    else:
        await send_with_at(event, "已取消操作")


@get_session_cmd.handle()
async def handle_get_session(event: Uninfo, command: str):
    """获取 sessionToken"""
    if command != "sessionToken" or event.group_id:
        return

    session_token = await redis_client.get(f"session_token:{event.user_id}")
    if not session_token:
        await send_with_at(event, "未绑定 sessionToken", at=False)
        return

    await send_with_at(event, f"sessionToken: {session_token.decode()}", at=False)
