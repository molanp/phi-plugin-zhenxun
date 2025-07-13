from datetime import datetime
from typing import Any, Literal
from typing_extensions import Self

from nonebot.compat import field_validator
from pydantic import BaseModel

from ...utils import Date


class RecordModel(BaseModel):
    date: datetime
    value: Any

    @field_validator("date")
    @classmethod
    def parse_iso(cls, value: Any) -> datetime:
        """自动将字符串转换为datetime对象"""
        return Date(value)


class LevelData(BaseModel):
    fc: bool = False
    """是否 Full Combo"""
    score: int = 0
    """得分"""
    acc: float = 0
    """准确率"""


class HistoryModel(LevelData):
    date: datetime
    """日期"""


class rksLine(BaseModel):
    rks_history: list[list[float]]
    rks_range: list[float]
    rks_date: list[int]


class dataLine(BaseModel):
    data_history: list[list[float]]
    data_range: list[float | str]
    """[min, max], 如果数字大于1024，则转为KiB，MiB，GiB，TiB，Pib"""
    data_date: list[int]


class rksLineWithdataLine(rksLine, dataLine):
    @classmethod
    def from_models(cls, rks: rksLine, data: dataLine) -> Self:
        """从两个模型实例创建合并实例"""
        merged_data = {**rks.model_dump(), **data.model_dump()}
        return cls(**merged_data)


class saveHistoryObject(BaseModel):
    scoreHistory: dict[
        str,
        dict[
            Literal["EZ", "HD", "IN", "AT", "LEGACY"],
            list[tuple[float, int, datetime, bool]],
        ],
    ]
    """歌曲成绩记录"""
    data: list[RecordModel]
    """data货币变更记录"""
    rks: list[dict[str, datetime | float]]
    """rks变更记录"""
    challengeModeRank: list[RecordModel]
    """课题模式成绩"""
    version: float | None
    """
    历史记录版本号

    - v1.0,取消对当次更新内容的存储，取消对task的记录，更正scoreHistory
    - v1.1,更正scoreHistory
    - v2,由于曲名错误，删除所有记录，曲名使用id记录
    - v3,添加课题模式历史记录
    """
    dan: list
    """民间考核"""


class BindSuccessData(BaseModel):
    internal_id: int = 0
    """用户内部ID"""
    have_api_token: bool = False
    """是否拥有API Token"""


class BindSuccessResponse(BaseModel):
    """绑定成功响应数据"""

    message: str
    """响应信息(e.g., "绑定成功")"""
    data: BindSuccessData = BindSuccessData()
    """响应数据"""


class PlatformDataItem(BaseModel):
    """平台数据项"""

    platform_name: str
    """平台名称"""
    platform_id: str
    """平台内用户ID"""
    create_at: str
    """创建时间"""
    update_at: str
    """更新时间"""
    authentication: int
    """认证状态"""


class UserData(BaseModel):
    """用户数据"""

    user_id: str
    """用户ID"""
    phigros_token: str
    """PhigrosToken"""
    api_token: str
    """用户api token"""
    create_at: str
    """创建时间"""
    update_at: str
    """更新时间"""
    platform_data: list[PlatformDataItem]
    """平台数据列表"""


class UserResponse(BaseModel):
    """用户响应"""

    data: UserData
    """用户详细数据"""
    user_id: str
    """用户ID（引用 definition 168966427）"""
    phigros_token: str
    """PhigrosToken（引用 definition 168966417）"""
    api_token: str
    """用户api token（引用 definition 168966428）"""
    create_at: str
    """创建时间"""
    update_at: str
    """更新时间"""
    platform_data: list[PlatformDataItem]
    """平台数据（引用 definition 169006958）"""


class DifficultyRecord(BaseModel):
    """难度记录"""

    fc: bool
    """是否 Full Combo"""
    score: float
    """得分"""
    acc: float
    """准确率"""


SongRecord = list[DifficultyRecord | None]
"""每个位置对应一个难度的成绩（None 表示未解锁）"""


class GetCloudSongResponse(BaseModel):
    """获取云歌曲响应"""

    data: SongRecord | DifficultyRecord
    """返回的成绩数据（可能是数组或单个难度）"""


class GameUserBasic(BaseModel):
    """游戏用户基础信息"""

    background: str
    """背景图"""
    selfIntro: str
    """自我介绍（仅 me 对象中存在）"""


class SummaryInfo(BaseModel):
    """分数概要信息"""

    rankingScore: float
    """排名分数"""
    challengeModeRank: int
    """挑战模式排名"""
    updatedAt: str
    """更新时间（仅 me 对象中存在）"""
    avatar: str
    """头像（仅 me 对象中存在）"""


class ModifiedTime(BaseModel):
    """修改时间"""

    iso: str
    """ISO 时间戳"""


class SaveInfo(BaseModel):
    """存档信息"""

    summary: SummaryInfo
    """分数概要"""
    modifiedAt: ModifiedTime
    """修改时间"""


class UserItem(BaseModel):
    """用户条目"""

    gameuser: GameUserBasic
    """基础信息（普通用户只有 background）"""
    saveInfo: SaveInfo
    """存档信息"""
    index: int
    """用户索引"""


class MeData(BaseModel):
    """当前用户数据"""

    save: dict[str, Any]
    """存档数据（oriSave 类型）"""
    history: dict[str, saveHistoryObject]
    """用户历史记录（saveHistory 类型）"""


class RanklistResponseData(BaseModel):
    """排行榜响应数据"""

    totDataNum: int
    """数据总数"""
    users: list[UserItem]
    """用户数组"""
    me: MeData
    """当前用户扩展数据"""


class RanklistRksResponseData(BaseModel):
    """RKS 排行榜响应数据"""

    rksRank: int
    totNum: int


class ScoreDetail(BaseModel):
    """歌曲得分详情"""

    score: float
    """得分"""
    acc: float
    """准确率"""
    fc: bool
    """是否 Full Combo"""


class SongRecordHistory(BaseModel):
    """成绩历史记录"""

    timestamp: str
    """记录时间"""
    record: DifficultyRecord
    """成绩记录"""


class BaseResponse(BaseModel):
    """基础请求响应"""

    message: str
    """响应信息"""


class saveHistoryModel(BaseModel):
    data: list[saveHistoryObject]


OriSave = dict[str, Any]
