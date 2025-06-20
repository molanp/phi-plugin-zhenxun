import base64
import struct


class ByteReader:
    def __init__(self, data, position=0):
        # 如果是str，假定是hex字符串；如果是bytes或bytearray，直接用
        if isinstance(data, str):
            self.data = bytearray.fromhex(data)
        else:
            self.data = bytearray(data)
        self.position = position

    def remaining(self):
        """返回剩余的字节数"""
        return len(self.data) - self.position

    def getByte(self):
        val = self.data[self.position]
        self.position += 1
        return val

    def putByte(self, num):
        self.data[self.position] = num
        self.position += 1

    def getAllByte(self):
        return base64.b64encode(self.data[self.position :]).decode()

    def getShort(self):
        self.position += 2
        return (self.data[self.position - 1] << 8) ^ (
            self.data[self.position - 2] & 0xFF
        )

    def putShort(self, num):
        self.data[self.position] = num & 0xFF
        self.position += 1
        self.data[self.position] = (num >> 8) & 0xFF
        self.position += 1

    def getInt(self):
        self.position += 4
        return (
            (self.data[self.position - 1] << 24)
            ^ ((self.data[self.position - 2] & 0xFF) << 16)
            ^ ((self.data[self.position - 3] & 0xFF) << 8)
            ^ (self.data[self.position - 4] & 0xFF)
        )

    def putInt(self, num):
        self.data[self.position] = num & 0xFF
        self.data[self.position + 1] = (num >> 8) & 0xFF
        self.data[self.position + 2] = (num >> 16) & 0xFF
        self.data[self.position + 3] = (num >> 24) & 0xFF
        self.position += 4

    def getFloat(self):
        val = struct.unpack_from("<f", self.data, self.position)[0]
        self.position += 4
        return val

    def putFloat(self, num):
        struct.pack_into("<f", self.data, self.position, num)
        self.position += 4

    def getVarInt(self):
        if self.data[self.position] > 127:
            self.position += 2
            return (0b01111111 & self.data[self.position - 2]) ^ (
                self.data[self.position - 1] << 7
            )
        else:
            val = self.data[self.position]
            self.position += 1
            return val

    def skipVarInt(self, num=None):
        if num:
            for _ in range(num):
                self.skipVarInt()
        else:
            if self.data[self.position] < 0:
                self.position += 2
            else:
                self.position += 1

    def getBytes(self):
        length = self.getByte()
        self.position += length
        return self.data[self.position - length : self.position]

    def getString(self):
        length = self.getVarInt()
        self.position += length
        return self.data[self.position - length : self.position].decode("utf-8")

    def putString(self, s):
        b = s.encode("utf-8")
        self.data[self.position] = len(b)
        self.position += 1
        self.data[self.position : self.position + len(b)] = b
        self.position += len(b)

    def skipString(self):
        self.position += self.getByte() + 1

    def insertBytes(self, bytes_):
        result = bytearray(len(self.data) + len(bytes_))
        result[0 : self.position] = self.data[0 : self.position]
        result[self.position : self.position + len(bytes_)] = bytes_
        result[self.position + len(bytes_) :] = self.data[self.position :]
        self.data = result

    def replaceBytes(self, length, bytes_):
        if len(bytes_) == length:
            self.data[self.position : self.position + length] = bytes_
            return
        result = bytearray(len(self.data) + len(bytes_) - length)
        result[0 : self.position] = self.data[0 : self.position]
        result[self.position : self.position + len(bytes_)] = bytes_
        result[self.position + len(bytes_) :] = self.data[self.position + length :]
        self.data = result
