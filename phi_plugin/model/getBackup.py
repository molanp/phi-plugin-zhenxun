import asyncio
from datetime import datetime
from pathlib import Path
import shutil
import zipfile

import aiofiles
from nonebot.adapters import Event
from nonebot.utils import run_sync
import ujson as json

from zhenxun.services.log import logger

from ..models import SstkData
from ..utils import to_dict
from .cls.saveHistory import saveHistory
from .fCompute import fCompute
from .path import backupPath, pluginDataPath, savePath
from .progress_bar import ProgressBar
from .send import send

MaxNum = 1e4


@run_sync
def zip(zip_path: Path, files_path: Path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root in files_path.rglob("*"):
            if root.is_file():
                arcname = root.relative_to(files_path)
                zipf.write(root, arcname)


class getBackup:
    @staticmethod
    async def backup(e: Event, send: "send") -> bool:
        """备份"""
        zip_name = (
            f"{datetime.now().isoformat().replace(':', '-').replace('.', '-')}.zip"
        )
        zip_path = backupPath / zip_name
        temp_dir = backupPath / "temp_backup"

        try:
            # 创建临时目录结构
            save_data_temp = temp_dir / "saveData"
            plugin_data_temp = temp_dir / "pluginData"
            save_data_temp.mkdir(parents=True, exist_ok=True)
            plugin_data_temp.mkdir(exist_ok=True)

            # 1. 备份 savePath 下的存档
            if not savePath.exists():
                await send.send_with_At(e, "存档目录不存在，请检查路径！")
                logger.warning("存档目录不存在，请检查路径！", "phi-plugin")
                return False

            list_dirs = [d for d in savePath.iterdir() if d.is_dir()]
            if len(list_dirs) >= MaxNum:
                await send.send_with_At(
                    e, "存档数量过多，请手动备份 /data/saveData/ 目录！"
                )
                logger.warning(
                    "存档数量过多，请手动备份 /data/saveData/ 目录！", "phi-plugin"
                )
            else:
                await send.send_with_At(e, "开始备份存档，请稍等...")
                logger.info("开始备份存档...", "phi-plugin")
                bar = ProgressBar("存档备份中", len(list_dirs))
                for idx, folder in enumerate(list_dirs):
                    target_folder = save_data_temp / folder.name
                    target_folder.mkdir(exist_ok=True)
                    for file in folder.iterdir():
                        if file.is_dir():
                            logger.warning(
                                f"备份错误：意料之外的文件夹 {file}",
                                "phi-plugin",
                            )
                        else:
                            shutil.copy(file, target_folder / file.name)
                    bar.render(completed=idx + 1)

            # 2. 备份 pluginDataPath 下的插件数据
            if not pluginDataPath.exists():
                await send.send_with_At(e, "插件数据目录不存在，请检查路径！")
                logger.warning("插件数据目录不存在，请检查路径！", "phi-plugin")
                return False

            list_files = [f for f in pluginDataPath.iterdir() if f.is_file()]
            if len(list_files) >= MaxNum:
                await send.send_with_At(
                    e, "插件数据数量过多，请手动备份 /data/pluginData/ 目录！"
                )
                logger.warning(
                    "插件数据数量过多，请手动备份 /data/pluginData/ 目录！",
                    "phi-plugin",
                )
            else:
                await send.send_with_At(e, "开始备份插件数据，请稍等...")
                logger.info("开始备份插件数据...", "phi-plugin")
                bar = ProgressBar("[phi-plugin] 插件数据备份中", len(list_files))
                for idx, file in enumerate(list_files):
                    shutil.copy(file, plugin_data_temp / file.name)
                    bar.render(completed=idx + 1)

            # 3. 提取 Redis 中 user_token 数据
            await send.send_with_At(e, "开始备份user_token，请稍等...")
            logger.info("开始备份user_token数据...", "phi-plugin")

            # 从数据库中获取所有未封禁用户的 uid -> sessionToken 映射
            users = await SstkData.filter(is_banned=False).values("uid", "sessionToken")
            user_token = {user["uid"]: user["sessionToken"] for user in users}

            # 异步写入 JSON 文件
            token_file = temp_dir / "user_token.json"
            async with aiofiles.open(token_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(user_token, ensure_ascii=False))

            # 4. 打包压缩
            zip_path.parent.mkdir(parents=True, exist_ok=True)
            await send.send_with_At(e, "开始压缩备份数据，请稍等...")
            logger.info("开始压缩备份数据...", "phi-plugin")

            await zip(zip_path, temp_dir)

            logger.success(f"备份完成 {zip_path}", "phi-plugin")
            await send.send_with_At(
                e, f"{zip_name.replace('.zip', '')} 成功备份到 {backupPath} 目录下"
            )

            # 如果命令包含 'back' 则直接发送压缩包
            if "back" in e.get_plaintext():
                async with aiofiles.open(zip_path, "rb") as f:
                    data = await f.read()
                await fCompute.sendFile(e, data, zip_name)

            return True

        except Exception as ex:
            logger.error("备份出错", "phi-plugin", e=ex)
            return False
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    @staticmethod
    async def restore(zip_path: Path) -> bool:
        """
        从 zip 文件中恢复数据：
            - saveData/ 下的 history.json 和 save.json
            - pluginData/ 下的 JSON 文件
            - user_token.json 中的用户 sessionToken

        :param zip_path: zip 文件路径
        :return: 是否成功
        """
        if not zip_path.exists():
            raise FileNotFoundError(f"备份文件 {zip_path} 不存在")

        try:
            await getBackup._do_restore(zip_path)

            return True

        except Exception as err:
            logger.error("恢复备份失败", "phi-plugin", e=err)
            return False

    @staticmethod
    @run_sync
    def _do_restore(zip_path: Path):
        with zipfile.ZipFile(zip_path, "r") as zipf:
            # 1. 恢复存档数据
            getBackup._restore_save_data(zipf)

            # 2. 恢复插件数据
            getBackup._restore_plugin_data(zipf)

            #  3. 恢复用户数据
            asyncio.run(getBackup._restore_user_tokens(zipf))

    @staticmethod
    def _restore_save_data(zipf: zipfile.ZipFile):
        """恢复 saveData 下的历史和存档数据"""
        name_list = zipf.namelist()
        save_data_prefix = "saveData/"

        sessions = {
            name.split("/")[1]
            for name in name_list
            if name.startswith(save_data_prefix)
            and "/" in name[len(save_data_prefix) :]
        }

        for session in sessions:
            session_folder = savePath / session
            session_folder.mkdir(parents=True, exist_ok=True)

            # 恢复 history.json
            history_name = f"{save_data_prefix}{session}/history.json"
            if history_name in name_list:
                history_content = zipf.read(history_name).decode("utf-8")
                history_dict = json.loads(history_content)
                old_path = savePath / session / "history.json"

                if old_path.exists():
                    old_content = json.loads(old_path.read_text(encoding="utf-8"))
                    merged = saveHistory(old_content)
                    merged.add(saveHistory(history_dict))
                    (session_folder / "history.json").write_text(
                        json.dumps(to_dict(merged), ensure_ascii=False),
                        encoding="utf-8",
                    )
                else:
                    (session_folder / "history.json").write_text(
                        json.dumps(history_dict, ensure_ascii=False),
                        encoding="utf-8",
                    )

            # 恢复 save.json
            save_name = f"{save_data_prefix}{session}/save.json"
            if save_name in name_list:
                save_content = zipf.read(save_name).decode("utf-8")
                now = json.loads(save_content)
                old_path = savePath / session / "save.json"

                if old_path.exists():
                    old = json.loads(old_path.read_text(encoding="utf-8"))
                    # 取更新时间较新的版本
                    if old.get("saveInfo", {}).get("modifiedAt", {}).get(
                        "iso", ""
                    ) > now.get("saveInfo", {}).get("modifiedAt", {}).get("iso", ""):
                        now = old
                (session_folder / "save.json").write_text(
                    json.dumps(now, ensure_ascii=False), encoding="utf-8"
                )

    @staticmethod
    def _restore_plugin_data(zipf: zipfile.ZipFile):
        """恢复 pluginData 下的插件配置文件"""
        name_list = zipf.namelist()
        plugin_data_files = [
            name
            for name in name_list
            if name.startswith("pluginData/")
            and "/" not in name[len("pluginData/") :].strip("/")
        ]

        for file_name in plugin_data_files:
            base_name = file_name[len("pluginData/") :]
            target_file = pluginDataPath / base_name
            target_file.parent.mkdir(parents=True, exist_ok=True)
            content = zipf.read(file_name)
            target_file.write_bytes(content)

    @staticmethod
    async def _restore_user_tokens(zipf: zipfile.ZipFile):
        """恢复 user_token.json 到数据库"""
        if "user_token.json" not in zipf.namelist():
            logger.warning("备份中未找到 user_token.json", "phi-plugin")
            return

        token_data = zipf.read("user_token.json").decode("utf-8")
        user_tokens: dict[str, str] = json.loads(token_data)

        for uid, token in user_tokens.items():
            await SstkData.add_sstk(uid, token)
