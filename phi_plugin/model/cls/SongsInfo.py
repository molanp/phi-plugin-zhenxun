from pathlib import Path
from typing import Any

from ..getInfo import getInfo
from .Chart import Chart


class SongsInfoObject:
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

    async def init(self, data: dict[str, Any] | None) -> "SongsInfoObject":
        """
        :paramm dict[str, Any] | None data: 原始数据
        """
        if not data:
            return self

        self.id = data["id"]
        self.song = data["song"]
        self.illustration = await getInfo.getill(self.song)
        self.can_t_be_letter = data.get("can_t_be_letter") or False
        self.can_t_be_guessill = data.get("can_t_be_guessill") or False
        self.chapter = data.get("chapter", "")
        self.bpm = data.get("bpm", "")
        self.composer = data.get("composer", "")
        self.length = data.get("length", "")
        self.illustrator = data.get("illustrator", "")
        self.spinfo = data.get("spinfo", "")
        self.chart = data.get("chart", {})
        self.sp_vis = data.get("sp_vis", False)
        self.illustration_big = data.get("illustration_big", "")
        return self


SongsInfo = SongsInfoObject()
