"""
评论对象字典
* **str** sessionToken
* **str** userObjectId 用户ObjectId
* **float** rks
* **Level** rank
* **int** score
* **float** acc
* **bool** fc
* **str|None** spInfo
* **int** challenge
* **datetime** time
* **str** comment
* **str|None** thisId 在add时添加
* **str|None** songId 仅在getByCommentId时添加
* **str|None** PlayerId 仅在查询时添加
* **str|None** avatar 仅在查询时添加
"""

import secrets

from .getFile import readFile as getFile
from .path import otherDataPath

dataPath = otherDataPath / "commentData.json"


class getComment:
    data = None
    """
    评论对象字典
    * **str** sessionToken
    * **str** userObjectId 用户ObjectId
    * **float** rks
    * **Level** rank
    * **int** score
    * **float** acc
    * **bool** fc
    * **str|None** spInfo
    * **int** challenge
    * **datetime** time
    * **str** comment
    * **str|None** thisId 在add时添加
    * **str|None** songId 仅在getByCommentId时添加
    * **str|None** PlayerId 仅在查询时添加
    * **str|None** avatar 仅在查询时添加
    """

    @classmethod
    async def load(cls):
        """初始化评论数据"""
        # 评论数据
        cls.data = await getFile.FileReader(dataPath)
        # 评论id映射曲目id
        cls.map = {}
        if not cls.data:
            cls.data = {}
            await getFile.SetFile(dataPath, cls.data)
        # 遍历所有曲目评论数据
        updated_data = {}
        for song_id, comments in cls.data.items():
            updated_comments = []
            for comment in comments:
                # 检查是否存在 thisId
                if not comment.get("thisId"):
                    continue
                # 建立 thisId 到曲目ID的映射
                cls.map[comment["thisId"]] = song_id
                updated_comments.append(comment)
            updated_data[song_id] = updated_comments

        cls.data = updated_data
        await getFile.SetFile(dataPath, cls.data)

    @classmethod
    async def get(cls, songId: str):
        """获取对应曲目的所有评论"""
        if cls.data is None:
            await cls.load()
            assert cls.data is not None
        return cls.data.get(songId, [])

    @classmethod
    async def getByCommentId(cls, commentId: str):
        """获取对应评论id的评论"""
        if cls.data is None:
            await cls.load()
            assert cls.data is not None
        songId = cls.data.get(commentId, None)
        if not songId:
            return None
        for comment in cls.data[songId]:
            if comment.get("thisId") == commentId:
                comment["songId"] = songId
                return comment
        return None

    @classmethod
    async def add(cls, id: str, comment: dict):
        """添加评论"""
        comment["thisId"] = str(secrets.randbits(32))
        if cls.data is None:
            await cls.load()
            assert cls.data is not None
        if id in cls.data:
            cls.data[id].append(comment)
        else:
            cls.data[id] = [comment]
        cls.map[comment["thisId"]] = id
        await getFile.SetFile(dataPath, cls.data)

    @classmethod
    async def delete(cls, commentId: str):
        """删除评论id对应的评论"""
        if cls.data is None:
            await cls.load()
            assert cls.data is not None

        songId = cls.map.get(commentId)
        if not songId:
            return False

        comments = cls.data.get(songId, [])
        for i, comment in enumerate(comments):
            if comment.get("thisId") == commentId:
                del comments[i]
                if commentId in cls.map:
                    del cls.map[commentId]
                await getFile.SetFile(dataPath, cls.data)
                return True

        if commentId in cls.map:
            del cls.map[commentId]
        return False
