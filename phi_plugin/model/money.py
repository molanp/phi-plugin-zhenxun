from .getdata import getdata


class money:
    @staticmethod
    async def getNoteNum(user_id: str):
        return await getdata.getpluginData(user_id)
