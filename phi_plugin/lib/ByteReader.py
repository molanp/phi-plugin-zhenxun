import base64
import struct

from zhenxun.services.log import logger


class ByteReader:
    """字节读取器类"""

    def __init__(self, data: str | bytes | bytearray, position: int = 0):
        """
        初始化字节读取器

        :param data: 数据
        :param position: 起始位置
        """
        if isinstance(data, str):
            self.data = bytearray.fromhex(data)
        else:
            self.data = bytearray(data)
        self.position = position

    def remaining(self) -> int:
        """
        返回剩余的字节数

        :return: 剩余字节数
        """
        return len(self.data) - self.position

    def getByte(self) -> int:  # sourcery skip: class-extract-method
        """
        读取一个字节

        :return: 读取的字节值
        """
        result = self.data[self.position]
        self.position += 1
        return result

    def putByte(self, num: int) -> None:
        """
        写入一个字节

        :param num: 要写入的字节值
        """
        self.data[self.position] = num & 0xFF
        self.position += 1

    def getAllByte(self) -> bytes:
        """
        返回base64编码的数据

        :return: base64编码的数据
        """
        try:
            return base64.b64decode(self.data[self.position :])
        except Exception as e:
            logger.error("解码 base64 数据失败", "phi-plugin", e=e)
            raise ValueError(f"解码 base64 数据失败: {e}") from e

    def getShort(self) -> int:
        """
        读取一个短整型

        :return: 读取的短整型值
        """
        self.position += 2
        return (self.data[self.position - 1] << 8) ^ (
            self.data[self.position - 2] & 0xFF
        )

    def putShort(self, num: int) -> None:
        """
        写入一个短整型

        :param num: 要写入的短整型值
        """
        self.data[self.position] = num & 0xFF
        self.data[self.position + 1] = (num >> 8) & 0xFF
        self.position += 2

    def getInt(self) -> int:
        """
        读取一个整型

        :return: 读取的整型值
        """
        self.position += 4
        return (
            (self.data[self.position - 1] << 24)
            ^ ((self.data[self.position - 2] & 0xFF) << 16)
            ^ ((self.data[self.position - 3] & 0xFF) << 8)
            ^ (self.data[self.position - 4] & 0xFF)
        )

    def putInt(self, num: int) -> None:
        """
        写入一个整型

        :param num: 要写入的整型值
        """
        self.data[self.position] = num & 0xFF
        self.data[self.position + 1] = (num >> 8) & 0xFF
        self.data[self.position + 2] = (num >> 16) & 0xFF
        self.data[self.position + 3] = (num >> 24) & 0xFF
        self.position += 4

    def getFloat(self) -> float:
        """
        读取一个浮点数

        :return: 读取的浮点数值
        """
        try:
            self.position += 4
            return struct.unpack(
                "<f", bytes(self.data[self.position - 4 : self.position])
            )[0]
        except Exception as e:
            logger.error("读取浮点数失败", "phi-plugin", e=e)
            raise ValueError(f"读取浮点数失败: {e}") from e

    def putFloat(self, num: float) -> None:
        """
        写入一个浮点数

        :param num: 要写入的浮点数值
        """
        try:
            self.position += 4
            struct.pack_into("<f", self.data, self.position - 4, num)
        except Exception as e:
            logger.error("写入浮点数失败", "phi-plugin", e=e)
            raise ValueError(f"写入浮点数失败: {e}") from e

    def getVarInt(self) -> int:
        """
        读取一个变长整型

        :return: 读取的变长整型值
        """
        if self.data[self.position] > 127:
            self.position += 2
            return (0b01111111 & self.data[self.position - 2]) ^ (
                self.data[self.position - 1] << 7
            )
        else:
            result = self.data[self.position]
            self.position += 1
            return result

    def skipVarInt(self, num: int | None = None) -> None:
        """
        跳过变长整型

        :param num: 要跳过的数量
        """
        if num:
            for _ in range(num):
                self.skipVarInt()
        else:
            self.position += 2 if self.data[self.position] < 0 else 1

    def getBytes(self) -> bytes:
        """
        读取字节数组

        :return: 读取的字节数组
        """
        try:
            length = self.getByte()
            self.position += length
            return bytes(self.data[self.position - length : self.position])
        except Exception as e:
            logger.error("读取字节数组失败", "phi-plugin", e=e)
            raise ValueError(f"读取字节数组失败: {e}") from e

    def getString(self) -> str:
        """
        读取字符串

        :return: 读取的字符串
        """
        try:
            length = self.getVarInt()
            self.position += length
            return self.data[self.position - length : self.position].decode("utf-8")
        except Exception as e:
            logger.error("读取字符串失败", "phi-plugin", e=e)
            raise ValueError(f"读取字符串失败: {e}") from e

    def putString(self, s: str) -> None:
        """
        写入字符串

        :param s: 要写入的字符串
        """
        try:
            b = s.encode("utf-8")
            self.data[self.position] = len(b)
            self.position += 1
            self.data[self.position : self.position + len(b)] = b
            self.position += len(b)
        except Exception as e:
            logger.error("写入字符串失败", "phi-plugin", e=e)
            raise ValueError(f"写入字符串失败: {e}") from e

    def skipString(self) -> None:
        """
        跳过字符串
        """
        try:
            self.position += self.getByte() + 1
        except Exception as e:
            logger.error("跳过字符串失败", "phi-plugin", e=e)
            raise ValueError(f"跳过字符串失败: {e}") from e

    def insertBytes(self, bytesData: bytes) -> None:
        """
        插入字节数组

        :param bytesData: 要插入的字节数组
        """
        try:
            result = bytearray(len(self.data) + len(bytesData))
            result[: self.position] = self.data[: self.position]
            result[self.position : self.position + len(bytesData)] = bytesData
            result[self.position + len(bytesData) :] = self.data[self.position :]
            self.data = result
        except Exception as e:
            logger.error("插入字节数组失败", "phi-plugin", e=e)
            raise ValueError(f"插入字节数组失败: {e}") from e

    def replaceBytes(self, length: int, bytesData: bytes) -> None:
        """
        替换字节数组

        :param length: 要替换的长度
        :param bytesData: 要替换的字节数组
        """
        try:
            if len(bytesData) == length:
                self.data[self.position : self.position + length] = bytesData
                return
            result = bytearray(len(self.data) + len(bytesData) - length)
            result[: self.position] = self.data[: self.position]
            result[self.position : self.position + len(bytesData)] = bytesData
            result[self.position + len(bytesData) :] = self.data[
                self.position + length :
            ]
            self.data = result
        except Exception as e:
            logger.error("替换字节数组失败", "phi-plugin", e=e)
            raise ValueError(f"替换字节数组失败: {e}") from e
