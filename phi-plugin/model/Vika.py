import contextlib
import re
from typing import Any

from ..config import VikaToken
from ..vika import Vika as __Vika

cfg = {
    "viewId": "viwpdf3HFtnvG",
    "sort": [{"field": "fldWVwne5p9xg", "order": "desc"}],
    "requestTimeout": 10000,
}


class _Vika:
    def __init__(self, token: str):
        try:
            self.vika = __Vika(token=token, field_key="id")
            self.PhigrosDan = self.vika.datasheet("dstkfifML5zGiURp6h")
        except Exception:
            self.PhigrosDan = None

    async def GetUserDanBySstk(self, session_token: str):
        """通过 sessionToken 获取用户的民间段位数据"""
        response = None
        if self.PhigrosDan:
            with contextlib.suppress(Exception):
                response = await self.PhigrosDan.records.query(  # type: ignore
                    {**cfg, "filterByFormula": f"{{fldB7Wx6wHX57}} = '{session_token}'"}
                )
            if getattr(response, "success", None):
                return make_response(response)
        return None

    async def GetUserDanById(self, object_id: str):
        """通过 ObjectId 获取用户的民间段位数据"""
        response = None
        if self.PhigrosDan:
            with contextlib.suppress(Exception):
                response = await self.PhigrosDan.records.query(  # type: ignore
                    {**cfg, "filterByFormula": f"{{fld9mDj3ktKD7}} = '{object_id}'"}
                )
            if getattr(response, "success", None):
                return make_response(response)
        return None

    async def GetUserDanByName(self, nickname: str):
        """通过 nickname 获取用户的民间段位数据"""
        response = None
        if self.PhigrosDan:
            with contextlib.suppress(Exception):
                response = await self.PhigrosDan.records.query(  # type: ignore
                    {**cfg, "filterByFormula": f"{{fldzkniADAUck}} = '{nickname}'"}
                )
            if getattr(response, "success", None):
                return make_response(response)
        return None


def make_response(response) -> list[dict[str, Any]] | None:
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


Vika = _Vika(VikaToken)
