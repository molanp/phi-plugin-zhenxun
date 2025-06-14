import asyncio
from pathlib import Path
import re
from typing import Any, Literal, TypedDict

from zhenxun.plugins.phi_plugin.model.cls.Chart import Chart
from zhenxun.services.log import logger

from ..config import PluginConfig
from ..utils import to_dict
from .cls.SongsInfo import SongsInfo, SongsInfoObject
from .constNum import MAX_DIFFICULTY, Level
from .fCompute import fCompute
from .getFile import readFile
from .path import (
    DlcInfoPath,
    configPath,
    imgPath,
    infoPath,
    oldInfoPath,
    originalIllPath,
    ortherIllPath,
)


class levelDetail(TypedDict):
    m: int
    """MaxTime"""
    d: list[tuple[int, int, int, int, int]]
    """note分布[tap,drag,hold,flick]"""
    t: tuple[int, int, int, int]
    """note统计[tap,drag,hold,flick]"""


class LevelRecordList(TypedDict):
    EZ: levelDetail
    HD: levelDetail
    IN: levelDetail
    AT: levelDetail
    LEGACY: levelDetail


class csvDetail(TypedDict):
    id: str
    """曲目id"""
    song: str
    """曲目名称"""
    composer: str
    """作曲"""
    illustrator: str
    """插画师"""
    EZ: str
    """EZ难度谱师"""
    HD: str
    """HD难度谱师"""
    IN: str
    """IN难度谱师"""
    AT: str | None
    """AT难度谱师"""


