from .getdata import get


class money:
    @staticmethod
    async def getNoteNum(user_id: str):
        return await get.getpluginData(user_id)
