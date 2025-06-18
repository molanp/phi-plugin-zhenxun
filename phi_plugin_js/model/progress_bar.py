from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TransferSpeedColumn,
)


class ProgressBar:
    def __init__(self, description: str = "Progress", total: int | None = None):
        """
        初始化 Rich 进度条

        :param description: 进度条描述
        :param total: 总任务数（可选）
        """
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
        )
        self.task_id = self.progress.add_task(description, total=total or None)
        self.started = False

    def render(self, completed: int, total: int | None = None) -> None:
        """
        更新进度

        :param completed: 已完成数量
        :param total: 总数量（首次调用时可以设置）
        """
        if not self.started:
            self.progress.start()
            self.started = True

        if total is not None and self.progress.tasks[0].total != total:
            self.progress.update(self.task_id, total=total)

        self.progress.update(self.task_id, completed=completed)

    def finish(self) -> None:
        """结束进度条"""
        if self.started:
            self.progress.stop()
