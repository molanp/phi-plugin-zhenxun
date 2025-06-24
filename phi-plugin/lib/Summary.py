import base64
import time

from .ByteReader import ByteReader


class Summary:
    """存档摘要"""

    def __init__(self, summary: str) -> None:
        """
        初始化

        :param summary: Base64编码的摘要数据
        """
        now = time.strftime("%Y %b.%d %H:%M:%S", time.localtime())
        self.updatedAt = now
        self.saveVersion = 0
        self.challengeModeRank = 0
        self.rankingScore = 0.0
        self.gameVersion = 0
        self.avatar = ""

        self.cleared: list[int] = [0, 0, 0, 0]
        self.fullCombo: list[int] = [0, 0, 0, 0]
        self.phi: list[int] = [0, 0, 0, 0]

        reader = ByteReader(base64.b64decode(summary))
        self.saveVersion = reader.getByte()
        self.challengeModeRank = reader.getShort()
        self.rankingScore = reader.getFloat()
        self.gameVersion = reader.getVarInt()
        self.avatar = reader.getString()
        for level in range(4):
            self.cleared[level] = reader.getShort()
            self.fullCombo[level] = reader.getShort()
            self.phi[level] = reader.getShort()
