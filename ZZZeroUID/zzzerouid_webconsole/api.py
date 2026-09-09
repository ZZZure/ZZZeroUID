"""ZZZeroUID 控制台 API：``/api/zzzerouid/...``，需 WebConsole 登录。"""

from __future__ import annotations

import re

from fastapi import Query
from fastapi.responses import Response, FileResponse, JSONResponse

from gsuid_core.models import Event
from gsuid_core.utils.path_safety import PathEscapeError, safe_join, is_safe_filename
from gsuid_core.webconsole.plugin_page import (
    ApiOk,
    ApiFail,
    PluginAPI,
    api_ok,
    api_fail,
)

from .data import (
    is_zzz_uid,
    load_gacha,
    delete_gacha,
    list_characters,
    delete_character,
    summarize_players,
    load_character_raw,
)
from ..utils.name_convert import char_id_to_char_name
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH, SQUARE_AVATAR
from ..zzzerouid_gachalog.draw_gachalogs import draw_card
from ..zzzerouid_char_detail.draw_new_char_detail_card import draw_char_detail_img

api = PluginAPI()
_CHAR_ID_RE = re.compile(r"^\d{4,8}$")


def _web_event() -> Event:
    return Event(
        bot_id="webconsole",
        bot_self_id="webconsole",
        user_type="direct",
        user_id="0",
        sender={"nickname": "绳匠"},
    )


def _bad_uid() -> JSONResponse:
    return JSONResponse(api_fail("invalid uid"), status_code=400)


@api.get("/players")
async def list_players() -> ApiOk:
    return api_ok(summarize_players(PLAYER_PATH))


@api.get("/players/{uid}/gacha")
async def get_gacha(
    uid: str,
    pool: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
) -> ApiOk | ApiFail:
    if not is_zzz_uid(uid):
        return api_fail("invalid uid")
    data = load_gacha(PLAYER_PATH, uid, pool, limit)
    if data is None:
        return api_fail("gacha log not found")
    return api_ok(data)


@api.get("/players/{uid}/gacha/preview")
async def preview_gacha(uid: str) -> Response:
    if not is_zzz_uid(uid):
        return _bad_uid()
    result = await draw_card(uid, _web_event())
    if isinstance(result, str):
        return JSONResponse(api_fail(result), status_code=400)
    return Response(content=result, media_type="image/png")


@api.get("/players/{uid}/characters")
async def get_characters(uid: str) -> ApiOk | ApiFail:
    if not is_zzz_uid(uid):
        return api_fail("invalid uid")
    return api_ok(list_characters(PLAYER_PATH, uid))


@api.get("/players/{uid}/characters/{char_id}")
async def get_character(uid: str, char_id: str) -> ApiOk | ApiFail:
    if not is_zzz_uid(uid) or not _CHAR_ID_RE.match(char_id):
        return api_fail("invalid id")
    data = load_character_raw(PLAYER_PATH, uid, char_id)
    if data is None:
        return api_fail("character not found")
    row = None
    for item in list_characters(PLAYER_PATH, uid):
        if item["id"] == char_id:
            row = item
            break
    return api_ok({"summary": row, "raw": data})


@api.get("/players/{uid}/characters/{char_id}/preview")
async def preview_character(uid: str, char_id: str) -> Response:
    if not is_zzz_uid(uid) or not _CHAR_ID_RE.match(char_id):
        return _bad_uid()
    name = char_id_to_char_name(char_id)
    if not name:
        return JSONResponse(api_fail("unknown character"), status_code=400)
    result = await draw_char_detail_img(uid, _web_event(), name)
    if isinstance(result, str):
        return JSONResponse(api_fail(result), status_code=400)
    return Response(content=result, media_type="image/png")


@api.delete("/players/{uid}/gacha")
async def remove_gacha(uid: str) -> ApiOk | ApiFail:
    if not is_zzz_uid(uid):
        return api_fail("invalid uid")
    if not delete_gacha(PLAYER_PATH, uid):
        return api_fail("gacha log not found")
    return api_ok({"uid": uid}, msg="deleted")


@api.delete("/players/{uid}/characters/{char_id}")
async def remove_character(uid: str, char_id: str) -> ApiOk | ApiFail:
    if not is_zzz_uid(uid) or not _CHAR_ID_RE.match(char_id):
        return api_fail("invalid id")
    if not delete_character(PLAYER_PATH, uid, char_id):
        return api_fail("character not found")
    return api_ok({"uid": uid, "char_id": char_id}, msg="deleted")


@api.get("/assets/avatar/{char_id}")
async def character_avatar(char_id: str) -> Response:
    if not _CHAR_ID_RE.match(char_id) or not is_safe_filename(char_id):
        return _bad_uid()
    name = f"role_square_avatar_{char_id}.png"
    try:
        path = safe_join(SQUARE_AVATAR, name)
    except PathEscapeError:
        return JSONResponse(api_fail("not found"), status_code=404)
    if not path.is_file():
        return JSONResponse(api_fail("not found"), status_code=404)
    return FileResponse(path=str(path), media_type="image/png")
