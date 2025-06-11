from pathlib import Path
from typing import Any

from ..getInfo import getInfo
from .Chart import Chart


class SongsInfo:
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
    chart: dict[str, Chart] = {}  # noqa: RUF012
    """谱面详情"""
    sp_vis: bool = False
    """是否是特殊谱面"""
    illustration_big: str | Path = ""
    """?大曲绘"""

    @classmethod
    async def init(cls, data: dict[str, Any] | None) -> "SongsInfo":
        """
        :paramm dict[str, Any] | None data: 原始数据
        """
        instance = cls()
        if not data:
            return instance

        instance.id = data["id"]
        instance.song = data["song"]
        instance.illustration = await getInfo.getill(instance.song)
        instance.can_t_be_letter = data.get("can_t_be_letter") or False
        instance.can_t_be_guessill = data.get("can_t_be_guessill") or False
        instance.chapter = data.get("chapter", "")
        instance.bpm = data.get("bpm", "")
        instance.composer = data.get("composer", "")
        instance.length = data.get("length", "")
        instance.illustrator = data.get("illustrator", "")
        instance.spinfo = data.get("spinfo", "")
        instance.chart = data.get("chart", {})
        instance.sp_vis = data.get("sp_vis", False)
        instance.illustration_big = data.get("illustration_big", "")
        return instance
