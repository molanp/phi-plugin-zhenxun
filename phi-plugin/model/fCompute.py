from datetime import datetime
from pathlib import Path
import random
import re
from typing import Literal

from nonebot_plugin_alconna import File, UniMessage
from nonebot_plugin_uninfo import Uninfo
from pydantic import BaseModel

from zhenxun.models.level_user import LevelUser
from zhenxun.services.log import logger
from zhenxun.utils.rules import ensure_group

from ..utils import Date
from .constNum import MAX_DIFFICULTY


class match_request_return_2(BaseModel):
    NEW: bool
    F: bool
    C: bool
    B: bool
    A: bool
    S: bool
    V: bool
    FC: bool
    PHI: bool


class match_request_return(BaseModel):
    range: list[float]
    """[min, max]"""
    isask: list[bool]
    """[EZ, HD, IN, AT]"""
    scoreAsk: match_request_return_2


class fCompute:
    @staticmethod
    def rks(acc: float, difficulty: float) -> float:
        """计算等效rks"""
        if acc == 100:
            # 满分原曲定数即为有效rks
            return difficulty
        elif acc < 70:
            # 无效rks
            return 0
        else:
            # 非满分计算公式 [(((acc - 55) / 45) ^ 2) * 原曲定数]
            return difficulty * (((acc - 55) / 45) ** 2)

    @staticmethod
    def suggest(rks: float, difficulty: float, count: int | None = None) -> str:
        """
        计算所需acc

        :param rks: 目标rks
        :param difficulty: 定数
        :param count: 保留位数
        :return: 所需acc
        """
        ans = 45 * (rks / difficulty) ** 0.5 + 55

        if ans >= 100:
            return "无法推分"
        elif count is not None:
            return f"{ans:.{count}f}%"
        else:
            return str(ans)

    @staticmethod
    async def sendFile(file: bytes, filename: str):
        """发送文件"""
        try:
            await UniMessage(File(raw=file, name=filename)).send()
        except Exception as err:
            logger.error("文件上传错误", "phi-plugin:sendFile", e=err)
            await UniMessage(f"文件上传错误: {err}").send()

    @staticmethod
    async def getBackground(save_background: str) -> Path | str | Literal[False]:
        """获取角色介绍背景曲绘"""
        from .getInfo import getInfo

        try:
            match save_background:
                case "Another Me ":
                    save_background = "Another Me (KALPA)"

                case "Another Me":
                    save_background = "Another Me (Rising Sun Traxx)"

                case "Re_Nascence (Psystyle Ver.) ":
                    save_background = "Re_Nascence (Psystyle Ver.)"

                case "Energy Synergy Matrix":
                    save_background = "ENERGY SYNERGY MATRIX"

                case "Le temps perdu-":
                    save_background = "Le temps perdu"
            return await getInfo.getill(
                getInfo.idgetsong(save_background) or save_background
            )
        except Exception as e:
            logger.error("获取背景曲绘错误", "phi-plugin", e=e)
            return False

    @staticmethod
    def ped(num: int, cover: int) -> str:
        """
        为数字添加前导零

        :param num: 原数字
        :param cover: 总位数
        """
        return f"{num:0{cover}d}"

    @staticmethod
    def std_score(score: int) -> str:
        """标准化分数"""
        s1 = score // 1_000_000
        s2 = (score // 1_000) % 1_000
        s3 = score % 1_000
        return f"{s1}'{fCompute.ped(s2, 3)}'{fCompute.ped(s3, 3)}"

    @staticmethod
    def randBetween(min: int, max: int) -> int:
        """
        随机数，包含上下界

        :param min: 最小值
        :param max: 最大值
        """
        return random.randint(min, max)

    @staticmethod
    def randArray(arr: list) -> list:
        """
        随机打乱数组

        :param arr: 数组
        """
        arr = arr.copy()
        new_arr = []
        while arr:
            index = random.randint(0, len(arr) - 1)
            new_arr.append(arr.pop(index))
        return new_arr

    @staticmethod
    def formatDate(date: datetime | str | float | None) -> str:
        """
        转换时间格式

        :param date: 时间表示
        :return: 格式化后的字符串，如 '2020/10/8 10:08:08'
        """
        dt = Date(date)

        return dt.strftime("%Y/%m/%d %H:%M:%S")

    @staticmethod
    def formatDateToNow(date: datetime | str | float | None) -> str:
        """
        计算当前时间与指定时间之间的天数差，并返回格式如 '-3d' 的字符串

        :param date: 时间表示
        :return: 格式化后的字符串，如 '-3d'
        """
        dt = Date(date)

        now = datetime.now()
        delta_days = (now - dt).days

        return f"-{delta_days}d"

    @staticmethod
    def convertRichText(rich_text: str, only_text: bool = False) -> str:
        """
        转换Unity富文本格式字符串为HTML格式或纯文本

        :param rich_text: 原始富文本字符串
        :param only_text: 是否只返回纯文本
        :return: 转换后的字符串
        """
        if not rich_text:
            return rich_text

        # 转义 < 和 > 防止 HTML 注入
        rich_text = rich_text.replace("<", "&lt;").replace(">", "&gt;")

        # 定义正则表达式
        color_tag = r"&lt;color\s*=\s*(.*?)&gt;(.*?)&lt;\/color&gt;"
        italic_tag = r"&lt;i&gt;(.*?)&lt;\/i&gt;"
        bold_tag = r"&lt;b&gt;(.*?)&lt;\/b&gt;"

        # 处理 <color=...> 标签
        while re.search(color_tag, rich_text):
            rich_text = re.sub(
                color_tag,
                lambda m: (
                    """<span style="color:"""
                    f"""{m.group(1).replace(" ", "").replace('"', "")}">"""
                    f"{m.group(2)}</span>"
                ),
                rich_text,
            )

        # 处理 <i> 标签
        while re.search(italic_tag, rich_text):
            rich_text = re.sub(
                italic_tag,
                lambda m: m.group(1) if only_text else f"<i>{m.group(1)}</i>",
                rich_text,
            )

        # 处理 <b> 标签
        while re.search(bold_tag, rich_text):
            rich_text = re.sub(
                bold_tag,
                lambda m: m.group(1) if only_text else f"<b>{m.group(1)}</b>",
                rich_text,
            )

        # 换行符处理（可选）
        rich_text = re.sub(r"\n\r?", "<br>", rich_text)

        # 如果只保留纯文本，移除所有标签
        if only_text:
            rich_text = re.sub(r"<[^>]+>", "", rich_text)
            rich_text = rich_text.replace("&lt;", "<").replace("&gt;", ">")

        return rich_text

    @staticmethod
    async def is_superuser(session: Uninfo) -> bool:
        """是否是超级管理员"""
        if not ensure_group(session):
            return False
        level = await LevelUser.get_user_level(
            session.user.id,
            session.scene.id,
        )
        return level >= 9

    @staticmethod
    def match_range(msg: str, r: list | None = None) -> list[float]:
        """
        从消息中提取难度范围

        :param msg: 用户输入消息
        :param r: 初始范围数组 [min, max]
        :return: 处理后的范围 [min, max]
        """
        if r is None:
            r = [0, MAX_DIFFICULTY]

        if range_match := re.search(r"(\d+\.?\d*)\s*[-～~]\s*(\d+\.?\d*)", msg):
            min_val = float(range_match[1])
            max_val = float(range_match[2])
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            if max_val.is_integer() and "." not in range_match[2]:
                max_val += 0.9
            r[0], r[1] = min_val, max_val
            return r

        if bound_match := re.search(r"(\d+\.?\d*)\s*([+-])", msg):
            num = float(bound_match[1])
            if bound_match[2] == "+":
                r[0] = num
            else:
                r[1] = num
                if num.is_integer() and "." not in bound_match[1]:
                    r[1] += 0.9
            return r

        if single_match := re.search(r"\d+\.?\d*", msg):
            val = float(single_match.group())
            r[0] = r[1] = val
            if "." not in single_match.group():
                r[1] += 0.9
            return r

        return r

    @staticmethod
    def match_request(msg: str, max_range: float | None = None) -> match_request_return:
        """
        匹配消息中对成绩的筛选条件

        :param msg: 用户输入的原始消息
        :param max_range: 最大难度范围
        :return: 包含筛选条件的模型
        ```
        """
        result = match_request_return(
            **{
                "range": [0, max_range or MAX_DIFFICULTY],
                "isask": [False, False, False, False],
                "scoreAsk": {
                    "NEW": False,
                    "F": False,
                    "C": False,
                    "B": False,
                    "A": False,
                    "S": False,
                    "V": False,
                    "FC": False,
                    "PHI": False,
                },
            }
        )

        clean_msg = msg.upper()

        # 处理难度模式筛选：EZ HD IN AT
        modes = ["EZ", "HD", "IN", "AT"]
        if mode_indices := [
            index for index, mode in enumerate(modes) if mode in clean_msg
        ]:
            for i in mode_indices:
                result.isask[i] = True

        # 处理成绩等级筛选：NEW F C B A S V FC PHI AP
        rating_keys = ["NEW", "F", "C", "B", "A", "S", "V", "FC", "PHI"]
        has_rating = any(f" {r}" in clean_msg for r in [*rating_keys, "AP"])

        if has_rating:
            for rating in rating_keys:
                if f" {rating}" in clean_msg:
                    setattr(result.scoreAsk, rating, True)
            if " AP" in clean_msg:
                result.scoreAsk.PHI = True

        # 提取难度范围
        result.range = fCompute.match_range(msg, result.range)

        return result

    @staticmethod
    def rate(real_score: float | None, tot_score: float, fc: bool = False) -> str:
        """
        根据真实成绩与总成绩计算成绩等级

        :param real_score: 真实成绩
        :param tot_score: 总成绩
        :param fc: 是否 Full Combo
        :return: 成绩等级：'F', 'C', 'B', 'A', 'S', 'V', 'FC', 'phi'
        """
        if not real_score:
            return "F"
        elif real_score == tot_score:
            return "phi"
        elif fc:
            return "FC"
        elif real_score >= tot_score * 0.96:
            return "V"
        elif real_score >= tot_score * 0.92:
            return "S"
        elif real_score >= tot_score * 0.88:
            return "A"
        elif real_score >= tot_score * 0.82:
            return "B"
        elif real_score >= tot_score * 0.70:
            return "C"
        else:
            return "F"

    @staticmethod
    def date_to_string(dt: str | datetime | float) -> str:
        """
        转换时间格式

        :param dt: 时间（字符串或 datetime 对象）
        :return: 格式化后的字符串，如 '2020/10/8 10:08:08' 或 空字符串
        """
        if not dt:
            return ""
        # 统一转为 datetime 对象
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            except ValueError:
                # 如果不支持 ISO 格式，尝试其他常见格式
                dt = datetime.strptime(dt.replace("Z", "+00:00"), "%Y/%m/%d %H:%M:%S")
        if isinstance(dt, float | int):
            dt = Date(dt)

        # 格式化月份和日期（前导零）
        month = f"0{dt.month}" if dt.month < 10 else dt.month
        day = f"0{dt.day}" if dt.day < 10 else dt.day

        # 提取时间部分（小时:分钟:秒）
        time_str = dt.strftime("%H:%M:%S")

        return f"{dt.year}/{month}/{day} {time_str}"

    @staticmethod
    def range(value: float, range_list: list) -> float:
        """
        计算一个值在给定区间中的百分比位置，并返回对应的百分数

        :param value: 需要计算的值
        :param range_list: 区间数组，例如 [0, 1]
        :return: 百分数
        """
        if range_list[0] == range_list[-1]:
            return 50
        percentage = (value - range_list[0]) / (range_list[-1] - range_list[0]) * 100
        return round(percentage, 4)

    @staticmethod
    def fuzzySearch(search_str: str, data: dict) -> list:
        """
        模糊搜索，返回相似度大于0.8的结果

        :param search_str: 搜索字符串
        :param data: 搜索数据，格式为 {key: [value_list]}
        :return: 相似度大于0.8的结果列表，每个元素包含 key、score、value
        """
        result = []
        for key, values in data.items():
            score = fCompute.jaroWinklerDistance(search_str, key)
            if score > 0.8:
                result.extend(
                    {"key": key, "score": score, "value": value} for value in values
                )
        # 按照相似度降序排序
        return sorted(result, key=lambda x: x["score"], reverse=True)

    @staticmethod
    def jaroWinklerDistance(s1: str, s2: str) -> float:
        """
        使用 Jaro-Winkler 编辑距离算法计算两个字符串的相似度（0~1）

        :param s1: 字符串1
        :param s2: 字符串2
        :return: 相似度数值，范围 0~1
        """
        if s1 == s2:
            return 1.0

        # 去除空格和其他符号，并转为小写
        pattern = re.compile(
            r"[\s~`!@#$%^&*()\-=_+\[\]「」『』{}|;:'\",<.>/?！￥…（）—【】、；‘’：“”，《。》？↑↓←→]+"
        )
        s1 = pattern.sub("", s1).lower()
        s2 = pattern.sub("", s2).lower()

        if not s1 or not s2:
            return 0.0

        if s1 == s2:
            return 1.0

        max_len = max(len(s1), len(s2))
        search_range = (max_len // 2) - 1

        s1_matches = [False] * len(s1)
        s2_matches = [False] * len(s2)
        m = 0  # 匹配字符数量

        # 查找匹配字符
        for i in range(len(s1)):
            start = max(0, i - search_range)
            end = min(i + search_range + 1, len(s2))
            for j in range(start, end):
                if not s2_matches[j] and s1[i] == s2[j]:
                    s1_matches[i] = s2_matches[j] = True
                    m += 1
                    break

        if m == 0:
            return 0.0

        # 计算转置数
        k = 0
        n_trans = 0
        for i in range(len(s1)):
            if s1_matches[i]:
                while not s2_matches[k]:
                    k += 1
                if s1[i] != s2[k]:
                    n_trans += 1
                k += 1

        # 计算 Jaro 距离
        weight = (m / len(s1) + m / len(s2) + (m - n_trans / 2) / m) / 3

        # 如果大于 0.7，应用 Jaro-Winkler 修正
        if weight > 0.7:
            i = 0  # 公共前缀长度
            while i < min(len(s1), len(s2), 4) and s1[i] == s2[i]:
                i += 1
            weight += i * 0.1 * (1 - weight)

        return weight

    @staticmethod
    def getAdapterName(session: Uninfo) -> str:
        """获取适配器名称"""
        return str(session.adapter)
