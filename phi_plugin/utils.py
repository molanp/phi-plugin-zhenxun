import contextlib
from datetime import datetime, timezone
from typing import Any

from nonebot import get_bot, require
from nonebot.adapters import Event

require("nonebot_plugin_uninfo")
from nonebot_plugin_uninfo import Uninfo, get_session


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
    将多种格式的时间输入转换为 Python datetime 对象，并始终使用 UTC 时区。

    :param str | float | int | datetime | None date_input: 时间表示
    :return: 解析后的时间对象，失败返回时间戳 0 对应的 UTC 时间
    """
    if date_input is None:
        return datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)

    if isinstance(date_input, datetime):
        # 如果已有时区信息，则转成 UTC
        if date_input.tzinfo is not None:
            return date_input.astimezone(timezone.utc)
        # 无时区信息则视为 UTC
        return date_input.replace(tzinfo=timezone.utc)

    try:
        if isinstance(date_input, str):
            # 优先尝试 ISO 格式
            with contextlib.suppress(ValueError):
                dt = datetime.fromisoformat(date_input)
                return (
                    dt.replace(tzinfo=timezone.utc)
                    if dt.tzinfo is None
                    else dt.astimezone(timezone.utc)
                )

            # 常见格式列表
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
                        # 假设是 GMT/UTC 时间
                        return dt.replace(tzinfo=timezone.utc)
                    # 没有时区信息，直接作为 UTC 处理
                    return dt.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

        elif isinstance(date_input, float | int):
            timestamp = float(date_input)
            if timestamp < 0:
                return datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)
            if timestamp > 1e12:  # 毫秒转秒
                timestamp /= 1000
            return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc)

    except Exception:
        # 所有异常都兜底返回时间戳 0 的 UTC 时间
        return datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)

    # 如果所有解析失败
    return datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)


async def Event2session(event: Event) -> Uninfo:
    """
    通过Event获取session

    :param event: 一个包含self_id的Event
    """
    self_id = getattr(event, "self_id", None)
    if not self_id:
        raise ValueError("Event对象缺少self_id属性")
    bot = get_bot(self_id)
    session = await get_session(bot, event)
    if session is None:
        raise ValueError("不支持的适配器!")
    return session
