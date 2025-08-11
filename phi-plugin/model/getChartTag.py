from ..models import ChartTag


class getChartTag:
    @staticmethod
    async def get(
        songId: str, rank: str, all: bool = False
    ) -> list[dict[str, str | int]]:
        """
        获取对应曲目的所有tag评分

        :param str songId: id
        :param str rank: 难度
        :param bool all: 是否返回总评价为负的标签

        :return: 标签统计信息字典
        ```
        [
            {
                "name": tag,
                "value": score,
            }
        ]
        ```
        """
        data = await ChartTag.get_tag_stats(songId, rank)
        arr = []
        for tag, v in data.items():
            score = v[0] - v[1]

            if not all and score <= 0:
                continue
            arr.append(
                {
                    "name": tag,
                    "value": score,
                }
            )
        return arr

    @staticmethod
    async def add(songId: str, tag: str, rank: str, agree: bool, userId: str):
        """
        添加tag

        :param songId: 曲目id
        :param tag: tag
        :param rank: 难度
        :param agree: 是否同意
        :param userId: userId
        """
        return bool(
            await ChartTag.update_or_create(
                songId=songId,
                tag=tag,
                rank=rank,
                userId=userId,
                defaults={"is_agree": agree},
            )
        )

    @staticmethod
    async def cancel(songId: str, tag: str, rank: str, userId: str):
        """
        取消tag

        :param str songId: 曲目id
        :param str tag: tag
        :param str rank: 难度
        :param str userId: userId
        """
        return bool(
            await ChartTag.filter(
                songId=songId, tag=tag, rank=rank, userId=userId
            ).delete()
        )
