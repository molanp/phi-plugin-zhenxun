class Chart:
    def __init__(self, data: dict):
        """
        初始化 Chart 对象

        :param data: 包含曲目信息的字典对象
        """
        self.id = data.get("id")  # 允许 id 为 None
        self.rank = data.get("rank")  # 允许 rank 为 None

        # 确保存在 charter 字段，否则抛出 KeyError
        self.charter = data["charter"]

        # 强制转换为数字类型，若字段不存在或无法转换将引发异常
        self.difficulty = float(data["difficulty"])
        self.tap = float(data["tap"])
        self.drag = float(data["drag"])
        self.hold = float(data["hold"])
        self.flick = float(data["flick"])
        self.combo = float(data["combo"])
