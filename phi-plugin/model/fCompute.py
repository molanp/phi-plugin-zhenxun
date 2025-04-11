import datetime
import math
import random
import re

from zhenxun.services.log import logger

from .constNum import MAX_DIFFICULTY
from .get_info import getInfo


class Compute:
    def rks(self, acc: float, difficulty: float) -> float:
        if acc == 100:
            return difficulty
        elif acc < 70:
            return 0.0
        else:
            return difficulty * (((acc - 55) / 45) ** 2)

    def suggest(
        self, rks: float, difficulty: float, count: int | None = None
    ) -> str:
        ans = 45 * math.sqrt(rks / difficulty) + 55
        if ans >= 100:
            return "无法推分"
        else:
            return f"{ans:.{count}f}%" if count is not None else str(ans)

    async def get_background(self, save_background: str) -> str | None:
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
            return getInfo.getill(save_background)
        except Exception as err:
            logger.error("获取背景曲绘错误", e=err)
            return None

    def ped(self, num: int, cover: int) -> str:
        return f"{str(num).zfill(cover)}"[-cover:]

    def std_score(self, score: int) -> str:
        s1 = score // 1_000_000
        s2 = (score // 1_000) % 1_000
        s3 = score % 1_000
        return f"{s1}'{self.ped(s2, 3)}'{self.ped(s3, 3)}"

    def rand_between(self, min_val: int, max_val: int) -> int:
        return self.rand_array([*range(min_val, max_val + 1)])[0]

    def rand_array(self, arr: list) -> list:
        new_arr = arr.copy()
        random.shuffle(new_arr)
        return new_arr

    def format_date(self, date: str | int | datetime.datetime) -> str:
        if isinstance(date, str):
            # 处理 ISO 格式字符串（如 "2023-10-05T07:41:24.503Z"）
            if "T" in date:
                dt = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
            else:
                dt = datetime.datetime.fromtimestamp(int(date) / 1000)
        elif isinstance(date, int):
            dt = datetime.datetime.fromtimestamp(date / 1000)
        else:
            dt = date
        return dt.strftime("%Y/%m/%d %H:%M:%S")

    def convert_rich_text(self, rich_text: str, only_text: bool = False) -> str:
        rich_text = rich_text.replace("<", "&lt;").replace(">", "&gt;")
        patterns = [
            (
                r"&lt;color\s*=\s*.*?&gt;(.*?)&lt;/color&gt;",
                r"<span style='color:\1'>\g<1></span>",
            ),
            (r"&lt;i&gt;(.*?)&lt;/i&gt;", r"<i>\g<1></i>"),
            (r"&lt;b&gt;(.*?)&lt;/b&gt;", r"<b>\g<1></b>"),
        ]
        for pattern, replacement in patterns:
            rich_text = re.sub(
                pattern, r"\g<1>" if only_text else replacement, rich_text
            )
        rich_text = rich_text.replace("\n\r?", "<br>")
        if only_text:
            rich_text = rich_text.replace("&lt;", "<").replace("&gt;", ">")
        return rich_text

    def match_range(self, msg: str, range_: list[float]) -> None:
        """
        解析消息中的难度范围并更新 range_ 列表
        """
        range_[0] = 0.0
        range_[1] = MAX_DIFFICULTY

        if range_match := re.search(
            r"[0-9]+(.[0-9]+)?\s*[-～~]\s*[0-9]+(.[0-9]+)?", msg
        ):
            self._extracted_from_match_range_11(range_match, range_)
        elif plus_match := re.search(r"[0-9]+(.[0-9]+)?\s*[-+]", msg):
            value = float(plus_match.group().split(" ")[0])
            if "+" in msg:
                range_[0] = value
            else:
                range_[1] = value
                if range_[1] % 1 == 0 and ".0" not in str(value):
                    range_[1] += 0.9

        elif single_match := re.search(r"[0-9]+(.[0-9]+)?", msg):
            value = float(single_match.group())
            range_[0] = range_[1] = value
            if "." not in str(value):
                range_[1] += 0.9

    # TODO Rename this here and in `match_range`
    def _extracted_from_match_range_11(self, range_match, range_):
        parts = re.split(r"\s*[-～~]\s*", range_match.group())
        part1 = float(parts[0])
        part2 = float(parts[1])
        range_[0] = part1
        range_[1] = part2
        if range_[0] > range_[1]:
            range_[0], range_[1] = range_[1], range_[0]
        if range_[1] % 1 == 0 and ".0" not in parts[1]:
            range_[1] += 0.9

    def match_request(
        self, e_msg: str
    ) -> dict[str, list[bool] | dict[str, bool] | list[float]]:
        """
        解析消息中的过滤条件并返回结构化对象
        """
        msg = re.sub(r"^[#/](.*?)(lvsco(re)?)\s*", "", e_msg)
        msg = msg.upper()

        # 初始化难度筛选标志（EZ, HD, IN, AT）
        isask = [True, True, True, True]

        # 处理难度等级（EZ/HD/IN/AT）
        if any(word in msg for word in ["EZ", "HD", "IN", "AT"]):
            isask = [False, False, False, False]
            if "EZ" in msg:
                isask[0] = True
            if "HD" in msg:
                isask[1] = True
            if "IN" in msg:
                isask[2] = True
            if "AT" in msg:
                isask[3] = True

        # 清理消息中的关键词
        msg = re.sub(r"(LIST|AT|IN|HD|EZ)*", "", msg)

        # 初始化成绩评级筛选（NEW/F/C/B/A/S/V/FC/PHI）
        score_ask = {
            "NEW": True,
            "F": True,
            "C": True,
            "B": True,
            "A": True,
            "S": True,
            "V": True,
            "FC": True,
            "PHI": True,
        }

        # 处理评级关键词（如 "NEW", "F", "AP"）
        if any(
            word in msg
            for word in ["NEW", "F", "C", "B", "A", "S", "V", "FC", "PHI", "AP"]
        ):
            score_ask = dict.fromkeys(score_ask, False)
            ratings = ["NEW", "F", "C", "B", "A", "S", "V", "FC", "PHI"]
            for rating in ratings:
                if f" {rating}" in msg:
                    score_ask[rating] = True
            if " AP" in msg:
                score_ask["PHI"] = True

        # 清理消息中的评级关键词
        msg = re.sub(r"(NEW|F|C|B|A|S|V|FC|PHI|AP)*", "", msg)

        # 解析难度范围
        range_ = [0.0, MAX_DIFFICULTY]
        self.match_range(msg, range_)

        return {"range": range_, "isask": isask, "scoreAsk": score_ask}

    def rate(self, real_score: float, tot_score: float, fc: bool) -> str:
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

    def date_to_string(self, date: str | int | datetime.datetime) -> str | None:
        if not date:
            return None
        if isinstance(date, str):
            if "T" in date:
                dt = datetime.datetime.fromisoformat(date.replace("Z", "+00:00"))
            else:
                dt = datetime.datetime.fromtimestamp(int(date) / 1000)
        elif isinstance(date, int):
            dt = datetime.datetime.fromtimestamp(date / 1000)
        else:
            dt = date
        return dt.strftime("%Y/%m/%d %H:%M:%S")

    def range_percent(self, value: float, range_: list[float]) -> float:
        if range_[0] == range_[-1]:
            return 50.0
        else:
            return (value - range_[0]) / (range_[-1] - range_[0]) * 100


# 实例化计算对象
fCompute = Compute()
