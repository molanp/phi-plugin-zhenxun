from pathlib import Path
import re
from typing import Any, Literal

from pydantic import BaseModel

from zhenxun.services.log import logger

from ..config import PluginConfig, onLinePhiIllUrl
from ..utils import to_dict
from .cls.Chart import Chart
from .cls.SongsInfo import SongsInfo, SongsInfoObject
from .constNum import MAX_DIFFICULTY, Level
from .fCompute import fCompute
from .getFile import readFile
from .path import DlcInfoPath, configPath, imgPath, infoPath, oldInfoPath, ortherIllPath


class levelDetail(BaseModel):
    m: float = 0
    """MaxTime"""
    d: list[tuple[float, float, float, float, float]] = []
    """note分布[tap,drag,hold,flick]"""
    t: tuple[float, float, float, float] = (0, 0, 0, 0)
    """note统计[tap,drag,hold,flick]"""


class LevelRecordList(BaseModel):
    EZ: levelDetail = levelDetail()
    HD: levelDetail = levelDetail()
    IN: levelDetail = levelDetail()
    AT: levelDetail = levelDetail()


class csvDetail(BaseModel):
    id: str
    """曲目id"""
    song: str
    """曲目名称"""
    composer: str = ""
    """作曲"""
    illustrator: str = ""
    """插画师"""
    EZ: str
    """EZ难度谱师"""
    HD: str
    """HD难度谱师"""
    IN: str
    """IN难度谱师"""
    AT: str | None
    """AT难度谱师"""


