from .ByteReader import ByteReader
from .Util import Util


class GameProgress:
    """游戏进度"""

    def __init__(self, data: bytes | str) -> None:
        """
        初始化

        :param data: 二进制数据
        """
        reader = ByteReader(data)
        tem = reader.getByte()
        self.isFirstRun = Util.getBit(tem, 0)
        self.legacyChapterFinished = Util.getBit(tem, 1)
        self.alreadyShowCollectionTip = Util.getBit(tem, 2)
        self.alreadyShowAutoUnlockINTip = Util.getBit(tem, 3)
        self.completed = reader.getString()
        self.songUpdateInfo = reader.getVarInt()
        self.challengeModeRank = reader.getShort()
        self.money: list[int] = [0, 0, 0, 0, 0]
        self.money[0] = reader.getVarInt()
        self.money[1] = reader.getVarInt()
        self.money[2] = reader.getVarInt()
        self.money[3] = reader.getVarInt()
        self.money[4] = reader.getVarInt()
        self.unlockFlagOfSpasmodic = reader.getByte()
        self.unlockFlagOfIgallta = reader.getByte()
        self.unlockFlagOfRrharil = reader.getByte()
        self.flagOfSongRecordKey = reader.getByte()
        self.randomVersionUnlocked = reader.getByte()
        tem = reader.getByte()
        self.chapter8UnlockBegin = Util.getBit(tem, 0)
        self.chapter8UnlockSecondPhase = Util.getBit(tem, 1)
        self.chapter8Passed = Util.getBit(tem, 2)
        self.chapter8SongUnlocked = reader.getByte()
