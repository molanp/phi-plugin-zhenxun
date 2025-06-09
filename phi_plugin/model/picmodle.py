from nonebot import require
from nonebot_plugin_alconna import Image

from ..config import PATH


class picmodle:
    @classmethod
    async def alias(cls, info):
        """曲目图鉴"""
        return await cls.common(
            "atlas",
            {
                **info,
                "length": info.get("length").replace(":", "'") + "''"
                if info.length
                else "-",
            },
        )

    @classmethod
    async def b19(cls, data):
        """b19"""
        return await cls.common("b19", data)

    @classmethod
    async def arcgros_b19(cls, data):
        """arcgros b19"""
        return await cls.common("arcgrosB19", data)

    @classmethod
    async def update(cls, data):
        """更新"""
        return await cls.common("update", data)

    @classmethod
    async def tasks(cls, data):
        """任务"""
        return await cls.common("tasks", data)

    @classmethod
    async def user_info(cls, info: dict, picversion: int):
        """
        个人信息

        :param dict info: 用户信息
        :param {1|2} picversion: 版本
        """
        if picversion == 1 or picversion != 2:
            return await cls.render(
                "userinfo/userinfo",
                {**info},
            )
        else:
            return await cls.render(
                "userinfo/userinfo-old",
                {**info},
            )

    @classmethod
    async def lvsco(cls, data: dict):
        """lvsco"""
        return await cls.common("lvsco", data)

    @classmethod
    async def list(cls, data: dict):
        """列表"""
        return await cls.common("list", data)

    @classmethod
    async def score(cls, data: dict, picversion: int):
        """
        单曲成绩

        :param dict data: 单曲数据
        :param 1|2 picversion: 版本
        """
        if picversion == 1:
            return await cls.render("score/score", {**data})
        else:
            return await cls.render("score/scoreOld", {**data})

    @classmethod
    async def ill(cls, data: dict):
        """曲绘"""
        return await cls.common("ill", data)

    @classmethod
    async def guess(cls, data: dict):
        """猜歌"""
        return await cls.common("guess", data)

    @classmethod
    async def rand(cls, data: dict):
        """随机"""
        return await cls.common("rand", data)

    @classmethod
    async def help(cls, data: dict):
        """帮助"""
        return await cls.common("help", data)

    @classmethod
    async def chap(cls, data: dict):
        """章节"""
        return await cls.common("chap", data)

    @classmethod
    async def common(cls, kind: str, data: dict):
        """
        :param {'alias'|'task'|'b19'|'arcgrosB19'|'update'|'tasks'|'lvsco'|'list'|'ill'|'chartInfo'|'guess'|'rand'|'help'|'chap'|'rankingList'|'clg'} kind: 类型
        :param dict data: 数据
        """  # noqa: E501
        return await cls.render(
            f"{kind}/{kind}",
            {
                **data,
                "_res_path": PATH / "resources",
            },
        )

    @classmethod
    async def render(cls, path: str, params: dict) -> Image:
        """
        渲染函数

        :param str path: 模板路径
        :param dict params: 渲染参数
        """
        require("nonebot_plugin_htmlrender")
        from nonebot_plugin_htmlrender import template_to_pic

        template_dir = PATH / "resources" / "html" / path
        pic = await template_to_pic(
            template_path=str(template_dir),
            template_name=f"{path}.html",
            templates=params,
        )
        return Image(raw=pic)
