from .ByteReader import ByteReader
from .Util import Util


class GameSettings:
    """游戏设置"""

    def __init__(self, data: bytes) -> None:
        """
        初始化

        :param data: 二进制数据
        """
        reader = ByteReader(data)
        tem = reader.getByte()
        self.chordSupport = Util.getBit(tem, 0)
        self.fcAPIndicator = Util.getBit(tem, 1)
        self.enableHitSound = Util.getBit(tem, 2)
        self.lowResolutionMode = Util.getBit(tem, 3)
        self.deviceName = reader.getString()
        self.bright = reader.getFloat()
        self.musicVolume = reader.getFloat()
        self.effectVolume = reader.getFloat()
        self.hitSoundVolume = reader.getFloat()
        self.soundOffset = reader.getFloat()
        self.noteScale = reader.getFloat()

