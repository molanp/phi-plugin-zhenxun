from typing import ClassVar

from tortoise import fields

from zhenxun.services.db_context import Model


class SstkData(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    uid = fields.TextField(description="用户uid")
    """用户图寻uid"""
    sessionToken = fields.TextField(description="用户SessionToken")
    """用户图寻昵称"""
    is_banned = fields.BooleanField(
        default=False,
        description="是否被封禁",
        help_text="True: 被封禁, False: 未被封禁",
    )
    """是否被封禁"""

    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        table = "phiPlugin_sstkData"
        table_description = "Phi sstk 数据表"
        indexes: ClassVar = [("uid", "sessionToken")]

    @classmethod
    async def _exists(cls, **filters) -> bool:
        """
        检测符合过滤条件的用户是否存在

        :param filters: 过滤条件（如uid='123', uin='456'）
        :return: 存在返回True，否则False
        """
        return await cls.filter(**filters).exists()

    @classmethod
    async def get_sstk(cls, uid: str) -> str | None:
        """
        获取用户数据

        :param uid: 用户uid
        :return: 用户sessionToken
        """
        data = await cls.get_or_none(uid=uid)
        return data.sessionToken if data else None

    @classmethod
    async def add_sstk(cls, uid: str, sessionToken: str) -> bool:
        """
        添加用户数据
        :param uid: 用户uid
        :param sessionToken: 用户sessionToken
        :return: 是否添加成功
        """
        data = await cls.get_or_none(uid=uid)
        if data:
            data.sessionToken = sessionToken
        else:
            data = cls(uid=uid, sessionToken=sessionToken)
        await data.save()
        return True

    @classmethod
    async def delete_sstk(cls, uid: str) -> bool:
        """
        删除用户数据
        :param uid: 用户uid
        :return: 是否删除成功
        """
        data = await cls.get_or_none(uid=uid)
        if data:
            await data.delete()
            return True
        return False

    @classmethod
    async def ban_sstk(cls, uid: str) -> bool:
        """
        封禁用户数据
        :param uid: 用户uid
        :return: 是否封禁成功
        """
        data = await cls.get_or_none(uid=uid, is_banned=False)
        if data:
            data.is_banned = True
            await data.save()
            return True
        return False

    @classmethod
    async def unban_sstk(cls, uid: str) -> bool:
        """
        解封用户数据
        :param uid: 用户uid
        :return: 是否解封成功
        """
        data = await cls.get_or_none(uid=uid, is_banned=True)
        if data:
            data.is_banned = False
            await data.save()
            return True
        return False

    @classmethod
    async def is_ban_sessionToken(cls, sessionToken: str) -> bool:
        """
        检测 sessionToken 是否被封禁
        :param sessionToken: 用户sessionToken
        :return: 是否被封禁
        """
        data = await cls.get_or_none(sessionToken=sessionToken, is_banned=True)
        return bool(data)

    @classmethod
    async def get_ban_sstk(cls) -> list[str]:
        """
        获取所有被封禁的 sessionToken
        :return: 被封禁的 sessionToken 列表
        """
        data = await cls.filter(is_banned=True).values_list("sessionToken", flat=True)
        return list(data)  # type: ignore


class RksRank(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增ID"""
    sessionToken = fields.TextField(description="用户SessionToken")
    """关联用户的SessionToken"""
    rks = fields.FloatField(description="用户RKS分数")
    """用户的RKS数值"""
    created_at = fields.DatetimeField(auto_now_add=True)
    """记录创建时间"""
    updated_at = fields.DatetimeField(auto_now=True)
    """最后更新时间"""

    class Meta:  # type: ignore
        table = "phiPlugin_rksRank"
        table_description = "Phi RKS数据表"
        indexes: ClassVar = [
            ("sessionToken", "rks"),
        ]

    @classmethod
    async def get_user_rks(cls, sessionToken: str) -> float | None:
        """
        获取用户RKS
        :param sessionToken: 用户SessionToken
        :return: 用户RKS
        """
        data = await cls.get_or_none(sessionToken=sessionToken)
        return data.rks if data else None

    @classmethod
    async def set_user_rks(cls, sessionToken: str, rks: float) -> bool:
        """
        添加/设置用户RKS
        :param sessionToken: 用户SessionToken
        :param rks: 用户RKS
        """
        data = await cls.get_or_none(sessionToken=sessionToken)
        if data:
            data.rks = rks
        else:
            data = cls(sessionToken=sessionToken, rks=rks)
        await data.save()
        return True

    @classmethod
    async def delete_user_rks(cls, sessionToken: str) -> bool:
        """
        删除用户RKS
        :param sessionToken: 用户SessionToken
        :return: 是否删除成功
        """
        data = await cls.get_or_none(sessionToken=sessionToken)
        if data:
            await data.delete()
            return True
        return False

    @classmethod
    async def getAllRank(cls) -> list[dict]:
        """
        获取RKS排名
        :param limit: 排行榜限制数量
        :return: 排行榜数据
        """
        return await cls.filter().order_by("-rks").values()

    @classmethod
    async def getUserRank(cls, sessionToken: str) -> int | None:
        """
        获取用户排名
        :param sessionToken: 用户SessionToken
        :return: 用户排名
        """
        data = await cls.get_or_none(sessionToken=sessionToken)
        return data.id if data else None

    @classmethod
    async def getRankUsers(cls, min_rank: int, max_rank: int) -> list[dict]:
        """
        获取指定排名范围的用户数据（基于RKS分数降序）

        :param min_rank: 起始排名（0起始）
        :param max_rank: 结束排名（不包含）
        :return: 包含用户数据的字典列表
        """
        # 按 RKS 降序排列，从 min_rank 开始取 (max_rank - min_rank) 条记录
        query = (
            cls.filter().order_by("-rks").offset(min_rank).limit(max_rank - min_rank)
        )
        return await query.values()
