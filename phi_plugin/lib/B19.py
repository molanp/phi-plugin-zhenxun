from collections.abc import Iterator

from .ByteReader import ByteReader
from .PhigrosUser import PhigrosUser
from .SongExpect import SongExpect
from .SongLevel import SongLevel
from .Util import Util

# from .Level import Level  # 需根据实际 Level 枚举实现


class B19:
    """B19 计算类"""

    def __init__(self, data: bytes) -> None:
        self.data: bytes = data
        self.reader: ByteReader = ByteReader(data)
        self.length: int | None = None
        self.fc: int | None = None

    def __iter__(self) -> Iterator[str]:
        index = 0
        length = len(self.data)
        reader = self.reader
        while index < length:
            id_ = reader.getString()
            index += len(id_) + 1
            yield id_

# TODO: 逆天函数我找不到这个定义，
    def getB19(self, num: int) -> list[SongLevel]:
        minIndex = 1
        b19: list[SongLevel] = [SongLevel() for _ in range(num + 1)]
        for id_ in self:
            levels = PhigrosUser().getSaveInfo()
            level = len(levels) - 1
            while level >= 0:
                if levels[level] <= b19[minIndex].rks and levels[level] <= b19[0].rks:
                    break
                level -= 1
            level += 1
            if level == len(levels):
                continue
            self.length = self.reader.getByte()
            self.fc = self.reader.getByte()
            self.go(level)
            for l in range(level, len(levels)):
                if self.levelNotExist(l):
                    continue
                songLevel = SongLevel()
                songLevel.s = self.reader.getInt()
                songLevel.a = self.reader.getFloat()
                if songLevel.a < 70:
                    continue
                if songLevel.s == 1000000:
                    songLevel.rks = levels[l]
                    if levels[l] > b19[0].rks:
                        songLevel.set(id_, l, self.getFC(l), levels[l])
                        b19[0] = songLevel
                else:
                    songLevel.rks = (songLevel.a - 55) / 45
                    songLevel.rks *= songLevel.rks * levels[l]
                if songLevel.rks < b19[minIndex].rks:
                    continue
                songLevel.set(id_, l, self.getFC(l), levels[l])
                b19[minIndex] = songLevel
                minIndex = self._minSongLevel(b19)
        for minIndex in range(1, 20):
            if getattr(b19[minIndex], "id", None) is None:
                break
        b19.sort(key=lambda x: x.rks)
        return b19[: num + 1]

    def getExpect(self, id_: str) -> list[SongExpect]:
        for songId in self:
            if songId != id_:
                continue
            minRks = self.getMinRks()
            levels = PhigrosUser.getInfo(id_)
            self.length = self.reader.getByte()
            self.reader.position += 1
            lst: list[SongExpect] = []
            for level in range(len(levels)):
                if self.levelNotExist(level):
                    continue
                if levels[level] <= minRks:
                    continue
                score = self.reader.getInt()
                if score == 1000000:
                    continue
                acc = self.reader.getFloat()
                expect = (minRks / levels[level]) ** 0.5 * 45 + 55
                if expect > acc:
                    lst.append(SongExpect(id_, level, acc, expect))
            return lst
        raise ValueError("不存在该id的曲目。")

    def getExpects(self) -> list[SongExpect]:
        minRks = self.getMinRks()
        lst: list[SongExpect] = []
        for id_ in self:
            levels = PhigrosUser.getInfo(id_)
            level = len(levels) - 1
            while level >= 0:
                if levels[level] <= minRks:
                    break
                level -= 1
            level += 1
            if level == len(levels):
                continue
            self.length = self.reader.getByte()
            self.reader.position += 1
            self.go(level)
            for l in range(level, len(levels)):
                if self.levelNotExist(l):
                    continue
                score = self.reader.getInt()
                if score == 1000000:
                    self.reader.position += 4
                    continue
                acc = self.reader.getFloat()
                expect = (minRks / levels[l]) ** 0.5 * 45 + 55
                if expect > acc:
                    lst.append(SongExpect(id_, l, acc, expect))
        lst.sort(key=lambda x: x.rks)
        return lst

    def getMinRks(self) -> float:
        minIndex = 0
        b19 = [0.0 for _ in range(19)]
        for id_ in self:
            levels = PhigrosUser.getInfo(id_)
            level = len(levels) - 1
            while level >= 0:
                if levels[level] <= b19[minIndex]:
                    break
                level -= 1
            level += 1
            if level == len(levels):
                continue
            self.length = self.reader.getByte()
            self.fc = self.reader.getByte()
            self.go(level)
            for l in range(level, len(levels)):
                if self.levelNotExist(l):
                    continue
                score = self.reader.getInt()
                acc = self.reader.getFloat()
                if acc < 70:
                    continue
                if score == 1000000:
                    rks = levels[l]
                else:
                    rks = (acc - 55) / 45
                    rks *= rks * levels[l]
                if rks <= b19[minIndex]:
                    continue
                b19[minIndex] = rks
                minIndex = self._minRks(b19)
        return b19[minIndex]

    def _minSongLevel(self, array: list[SongLevel]) -> int:
        index = -1
        min_ = float("inf")
        for i in range(1, len(array)):
            if getattr(array[i], "id", None) is None:
                return i
            if array[i].rks < min_:
                index = i
                min_ = array[i].rks
        return index

    def _minRks(self, array: list[float]) -> int:
        index = -1
        min_ = 17.0
        for i in range(19):
            if array[i] == 0:
                return i
            if array[i] < min_:
                index = i
                min_ = array[i]
        return index

    def go(self, index: int) -> None:
        if self.length is None:
            return
        for i in range(index):
            if Util.getBit(self.length, i):
                self.reader.position += 8

    def levelNotExist(self, level: int) -> bool:
        if self.length is None:
            return True
        return not Util.getBit(self.length, level)

    def getFC(self, index: int) -> bool:
        if self.fc is None:
            return False
        return Util.getBit(self.fc, index)
