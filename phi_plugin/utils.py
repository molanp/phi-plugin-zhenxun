import contextlib
from datetime import datetime
from typing import Any


def to_dict(c: Any) -> dict:
    if c is None:
        return {}

    def convert(value: Any) -> Any:
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "to_dict"):
            return value.to_dict()
        if isinstance(value, list | tuple):
            return [convert(v) for v in value]
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}

        # 新增：如果是类对象，提取类属性
        if isinstance(value, type):
            return {
                k: convert(v) for k, v in vars(value).items() if not k.startswith("__")
            }

        # 实例对象处理
        if hasattr(value, "__dict__"):
            return {
                k: convert(v) for k, v in vars(value).items() if not k.startswith("__")
            }

        return value

    return dict(convert(c))


def Date(date_input: str | float | datetime | None) -> datetime:
    """
    将多种格式的时间输入转换为 Python datetime 对象，并始终使用本地时区。

    :param str | float | int | datetime | None date_input: 时间表示
    :return: 解析后的时间对象，失败返回时间戳 0 对应的本地时间
    """
    if date_input is None:
        return datetime.fromtimestamp(0)

    if isinstance(date_input, datetime):
        return date_input if date_input.tzinfo is None else date_input.astimezone(None)
    try:
        if isinstance(date_input, str):
            with contextlib.suppress(ValueError):
                return datetime.fromisoformat(date_input)
            formats = (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%Y/%m/%d %H:%M:%S",
                "%a, %d %b %Y %H:%M:%S %Z",
                "%a %b %d %H:%M:%S %Y",
            )

            for fmt in formats:
                try:
                    return datetime.strptime(date_input, fmt)
                except ValueError:
                    continue

        elif isinstance(date_input, float | int):
            timestamp = float(date_input)
            if timestamp < 0:
                return datetime.fromtimestamp(0)
            if timestamp > 1e12:
                timestamp /= 1000
            return datetime.fromtimestamp(timestamp)

    except Exception:
        return datetime.fromtimestamp(0)

    return datetime.fromtimestamp(0)
