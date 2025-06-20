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
