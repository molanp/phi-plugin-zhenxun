from ..models import RksRank


class getRksRank:
    @staticmethod
    async def addUserRks(sessionToken: str, rks: float):
        """添加成绩"""
        return await RksRank.set_user_rks(sessionToken, rks)

    @staticmethod
    async def delUserRks(sessionToken: str):
        """删除成绩"""
        return await RksRank.delete_user_rks(sessionToken)

    @staticmethod
    async def getUserRks(sessionToken: str):
        """获取用户rks"""
        return await RksRank.get_user_rks(sessionToken)

    @staticmethod
    async def getUserRank(sessionToken: str):
        """获取用户排名"""
        return await RksRank.getUserRank(sessionToken)

    @staticmethod
    async def getRankUser(min: int, max: int):
        """获取排名对应的用户sessionToken"""
        return await RksRank.getRankUser(min, max)

    @staticmethod
    async def getRankByRks(rks: float):
        """获取指定rks的排名"""
        return await RksRank.getRankByRks(rks)

    @staticmethod
    async def getAllRank():
        """获取排名总数"""
        return await RksRank.getAllRank()
