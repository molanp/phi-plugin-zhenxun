from typing import Any

from nonebot import require

require("nonebot_plugin_uninfo")
from nonebot_plugin_uninfo import Uninfo

from .fCompute import fCompute


class makeRequestFnc:
    @staticmethod
    def makePlatform(e: Uninfo) -> dict[str, Any]:
        return {
            "platform": fCompute.getAdapterName(e),
            "platform_id": e.user.id,
        }
