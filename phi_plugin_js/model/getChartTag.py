from pydantic import BaseModel

from ..utils import to_dict
from .getFile import readFile as getFile
from .path import otherDataPath

dataPath = otherDataPath / "chartTagData.json"


class TagObject(BaseModel):
    agree: list[str] = []
    disagree: list[str] = []


class getChartTag(BaseModel):
    # 评论数据
    data: (
        dict[
            str,  # idString
            dict[
                str,  # levelKind
                TagObject,
            ],
        ]
        | None
    ) = None

    @classmethod
    async def init(cls):
        cls.data = await getFile.FileReader(dataPath)
        if cls.data is None:
            cls.data = {}
            await getFile.SetFile(dataPath, cls.data)
        return cls

    @classmethod
    async def get(cls, songId: str, rank: str, all: bool = False) -> list[str]:
        """
        获取对应曲目的所有tag

        :param str songId: id
        :param str rank: 难度
        :param bool all: 是否返回value为负的标签
        """
        if cls.data is None:
            await cls.init()
            assert cls.data is not None
        d = cls.data.get(songId, {}).get(rank)
        if d is None:
            return []
        arr = []
        keys = to_dict(d).keys()

        for key in keys:
            obj: TagObject = getattr(d, key)
            score = len(obj.agree) - len(obj.disagree)

            if not all and score <= 0:
                continue

            arr.append({"name": key, "value": score})
        return arr

    @classmethod
    async def add(cls, id: str, tag: str, rank: str, agree: bool, userId: str) -> bool:
        """
        添加tag

        :param id: id
        :param tag: tag
        :param rank: 难度
        :param agree: 是否同意
        :param userId: userId
        """
        if cls.data is None:
            await cls.init()
            assert cls.data is not None
        if not cls.data.get(id):
            cls.data[id] = {}
        if not cls.data[id].get(rank):
            cls.data[id][rank] = TagObject()
        tag_obj: TagObject = getattr(cls.data[id][rank], tag)
        if agree:
            # 加入agree
            if userId not in tag_obj.agree:
                tag_obj.agree.append(userId)
            # 删除disagree
            if userId in tag_obj.disagree:
                tag_obj.disagree.remove(userId)
        else:
            # 加入disagree
            if userId not in tag_obj.disagree:
                tag_obj.disagree.append(userId)
            # 删除agree
            if userId in tag_obj.agree:
                tag_obj.agree.remove(userId)
        return await getFile.SetFile(dataPath, to_dict(cls.data))

    @classmethod
    async def cancel(cls, id: str, tag: str, rank: str, userId: str):
        """
        取消tag

        :param str id: id
        :param str tag: tag
        :param str rank: 难度
        :param str userId: userId
        """
        if cls.data is None:
            await cls.init()
            assert cls.data is not None
        if not cls.data.get(id):
            cls.data[id] = {}
        if not cls.data[id].get(rank):
            cls.data[id][rank] = TagObject()
        tag_obj: TagObject = getattr(cls.data[id][rank], tag)
        # 删除agree
        if userId in tag_obj.agree:
            tag_obj.agree.remove(userId)
        # 删除disagree
        if userId in tag_obj.disagree:
            tag_obj.disagree.remove(userId)
        # 取消tag后检查是否为空
        if not tag_obj.agree and not tag_obj.disagree:
            del cls.data[id][rank]
        return await getFile.SetFile(dataPath, cls.data)
