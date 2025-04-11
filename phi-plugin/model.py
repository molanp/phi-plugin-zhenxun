from typing import ClassVar

from tortoise import fields
from zhenxun.services.db_context import Model


class PhigrosUserData(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    uid = fields.TextField(description="用户唯一标识符（类型+用户ID组合）")
    """用户id"""
    sessionToken = fields.TextField(null=True, default=None)
    """sessionToken"""

    class Meta:  # pyright: ignore [reportIncompatibleVariableOverride]
        table = "phigros_user_data"
        table_description = "Phigros用户数据表"
        indexes: ClassVar = [("uid",)]

    @classmethod
    async def get_session_token(cls, uid) -> str | None:
        user = await PhigrosUserData.get_or_none(uid=uid)
        return user.sessionToken if user else None

    @classmethod
    async def set_session_token(cls, uid, sessionToken) -> str:
        user, created = await PhigrosUserData.get_or_create(uid=uid)
        if not created:
            user.sessionToken = sessionToken
            await user.save(update_fields=["sessionToken"])
        return uid

    @classmethod
    async def delete_session_token(cls, uid) -> str:
        user = await PhigrosUserData.get_or_none(uid=uid)
        if user:
            await user.delete()
        return uid
