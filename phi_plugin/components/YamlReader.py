from typing import Any
from ..model.getFile import readFile


class YamlReader:

    def __init__(self, yamlPath):
        """
        :param yamlPath: yaml文件绝对路径
        """
        self.yamlPath = yamlPath

    async def initYaml(self):
        """
        初始化yaml文件
        """
        try:
            self.document: dict = await readFile.FileReader(self.yamlPath, "TAML") # type: ignore
        except Exception as e:
            raise e

    def has(self, keyPath) -> bool:
        """
        检查集合是否包含key的值

        :param keyPath: key路径
        :return: bool
        """
        return keyPath in self.document

    def get(self, keyPath) -> Any:
        """
        返回key的值

        :param keyPath: key路径
        """
        return self.document.get(keyPath)

    async def set(self, keyPath, value) -> None:
        """
        修改某个key的值

        :param keyPath: key路径
        :param value: key的值
        """
        self.document[keyPath] = value
        await self.save()

    async def delete(self, keyPath):
        """
        删除某个key

        :param keyPath: key路径
        """
        self.document.pop(keyPath)
        await self.save()

    async def addIn(self, keyPath, value):
        """
        在key中添加数据

        :param keyPath: key路径
        :param value: key的值
        """
        await self.set(keyPath, self.get(keyPath) + [value])

    async def save(self):
        """
        保存当前文档内容到 YAML 文件
        """
        await readFile.SetFile(self.yamlPath, self.document, "YAML")
