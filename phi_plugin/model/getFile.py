import asyncio
import csv
from io import StringIO
from pathlib import Path
from typing import Any, Literal, cast

import aiofiles
from ruamel.yaml import YAML
import ujson as json

from zhenxun.services.log import logger

from .getRksRank import getRksRank
from .getSave import getSave
from .path import dataPath, pluginDataPath, savePath

_SUPPORTED_FORMATS = Literal["JSON", "YAML", "CSV", "TXT"]


async def csv_write(file_path: str | Path, data: list[dict[str, Any]]):
    """
    data: list[dict]
    ```
    [
        {
            "id": "1",
            "name": "张三",
            "age": "18"
        },
        {
            "id": "2",
            "name": "李四",
            "age": "19"
        }
    ]
    """
    fieldnames = data[0].keys()

    async with aiofiles.open(file_path, mode="w", encoding="utf-8", newline="") as f:
        # 先写入表头
        csv.DictWriter(f, fieldnames=fieldnames)
        await f.write(",".join(fieldnames) + "\n")

        # 逐行写入数据
        for row in data:
            line = ",".join([str(row.get(field, "")) for field in fieldnames]) + "\n"
            await f.write(line)


async def csv_read(file_path: str | Path) -> list[dict[str, Any]]:
    """
    return list[dict]
    ```
    [
        {
            "id": 1,
            "name": "n1",
            "age": 114
        },
        {
            "id": 2,
            "name": "n2",
            "age": 39
        }
    ]
    """
    async with aiofiles.open(file_path, encoding="utf-8") as f:
        content = await f.read()

    # 使用 StringIO 模拟文件对象供 csv 模块使用
    f_obj = StringIO(content)
    reader = csv.DictReader(f_obj)
    return [dict(row) for row in reader]


