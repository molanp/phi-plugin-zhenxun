from zhenxun.services.log import logger


class LevelRecord:
    """关卡记录类"""

    def __init__(self, fc: bool = False, score: int = 0, acc: float = 0):
        """
        初始化关卡记录

        :param fc: 是否全连
        :param score: 分数
        :param acc: 准确率
        """
        self.fc = fc
        self.score = score
        self.acc = acc

    def __str__(self) -> str:
        """
        返回字符串表示

        :return: 字符串表示
        """
        try:
            return (
                f'{{"fc":{str(self.fc).lower()},"score":{self.score},"acc":{self.acc}}}'
            )
        except Exception as e:
            logger.error(f"生成字符串表示失败: {e}", "phi-plugin")
            raise ValueError(f"生成字符串表示失败: {e}")
