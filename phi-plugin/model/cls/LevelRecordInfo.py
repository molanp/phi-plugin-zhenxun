from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from ...utils import Rating
from ..constNum import LevelItem
from ..fCompute import fCompute
from ..getInfo import getInfo


class LevelRecordInfo(BaseModel):
    fc: bool = False
    """是否 Full Combo"""
    score: int = 0
    """得分"""
    acc: float = 0
    """准确率"""
    id: str = ""
    """曲目id"""
    rank: LevelItem | str = ""
    """Level"""
    Rating: Literal[
        "phi",
        "FC",
        "V",
        "S",
        "A",
        "B",
        "C",
        "F",
    ] = "F"
    """评分等级"""
    song: str = ""
    """曲名"""
    illustration: str | Path = ""
    """曲绘链接"""
    difficulty: float = 0.0
    """定数"""
    rks: float = 0.0
    """等效RKS"""
    ### 不允许序列化的字段
    suggest: str = Field(default="", exclude=True)
    """推分建议"""
    num: int = Field(default=0, exclude=True)
    """是 Best 几"""
    date: datetime = Field(default=datetime.now(), exclude=True)
    """更新时间(iso)"""

    # 私有字段
    lazy_song_id: str = Field(default="", exclude=True)
    lazy_index: int = Field(default=0, exclude=True)
    lazy_raw_data: dict[str, Any] | None = Field(default=None, exclude=True)
    is_lazy: bool = Field(default=False, exclude=True)
    initialized: bool = Field(default=True, exclude=True)  # 默认为已初始化

    @classmethod
    def lazy_init(cls, data: dict, id: str, index: int) -> "LevelRecordInfo":
        """
        惰性初始化方法，只设置基本字段
        """
        # 检查数据是否包含完整字段，如果包含则直接初始化
        if cls._is_data_complete(data):
            # 数据已经完整，直接创建实例而不调用 init
            instance = cls(**data)
            # 标记为已初始化
            instance.initialized = True
            instance.is_lazy = False
            return instance
        # 数据不完整，使用惰性加载
        instance = cls(
            fc=data.get("fc", False),
            score=data.get("score", 0),
            acc=data.get("acc", 0.0),
        )
        instance.lazy_raw_data = data
        instance.lazy_song_id = id
        instance.lazy_index = index
        instance.is_lazy = True
        instance.initialized = False
        return instance

    @classmethod
    def _is_data_complete(cls, data: dict) -> bool:
        """
        检查传入数据是否包含完整字段
        """
        # 定义完整字段列表
        complete_fields = [
            "song",
            "rank",
            "difficulty",
            "rks",
            "Rating",
            "illustration",
        ]

        # 检查是否包含完整字段
        return all(field in data for field in complete_fields)

    def _ensure_initialized(self):
        """
        确保完全初始化
        """
        if not self.initialized and self.is_lazy and self.lazy_raw_data is not None:
            # 完整初始化
            full_instance = LevelRecordInfo.init(
                self.lazy_raw_data, self.lazy_song_id, self.lazy_index
            )
            # 复制所有字段
            for field_name in LevelRecordInfo.model_fields:
                setattr(self, field_name, getattr(full_instance, field_name))
            self.initialized = True
            self.is_lazy = False

    # 重写 __getattribute__ 实现惰性加载
    def __getattribute__(self, name: str):
        # 避免无限递归，对特殊属性直接返回
        if name in {
            "initialized",
            "is_lazy",
            "lazy_raw_data",
            "lazy_song_id",
            "lazy_index",
        }:
            return object.__getattribute__(self, name)

        # 检查是否是模型字段且需要初始化
        if name in {
            "song",
            "rank",
            "difficulty",
            "rks",
            "Rating",
            "illustration",
        } and not object.__getattribute__(self, "initialized"):
            object.__getattribute__(self, "_ensure_initialized")()
        return object.__getattribute__(self, name)

    @classmethod
    def init(cls, data: dict, id: str, rank: int | str) -> "LevelRecordInfo":
        """
        :param data: 原始数据
        :param id: 曲目id
        :param rank: 难度
        """
        data_ = {"fc": data["fc"], "score": data["score"], "acc": data["acc"], "id": id}
        song = getInfo.idgetsong(id)
        info = getInfo.info(song) if song else None
        data_["rank"] = (
            getInfo.Level[rank] if isinstance(rank, int) else rank
        )  # EZ HD IN AT LEGACY
        data_["Rating"] = Rating(data_["score"], data_["fc"])  # V S A
        if not info:
            data_["song"] = id
            data_["difficulty"] = 0
            data_["rks"] = 0
            return cls(**data_)
        data_["song"] = info.song  # 曲名
        data_["illustration"] = getInfo.getill(data_["song"])  # 曲绘链接
        difficulty = (
            info.chart[data_["rank"]].difficulty
            if data_["rank"] in info.chart
            else None
        )
        if info.chart and difficulty:
            assert isinstance(difficulty, float)
            data_["difficulty"] = difficulty  # 难度
            data_["rks"] = fCompute.rks(data_["acc"], data_["difficulty"])  # 等效rks
        else:
            data_["difficulty"] = 0
            data_["rks"] = 0
        return cls(**data_)

    @classmethod
    def to_tuple(cls) -> tuple[float, int, datetime, bool]:
        return (
            cls.acc,
            cls.score,
            cls.date,
            cls.fc,
        )
