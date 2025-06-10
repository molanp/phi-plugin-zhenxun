import re

from zhenxun.services.log import logger

from ..config import PluginConfig
from ..vika import Vika

cfg = {
    "viewId": "viwpdf3HFtnvG",
    "sort": [{"field": "fldWVwne5p9xg", "order": "desc"}],
    "requestTimeout": 10000,
}


class _VikaData:
    def __init__(self, token: str):
        self.vika = Vika(token=token, field_key="id")
        self.PhigrosDan = self.vika.datasheet("dstkfifML5zGiURp6h")

    async def GetUserDanBySstk(self, session_token: str) -> list[dict] | None:
        """通过 sessionToken 获取用户的民间段位数据"""
        try:
            response = await self.PhigrosDan.records.query(  # type: ignore
                {**cfg, "filterByFormula": f"{{fldB7Wx6wHX57}} = '{session_token}'"}
            )
            if response.success:
                return make_response(response)
        except Exception as e:
            logger.error(f"Error in GetUserDanBySstk: {e!s}")
        return None

    async def GetUserDanById(self, object_id: str) -> list[dict] | None:
        """通过 ObjectId 获取用户的民间段位数据"""
        try:
            response = await self.PhigrosDan.records.query(  # type: ignore
                {**cfg, "filterByFormula": f"{{fld9mDj3ktKD7}} = '{object_id}'"}
            )
            if response.success:
                return make_response(response)
        except Exception as e:
            logger.error(f"Error in GetUserDanById: {e!s}")
        return None

    async def GetUserDanByName(self, nickname: str) -> list[dict] | None:
        """通过 nickname 获取用户的民间段位数据"""
        try:
            response = await self.PhigrosDan.records.query( # type: ignore
                {**cfg, "filterByFormula": f"{{fldzkniADAUck}} = '{nickname}'"}
            )
            if response.success:
                return make_response(response)
        except Exception as e:
            logger.error(f"Error in GetUserDanByName: {e!s}")
        return None


def make_response(response) -> list[dict] | None:
    records = getattr(response.data, "records", [])
    if not records:
        return None
    result = []
    for record in records:
        fields = record.fields
        dan = fields.get("fldWVwne5p9xg", "")
        match = re.search(r"\d+", dan)
        dan_num = int(match.group()) if match else 0
        score = (
            fields.get("fldTszelbRQIu", "").split("\n")
            if fields.get("fldTszelbRQIu")
            else None
        )
        img_url = fields.get("fldqbC6IK8m3o", [{}])[0].get("url")
        staffer = fields.get("fldoKAoJoBSJO", {}).get("name")

        result.append(
            {
                "sessionToken": fields.get("fldB7Wx6wHX57"),
                # "ObjectId": fields.get("fld9mDj3ktKD7"),
                "nickname": fields.get("fldzkniADAUck"),
                "Dan": dan,
                "dan_num": dan_num,
                "EX": fields.get("fldbILNU5o7Nl", "") == "是",
                "img": img_url,
                "score": score,
                "staffer": staffer,
            }
        )
    return sorted(result, key=lambda x: -x["dan_num"]) if result else None


VikaData = _VikaData(PluginConfig.get("VikaToken"))
