from .SaveManager import SaveManager


class Util:
    """工具类"""

    @staticmethod
    def getBit(data: int, index: int) -> bool:
        """
        获取位值

        :param data: 数据
        :param index: 索引
        :return: 位值
        """
        return bool(data & (1 << index))

    @staticmethod
    def modifyBit(data: int, index: int, b: bool) -> int:
        """
        修改位值

        :param data: 数据
        :param index: 索引
        :param b: 新值
        :return: 修改后的数据
        """
        result = 1 << index
        if b:
            data |= result
        else:
            data &= ~result
        return data

    @staticmethod
    async def repair(session: str, index: int) -> str:
        """
        修复存档

        :param session: 会话令牌
        :param index: 存档索引
        :return: 修复结果
        """
        array = await SaveManager.saveArray(session)
        if len(array) == 1:
            raise ValueError("存档无误")

        builder = ""
        for i, item in enumerate(array):
            if i == index:
                continue
            response = await SaveManager.delete(session, item["objectId"])
            builder += str(response) + "\n"
        return builder
