import contextlib
from pathlib import Path
import re
from typing import Any, Literal

from nonebot import __version__

from zhenxun.configs.config import Config
from zhenxun.configs.utils import RegisterConfig

PATH = Path(__file__).parent

VERSION_PATTERN = re.compile(
    r"https://img\.shields\.io/badge/(?P<type>插件版本|Phigros)-(?P<version>(.*))-9cf"
)
currentVersion = "未知"
phigros_ver = "未知"
with contextlib.suppress(Exception):
    if (PATH / "README.md").exists():
        with open(PATH / "README.md", encoding="utf-8") as f:
            README = f.read()
        for match in VERSION_PATTERN.finditer(README):
            ver_type = match["type"]
            version = match["version"]

            if ver_type == "插件版本":
                currentVersion = f"v{version}"
            elif ver_type == "Phigros":
                phigros_ver = version

Version: dict[Literal["ver", "phigros", "nonebot"], str] = {
    "ver": currentVersion,
    "phigros": phigros_ver,
    "nonebot": __version__,
}

CONFIG = (
    [
        RegisterConfig(
            key="cmdhead",
            value="/phi",
            type=str,
            help="命令前缀，默认 /phi，建议使用 /phi 作为前缀",
        ),
        RegisterConfig(
            key="VikaToken",
            value=None,
            type=str,
            help="Vika API Token, 用户的开发者Token，",
        ),
        RegisterConfig(
            key="B19MaxNum",
            value=22,
            type=int,
            help="用户可以获取B19图片成绩的最大数量，建议不要太大",
        ),
        RegisterConfig(
            key="HistoryDayNum",
            value=10,
            type=int,
            help="/update 展现历史成绩的单日最大数量，至少为2",
        ),
        RegisterConfig(
            key="HistoryScoreDate",
            value=2,
            type=int,
            help="/update 展现历史成绩的最大天数",
        ),
        RegisterConfig(
            key="HistoryScoreNum",
            value=20,
            type=int,
            help="/update 展现历史成绩的最大数量",
        ),
        RegisterConfig(
            key="listScoreMaxNum",
            value=3,
            type=int,
            help="/list 最大渲染成绩数量，建议为3的倍数",
        ),
        RegisterConfig(
            key="isGuild",
            value=False,
            type=bool,
            help="开启后文字版仅限私聊，关闭文字版图片，文字版将折叠为长消息",
        ),
        RegisterConfig(
            key="TapTapLoginQRcode",
            value=True,
            type=bool,
            help="登录TapTap绑定是否发送二维码，开启仅发送二维码，关闭直接发送链接",
        ),
        RegisterConfig(
            key="WordB19Img", value=False, type=bool, help="文字版B19曲绘图片"
        ),
        RegisterConfig(
            key="WordSuggImg", value=True, type=bool, help="Suggest曲绘图片"
        ),
        RegisterConfig(
            key="otherinfo",
            value=0,
            type=int,
            help=(
                "使用曲库的模式，若启用自定义则重名的以自定义为准。"
                "0: 原版曲库;1:原版+自定义;2:仅自定义"
            ),
        ),
        RegisterConfig(
            key="GuessTipCd",
            value=0,
            type=int,
            help="[猜曲绘]提示间隔时间，单位：秒",
        ),
        RegisterConfig(
            key="GuessTipRecall",
            value=False,
            type=bool,
            help="[猜曲绘]是否在下一条提示发出的时候撤回上一条",
        ),
        RegisterConfig(
            key="LetterNum", value=1, type=int, help="[开字母设置]开字母的条数"
        ),
        RegisterConfig(
            key="LetterIllustration",
            value="不发送",
            type=str,
            help=(
                "[开字母设置]猜对后是否发送以及发送什么曲绘，水印版需要占用渲染资源，不发图片更快."
                "[水印版,原版,不发送]"
            ),
        ),
        RegisterConfig(
            key="LetterTimeLength",
            value=300,
            type=int,
            help="[开字母设置]猜字母待机时长，无人回答多长时间后结束，单位：秒",
        ),
        RegisterConfig(
            key="GuessTipsTipCD",
            value=0,
            type=int,
            help="[提示猜歌]提示猜歌提示的冷却时间间隔，单位：秒",
        ),
        RegisterConfig(
            key="GuessTipsTipNum",
            value=0,
            type=int,
            help="[提示猜歌]提示猜歌的提示条数（除曲绘外），若总提示条数小于设定条数则将会发送全部提示",
        ),
        RegisterConfig(
            key="GuessTipsTimeout",
            value=30,
            type=int,
            help="[提示猜歌]提示猜歌超时时长，单位：秒",
        ),
        RegisterConfig(
            key="GuessTipsAnsTime",
            value=5,
            type=int,
            help="[提示猜歌]发送曲绘后多久公布答案，单位：秒",
        ),
        RegisterConfig(
            key="allowComment",
            value=False,
            type=bool,
            help="是否开启曲目评论功能，该功能目前暂无敏感词校验",
        ),
        RegisterConfig(
            key="commentsAPage",
            value=20,
            type=int,
            help="每页最大渲染评论数量",
        ),
        RegisterConfig(
            key="allowChartTag",
            value=False,
            type=bool,
            help="是否开启谱面标签功能，该功能目前暂无敏感词校验",
        ),
        RegisterConfig(
            key="phigrousUpdateUrl",
            value="https://phiupdateinfo.pmya.xyz/",
            type=str,
            help="Phigros更新信息API地址",
        ),
    ],
)


class PluginConfig:
    @staticmethod
    def get(key: str, default: None | Any = None) -> Any:
        """获取配置项的值"""
        return Config.get_config("phi-plugin", key.upper(), default)

    @staticmethod
    def set(key: str, value):
        """设置配置项的值"""
        Config.set_config("phi-plugin", key.upper(), value, True)


onLinePhiIllUrl = "https://gitee.com/Steveeee-e/phi-plugin-ill/raw/main"
"""在线曲绘地址"""

try:
    cmdhead = PluginConfig.get("cmdhead", "/phi")
    """命令前缀"""
    VikaToken = PluginConfig.get("VikaToken")
except Exception:
    cmdhead = "/phi"
    """命令前缀"""
    VikaToken = ""

recmdhead = re.escape(cmdhead)
