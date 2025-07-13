from ..models import RksRank


class getRksRank:
    @classmethod
    async def addUserRks(cls, sessionToken, rks):
        """添加成绩"""
        return await RksRank.set_user_rks(sessionToken, rks * -1)

    @classmethod
    async def delUserRks(cls, sessionToken):
        """删除成绩"""
        return await RksRank.delete_user_rks(sessionToken)

    @classmethod
    async def getUserRks(cls, sessionToken):
        """获取用户rks"""
        return await RksRank.get_user_rks(sessionToken)

    @classmethod
    async def getUserRank(cls, sessionToken):
        """获取用户排名"""
        return await RksRank.getUserRank(sessionToken)

    @classmethod
    async def getRankUser(cls, min, max):
        """获取排名对应的用户"""
        return await RksRank.getRankUser(min, max)

    @classmethod
    async def getRankByRks(cls, rks: float):
        """获取指定rks的排名"""
        return await RksRank.getRankByRks(rks)

    @classmethod
    async def getAllRank(cls):
        """获取所有排名"""
        return await RksRank.getAllRank()
