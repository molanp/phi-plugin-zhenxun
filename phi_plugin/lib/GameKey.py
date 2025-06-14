from zhenxun.services.log import logger

from .GameKeyValue import GameKeyValue
from .SaveModule import MapSaveModule
from .Util import Util


class GameKey(MapSaveModule):
    """游戏键类"""

    def __init__(self) -> None:
        """初始化"""
        super().__init__()
        self.name: str = "gameKey"
        self.version: int = 1
        self.lanotaReadKeys: int = 0

    def getBytes(self, outputStream: list[int], entry: tuple) -> None:
        """
        获取字节数组

        :param outputStream: 输出流
        :param entry: 键值对
        """
        try:
            key, value = entry
            # 写入键
            strBytes = key.encode()
            outputStream.append(len(strBytes))
            outputStream.extend(strBytes)
            # 写入值
            length = 0
            num = 1
            for index in range(5):
                if value.get(index) != 0:
                    length = Util.modifyBit(length, index, True)
                    num += 1
            outputStream.append(num)
            outputStream.append(length)
            for index in range(5):
                if value.get(index) != 0:
                    outputStream.append(value.get(index))
        except Exception as e:
            logger.error(f"获取字节数组失败: {e}", "phi-plugin")
            raise ValueError(f"获取字节数组失败: {e}")

    def putBytes(self, data: bytes, position: int) -> None:
        """
        写入字节数组

        :param data: 数据
        :param position: 位置
        """
        try:
            # 读取键
            keyLength = data[position]
            key = data[position + 1 : position + 1 + keyLength].decode()
            position += keyLength + 2
            # 读取值
            length = data[position]
            position += 1
            value = GameKeyValue()
            for index in range(5):
                if Util.getBit(length, index):
                    value.set(index, data[position])
                    position += 1
            self[key] = value
        except Exception as e:
            logger.error(f"写入字节数组失败: {e}", "phi-plugin")
            raise ValueError(f"写入字节数组失败: {e}")
