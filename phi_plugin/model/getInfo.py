from pathlib import Path
import re
from typing import Any, Literal

from zhenxun.services.log import logger

from ..config import PluginConfig
from ..utils import to_dict
from .cls.SongsInfo import SongsInfo
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


class getInfo:
    initIng = False

    @classmethod
    async def init(cls):
        if cls.initIng:
            return
        if not (originalIllPath / "插眼").exists():
            logger.error(
                "未下载曲绘文件，建议使用 /phi downill 命令进行下载", "phi-plugin"
            )
        cls.initIng = True
        # 之前改过一次名称，修正别名
        nick = await readFile.FileReader(configPath / "nickconfig.yaml", "TXT")
        if nick:
            wait_to_replace = {
                "Winter↑cube↓": "Winter ↑cube↓",
                "Cipher: /2&//<|0": "Cipher : /2&//<|0",
                "NYA!!!(Phigros ver.)": "NYA!!! (Phigros ver.)",
                "JunXion Between Life And Death(VIP Mix)": (
                    "JunXion Between Life And Death(VIP Mix)"
                ),
                "Dash from SOUL NOTES": "Dash",
                "Drop It from SOUL NOTES": "Drop It",
                "Diamond Eyes from SOUL NOTES": "Diamond Eyes",
            }
            flag = False
            for old, new in wait_to_replace.items():
                if old in nick:
                    flag = True
                    nick = nick.replace(old, new)
            if flag:
                await readFile.SetFile(configPath / "nickconfig.yaml", nick, "TXT")
                logger.success("自动修正别名", "phi-plugin")

        # 扩增曲目信息
        cls.DLC_Info: dict[str, dict[str, list[str]]] = {}
        for file in DlcInfoPath.iterdir():
            if file.suffix == ".json":
                cls.DLC_Info[file.stem] = await readFile.FileReader(file)

        # 头像id
        csv_avatar = await readFile.FileReader(infoPath / "avatar.csv")
        cls.avatarid: dict[str, str] = {}

        for item in csv_avatar:
            cls.avatarid[item["id"]] = item["id"]

        # Tips
        cls.Tips: list[str] = await readFile.FileReader(infoPath / "tips.yaml")
        # 原版信息
        cls.ori_info: dict[str, SongsInfo] = {}
        # 通过id获取曲名
        cls.songsid: dict[str, str] = {}
        # 原曲名称获取id
        cls.idssong: dict[str, str] = {}
        # 含有曲绘的曲目列表，原曲名称
        cls.illlist: list[str] = []
        # 自定义信息
        user_song = await readFile.FileReader(configPath / "nickconfig.yaml", "TXT")
        if PluginConfig.get("otherinfo"):
            for item in user_song.values():
                if item.get("illustration_big"):
                    cls.illlist.append(item["song"])
        # SP信息
        cls.sp_info: dict[str, SongsInfo]
        sp_info: dict[str, dict[str, Any]] = await readFile.FileReader(
            infoPath / "spinfo.json"
        )

        for song, value in sp_info.items():
            value = await SongsInfo.init(value)
            value.sp_vis = True
            if value.illustration_big:
                cls.illlist.append(value.song)
            cls.sp_info[song] = value

        # 难度映射
        cls.Level = Level
        # 最高定数
        cls.MAX_DIFFICULTY = 0
        # 所有曲目曲名列表
        cls.songlist = []
        #  note统计
        """
        数据结构
        {
            idString: {
                levelStr: {
                    'm': int,
                    'd': List[Tuple[int, int, int, int, int]],
                    't': Tuple[int, int, int, int]
                },
                ...
            },
            ...
        }
        """
        noteInfo: dict[
            str,
            dict[
                str,
                dict[
                    str,
                    int | list[tuple[int, int, int, int]] | tuple[int, int, int, int],
                ],
            ],
        ] = await readFile.FileReader(infoPath / "notesInfo.json")
        CsvInfo: list[dict] = await readFile.FileReader(infoPath / "info.csv")
        Csvdif: list[dict] = await readFile.FileReader(infoPath / "difficulty.csv")
        Jsoninfo: dict = await readFile.FileReader(infoPath / "infolist.json")
        oldDif: list[dict] = await readFile.FileReader(oldInfoPath / "difficulty.csv")
        oldNotes: dict = await readFile.FileReader(oldInfoPath / "notesInfo.json")

        OldDifList: dict[str, dict] = {item["id"]: item for item in oldDif}

        cls.updatedSong = []
        cls.updatedChart = {}

        for i in range(len(CsvInfo)):
            song_data = CsvInfo[i]

            # 检查是否为新增曲目
            if not OldDifList.get(song_data["id"]):
                cls.updatedSong.append(song_data["song"])

            # 特殊曲目名称修正
            match song_data["id"]:
                case "AnotherMe.DAAN":
                    song_data["song"] = "Another Me (KALPA)"
                case "AnotherMe.NeutralMoon":
                    song_data["song"] = "Another Me (Rising Sun Traxx)"

            # 构建 songsid 和 idssong 映射
            cls.songsid[f"{song_data['id']}.0"] = song_data["song"]
            cls.idssong[song_data["song"]] = f"{song_data['id']}.0"

            # 构建 ori_info
            song_name = song_data["song"]
            json_info = Jsoninfo.get(song_data["id"])
            if not json_info:
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
            chart = json_info.setdefault("chart", {})

            # 遍历每个难度等级
            for level in cls.Level:
                if not song_data.get(level):  # 当前难度不存在
                    continue

                id_key = song_data["id"]
                # 获取新旧数据
                new_dif = (
                    float(Csvdif[i][level])
                    if isinstance(Csvdif[i], dict) and Csvdif[i].get(level)
                    else 0
                )
                new_notes = noteInfo[id_key][level]
                assert isinstance(new_notes["t"], tuple)
                old_level_data = OldDifList.get(id_key, {}).get(level)
                old_note_data = oldNotes.get(id_key, {}).get(level)

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
                    if song_name not in cls.updatedChart:
                        cls.updatedChart[song_name] = {}
                    cls.updatedChart[song_name][level] = {
                        "difficulty": update_difficulty,
                        "tap": update_tap,
                        "drag": update_drag,
                        "hold": update_hold,
                        "flick": update_flick,
                        "combo": update_combo,
                        "isNew": not old_level_data,  # 如果没有旧难度就是全新
                    }

                # 更新 chart 数据
                chart[level] = {
                    "charter": song_data[level],
                    "difficulty": new_dif,
                    "tap": new_notes["t"][0],
                    "drag": new_notes["t"][1],
                    "hold": new_notes["t"][2],
                    "flick": new_notes["t"][3],
                    "combo": sum(new_notes["t"][:4]),
                    "maxTime": new_notes["m"],
                    "distribution": new_notes["d"],
                }

                # 更新最高定数
                cls.MAX_DIFFICULTY = max(cls.MAX_DIFFICULTY, new_dif)

            # 添加曲目到列表
            cls.illlist.append(song_name)
            cls.songlist.append(song_name)
            # 完成 ori_info 构建
            cls.ori_info[song_name] = await SongsInfo.init(json_info)
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
        # 默认别名,以曲名为key
        cls.nicklist: dict[str, list[str]] = {}
        # 以别名为key
        cls.songnick: dict[str, list[str]] = {}
        for id in nicklistTemp:
            song = cls.idgetsong(f"{id}.0") or id
            cls.nicklist[song] = nicklistTemp[id]
            for item in nicklistTemp[id]:
                if item in cls.songnick:
                    cls.songnick[item].append(song)
                else:
                    cls.songnick[item] = [song]
        # 章节列表，以章节名为key
        cls.chapList: dict[str, list[str]] = await readFile.FileReader(
            infoPath, "chaplist.yaml"
        )
        # 章节别名， 以别名为key
        cls.chapNick: dict[str, list[str]] = {}
        for chapter, aliases in cls.chapList.items():
            for alias in aliases:
                if alias in cls.chapNick:
                    cls.chapNick[alias].append(chapter)
                else:
                    cls.chapNick[alias] = [chapter]
        # jrrp
        cls.word: dict[str, list[str]] = await readFile.FileReader(
            infoPath, "jrrp.json"
        )
        # 按dif分的info
        cls.info_by_difficulty = {}

        for song_data in cls.ori_info.values():
            chart = song_data.chart
            for level, chart_data in chart.items():
                difficulty = chart_data["difficulty"]
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
        cls.initIng = False
        logger.success("初始化曲目信息完成", "phi-plugin")

    @classmethod
    async def info(
        cls, song: str | None = None, original: bool = False
    ) -> SongsInfo | None:
        """
        获取曲目信息

        :param str song: 原曲曲名
        :param bool original: 仅使用原版
        """
        result: dict[str, dict[str, Any]]
        match 0 if original else PluginConfig.get("otherinfo"):
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
                raise ValueError("Invalid otherinfo")
        return (
            await SongsInfo.init(result[song])
            if song is not None and song in result
            else None
        )

    @classmethod
    async def all_info(cls, original: bool = False) -> dict[str, SongsInfo]:
        """
        获取全部曲目信息

        :param original: 仅使用原版
        """

        match 0 if original else PluginConfig.get("otherinfo"):
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
                raise ValueError("Invalid otherinfo")

    @classmethod
    async def songsnick(cls, mic) -> list[str] | bool:
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
                SongId = cls.SongGetId(song)
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

    @classmethod
    def idgetavatar(cls, id: str):
        """
        通过id获得头像文件名称

        :param str id: id

        :return: file name
        """
        return cls.avatarid[id] if id in cls.avatarid else "Introduction"

    @classmethod
    def idgetsong(cls, id: str) -> str | None:
        """
        根据曲目id获取原名

        :param str id: 曲目id

        :return: 原名
        """
        return cls.songsid.get(id)

    @classmethod
    def SongGetId(cls, song: str) -> str | None:
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
                getInfo.idgetsong(save_background) or save_background
            )
        except Exception as e:
            logger.error("获取背景曲绘错误", "phi-plugin", e=e)
            return False