class getInfo:
    inited: bool = False
    DLC_Info: dict[str, dict[str, list[str]]] = {}  # noqa: RUF012
    """扩增曲目信息"""
    avatarid: dict[str, str] = {}  # noqa: RUF012
    """头像id"""
    Tips: list[str] = []  # noqa: RUF012
    """Tips"""
    ori_info: dict[str, SongsInfoObject] = {}  # noqa: RUF012
    """原版信息"""
    songsid: dict[str, str] = {}  # noqa: RUF012
    """通过id获取曲名"""
    idssong: dict[str, str] = {}  # noqa: RUF012
    """原曲名称获取id"""
    illlist: list[str] = []  # noqa: RUF012
    """含有曲绘的曲目列表，原曲名称"""
    sp_info: dict[str, SongsInfoObject] = {}  # noqa: RUF012
    """SP信息"""
    Level: list[str] = Level
    """难度映射"""
    MAX_DIFFICULTY: float = 0
    """最高定数"""
    songlist: list[str] = []  # noqa: RUF012
    """所有曲目曲名列表"""
    updatedSong: list[str] = []  # noqa: RUF012
    updatedChart: dict[str, dict[str, Chart]] = {}  # noqa: RUF012
    nicklist: dict[str, list[str]] = {}  # noqa: RUF012
    """默认别名,以曲名为key"""
    songnick: dict[str, list[str]] = {}  # noqa: RUF012
    """以别名为key"""
    chapList: dict[str, list[str]]
    """章节列表，以章节名为key"""
    chapNick: dict[str, list[str]] = {}  # noqa: RUF012
    """章节别名， 以别名为key"""
    word: dict[str, list[str]] = {}  # noqa: RUF012
    """jrrp"""
    info_by_difficulty: dict[float | str, list[dict]] = {}  # noqa: RUF012
    """按dif分的info"""

    @classmethod
    async def init(cls):
        if cls.inited:
            return cls
        for file in DlcInfoPath.iterdir():
            if file.suffix == ".json":
                cls.DLC_Info[file.stem] = await readFile.FileReader(file)

        csv_avatar = await readFile.FileReader(infoPath / "avatar.csv")

        for item in csv_avatar:
            cls.avatarid[item["id"]] = item["id"]

        cls.Tips = await readFile.FileReader(infoPath / "tips.yaml")
        user_song = await readFile.FileReader(configPath / "nickconfig.yaml", "TXT")
        if PluginConfig.get("otherinfo"):
            for item in user_song.values():
                if item.get("illustration_big"):
                    cls.illlist.append(item["song"])
        sp_info = await readFile.FileReader(infoPath / "spinfo.json")

        for song, value in sp_info.items():
            value = await SongsInfo.init(value)
            value.sp_vis = True
            if value.illustration_big:
                cls.illlist.append(value.song)
            cls.sp_info[song] = value

        #  note统计
        noteInfo: dict[str, LevelRecordList] = {
            k: LevelRecordList(**v)
            for k, v in (await readFile.FileReader(infoPath / "notesInfo.json")).items()
        }
        CsvInfo: list[csvDetail] = [
            csvDetail(**{str(k): v for k, v in item.items()})
            for item in await readFile.FileReader(infoPath / "info.csv")
        ]
        Csvdif: list[dict] = await readFile.FileReader(infoPath / "difficulty.csv")
        Jsoninfo: dict = await readFile.FileReader(infoPath / "infolist.json")
        oldDif: list[dict] = await readFile.FileReader(oldInfoPath / "difficulty.csv")
        oldNotes: dict[str, LevelRecordList] = {
            k: LevelRecordList(**v)
            for k, v in (
                await readFile.FileReader(oldInfoPath / "notesInfo.json")
            ).items()
        }

        OldDifList: dict[str, dict[str, float]] = {item["id"]: item for item in oldDif}

        for i in range(len(CsvInfo)):
            song_data = CsvInfo[i]

            # 检查是否为新增曲目
            if not OldDifList.get(song_data.id):
                cls.updatedSong.append(song_data.song)

            # 特殊曲目名称修正
            match song_data.id:
                case "AnotherMe.DAAN":
                    song_data.song = "Another Me (KALPA)"
                case "AnotherMe.NeutralMoon":
                    song_data.song = "Another Me (Rising Sun Traxx)"

            # 构建 songsid 和 idssong 映射
            cls.songsid[f"{song_data.id}.0"] = song_data.song
            cls.idssong[song_data.song] = f"{song_data.id}.0"

            # 构建 ori_info
            song_name = song_data.song
            cls.ori_info[song_name] = SongsInfoObject(**Jsoninfo.get(song_data.id, {}))
            if cls.ori_info.get(song_name) is None:
                logger.info(f"曲目详情未更新：{song_name}", "phi-plugin")
                cls.ori_info[song_name] = SongsInfoObject(
                    **{
                        "song": song_name,
                        "chapter": "",
                        "bpm": "",
                        "length": "",
                        "chart": {},
                    }
                )
            cls.ori_info[song_name].song = song_name
            cls.ori_info[song_name].id = f"{song_data.id}.0"
            cls.ori_info[song_name].composer = song_data.composer
            cls.ori_info[song_name].illustrator = song_data.illustrator

            # 遍历每个难度等级
            for level in cls.Level:
                if not getattr(song_data, level, None):  # 当前难度不存在
                    continue

                id_key = song_data.id
                # 获取新旧数据
                new_dif = (
                    float(Csvdif[i][level])
                    if isinstance(Csvdif[i], dict) and Csvdif[i].get(level)
                    else 0
                )
                new_notes: levelDetail = getattr(noteInfo[id_key], level, levelDetail())
                old_level_data = OldDifList.get(id_key, {}).get(level)
                old_note_data: levelDetail | None = getattr(
                    oldNotes.get(id_key, {}), level, None
                )

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
                    if old_note_data and new_notes and old_note_data.t != new_notes.t:
                        t_old = old_note_data.t
                        t_new = new_notes.t
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
                    if song_name not in cls.updatedChart:
                        cls.updatedChart[song_name] = {}
                    cls.updatedChart[song_name][level] = Chart(
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
                cls.ori_info[song_name].chart[level] = Chart(
                    **{
                        "charter": getattr(song_data, level, ""),
                        "difficulty": new_dif,
                        "tap": new_notes.t[0],
                        "drag": new_notes.t[1],
                        "hold": new_notes.t[2],
                        "flick": new_notes.t[3],
                        "combo": sum(new_notes.t[:4]),
                        "maxTime": new_notes.m,
                        "distribution": new_notes.d,
                    }
                )

                # 更新最高定数
                cls.MAX_DIFFICULTY = max(cls.MAX_DIFFICULTY, new_dif)

            # 添加曲目到列表
            cls.illlist.append(song_name)
            cls.songlist.append(song_name)
        if cls.MAX_DIFFICULTY != MAX_DIFFICULTY:
            logger.error(
                "MAX_DIFFICULTY 常量未更新，请回报作者！"
                f"MAX_DIFFICULTY: {MAX_DIFFICULTY}, "
                f"cls.MAX_DIFFICULTY: {cls.MAX_DIFFICULTY}",
                "phi-plugin",
            )
        nicklistTemp: dict[str, list[str]] = await readFile.FileReader(
            infoPath / "nicklist.yaml"
        )
        for id in nicklistTemp:
            song = await cls.idgetsong(f"{id}.0") or id
            cls.nicklist[song] = nicklistTemp[id]
            for item in nicklistTemp[id]:
                if item in cls.songnick:
                    cls.songnick[item].append(song)
                else:
                    cls.songnick[item] = [song]
        cls.chapList = await readFile.FileReader(infoPath / "chaplist.yaml")
        for chapter, aliases in cls.chapList.items():
            for alias in aliases:
                if alias in cls.chapNick:
                    cls.chapNick[alias].append(chapter)
                else:
                    cls.chapNick[alias] = [chapter]
        cls.word = await readFile.FileReader(infoPath / "jrrp.json")

        for song_data in cls.ori_info.values():
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
                if difficulty in cls.info_by_difficulty:
                    cls.info_by_difficulty[difficulty].append(entry)
                else:
                    cls.info_by_difficulty[difficulty] = [entry]
        cls.inited = True
        logger.info("初始化曲目信息完成", "phi-plugin")
        return cls

    @classmethod
    async def info(cls, song: str, original: bool = False) -> SongsInfoObject | None:
        """
        获取曲目信息

        :param str song: 原曲曲名
        :param bool original: 仅使用原版
        """
        result: dict[str, dict[str, Any]]
        match 0 if original else PluginConfig.get("otherinfo", 0):
            case 0:
                result = {**to_dict(cls.ori_info), **to_dict(cls.sp_info)}
            case 1:
                result = {
                    **to_dict(cls.ori_info),
                    **to_dict(cls.sp_info),
                    **(await readFile.FileReader(configPath / "otherinfo.yaml")),
                }
            case 2:
                result = await readFile.FileReader(configPath / "otherinfo.yaml")
            case _:
                raise ValueError(f"Invalid otherinfo: {original}")
        return await SongsInfo().init(result[song]) if song in result else None

    @classmethod
    async def all_info(cls, original: bool = False) -> dict[str, SongsInfoObject]:
        """
        获取全部曲目信息

        :param original: 仅使用原版
        """
        match 0 if original else PluginConfig.get("otherinfo", 0):
            case 0:
                return {**cls.ori_info, **cls.sp_info}
            case 1:
                return {
                    **cls.ori_info,
                    **cls.sp_info,
                    **(await readFile.FileReader(configPath / "otherinfo.yaml")),
                }
            case 2:
                return await readFile.FileReader(configPath / "otherinfo.yaml")
            case _:
                raise ValueError(f"Invalid otherinfo: {original}")

    @classmethod
    async def songsnick(cls, mic) -> list[str] | Literal[False]:
        """
        匹配歌曲名称，根据参数返回原曲名称列表

        :param str mic: 别名
        :return: 原曲名称列表或 False
        """
        nickconfig = await readFile.FileReader(configPath / "nickconfig.yaml")
        all_songs = []

        # 如果 mic 是一个有效的歌曲名称，直接添加
        if cls.info(mic):
            all_songs.append(mic)

        # 添加 songnick 中的别名对应的原曲名称
        if mic in cls.songnick:
            all_songs.extend(cls.songnick[mic])

        # 添加 nickconfig 中的别名对应的歌曲名称
        if nickconfig:
            all_songs.extend(nickconfig.values())

        # 去重并判断是否非空
        return list(set(all_songs)) if all_songs else False

    @classmethod
    async def fuzzysongsnick(cls, mic: str, Distance: float = 0.85) -> list[str]:
        """
        根据参数模糊匹配返回原曲名称列表，按照匹配程度降序排列

        :param mic: 别名
        :param Distance: 匹配阈值，猜词0.95
        :return: 原曲名称数组，按照匹配程度降序
        """
        result = []  # 存储匹配结果 { song, dis }

        # 获取用户配置和所有曲目信息
        usernick = await readFile.FileReader(configPath / "nickconfig.yaml")
        allinfo = await cls.all_info()

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
        for std in cls.songnick:
            dis = fCompute.jaroWinklerDistance(mic, std)
            if dis >= Distance:
                result.extend({"song": song, "dis": dis} for song in cls.songnick[std])
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

    @classmethod
    async def getill(
        cls, song: str, kind: Literal["common", "blur", "low"] = "common"
    ) -> str | Path:
        """
        获取曲绘，返回地址

        :param str  song: 原名
        :param str kind: 清晰度

        :return str | Path: 网址或文件地址
        """
        songsinfo = (await cls.all_info()).get(song, {})
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
        elif cls.ori_info.get(song) or cls.sp_info.get(song):
            if cls.ori_info.get(song):
                SongId = await cls.SongGetId(song)
                assert SongId is not None
                if kind == "common":
                    ans = f"{onLinePhiIllUrl}/ill/" + re.sub(r"\.0$", ".png", SongId)
                elif kind == "blur":
                    ans = f"{onLinePhiIllUrl}/illBlur/" + re.sub(
                        r"\.0$", ".png", SongId
                    )
                elif kind == "low":
                    ans = f"{onLinePhiIllUrl}/illLow/" + re.sub(r"\.0$", ".png", SongId)
            else:
                ans = f"{onLinePhiIllUrl}/SP/" + f"{song}.png"
        if not ans:
            logger.warning(f"歌曲 {song} 背景不存在(kind: {kind})", "phi-plugin")
            ans = imgPath / "phigros.png"
        return ans

    @staticmethod
    def getTableImg(dif: str) -> str:
        return f"{onLinePhiIllUrl}/table/" + f"{dif}.png"

    @staticmethod
    def getChapIll(name: str) -> str:
        """
        返回章节封面地址

        :param str name: 标准章节名
        """
        return f"{onLinePhiIllUrl}/chap/" + f"{name}.png"

    @classmethod
    async def idgetavatar(cls, id: str):
        """
        通过id获得头像文件名称

        :param str id: id

        :return: file name
        """
        return cls.avatarid[id] if id in cls.avatarid else "Introduction"

    @classmethod
    async def idgetsong(cls, id: str) -> str | None:
        """
        根据曲目id获取原名

        :param str id: 曲目id

        :return: 原名
        """
        return cls.songsid.get(id)

    @classmethod
    async def SongGetId(cls, song: str) -> str | None:
        """
        通过原曲曲目获取曲目id

        :param str song: 原曲曲名

        :return: 曲目id
        """
        return cls.idssong.get(song)

    @classmethod
    async def getBackground(cls, save_background: str) -> Path | str | bool:
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
            return await cls.getill(
                await cls.idgetsong(save_background) or save_background
            )
        except Exception as e:
            logger.error("获取背景曲绘错误", "phi-plugin", e=e)
            return False
