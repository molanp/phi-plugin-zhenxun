import sys


class ProgressBar:
    def __init__(self, dsc: str = "进度", bar_length: int = 25):
        """
        初始化进度条

        :param dsc: 进度条描述，默认为“进度”
        :param bar_length: 进度条长度（字符数），默认为25
        """
        self.dsc = dsc
        self.length = bar_length

    def render(self, completed: int, total: int) -> None:
        """
        渲染进度条

        :param completed: 已完成数量
        :param total: 总数量
        """
        if total <= 0:
            raise ValueError("总进度必须大于0")

        percent = completed / total
        cell_num = int(percent * self.length)

        # 构建进度块
        cell = "█" * cell_num
        empty = "░" * (self.length - cell_num)

        # 单行刷新输出
        progress_line = f"\r{self.dsc}：{cell}{empty} {completed}/{total}"
        sys.stdout.write(progress_line)
        sys.stdout.flush()

        # 当进度完成时换行
        if completed >= total:
            sys.stdout.write("\n")
            sys.stdout.flush()
