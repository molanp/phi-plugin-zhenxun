import json
from typing import Any, TypedDict

import httpx

from ..config import PluginConfig
from .cls.saveHistory import saveHistory


class baseAu(TypedDict):
    """基础鉴权"""

    platform: str
    """平台名称"""
    platform_id: str
    """用户平台内id"""
    token: str | None
    """PhigrosToken"""
    api_user_id: str | None
    """用户api内id"""
    api_token: str | None
    """用户 apiToken"""


class highAu(TypedDict):
    """高级鉴权"""

    platform: str
    """平台名称"""
    platform_id: str
    """用户平台内id"""
    token: str | None
    """PhigrosToken"""
    api_user_id: str | None
    """用户api内id"""
    api_token: str
    """用户 apiToken"""


class BindSuccessData(TypedDict):
    internal_id: int
    """用户内部ID"""
    have_api_token: bool
    """是否拥有API Token"""


class BindSuccessResponse(TypedDict):
    """绑定成功响应数据"""

    message: str
    """响应信息(e.g., "绑定成功")"""
    data: BindSuccessData
    """响应数据"""


class PlatformDataItem(TypedDict):
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


class UserData(TypedDict):
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


class UserResponse(TypedDict):
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


class TokenManageParams(TypedDict):
    """Token管理参数"""

    operation: str
    """操作类型 'delete' 或 'rmau'"""
    platform: str
    """平台名称"""
    platform_id: str
    """平台内用户ID"""


class SongInfoRequest(TypedDict):
    """歌曲信息请求"""

    song_id: str
    """歌曲ID"""
    difficulty: str
    """难度等级（levelKind）"""


class DifficultyRecord(TypedDict):
    """难度记录"""

    fc: bool
    """是否 Full Combo"""
    score: float
    """得分"""
    acc: float
    """准确率"""


SongRecord = list[DifficultyRecord | None]
"""每个位置对应一个难度的成绩（None 表示未解锁）"""


class GetCloudSongResponse(TypedDict):
    """获取云歌曲响应"""

    data: SongRecord | DifficultyRecord
    """返回的成绩数据（可能是数组或单个难度）"""


class GameUserBasic(TypedDict):
    """游戏用户基础信息"""

    background: str
    """背景图"""
    selfIntro: str
    """自我介绍（仅 me 对象中存在）"""


class SummaryInfo(TypedDict):
    """分数概要信息"""

    rankingScore: float
    """排名分数"""
    challengeModeRank: int
    """挑战模式排名"""
    updatedAt: str
    """更新时间（仅 me 对象中存在）"""
    avatar: str
    """头像（仅 me 对象中存在）"""


class ModifiedTime(TypedDict):
    """修改时间"""

    iso: str
    """ISO 时间戳"""


class SaveInfo(TypedDict):
    """存档信息"""

    summary: SummaryInfo
    """分数概要"""
    modifiedAt: ModifiedTime
    """修改时间"""


class ChallengeListItem(TypedDict):
    """挑战模式条目"""

    ChallengeMode: int
    """挑战模式编号"""
    ChallengeModeRank: int
    """挑战模式排名"""
    date: str
    """日期"""


class UserItem(TypedDict):
    """用户条目"""

    gameuser: GameUserBasic
    """基础信息（普通用户只有 background）"""
    saveInfo: SaveInfo
    """存档信息"""
    index: int
    """用户索引"""


class MeData(TypedDict):
    """当前用户数据"""

    save: dict[str, Any]
    """存档数据（oriSave 类型）"""
    history: dict[str, saveHistory]
    """用户历史记录（saveHistory 类型）"""


class RanklistResponseData(TypedDict):
    """排行榜响应数据"""

    totDataNum: int
    """数据总数"""
    users: list[UserItem]
    """用户数组"""
    me: MeData
    """当前用户扩展数据"""


class ScoreDetail(TypedDict):
    """歌曲得分详情"""

    score: float
    """得分"""
    acc: float
    """准确率"""
    fc: bool
    """是否 Full Combo"""


class SongRecordHistory(TypedDict):
    """成绩历史记录"""

    timestamp: str
    """记录时间"""
    record: DifficultyRecord
    """成绩记录"""


class highAuWithTokenManage(highAu):
    """token管理"""

    data: TokenManageParams


class HighAuWithSongInfo(highAu, SongInfoRequest):
    pass


OriSave = dict[str, Any]


class BaseAuWithRequest(baseAu):
    request: str


class BaseAuWithsaveHistory(BaseAuWithRequest, saveHistory):
    pass


