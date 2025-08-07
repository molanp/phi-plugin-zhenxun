from typing import Any, Literal

from zhenxun.services.log import logger
from zhenxun.utils.http_utils import AsyncHttpx

from ..config import PluginConfig
from .cls.models import (
    BaseResponse,
    BindSuccessResponse,
    GetCloudSongResponse,
    RanklistResponseData,
    RanklistRksResponseData,
    SaveInfo,
    ScoreDetail,
    SongRecordHistory,
    UserResponse,
    commentObject,
    saveHistoryModel,
    tokenManageParams,
)


class makeRequest:
    @staticmethod
    async def bind(params: dict) -> BindSuccessResponse:
        """
        绑定平台账号与用户Token

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
            - str api_token: 用户api token
        """
        return BindSuccessResponse(**await makeFetch(burl("/bind"), params))

    @staticmethod
    async def unbind(params: dict) -> BaseResponse:
        """
        解绑平台账号

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
            - str api_token: 用户api token
        """
        return BaseResponse(**await makeFetch(burl("/unbind"), params))

    @staticmethod
    async def clear(params: dict) -> BaseResponse:
        """
        清空用户数据

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id
            - str api_token: 用户api token

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
        """
        return BaseResponse(**await makeFetch(burl("/clear"), params))

    @staticmethod
    async def setApiToken(params: dict) -> BaseResponse:
        """
        设置或更新用户的 API Token

        :param params: 登录信息,需包含以下字段

            - user_id: 用户 ID
            - ?token_old: 原有API Token（如已有Token时必填）
            - ?token_new: 新的API Token
            - platform: 平台名称
            - platform_id: 用户平台内id
        """
        return BaseResponse(**await makeFetch(burl("/setApiToken"), params))

    @staticmethod
    async def tokenList(params: dict) -> UserResponse:
        """
        获取用户 API Token 列表

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id
            - str api_token: 用户api token

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
        :return: UserResponse
        """
        return UserResponse(**(await makeFetch(burl("/tokenList"), params))["data"])

    @staticmethod
    async def tokenManage(params: tokenManageParams) -> BaseResponse:
        """
        管理用户 API Token

        :param tokenManageParams params:
        """
        return BaseResponse(**await makeFetch(burl("/token/manage"), params))

    @staticmethod
    async def getCloudSong(params: dict) -> GetCloudSongResponse:
        """
        获取用户云存档单曲数据

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id
            - str api_token: 用户api token
            - str song_id: 歌曲ID
            - Literal[EZ,HD,IN,AT] difficulty: 难度

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
        """
        return GetCloudSongResponse(
            **(await makeFetch(burl("/get/cloud/song"), params))["data"]
        )

    @staticmethod
    async def getCloudSaves(params: dict) -> dict[str, Any]:
        """
        获取用户云存档数据

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
            - str api_token: 用户api token
        """
        return (await makeFetch(burl("/get/cloud/saves"), params))["data"]

    @staticmethod
    async def getCloudSaveInfo(params: dict) -> SaveInfo:
        """
        获取用户云存档saveInfo数据

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
            - str api_token: 用户api token
        """
        return SaveInfo(
            **(await makeFetch(burl("/get/cloud/saveInfo"), params))["data"]
        )

    @staticmethod
    async def getRanklistUser(params: dict) -> RanklistResponseData:
        """
        根据用户获取排行榜相关信息

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
            - str api_token: 用户api token
        """
        return RanklistResponseData(
            **(await makeFetch(burl("/get/ranklist/user"), params))["data"]
        )

    @staticmethod
    async def getRanklistRank(request_rank: int) -> RanklistResponseData:
        """
        根据名次获取排行榜相关信息

        :param int request_rank: 请求的排名
        """
        return RanklistResponseData(
            **(
                await makeFetch(
                    burl("/get/ranklist/rank"), {"request_rank": request_rank}
                )
            )["data"]
        )

    @staticmethod
    async def getRanklistRks(request_rks: float) -> RanklistRksResponseData:
        """
        获取rks大于目标值的用户数量

        :param float request_rks: 请求的rks
        """
        return (
            await makeFetch(burl("/get/ranklist/rksRank"), {"request_rks": request_rks})
        )["data"]

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

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
            - str api_token: 用户api token


        - 如果 params 中含有 song_id(str)，返回 ScoreDetail
        - 如果 params 中含有 difficulty(Literal[EZ,HD,IN,AT])，返回 list[SongRecordHistory]
        - 否则返回 dict[str, ScoreDetail]

        :param baseAu & songInfoRequest params: 请求参数，包含 baseAu 和歌曲信息
        （song_id 或 difficulty）

        :returns:
        Dict[str, Union[ScoreDetail, List[songRecordHistory], Dict[str, ScoreDetail]]]
        返回结果类型根据参数动态变化。
        """
        return (await makeFetch(burl("/get/history/record"), params))["data"]

    @staticmethod
    async def setHistory(params: dict) -> BaseResponse:
        """
        上传用户的历史记录

        :param dict params: {baseAu & {data: saveHistory}}
        """
        return BaseResponse(**await makeFetch(burl("/set/history"), params))

    @staticmethod
    async def setUsersToken(params: dict) -> BaseResponse:
        """
        上传用户 token 数据。

        :param params: 包含用户 token 信息的字典，格式为：
        ```
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
        """
        查询用户是否被禁用

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
            - str api_token: 用户api token
        """
        return (await makeFetch(burl("/get/banUser"), params))["data"]

    @staticmethod
    async def getCommentsBySongID(
        params: dict[Literal["songId"], str],
    ) -> list[commentObject]:
        """获取歌曲评论"""
        return [
            commentObject(**i)
            for i in (await makeFetch(burl("/comment/get/bySongId"), params))["data"]
        ]

    @staticmethod
    async def getCommentsByUserId(
        params: dict,
    ) -> list[commentObject]:
        """
        获取歌曲评论

        :param dict params: 请求参数字典

            - str platform: 平台名称
            - str platform_id: 用户平台内id

            可选字段:

            - str token: PhigrosToken
            - str api_user_id: 用户api内id
            - str api_token: 用户api token
        """
        return [
            commentObject(**i)
            for i in (await makeFetch(burl("/comment/get/byUserId"), params))["data"]
        ]

    @staticmethod
    async def addComment(params: dict) -> BaseResponse:
        """
        添加单条评论

        :param dict params: {baseAu & {data: {comment: commentObject}}}
        """
        return BaseResponse(**await makeFetch(burl("/comment/add"), params))

    @staticmethod
    async def delComment(params: dict) -> BaseResponse:
        """
        删除单条评论

        :param dict params: {baseAu & {commentId: commentId}}
        """
        return BaseResponse(**await makeFetch(burl("/comment/del"), params))

    @staticmethod
    async def updateComments(params: dict) -> BaseResponse:
        """
        批量添加评论

        :param dict params: ```
        {
            data: {
                comments: [
                    commentObject,
                    commentObject,
                    ...
                ]
            }
        }
        ```
        """
        return BaseResponse(**await makeFetch(burl("/comment/update"), params))


async def makeFetch(url: str, params: Any) -> dict:
    logger.debug(f"请求API: {url} with params: {params}", "phi-plugin:makeFetch")
    try:
        response = await AsyncHttpx.post(
            url, json=params, headers={"Content-Type": "application/json"}
        )
        json = response.json()
        logger.debug(f"API响应: {url} with response: {json}", "phi-plugin:makeFetch")
        return json
    except Exception as e:
        logger.error(f"API请求失败, URL {url}", "phi-plugin", e=e)
        raise ValueError("API请求失败") from e


def burl(path: str) -> str:
    if base_url := PluginConfig.get("phiPluginApiUrl"):
        return f"{base_url}{path}"
    else:
        raise ValueError("请先设置API地址")
