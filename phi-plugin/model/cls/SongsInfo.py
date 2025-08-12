from pydantic import BaseModel

from ..constNum import LevelItem
from .Chart import Chart


class SongsInfoObject(BaseModel):
    id: str = ""
    """曲目id"""
    song: str = ""
    """曲目名称"""
    illustration: str = ""
    """曲绘略缩图名称"""
    can_t_be_letter: bool = False
    """是否不参与猜字母"""
    can_t_be_guessill: bool = False
    """是否不参与猜曲绘"""
    chapter: str = ""
    """章节"""
    bpm: str = ""
    """BPM"""
    composer: str = ""
    """作曲"""
    length: str = ""
    """时长"""
    illustrator: str = ""
    """画师"""
    spinfo: str = ""
    """特殊信息"""
    chart: dict[LevelItem | str, Chart] = {}
    """谱面详情"""
    sp_vis: bool = False
    """是否是特殊谱面"""
    illustration_big: str = ""
    """曲绘"""