class makeRequest:
    @staticmethod
    async def bind(params: baseAu) -> dict:
        """
        绑定平台账号与用户Token

        :param params:  基础参数
        :return: {"message": str}
        """
        return await makeFetch(burl("/bind"), params)

    @staticmethod
    async def unbind(params: dict) -> dict:
        """
        解绑平台账号

        :param params: 请求参数字典，必须包含以下字段：

            - platform (str): 平台名称
            - platform_id (str): 用户在平台内的唯一标识
        :return: {"message": str}
        """
        return await makeFetch(burl("/unbind"), params)

    @staticmethod
    async def clear(params: highAu) -> dict:
        """
        清空用户数据

        :param params: 登录信息
        :return: {"message": str}
        """
        return await makeFetch(burl("/clear"), params)

    @staticmethod
    async def setApiToken(params: highAu) -> dict:
        """
        设置或更新用户的 API Token

        :param params: 登录信息,需包含以下字段

            - user_id: 用户 ID
            - token_old: 原有API Token（如已有Token时必填）
            - token_new: 新的API Token
            - platform: 平台名称
            - platform_id: 用户平台内id
        :return: {"message": str}
        """
        return await makeFetch(burl("/setApiToken"), params)

    @staticmethod
    async def tokenList(params: highAu) -> UserResponse:
        """
        获取用户 API Token 列表

        :param params:
        :return: UserResponse
        """
        return UserResponse(**(await makeFetch(burl("/tokenList"), params))["data"])

    @staticmethod
    async def tokenManage(params: highAuWithTokenManage) -> dict:
        """
        管理用户 API Token

        :param highAuWithTokenManage params:
        :return: {"message": string}
        """
        return await makeFetch(burl("/token/manage"), params)

    @staticmethod
    async def getCloudSong(params: HighAuWithSongInfo) -> GetCloudSongResponse:
        """获取用户云存档单曲数据"""
        return GetCloudSongResponse(
            **(await makeFetch(burl("/get/cloud/song"), params))["data"]
        )

    @staticmethod
    async def getCloudSaves(params: baseAu) -> OriSave:
        """获取用户云存档数据"""
        return (await makeFetch(burl("/get/cloud/saves"), params))["data"]

    @staticmethod
    async def getCloudSaveInfo(params: baseAu) -> SaveInfo:
        """获取用户云存档saveInfo数据"""
        return SaveInfo(
            **(await makeFetch(burl("/get/cloud/saveInfo"), params))["data"]
        )

    @staticmethod
    async def getRanklistUser(params: baseAu) -> RanklistResponseData:
        """根据用户获取排行榜相关信息"""
        return RanklistResponseData(
            **(await makeFetch(burl("/get/ranklist/user"), params))["data"]
        )

    @staticmethod
    async def getRanklistRank(params: dict) -> RanklistResponseData:
        """
        根据名次获取排行榜相关信息

        :param params: 请求参数,需包含以下内容

            - request_rank: 请求的排名
        """
        return RanklistResponseData(
            **(await makeFetch(burl("/get/ranklist/rank"), params))["data"]
        )

    @staticmethod
    async def getHistory(params: BaseAuWithRequest) -> dict[str, list[Any]]:
        """
        获取用户data历史记录

        :param params: {baseAu & {request: keyof saveHistoryObject}
        :return:  {data: list[saveHistoryObject]}
        """
        return (await makeFetch(burl("/get/history/histor"), params))["data"]

    @staticmethod
    async def getHistoryRecord(
        params: HighAuWithSongInfo,
    ) -> ScoreDetail | list[SongRecordHistory] | dict[str, dict[str, ScoreDetail]]:
        """
        获取用户成绩历史记录。

        根据传入参数不同，返回不同类型的成绩数据：

        - 如果 params 中含有 song_id，返回 ScoreDetail
        - 如果 params 中含有 difficulty，返回 list[SongRecordHistory]
        - 否则返回 dict[str, ScoreDetail]

        :param HighAuWithSongInfo params: 请求参数，包含 baseAu 和歌曲信息
        （song_id 或 difficulty）

        :returns:
        Dict[str, Union[ScoreDetail, List[songRecordHistory], Dict[str, ScoreDetail]]]
        返回结果类型根据参数动态变化。
        """
        return (await makeFetch(burl("/get/history/record"), params))["data"]

    @staticmethod
    async def setHistory(params: BaseAuWithsaveHistory) -> dict:
        """
        上传用户的历史记录

        :returns: {"message": str}
        """
        return (await makeFetch(burl("/set/history"), params))["data"]

    @staticmethod
    async def setUsersToken(params: dict) -> dict:
        """
        上传用户 token 数据。

        :param params: 包含用户 token 信息的字典，格式为：

                {
                    "data": {
                        "userId1": "token1",
                        "userId2": "token2",
                        ...
                    }
                }
        :return: {"message": "success"}
        """
        return await makeFetch(burl("/set/usersToken"), params)


async def makeFetch(url: str, params: dict | Any) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url, json=params, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            try:
                json_data = e.response.json()
                error_message = json_data.get("error", json_data)
            except json.JSONDecodeError:
                error_message = e.response.text
            raise httpx.NetworkError(
                f"HTTP 错误 {e.response.status_code}: {error_message}"
            ) from e
        except httpx.RequestError as e:
            raise httpx.RequestError(f"请求失败: {e}") from e

        try:
            return response.json()
        except json.JSONDecodeError as e:
            text = response.text
            raise ValueError(f"JSON 解析失败: {text}") from e


def burl(path: str) -> str:
    if base_url := PluginConfig.get("phiPluginApiUrl"):
        return f"{base_url}{path}"
    else:
        raise ValueError("请先设置API地址")
