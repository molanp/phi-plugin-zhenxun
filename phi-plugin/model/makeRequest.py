from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from ..config import PluginConfig
from .cls.models import (
    BaseResponse,
    BindSuccessResponse,
    GetCloudSongResponse,
    OriSave,
    RanklistResponseData,
    RanklistRksResponseData,
    SaveInfo,
    ScoreDetail,
    SongRecordHistory,
    UserResponse,
    saveHistoryModel,
)


class makeRequest:
    @staticmethod
    async def bind(params: dict) -> BindSuccessResponse:
        """
        绑定平台账号与用户Token

        :param params:  基础参数
        """
        return BindSuccessResponse(**await makeFetch(burl("/bind"), params))

    @staticmethod
    async def unbind(params: dict) -> BaseResponse:
        """
        解绑平台账号

        :param params: 请求参数字典，必须包含以下字段：

            - platform (str): 平台名称
            - platform_id (str): 用户在平台内的唯一标识
        """
        return BaseResponse(**await makeFetch(burl("/unbind"), params))

    @staticmethod
    async def clear(params: dict) -> BaseResponse:
        """
        清空用户数据

        :param params: 登录信息
        """
        return BaseResponse(**await makeFetch(burl("/clear"), params))

    @staticmethod
    async def setApiToken(params: dict) -> BaseResponse:
        """
        设置或更新用户的 API Token

        :param params: 登录信息,需包含以下字段

            - user_id: 用户 ID
            - token_old: 原有API Token（如已有Token时必填）
            - token_new: 新的API Token
            - platform: 平台名称
            - platform_id: 用户平台内id
        """
        return BaseResponse(**await makeFetch(burl("/setApiToken"), params))

    @staticmethod
    async def tokenList(params: dict) -> UserResponse:
        """
        获取用户 API Token 列表

        :param params:
        :return: UserResponse
        """
        return UserResponse(**(await makeFetch(burl("/tokenList"), params))["data"])

    @staticmethod
    async def tokenManage(params: dict) -> BaseResponse:
        """
        管理用户 API Token

        :param params:
        """
        return BaseResponse(**await makeFetch(burl("/token/manage"), params))

    @staticmethod
    async def getCloudSong(params: dict) -> GetCloudSongResponse:
        """获取用户云存档单曲数据"""
        return GetCloudSongResponse(
            **(await makeFetch(burl("/get/cloud/song"), params))["data"]
        )

    @staticmethod
    async def getCloudSaves(params: dict) -> OriSave:
        """获取用户云存档数据"""
        return (await makeFetch(burl("/get/cloud/saves"), params))["data"]

    @staticmethod
    async def getCloudSaveInfo(params: dict) -> SaveInfo:
        """获取用户云存档saveInfo数据"""
        return SaveInfo(
            **(await makeFetch(burl("/get/cloud/saveInfo"), params))["data"]
        )

    @staticmethod
    async def getRanklistUser(params: dict) -> RanklistResponseData:
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
    async def getRanklistRks(params: dict) -> RanklistRksResponseData:
        """
        获取rks大于目标值的用户数量

        :param params: 请求参数,需包含以下内容

            - request_rks: 请求的排名
        """
        return (await makeFetch(burl("/get/ranklist/rksRank"), params))["data"]

    @staticmethod
    async def getHistory(params: dict) -> saveHistoryModel:
        """
        获取用户data历史记录

        :param params: {baseAu & {request: keyof saveHistoryObject}
        """
        return (await makeFetch(burl("/get/history/histor"), params))["data"]

    @staticmethod
    async def getHistoryRecord(
        params: dict,
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
    async def setHistory(params: dict) -> BaseResponse:
        """上传用户的历史记录"""
        return BaseResponse(**await makeFetch(burl("/set/history"), params))

    @staticmethod
    async def setUsersToken(params: dict) -> BaseResponse:
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
        """
        return BaseResponse(**await makeFetch(burl("/set/usersToken"), params))

    @staticmethod
    async def getUserBan(params: dict) -> bool:
        "查询用户是否被禁用"
        return (await makeFetch(burl("/get/banUser"), params))["data"]


async def makeFetch(url: str, params: dict) -> dict:
    try:
        response = await AsyncHttpx.post(
            url, json=params, headers={"Content-Type": "application/json"}
        )
        return response.json()
    except Exception as e:
        logger.error(f"API请求失败, URL {url}", "phi-plugin", e=e)
        raise ValueError("API请求失败") from e


def burl(path: str) -> str:
    if base_url := PluginConfig.get("phiPluginApiUrl"):
        return f"{base_url}{path}"
    else:
        raise ValueError("请先设置API地址")
