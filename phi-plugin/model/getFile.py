# import asyncio
import csv
from io import StringIO
from pathlib import Path
from typing import Any, Literal, cast

import aiofiles
from ruamel.yaml import YAML
import ujson as json

from zhenxun.services.log import logger

SUPPORTED_FORMATS = Literal["JSON", "YAML", "CSV", "TXT"]


async def csv_write(file_path: str | Path, data: list[dict[str, Any]]):
    """
    data: list[dict]
    ```
    [
        {
            "id": "1",
            "name": "a",
            "age": "99"
        },
        {
            "id": "2",
            "name": "b",
            "age": "114"
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


class FileManager:
    @classmethod
    async def ReadFile(
        cls,
        file_path: str | Path,
        style: SUPPORTED_FORMATS | None = None,
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
                    style = cast(SUPPORTED_FORMATS, ext)
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
        style: SUPPORTED_FORMATS | None = None,
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
                    style = cast(SUPPORTED_FORMATS, ext)
                else:
                    style = None
            match style:
                case "JSON":
                    data = json.dumps(data, default=str, ensure_ascii=False)
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
