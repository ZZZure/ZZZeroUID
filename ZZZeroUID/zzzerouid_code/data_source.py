import json
from re import sub, compile, findall
from time import time
from typing import Literal
from datetime import datetime, timezone, timedelta

from httpx import AsyncClient

TZ = timezone(timedelta(hours=8))


async def get_data(type: Literal["activity", "index", "code"], data: dict = {}) -> dict:
    """米哈游接口请求"""

    url = {
        "activity": "https://bbs-api.miyoushe.com/apihub/api/home/new?gids=8&parts=1%2C3%2C4&device=OnePlus%20IN2025&cpu=placeholder&version=3",
        "index": "https://api-takumi.mihoyo.com/event/miyolive/index",
        "code": "https://api-takumi-static.mihoyo.com/event/miyolive/refreshCode",
    }
    async with AsyncClient() as client:
        try:
            if type == "index":
                res = await client.get(url[type], headers={"x-rpc-act_id": data.get("actId", "")})
            elif type == "code":
                res = await client.get(
                    url[type],
                    params={
                        "version": data.get("version", ""),
                        "time": f"{int(time())}",
                    },
                    headers={"x-rpc-act_id": data.get("actId", "")},
                )
            else:
                res = await client.get(url[type])
            return res.json()
        except Exception as e:
            return {"error": f"[{e.__class__.__name__}] {type} 接口请求错误"}


async def get_act_id() -> str:
    """获取 ``act_id``"""

    ret = await get_data("activity")
    if "error" in ret or ret["retcode"] != 0:
        return ""

    navigator = ret["data"]["navigator"]
    if not isinstance(navigator, list):
        return ""

    for nav in navigator:
        if not isinstance(nav, dict):
            continue
        name = nav["name"] if "name" in nav else ""
        app_path = nav["app_path"] if "app_path" in nav else ""
        if not isinstance(name, str) or not isinstance(app_path, str):
            continue
        # 入口名已从「前瞻直播」收成「x.x前瞻」
        if "前瞻" not in name and "event/live" not in app_path:
            continue
        matched = findall(r"act_id=([^&]+)", app_path)
        if matched:
            return matched[0]

    return ""


async def get_live_data(act_id: str) -> dict:
    """获取直播数据，尤其是 ``code_ver``"""

    ret = await get_data("index", {"actId": act_id})
    if ret.get("error") or ret.get("retcode") != 0:
        return {"error": ret.get("error") or "前瞻直播数据异常"}

    live_raw = ret["data"]["live"]
    live_temp = json.loads(ret["data"]["template"])
    live_data = {
        "code_ver": live_raw["code_ver"],
        "title": live_raw["title"].replace("特别直播", ""),
        "header": live_temp["kvDesktop"],
        "room": live_temp["liveConfig"][0]["desktop"],
    }
    if live_raw["is_end"]:
        live_data["review"] = live_temp["reviewUrl"]["args"]["post_id"]
    else:
        now = datetime.fromtimestamp(time(), TZ)
        start = datetime.strptime(live_raw["start"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
        if now < start:
            live_data["start"] = live_raw["start"]

    return live_data


async def get_code(version: str, act_id: str) -> dict[str, str] | list[dict[str, str]]:
    """获取兑换码"""

    ret = await get_data("code", {"version": version, "actId": act_id})
    if "error" in ret or ret["retcode"] != 0:
        err = ret["error"] if "error" in ret else "兑换码数据异常"
        return {"error": err if isinstance(err, str) and err else "兑换码数据异常"}
    code_list = ret["data"]["code_list"]
    if not isinstance(code_list, list):
        return {"error": "兑换码数据异常"}

    remove_tag = compile("<.*?>")
    code_data: list[dict[str, str]] = []
    for code_info in code_list:
        if not isinstance(code_info, dict):
            continue
        title = code_info["title"] if "title" in code_info else ""
        code = code_info["code"] if "code" in code_info else ""
        if not isinstance(title, str) or not isinstance(code, str) or not code:
            continue
        plain = sub(remove_tag, "", sub("</p>", "\n", title))
        items = "\n".join(line.strip() for line in plain.splitlines() if line.strip())
        code_data.append({"items": items, "code": code})
    return code_data


async def get_code_msg() -> str:
    """生成最新前瞻直播兑换码消息"""

    act_id = await get_act_id()
    if not act_id:
        return "暂无前瞻直播资讯！"

    live_data = await get_live_data(act_id)
    if "error" in live_data:
        err = live_data["error"]
        return err if isinstance(err, str) else "前瞻直播数据异常"

    code_ver = live_data["code_ver"]
    if not isinstance(code_ver, str):
        return "前瞻直播数据异常"
    code_data = await get_code(code_ver, act_id)
    if isinstance(code_data, dict):
        return code_data["error"]
    if not code_data:
        return "获取兑换码失败！"

    title = live_data["title"]
    lines: list[str] = [title] if isinstance(title, str) else []
    for code in code_data:
        lines.append(f"兑换码：{code['code']}")
        reward = code["items"].replace("\n", "、")
        if reward:
            lines.append(f"奖励：{reward}")
    return "\n".join(lines)
