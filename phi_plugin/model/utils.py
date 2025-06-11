import contextlib
from datetime import datetime, timezone
from typing import Any


def to_dict(c: object) -> dict:
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


def Date(date_input: str | float | None) -> datetime | None:
    """
    将多种格式的时间输入转换为 Python datetime 对象。

    参数:
        date_input (str or int or float): 时间表示

    返回:
        datetime: 解析后的时间对象，失败返回 None
    """
    if date_input is None:
        return None

    try:
        if isinstance(date_input, str):
            # 优先尝试 ISO 格式
            with contextlib.suppress(ValueError):
                dt = datetime.fromisoformat(date_input)
                return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
            # 尝试匹配常见格式
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
                    dt = datetime.strptime(date_input, fmt)
                    if fmt.endswith("%Z"):  # 如果包含时区（如 GMT）
                        return dt.replace(tzinfo=timezone.utc)
                    return dt.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

            raise ValueError("Unsupported date format")

        # 处理时间戳
        timestamp = float(date_input)
        if timestamp > 1e12:  # 毫秒转秒
            timestamp /= 1000
        return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)

    except Exception:
        return None
