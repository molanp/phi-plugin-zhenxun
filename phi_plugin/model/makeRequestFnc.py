from nonebot import require

require("nonebot_plugin_uninfo")
from nonebot_plugin_uninfo import Uninfo

from .fCompute import fCompute


class makeRequestFnc:
    @staticmethod
    def makePlatform(session: Uninfo) -> dict:
        return {
            "platform": fCompute.getAdapterName(session),
            "platform_id": session.user.id,
        }