class _getInfo:
    initIng = False
    DLC_Info: dict[str, dict[str, list[str]]] = {}  # noqa: RUF012
    """扩增曲目信息"""
    avatarid: dict[str, str] = {}  # noqa: RUF012
    """头像id"""
    Tips: list[str]
    """Tips"""
    ori_info: dict[str, SongsInfoObject]
    """原版信息"""
    songsid: dict[str, str] = {}  # noqa: RUF012
    """通过id获取曲名"""
    idssong: dict[str, str] = {}  # noqa: RUF012
    """原曲名称获取id"""
    illlist: list[str] = []  # noqa: RUF012
    """含有曲绘的曲目列表，原曲名称"""
    sp_info: dict[str, SongsInfoObject] = {}  # noqa: RUF012
    """SP信息"""
    Level = Level
    """难度映射"""
    MAX_DIFFICULTY = 0
    """最高定数"""
    songlist = []  # noqa: RUF012
    """所有曲目曲名列表"""
    updatedSong = []  # noqa: RUF012
    updatedChart: dict[str, dict[Literal["EZ", "HD", "IN", "AT", "LEGACY"], Chart]] = {}  # noqa: RUF012
    nicklist: dict[str, list[str]] = {}  # noqa: RUF012
    """默认别名,以曲名为key"""
    songnick: dict[str, list[str]] = {}  # noqa: RUF012
    """以别名为key"""
    chapList: dict[str, list[str]]
    """章节列表，以章节名为key"""
    chapNick: dict[str, list[str]] = {}  # noqa: RUF012
    """章节别名， 以别名为key"""
    word: dict[str, list[str]]
    """jrrp"""
    info_by_difficulty = {}  # noqa: RUF012
    """按dif分的info"""

    async def init(self):
        if self.initIng:
            return self
        if not (originalIllPath / "插眼").exists():
            logger.error(
                "未下载曲绘文件，建议使用 /phi downill 命令进行下载", "phi-plugin"
            )
        self.initIng = True
        for file in DlcInfoPath.iterdir():
            if file.suffix == ".json":
                self.DLC_Info[file.stem] = await readFile.FileReader(file)

        csv_avatar = await readFile.FileReader(infoPath / "avatar.csv")

        for item in csv_avatar:
            self.avatarid[item["id"]] = item["id"]

        self.Tips = await readFile.FileReader(infoPath / "tips.yaml")
        user_song = await readFile.FileReader(configPath / "nickconfig.yaml", "TXT")
        if PluginConfig.get("otherinfo"):
            for item in user_song.values():
                if item.get("illustration_big"):
                    self.illlist.append(item["song"])
        sp_info = await readFile.FileReader(infoPath / "spinfo.json")

        for song, value in sp_info.items():
            value = await SongsInfo.init(value)
            value.sp_vis = True
            if value.illustration_big:
                self.illlist.append(value.song)
            self.sp_info[song] = value

        #  note统计
        noteInfo: dict[str, LevelRecordList] = await readFile.FileReader(
            infoPath / "notesInfo.json"
        )
        CsvInfo: list[csvDetail] = await readFile.FileReader(infoPath / "info.csv")
        Csvdif: list[dict] = await readFile.FileReader(infoPath / "difficulty.csv")
        Jsoninfo: dict = await readFile.FileReader(infoPath / "infolist.json")
        oldDif: list[dict] = await readFile.FileReader(oldInfoPath / "difficulty.csv")
        oldNotes: dict[str, LevelRecordList] = await readFile.FileReader(
            oldInfoPath / "notesInfo.json"
        )

        OldDifList: dict[str, dict[str, float]] = {item["id"]: item for item in oldDif}

        for i in range(len(CsvInfo)):
            song_data = CsvInfo[i]

            # 检查是否为新增曲目
            if not OldDifList.get(song_data["id"]):
                self.updatedSong.append(song_data["song"])

            # 特殊曲目名称修正
            match song_data["id"]:
                case "AnotherMe.DAAN":
                    song_data["song"] = "Another Me (KALPA)"
                case "AnotherMe.NeutralMoon":
                    song_data["song"] = "Another Me (Rising Sun Traxx)"

            # 构建 songsid 和 idssong 映射
            self.songsid[f"{song_data['id']}.0"] = song_data["song"]
            self.idssong[song_data["song"]] = f"{song_data['id']}.0"

            # 构建 ori_info
            song_name = song_data["song"]
            json_info: dict | None = Jsoninfo.get(song_data["id"])
            if json_info is None:
                logger.info(f"曲目详情未更新：{song_name}", "phi-plugin")
                json_info = {
                    "song": song_name,
                    "chapter": "",
                    "bpm": "",
                    "length": "",
                    "chart": {},
                }
            else:
                json_info = dict(json_info)  # 浅拷贝防止污染原数据

            json_info["song"] = song_name
            json_info["id"] = f"{song_data['id']}.0"
            json_info["composer"] = song_data.get("composer", "")
            json_info["illustrator"] = song_data.get("illustrator", "")
            chart: dict[str, Chart] = json_info.setdefault("chart", {})

            # 遍历每个难度等级
            for level in self.Level:
                if not song_data.get(level):  # 当前难度不存在
                    continue

                id_key = song_data["id"]
                # 获取新旧数据
                new_dif = (
                    float(Csvdif[i][level])
                    if isinstance(Csvdif[i], dict) and Csvdif[i].get(level)
                    else 0
                )
                new_notes: levelDetail = noteInfo[id_key][level]
                old_level_data = OldDifList.get(id_key, {}).get(level)
                old_note_data: levelDetail | None = oldNotes.get(id_key, {}).get(level)

                # 判断是否发生变化
                is_new_chart = False
                update_difficulty = None
                update_tap = update_drag = update_hold = update_flick = update_combo = (
                    None
                )

                if OldDifList.get(id_key):
                    if not old_level_data or old_level_data != Csvdif[i][level]:
                        update_difficulty = (
                            [old_level_data, new_dif]
                            if old_level_data
                            else [None, new_dif]
                        )
                        is_new_chart = True
                    if (
                        old_note_data
                        and new_notes
                        and old_note_data["t"] != new_notes["t"]
                    ):
                        t_old = old_note_data["t"]
                        t_new = new_notes["t"]
                        if t_old[0] != t_new[0]:
                            update_tap = [t_old[0], t_new[0]]
                        if t_old[1] != t_new[1]:
                            update_drag = [t_old[1], t_new[1]]
                        if t_old[2] != t_new[2]:
                            update_hold = [t_old[2], t_new[2]]
                        if t_old[3] != t_new[3]:
                            update_flick = [t_old[3], t_new[3]]
                        old_combo = sum(t_old[:4])
                        new_combo = sum(t_new[:4])
                        if old_combo != new_combo:
                            update_combo = [old_combo, new_combo]
                        is_new_chart = True

                # 如果是新图表或有变动，记录到 updatedChart
                if is_new_chart:
                    if song_name not in self.updatedChart:
                        self.updatedChart[song_name] = {}
                    self.updatedChart[song_name][level] = Chart(
                        **{
                            "difficulty": update_difficulty,
                            "tap": update_tap,
                            "drag": update_drag,
                            "hold": update_hold,
                            "flick": update_flick,
                            "combo": update_combo,
                            "isNew": not old_level_data,  # 如果没有旧难度就是全新
                        }
                    )

                # 更新 chart 数据
                chart[level] = Chart(
                    **{
                        "charter": song_data.get(level, ""),
                        "difficulty": new_dif,
                        "tap": new_notes["t"][0],
                        "drag": new_notes["t"][1],
                        "hold": new_notes["t"][2],
                        "flick": new_notes["t"][3],
                        "combo": sum(new_notes["t"][:4]),
                        "maxTime": new_notes["m"],
                        "distribution": new_notes["d"],
                    }
                )

                # 更新最高定数
                self.MAX_DIFFICULTY = max(self.MAX_DIFFICULTY, new_dif)

            # 添加曲目到列表
            self.illlist.append(song_name)
            self.songlist.append(song_name)
            # 完成 ori_info 构建
            self.ori_info[song_name] = await SongsInfo.init(json_info)
        if self.MAX_DIFFICULTY != MAX_DIFFICULTY:
            logger.error(
                "MAX_DIFFICULTY 常量未更新，请回报作者！"
                f"MAX_DIFFICULTY: {MAX_DIFFICULTY}, "
                f"cls.MAX_DIFFICULTY: {self.MAX_DIFFICULTY}",
                "phi-plugin",
            )
        nicklistTemp: dict[str, list[str]] = await readFile.FileReader(
            infoPath / "nicklist.yaml"
        )
        for id in nicklistTemp:
            song = self.idgetsong(f"{id}.0") or id
            self.nicklist[song] = nicklistTemp[id]
            for item in nicklistTemp[id]:
                if item in self.songnick:
                    self.songnick[item].append(song)
                else:
                    self.songnick[item] = [song]
        self.chapList = await readFile.FileReader(infoPath / "chaplist.yaml")
        for chapter, aliases in self.chapList.items():
            for alias in aliases:
                if alias in self.chapNick:
                    self.chapNick[alias].append(chapter)
                else:
                    self.chapNick[alias] = [chapter]
        self.word = await readFile.FileReader(infoPath / "jrrp.json")

        for song_data in self.ori_info.values():
            chart = song_data.chart
            for level, chart_data in chart.items():
                difficulty = chart_data.difficulty
                if not difficulty:
                    continue  # 跳过无定数的数据

                # 构造要插入的数据项
                entry = {
                    "id": song_data.id,
                    "rank": level,
                    **to_dict(chart_data),
                }

                # 插入到对应难度的列表中
                if difficulty in self.info_by_difficulty:
                    self.info_by_difficulty[difficulty].append(entry)
                else:
                    self.info_by_difficulty[difficulty] = [entry]
        self.initIng = False
        logger.success("初始化曲目信息完成", "phi-plugin")
        return self

    async def info(self, song: str, original: bool = False) -> SongsInfoObject | None:
        """
        获取曲目信息

        :param str song: 原曲曲名
        :param bool original: 仅使用原版
        """
        result: dict[str, dict[str, Any]]
        match 0 if original else PluginConfig.get("otherinfo"):
            case 0:
                result = {**to_dict(self.ori_info), **to_dict(self.sp_info)}
            case 1:
                result = {
                    **to_dict(self.ori_info),
                    **to_dict(self.sp_info),
                    **(await readFile.FileReader(configPath / "otherinfo.yaml")),
                }
            case 2:
                result = await readFile.FileReader(configPath / "otherinfo.yaml")
            case _:
                raise ValueError("Invalid otherinfo")
        return await SongsInfo.init(result[song]) if song in result else None

    async def all_info(self, original: bool = False) -> dict[str, SongsInfoObject]:
        """
        获取全部曲目信息

        :param original: 仅使用原版
        """

        match 0 if original else PluginConfig.get("otherinfo"):
            case 0:
                return {**self.ori_info, **self.sp_info}
            case 1:
                return {
                    **self.ori_info,
                    **self.sp_info,
                    **(await readFile.FileReader(configPath / "otherinfo.yaml")),
                }
            case 2:
                return await readFile.FileReader(configPath / "otherinfo.yaml")
            case _:
                raise ValueError("Invalid otherinfo")

    async def songsnick(self, mic) -> list[str] | Literal[False]:
        """
        匹配歌曲名称，根据参数返回原曲名称列表

        :param str mic: 别名
        :return: 原曲名称列表或 False
        """
        nickconfig = await readFile.FileReader(configPath / "nickconfig.yaml")
        all_songs = []

        # 如果 mic 是一个有效的歌曲名称，直接添加
        if self.info(mic):
            all_songs.append(mic)

        # 添加 songnick 中的别名对应的原曲名称
        if mic in self.songnick:
            all_songs.extend(self.songnick[mic])

        # 添加 nickconfig 中的别名对应的歌曲名称
        if nickconfig:
            all_songs.extend(nickconfig.values())

        # 去重并判断是否非空
        return list(set(all_songs)) if all_songs else False

    async def fuzzysongsnick(self, mic: str, Distance: float = 0.85) -> list[str]:
        """
        根据参数模糊匹配返回原曲名称列表，按照匹配程度降序排列

        :param mic: 别名
        :param Distance: 匹配阈值，猜词0.95
        :return: 原曲名称数组，按照匹配程度降序
        """

        result = []  # 存储匹配结果 { song, dis }

        # 获取用户配置和所有曲目信息
        usernick = await readFile.FileReader(configPath / "nickconfig.yaml")
        allinfo = await self.all_info()

        # 遍历用户自定义别名（usernick[std] 是一组别名对应的歌曲）
        if usernick:
            for std in usernick:
                dis = fCompute.jaroWinklerDistance(mic, std)
                if dis >= Distance:
                    result.extend(
                        {"song": song, "dis": dis}
                        for song in list(usernick[std].values())
                    )
        # 遍历 songnick（别名到歌曲的映射）
        for std in self.songnick:
            dis = fCompute.jaroWinklerDistance(mic, std)
            if dis >= Distance:
                result.extend({"song": song, "dis": dis} for song in self.songnick[std])
        # 遍历所有曲目信息（检查歌曲名和 id）
        for std in allinfo:
            song_info = allinfo[std]
            dis = fCompute.jaroWinklerDistance(mic, std)
            if dis >= Distance:
                result.append({"song": song_info.song, "dis": dis})
            # 检查是否存在 id 字段，并进行相似度判断
            if song_info.id:
                dis_id = fCompute.jaroWinklerDistance(mic, song_info.id)
                if dis_id >= Distance:
                    result.append({"song": song_info.song, "dis": dis_id})

        # 排序：按 dis 从高到低
        result.sort(key=lambda x: -x["dis"])

        # 厺重 + 判断是否遇到完全匹配（dis == 1）则只保留前几个
        all_songs = []
        for i in result:
            if i["song"] in all_songs:
                continue
            # 如果第一个是完全匹配，后面小于 1 的就跳过
            if result and result[0]["dis"] == 1.0 and i["dis"] < 1.0:
                break
            all_songs.append(i["song"])

        return all_songs

    @staticmethod
    async def setnick(mic: str, nick: str):
        """
        设置别名

        :param str mic: 原名
        :param str nick: 别名
        """
        nickconfig = await readFile.FileReader(configPath / "nickconfig.yaml")
        if nickconfig.get(mic):
            nickconfig[mic].append(nick)
        else:
            nickconfig[mic] = [nick]
        await readFile.SetFile(configPath / "nickconfig.yaml", nickconfig)

    async def getill(
        self, song: str, kind: Literal["common", "blur", "low"] = "common"
    ) -> str | Path:
        """
        获取曲绘，返回地址

        :param str  song: 原名
        :param str kind: 清晰度

        :return str | Path: 网址或文件地址
        """
        songsinfo = (await self.all_info()).get(song, {})
        ans = to_dict(songsinfo).get("illustration_big")

        url_pattern = re.compile(
            r"^(?:(http|https|ftp)://)"  # 协议部分
            r"((?:[a-z0-9-]+\.)+[a-z0-9]+)"  # 域名
            r"((?:/[^/?#]*)+)?"  # 路径可选
            r"(\?[^#]*)?"  # 查询参数可选
            r"(#.*)?$",  # 锚点可选
            re.IGNORECASE,
        )

        if ans and not url_pattern.match(ans):
            ans = ortherIllPath / ans
        elif self.ori_info.get(song) or self.sp_info.get(song):
            if self.ori_info.get(song):
                SongId = self.SongGetId(song)
                assert SongId is not None
                if (originalIllPath / re.sub(r"\.0$", ".png", SongId)).exists():
                    ans = originalIllPath / re.sub(r"\.0$", ".png", SongId)
                elif (
                    originalIllPath / "ill" / re.sub(r"\.0$", ".png", SongId)
                ).exists():
                    if kind == "common":
                        ans = originalIllPath / "ill" / re.sub(r"\.0$", ".png", SongId)
                    elif kind == "blur":
                        ans = (
                            originalIllPath
                            / "illBlur"
                            / re.sub(r"\.0$", ".png", SongId)
                        )
                    elif kind == "low":
                        ans = (
                            originalIllPath / "illLow" / re.sub(r"\.0$", ".png", SongId)
                        )
                elif kind == "common":
                    ans = (
                        PluginConfig.get("onLinePhiIllUrl")
                        + "/ill/"
                        + re.sub(r"\.0$", ".png", SongId)
                    )
                elif kind == "blur":
                    ans = (
                        PluginConfig.get("onLinePhiIllUrl")
                        + "/illBlur/"
                        + re.sub(r"\.0$", ".png", SongId)
                    )
                elif kind == "low":
                    ans = (
                        PluginConfig.get("onLinePhiIllUrl")
                        + "/illLow/"
                        + re.sub(r"\.0$", ".png", SongId)
                    )
            elif (originalIllPath / "SP" / f"{song}.png").exists():
                ans = originalIllPath / "SP" / f"{song}.png"
            else:
                ans = PluginConfig.get("onLinePhiIllUrl") + "/SP/" + f"{song}.png"
        if not ans:
            logger.warning(f"{song} 背景不存在", "phi_plugin")
            ans = imgPath / "phigros.png"
        return ans

    @staticmethod
    def getTableImg(dif: str) -> str | Path:
        if (originalIllPath / "table" / f"{dif}.png").exists():
            return originalIllPath / "table" / f"{dif}.png"
        else:
            return PluginConfig.get("onLinePhiIllUrl") + "/table/" + f"{dif}.png"

    @staticmethod
    def getChapIll(name: str) -> str | Path:
        """
        返回章节封面地址

        :param str name: 标准章节名
        """
        if (originalIllPath / "chap" / f"{name}.png").exists():
            return originalIllPath / "chap" / f"{name}.png"
        else:
            return PluginConfig.get("onLinePhiIllUrl") + "/chap/" + f"{name}.png"

    def idgetavatar(self, id: str):
        """
        通过id获得头像文件名称

        :param str id: id

        :return: file name
        """
        return self.avatarid[id] if id in self.avatarid else "Introduction"

    def idgetsong(self, id: str) -> str | None:
        """
        根据曲目id获取原名

        :param str id: 曲目id

        :return: 原名
        """
        return self.songsid.get(id)

    def SongGetId(self, song: str) -> str | None:
        """
        通过原曲曲目获取曲目id

        :param str song: 原曲曲名

        :return: 曲目id
        """
        return self.idssong.get(song)

    async def getBackground(self, save_background: str) -> Path | str | bool:
        """
        获取角色介绍背景曲绘
        """
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
            return await self.getill(self.idgetsong(save_background) or save_background)
        except Exception as e:
            logger.error("获取背景曲绘错误", "phi-plugin", e=e)
            return False


getInfo = asyncio.run(_getInfo().init())
