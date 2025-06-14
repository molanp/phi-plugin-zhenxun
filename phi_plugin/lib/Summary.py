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

        self.cleared: list[int] = [0] * 4
        self.fullCombo: list[int] = [0] * 4
        self.phi: list[int] = [0] * 4

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

    def serialize(self) -> str:
        """
        序列化

        :return: Base64编码的序列化数据
        """
        reader = ByteReader(bytearray(33 + len(self.avatar.encode())))
        reader.putByte(self.saveVersion)
        reader.putShort(self.challengeModeRank)
        reader.putFloat(self.rankingScore)
        reader.putInt(self.gameVersion)
        reader.putString(self.avatar)
        for level in range(4):
            reader.putShort(self.cleared[level])
            reader.putShort(self.fullCombo[level])
            reader.putShort(self.phi[level])
        return base64.b64encode(reader.data).decode()

    def __str__(self) -> str:
        """
        获取字符串表示

        :return: 字符串表示
        """
        return f'{{"存档版本":{self.saveVersion},"课题分":{self.challengeModeRank},"RKS":{self.rankingScore:.4f},"游戏版本":{self.gameVersion},"头像":"{self.avatar}","EZ":[{self.cleared[0]},{self.fullCombo[0]},{self.phi[0]}],"HD":[{self.cleared[1]},{self.fullCombo[1]},{self.phi[1]}],"IN":[{self.cleared[2]},{self.fullCombo[2]},{self.phi[2]}],"AT":[{self.cleared[3]},{self.fullCombo[3]},{self.phi[3]}]}}'

    def to_string(self, save_url: str | None = None) -> str:
        """
        获取带存档URL的字符串表示

        :param save_url: 存档URL
        :return: 字符串表示
        """
        if save_url:
            return f'{{"saveUrl":"{save_url}","存档版本":{self.saveVersion},"课题分":{self.challengeModeRank},"RKS":{self.rankingScore:.4f},"游戏版本":{self.gameVersion},"头像":"{self.avatar}","EZ":[{self.cleared[0]},{self.fullCombo[0]},{self.phi[0]}],"HD":[{self.cleared[1]},{self.fullCombo[1]},{self.phi[1]}],"IN":[{self.cleared[2]},{self.fullCombo[2]},{self.phi[2]}],"AT":[{self.cleared[3]},{self.fullCombo[3]},{self.phi[3]}]}}'
        return str(self)