class readFile:
    @classmethod
    async def FileReader(
        cls,
        file_path: str | Path,
        style: _SUPPORTED_FORMATS | None = None,
    ) -> Any:
        """
        读取文件

        :param file_path: 完整路径
        :param style: 强制设置文件格式
        :return:  读取内容，失败返回 False
        """
        try:
            if not Path(file_path).exists():
                return False
            if style is None:
                ext = Path(file_path).suffix[1:].upper()
                if ext in ["JSON", "YAML", "CSV", "TXT"]:
                    style = cast(_SUPPORTED_FORMATS, ext)
                else:
                    style = None
            async with aiofiles.open(file_path, encoding="utf-8") as f:
                content = await f.read()
            match style:
                case "JSON":
                    return json.loads(content)
                case "YAML":
                    return YAML().load(content)
                case "CSV":
                    return await csv_read(file_path)
                case "TXT":
                    return content
                case _:
                    logger.error(
                        f"不支持的文件格式: {style}:{file_path}",
                        "phi-plugin",
                    )
                    return content
        except Exception as e:
            logger.error(f"读取文件失败: {file_path}", "phi-plugin", e=e)
            return False

    @classmethod
    async def SetFile(
        cls,
        file_path: str | Path,
        data: Any,
        style: _SUPPORTED_FORMATS | None = None,
    ) -> bool:
        """
        储存文件

        :param file_path: 完整路径，含后缀
        :param data: 储存内容
        :param style: 强制设置文件格式
        :return bool:  储存成功返回 True，失败返回 False
        """
        try:
            dir_path = Path(file_path).parent
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
            if not style:
                ext = Path(file_path).suffix[1:].upper()
                if ext in ["JSON", "YAML", "CSV", "TXT"]:
                    style = cast(_SUPPORTED_FORMATS, ext)
                else:
                    style = None
            match style:
                case "JSON":
                    data = json.dumps(data)
                case "YAML":
                    data = YAML().dump(data)
                case "CSV":
                    await csv_write(file_path, data)
                    return True
                case "TXT":
                    data = data
                case _:
                    logger.error(
                        f"不支持的文件格式: {style}:{file_path}",
                        "phi-plugin",
                    )
                    return False
            async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
                await f.write(str(data))
            return True
        except Exception as e:
            logger.error(f"写入文件失败: {file_path}", "phi-plugin", e=e)
            return False

    @classmethod
    async def DelFile(cls, path: str | Path) -> bool:
        try:
            if not Path(path).exists():
                return False
            Path(path).unlink()
            return True
        except Exception as e:
            logger.error(f"删除失败: {path}", "phi-plugin", e=e)
            return False

    @classmethod
    async def DelDir(cls, dir_path: str | Path) -> bool:
        """
        删除文件夹

        :param string dir_path: 完整路径
        :return bool:  删除成功返回 True，失败返回 False
        """
        try:
            if not Path(dir_path).exists():
                return False
            for file in Path(dir_path).glob("*"):
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    await cls.DelDir(file)
            Path(dir_path).rmdir()
            return True
        except Exception as e:
            logger.error(f"删除失败: {dir_path}", "phi-plugin", e=e)
            return False

    @classmethod
    async def rmEmptyDir(cls, dir_path: str | Path) -> bool:
        """
        删除空文件夹

        :param string dir_path: 完整路径
        :return bool:  删除成功返回 True，失败返回 False
        """
        try:
            if not Path(dir_path).exists():
                return False
            if not Path(dir_path).is_dir():
                return False
            for file in Path(dir_path).glob("*"):
                if file.is_file():
                    return False
                elif file.is_dir():
                    if not await cls.rmEmptyDir(file):
                        return False
            Path(dir_path).rmdir()
            return True
        except Exception as e:
            logger.error(
                f"删除失败: {dir_path}",
                "phi-plugin",
                e=e,
            )
            return False

    @classmethod
    async def movJsonFile(cls, _path: str | Path) -> None:
        """
        将本地 JSON 用户数据迁移到数据库，并整理结构

        :param _path: 待迁移的数据目录
        """
        root_path = Path(_path)
        if not root_path.exists():
            return

        # 读取 user_token.json
        user_token_path = root_path / "user_token.json"
        user_token = await readFile.FileReader(user_token_path) or {}

        # 获取所有用户 json 文件
        files = [
            f
            for f in root_path.iterdir()
            if f.is_file() and f.name.endswith(".json") and f.name != "user_token.json"
        ]
        tot = len(files)
        already = 0

        logger.info(f"共发现 {tot} 个用户文件", "[phi-plugin][数据整合，请勿中断进程]")

        for file in files:
            user_id = file.stem  # 去掉 .json 后缀
            try:
                json_data = await readFile.FileReader(file)
                if not json_data:
                    continue

                session = json_data.get("session")
                if not session:
                    continue

                # 更新映射关系
                user_token[user_id] = session

                # 存储 save.json 到新路径
                save_path = Path(savePath) / session / "save.json"
                await readFile.SetFile(save_path, json_data)

                # 存储 history.json（来自 pluginDataPath）
                plugin_data_path = Path(pluginDataPath) / f"{user_id}_.json"
                if plugin_data_path.exists():
                    json_ = await readFile.FileReader(plugin_data_path)
                    if json_:
                        tem_file = {
                            "data": json_.get("data"),
                            "rks": json_.get("rks"),
                            "scoreHistory": json_.get("scoreHistory"),
                            "CLGMOD": json_.get("CLGMOD"),
                            "version": json_.get("version"),
                        }
                        history_path = Path(savePath) / session / "history.json"
                        await readFile.SetFile(history_path, tem_file)

                # 删除原文件
                await readFile.DelFile(file)

                already += 1
            except Exception as e:
                logger.error(f"数据迁移失败 | 用户: {user_id}", e=e)

        # 等待所有文件处理完成
        while already < tot:
            logger.info(f"{already}/{tot}", "[phi-plugin][数据整合，请勿中断进程]")
            await asyncio.sleep(1)

        logger.info(f"{already}/{tot}", "[phi-plugin][数据整合完成]")

        # 写回 user_token.json
        await readFile.SetFile("user_token.json", user_token)

        # 存储到数据库
        already = 0
        tot = len(user_token)
        for user_id, session_token in user_token.items():
            logger.info(f"{already}/{tot}", "[phi-plugin][数据转移，请勿中断进程]")
            await getSave.add_user_token(user_id, session_token)

            try:
                save = await getSave.getSave(user_id)
                if not save:
                    continue

                rks = save.getRks()
                if rks is None or rks == float("nan"):
                    logger.warning(
                        f"奇怪的rks: {save.saveInfo['summary']['rankingScore']}",
                        "[phi-plugin][数据转移，请勿中断进程]",
                    )
                    continue

                await getRksRank.addUserRks(session_token, rks)
            except Exception as err:
                logger.error(
                    "数据转移失败: 跳过该用户 {user_id} {session_token}",
                    "phi-plugin",
                    e=err,
                )
            already += 1

        logger.info(f"{already}/{tot}", "[phi-plugin][数据转移完成]")

        # 删除旧的 user_token.json
        await readFile.DelFile(Path(dataPath) / "user_token.json")
