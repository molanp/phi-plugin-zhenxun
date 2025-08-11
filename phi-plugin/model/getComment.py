"""评论操作相关"""

from typing import TypedDict

from ..models import Comment


class CommentDict(TypedDict):
    sessionToken: str
    """评论者sessionToken"""
    ObjectId: str
    """评论者ObjectId"""
    PlayerId: str
    """评论者PlayerId"""
    avatar: str
    """评论者头像"""
    rks: float
    """评论者rankingScore"""
    challenge: float
    """评论者challengeModeRank"""
    rank: str
    """曲目难度"""
    score: int
    """评论者分数"""
    acc: float
    """评论者准确率"""
    fc: bool
    """评论者是否fc"""
    spInfo: str
    """评论者谱面信息"""
    comment: str
    """评论内容"""


class getComment:
    @staticmethod
    async def getBySongId(songId: str):
        """获取对应曲目的所有评论"""
        return await Comment.filter(songId=songId).order_by("-created_at")

    @staticmethod
    async def getByCommentId(commentId: int):
        """获取CommentId对应评论"""
        return await Comment.get_or_none(commentId=commentId)

    @staticmethod
    async def getBySstkAndObjectId(sessionToken: str, ObjectId: str):
        """获取sessionToken和ObjectId的全部评论"""
        return await Comment.filter(
            sessionToken=sessionToken, ObjectId=ObjectId
        ).order_by("-created_at")

    @staticmethod
    async def update(commentId: int, comment: CommentDict):
        """更新评论"""
        if Comment.exists(commentId=commentId):
            await Comment.filter(commentId=commentId).update(**comment)
            return True
        return False

    @staticmethod
    async def add(songId: str, comment: CommentDict):
        """添加评论"""
        return bool(await Comment.create(songId=songId, **comment))

    @staticmethod
    async def delete(commentId: int):
        """删除评论"""
        return bool(await Comment.filter(commentId=commentId).delete())
