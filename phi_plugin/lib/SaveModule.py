import inspect
import struct

from zhenxun.services.log import logger

from .GameKey import GameKey
from .Util import Util


class SaveModule:
    """存档模块基类"""

    @classmethod
    def loadFromBinary(cls, data: bytes) -> None:
        """
        从二进制数据加载

        :param data: 二进制数据
        """
        try:
            index = 0
            position = 0
            # 获取类的所有字段，保持声明顺序
            fields = inspect.getmembers(
                cls, lambda x: not inspect.isfunction(x) and not x.startswith("__")
            )
            for field_name, field_value in fields:
                field_type = type(field_value)
                if field_type is bool:
                    setattr(cls, field_name, Util.getBit(data[position], index))
                    index += 1
                    continue
                if index != 0:
                    index = 0
                    position += 1

                if field_type is str:
                    length = data[position]
                    position += 1
                    setattr(
                        cls, field_name, data[position : position + length].decode()
                    )
                    position += length
                elif field_type is float:
                    setattr(cls, field_name, SaveModule.getFloat(data, position))
                    position += 4
                elif field_type is int:
                    setattr(cls, field_name, SaveModule.getShort(data, position))
                    position += 2
                elif field_type is list:
                    array = getattr(cls, field_name)
                    for i in range(len(array)):
                        array[i] = SaveModule.getVarShort(data, position)
                        position += 2 if data[position] < 0 else 1
                elif field_type is bytes:
                    setattr(cls, field_name, data[position])
                    position += 1
                else:
                    raise ValueError("出现新类型。")
        except Exception as e:
            logger.error("加载二进制数据失败", "phi-plugin",e=e)
            raise ValueError("加载二进制数据失败") from e

    @classmethod
    def serialize(cls) -> bytes:
        """
        序列化

        :return: 序列化后的二进制数据
        """
        try:
            outputStream = []
            b = 0
            index = 0
            # 获取类的所有字段，保持声明顺序
            fields = inspect.getmembers(
                cls, lambda x: not inspect.isfunction(x) and not x.startswith("__")
            )
            for field_name, field_value in fields:
                field_type = type(field_value)
                if field_type is bool:
                    b = Util.modifyBit(b, index, field_value)
                    index += 1
                    continue
                if b != 0 and index != 0:
                    outputStream.append(b)
                    b = index = 0

                if field_type is str:
                    bytes_data = field_value.encode()
                    outputStream.append(len(bytes_data))
                    outputStream.extend(bytes_data)
                elif field_type is float:
                    outputStream.extend(SaveModule.float2bytes(field_value))
                elif field_type is int:
                    outputStream.extend(SaveModule.short2bytes(field_value))
                elif field_type is list:
                    for h in field_value:
                        outputStream.extend(SaveModule.varShort2bytes(h))
                elif field_type is bytes:
                    outputStream.append(field_value)
                else:
                    raise ValueError("出现新类型。")
            return bytes(outputStream)
        except Exception as e:
            logger.error("序列化失败", "phi-plugin",e=e)
            raise ValueError("序列化失败") from e

    @staticmethod
    def getInt(data: bytes, position: int) -> int:
        """
        获取整型

        :param data: 数据
        :param position: 位置
        :return: 整型值
        """
        return (
            (data[position + 3] << 24)
            ^ ((data[position + 2] & 0xFF) << 16)
            ^ ((data[position + 1] & 0xFF) << 8)
            ^ (data[position] & 0xFF)
        )

    @staticmethod
    def int2bytes(num: int) -> bytes:
        """
        整型转字节数组

        :param num: 整型值
        :return: 字节数组
        """
        return bytes(
            [
                num & 0xFF,
                (num >> 8) & 0xFF,
                (num >> 16) & 0xFF,
                (num >> 24) & 0xFF,
            ]
        )

    @staticmethod
    def getShort(data: bytes, position: int) -> int:
        """
        获取短整型

        :param data: 数据
        :param position: 位置
        :return: 短整型值
        """
        return ((data[position + 1] & 0xFF) << 8) ^ (data[position] & 0xFF)

    @staticmethod
    def short2bytes(num: int) -> bytes:
        """
        短整型转字节数组

        :param num: 短整型值
        :return: 字节数组
        """
        return bytes([num & 0xFF, (num >> 8) & 0xFF])

    @staticmethod
    def getVarShort(data: bytes, position: int) -> int:
        """
        获取变长短整型

        :param data: 数据
        :param position: 位置
        :return: 变长短整型值
        """
        if data[position] >= 0:
            return data[position]
        return (data[position + 1] << 7) ^ (data[position] & 0x7F)

    @staticmethod
    def varShort2bytes(num: int) -> bytes:
        """
        变长短整型转字节数组

        :param num: 变长短整型值
        :return: 字节数组
        """
        return (
            bytes([num])
            if num < 128
            else bytes([(num & 0x7F) | 0x80, (num >> 7) & 0xFF])
        )

    @staticmethod
    def getFloat(data: bytes, position: int) -> float:
        """
        获取浮点数

        :param data: 数据
        :param position: 位置
        :return: 浮点数值
        """
        return struct.unpack("<f", data[position : position + 4])[0]

    @staticmethod
    def float2bytes(num: float) -> bytes:
        """
        浮点数转字节数组

        :param num: 浮点数值
        :return: 字节数组
        """
        return struct.pack("<f", num)


class MapSaveModule(dict):
    """映射存档模块类"""

    def loadFromBinary(self, data: bytes) -> None:
        """
        从二进制数据加载

        :param data: 二进制数据
        """
        try:
            self.clear()
            length = SaveModule.getVarShort(data, 0)
            position = 2 if data[0] < 0 else 1
            for _ in range(length):
                self.putBytes(data, position)
                keyLength = data[position]
                position += keyLength + data[position + keyLength + 1] + 2
            if isinstance(self, GameKey):
                self.lanotaReadKeys = data[position]
        except Exception as e:
            logger.error("加载二进制数据失败", "phi-plugin", e=e)
            raise ValueError("加载二进制数据失败") from e

    def serialize(self) -> bytes:
        """
        序列化

        :return: 序列化后的二进制数据
        """
        try:
            outputStream = []
            outputStream.extend(SaveModule.varShort2bytes(len(self)))
            for key, value in self.items():
                self.getBytes(outputStream, (key, value))
            if isinstance(self, GameKey):
                outputStream.append(self.lanotaReadKeys)
            return bytes(outputStream)
        except Exception as e:
            logger.error("序列化失败", "phi-plugin",e=e)
            raise ValueError("序列化失败") from e

    def getBytes(self, outputStream: list[int], entry: tuple) -> None:
        """
        获取字节数组

        :param outputStream: 输出流
        :param entry: 键值对
        """
        raise NotImplementedError("子类必须实现此方法")

    def putBytes(self, data: bytes, position: int) -> None:
        """
        写入字节数组

        :param data: 数据
        :param position: 位置
        """
        raise NotImplementedError("子类必须实现此方法")
