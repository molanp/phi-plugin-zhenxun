from zhenxun.services.log import logger


class GameKeyValue:
    """游戏键值类"""

    def __init__(self) -> None:
        """初始化"""
        self.readCollection: int = 0
        self.unlockSingle: bool = False
        self.collection: int = 0
        self.illustration: bool = False
        self.avatar: bool = False

    def get(self, index: int) -> int | bool:
        """
        获取值

        :param index: 索引
        :return: 值
        """
        try:
            if index == 0:
                return self.readCollection
            elif index == 1:
                return self.bool2int(self.unlockSingle)
            elif index == 2:
                return self.collection
            elif index == 3:
                return self.bool2int(self.illustration)
            elif index == 4:
                return self.bool2int(self.avatar)
            else:
                raise ValueError("get参数超出范围。")
        except Exception as e:
            logger.error(f"获取值失败: {e}", "phi-plugin")
            raise ValueError(f"获取值失败: {e}")

    def set(self, index: int, value: int | bool) -> None:
        """
        设置值

        :param index: 索引
        :param value: 值
        """
        try:
            if index == 0:
                self.readCollection = value
            elif index == 1:
                self.unlockSingle = self.int2bool(value)
            elif index == 2:
                self.collection = value
            elif index == 3:
                self.illustration = self.int2bool(value)
            elif index == 4:
                self.avatar = self.int2bool(value)
            else:
                raise ValueError("set参数超出范围。")
        except Exception as e:
            logger.error(f"设置值失败: {e}", "phi-plugin")
            raise ValueError(f"设置值失败: {e}")

    def int2bool(self, value: int) -> bool:
        """
        将整数转换为布尔值

        :param value: 整数
        :return: 布尔值
        """
        if value == 0:
            return False
        elif value == 1:
            return True
        else:
            raise ValueError("int2bool参数超出范围。")

    def bool2int(self, value: bool) -> int:
        """
        将布尔值转换为整数

        :param value: 布尔值
        :return: 整数
        """
        return 1 if value else 0
