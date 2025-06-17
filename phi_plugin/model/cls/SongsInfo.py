from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .Chart import Chart


class SongsInfoObject(BaseModel):
    id: str = ""
    """id"""
    song: str = ""
    """曲目"""
    illustration: str | Path = ""
    """曲绘"""
    can_t_be_letter: bool = False
    """是否不参与猜字母"""
    can_t_be_guessill: bool = False
    """是否不参与猜曲绘"""
    chapter: str = ""
    """章节"""
    bpm: str = ""
    """bpm"""
    composer: str = ""
    """作曲"""
    length: str = ""
    """时长"""
    illustrator: str = ""
    """画师"""
    spinfo: str = ""
    """特殊信息"""
    chart: dict[str, Chart] = {}
    """谱面详情"""
    sp_vis: bool = False
    """是否是特殊谱面"""
    illustration_big: str | Path = ""
    """?大曲绘"""


class SongsInfo:
    @staticmethod
    async def init(data: dict[str, Any] | None) -> "SongsInfoObject":
        """
        :paramm dict[str, Any] | None data: 原始数据
        """
        if not data:
            return SongsInfoObject()
        from ..getInfo import getInfo

        return SongsInfoObject(
            **{
                "song": data["song"],
                "illustration": await getInfo.getill(data["song"]),
                "can_t_be_letter": data.get("can_t_be_letter") or False,
                "can_t_be_guessill": data.get("can_t_be_guessill") or False,
                "chapter": data.get("chapter", ""),
                "bpm": data.get("bpm", ""),
                "composer": data.get("composer", ""),
                "length": data.get("length", ""),
                "illustrator": data.get("illustrator", ""),
                "spinfo": data.get("spinfo", ""),
                "chart": data.get("chart", {}),
                "sp_vis": data.get("sp_vis", False),
                "illustration_big": data.get("illustration_big", ""),
            }
        )
