# -*- coding: utf-8 -*-
"""官方驱动盘评分规则缓存与本地回算。

米游社 avatar/info 会返回 equip_plan_info（含角色有效副属性方案）。
Enka / MiniGG 路径通常没有该字段；旧本地 JSON 也可能缺 valid / plan。

策略：
1. 任意用户经 MYS 刷新时，把「角色维度」的评分规则写入全局缓存。
2. Enka 刷新、旧缓存、查询绘图时：用缓存规则或已有 valid 回算。
"""

from __future__ import annotations

import json
import threading
from copy import deepcopy
from typing import Any, Set, Dict, List, Optional, cast
from datetime import datetime

from gsuid_core.logger import logger

from ..utils.resource.RESOURCE_PATH import MAIN_PATH

OFFICIAL_PLAN_CACHE_PATH = MAIN_PATH / "official_equip_plan.json"

_lock = threading.Lock()
_cache_mem: Optional[Dict[str, Any]] = None


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load_cache() -> Dict[str, Any]:
    global _cache_mem
    if _cache_mem is not None:
        return _cache_mem
    with _lock:
        if _cache_mem is not None:
            return _cache_mem
        if OFFICIAL_PLAN_CACHE_PATH.exists():
            try:
                with open(OFFICIAL_PLAN_CACHE_PATH, "r", encoding="utf-8") as f:
                    _cache_mem = json.load(f)
            except Exception as e:
                logger.warning(f"[官方评分缓存] 读取失败: {e}")
                _cache_mem = {}
        else:
            _cache_mem = {}
        if not isinstance(_cache_mem, dict):
            _cache_mem = {}
        if "plans" not in _cache_mem:
            if _cache_mem and all(str(k).isdigit() for k in _cache_mem.keys() if not str(k).startswith("_")):
                _cache_mem = {"version": 1, "plans": _cache_mem}
            else:
                _cache_mem = {"version": 1, "plans": dict(_cache_mem.get("plans") or {})}
        return _cache_mem


def _save_cache(cache: Dict[str, Any]) -> None:
    global _cache_mem
    with _lock:
        OFFICIAL_PLAN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = OFFICIAL_PLAN_CACHE_PATH.with_suffix(".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        tmp.replace(OFFICIAL_PLAN_CACHE_PATH)
        _cache_mem = cache


def extract_plan_rule(plan: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": plan.get("type", 1),
        "game_default": deepcopy(plan.get("game_default") or {"property_list": []}),
        "custom_info": deepcopy(plan.get("custom_info") or {"property_list": []}),
        "plan_only_special_property": bool(plan.get("plan_only_special_property", False)),
        "plan_effective_property_list": deepcopy(plan.get("plan_effective_property_list") or []),
        "updated_at": _now(),
        "source": "mys",
    }


def update_official_plan_cache(char_id: Any, plan: Dict[str, Any]) -> None:
    if not plan or not plan.get("plan_effective_property_list"):
        return
    cid = str(char_id)
    cache = _load_cache()
    plans: Dict[str, Any] = cache.setdefault("plans", {})
    rule = extract_plan_rule(plan)
    old = plans.get(cid)
    if (
        not old
        or old.get("plan_effective_property_list") != rule["plan_effective_property_list"]
        or old.get("game_default") != rule["game_default"]
    ):
        plans[cid] = rule
        _save_cache(cache)
        logger.info(f"[官方评分缓存] 更新角色 {cid} 有效词条规则")
    else:
        plans[cid]["updated_at"] = _now()


def get_cached_plan_rule(char_id: Any) -> Optional[Dict[str, Any]]:
    cid = str(char_id)
    plans = _load_cache().get("plans") or {}
    rule = plans.get(cid)
    if not rule or not rule.get("plan_effective_property_list"):
        return None
    return rule


def get_effective_ids_from_rule(rule: Dict[str, Any]) -> Set[int]:
    ids: Set[int] = set()
    for item in rule.get("plan_effective_property_list") or []:
        if isinstance(item, dict) and "id" in item:
            ids.add(int(item["id"]))
    return ids


def normalize_equip_properties(data: Dict[str, Any]) -> bool:
    """兼容旧 JSON：补齐 level / add，返回是否有改动。"""
    changed = False
    for eq in data.get("equip") or []:
        if not isinstance(eq, dict):
            continue
        for prop in eq.get("properties") or []:
            if not isinstance(prop, dict):
                continue
            if prop.get("level") is None and prop.get("add") is not None:
                prop["level"] = 1 + int(prop.get("add") or 0)
                changed = True
            elif prop.get("add") is None and prop.get("level") is not None:
                prop["add"] = max(0, int(prop.get("level") or 1) - 1)
                changed = True
            elif prop.get("level") is None and prop.get("add") is None:
                # 极旧数据只有 base：按 1 档计
                prop["level"] = 1
                prop["add"] = 0
                changed = True
        for prop in eq.get("main_properties") or []:
            if not isinstance(prop, dict):
                continue
            if prop.get("level") is None:
                prop["level"] = 1
                changed = True
            if prop.get("add") is None:
                prop["add"] = 0
                changed = True
            if "valid" not in prop:
                prop["valid"] = False
                changed = True
    return changed


def calc_invalid_property_cnt(properties: List[Dict[str, Any]]) -> int:
    """无效副属性强化次数之和 sum(add)，与官方样本一致。"""
    total = 0
    for prop in properties:
        if prop.get("valid"):
            continue
        total += int(prop.get("add") or 0)
    return total


def calc_valid_hit_count(properties: List[Dict[str, Any]]) -> int:
    total = 0
    for prop in properties:
        if prop.get("valid"):
            total += int(prop.get("level") or 0)
    return total


def apply_valid_flags_to_equip(
    equip: Dict[str, Any],
    effective_ids: Set[int],
) -> None:
    props = equip.get("properties") or []
    for prop in props:
        pid = int(prop.get("property_id") or 0)
        prop["valid"] = pid in effective_ids
        if prop.get("level") is None:
            prop["level"] = 1 + int(prop.get("add") or 0)
        if prop.get("add") is None:
            prop["add"] = max(0, int(prop.get("level") or 1) - 1)

    invalid_cnt = calc_invalid_property_cnt(props)
    equip["invalid_property_cnt"] = invalid_cnt
    equip["all_hit"] = invalid_cnt == 0


def build_equip_plan_info_from_rule(
    rule: Dict[str, Any],
    valid_property_cnt: int,
) -> Dict[str, Any]:
    return {
        "type": rule.get("type", 1),
        "game_default": deepcopy(rule.get("game_default") or {"property_list": []}),
        "cultivate_info": {
            "name": "cache_computed",
            "plan_id": "0",
            "is_delete": False,
            "old_plan": False,
        },
        "custom_info": deepcopy(rule.get("custom_info") or {"property_list": []}),
        "valid_property_cnt": valid_property_cnt,
        "plan_only_special_property": bool(rule.get("plan_only_special_property", False)),
        "equip_rating": "",
        "plan_effective_property_list": deepcopy(rule.get("plan_effective_property_list") or []),
        "equip_rating_score": 0,
        "_score_source": "cache_computed",
    }


def has_official_mys_plan(data: Dict[str, Any]) -> bool:
    plan = data.get("equip_plan_info")
    if not isinstance(plan, dict) or not plan:
        return False
    if plan.get("_score_source") == "cache_computed":
        return False
    if (plan.get("cultivate_info") or {}).get("name") == "cache_computed":
        return False
    if plan.get("plan_effective_property_list"):
        return True
    # 旧缓存可能只有评级+命中，无 effective 列表
    if plan.get("equip_rating") and plan.get("valid_property_cnt") is not None:
        return True
    return False


def _equip_props_have_real_valid_mix(equips: List[Dict[str, Any]]) -> bool:
    """是否存在至少一条 valid=True（排除 Enka 全 False 的假 valid）。"""
    saw_true = False
    for eq in equips:
        for p in eq.get("properties") or []:
            if p.get("valid") is True:
                saw_true = True
                break
        if saw_true:
            break
    return saw_true


def _collect_effective_ids_from_valids(equips: List[Dict[str, Any]]) -> Set[int]:
    ids: Set[int] = set()
    for eq in equips:
        for p in eq.get("properties") or []:
            if p.get("valid") is True and p.get("property_id") is not None:
                ids.add(int(p["property_id"]))
    return ids


def _apply_rule_to_equips(
    equips: List[Dict[str, Any]],
    effective_ids: Set[int],
) -> int:
    total_hit = 0
    for eq in equips:
        if "id" not in eq:
            continue
        apply_valid_flags_to_equip(eq, effective_ids)
        total_hit += calc_valid_hit_count(eq.get("properties") or [])
    return total_hit


def _need_recompute_valids(equips: List[Dict[str, Any]]) -> bool:
    for eq in equips:
        props = eq.get("properties") or []
        if not props:
            continue
        if any("valid" not in p for p in props):
            return True
        if eq.get("invalid_property_cnt") is None or eq.get("all_hit") is None:
            return True
    return False


def ensure_official_score(data: Dict[str, Any], *, force_recompute: bool = False) -> Dict[str, Any]:
    """保证 data 具备可用的官方/回算评分字段。兼容旧本地 JSON。

    返回的 data 可能被原地修改；若写入了回算结果会设 `_official_score_applied=True`。
    """
    char_id = data.get("id")
    if char_id is None:
        return data

    changed = normalize_equip_properties(data)
    if changed:
        data["_official_score_applied"] = True

    plan = data.get("equip_plan_info")
    equips: List[Dict[str, Any]] = data.get("equip") or []

    # ---- 路径 A：本地已有 MYS 方案（含旧存档里完整 equip_plan_info）----
    if has_official_mys_plan(data) and isinstance(plan, dict):
        if plan.get("plan_effective_property_list"):
            update_official_plan_cache(char_id, plan)
            rule = extract_plan_rule(plan)
            effective_ids = get_effective_ids_from_rule(rule)
            if effective_ids and (force_recompute or _need_recompute_valids(equips)):
                total_hit = _apply_rule_to_equips(equips, effective_ids)
                # 旧数据 valid 缺失时，同步刷新命中总数
                if plan.get("valid_property_cnt") is None or force_recompute:
                    plan["valid_property_cnt"] = total_hit
                    data["_official_score_applied"] = True
                else:
                    data["_official_score_applied"] = True
        else:
            # 仅有 rating + cnt：若盘上已有 valid 分布，补 invalid/all_hit
            if force_recompute or _need_recompute_valids(equips):
                if _equip_props_have_real_valid_mix(equips):
                    for eq in equips:
                        if "id" not in eq:
                            continue
                        props = eq.get("properties") or []
                        for p in props:
                            if "valid" not in p:
                                p["valid"] = False
                        eq["invalid_property_cnt"] = calc_invalid_property_cnt(props)
                        eq["all_hit"] = eq["invalid_property_cnt"] == 0
                    data["_official_score_applied"] = True
        return data

    # ---- 路径 B：盘上已有真实 valid=True（旧 MYS 存了词条但丢了 plan）----
    if _equip_props_have_real_valid_mix(equips):
        effective_ids = _collect_effective_ids_from_valids(equips)
        total_hit = 0
        for eq in equips:
            if "id" not in eq:
                continue
            props = eq.get("properties") or []
            for p in props:
                if "valid" not in p:
                    p["valid"] = False
                if p.get("level") is None:
                    p["level"] = 1 + int(p.get("add") or 0)
                if p.get("add") is None:
                    p["add"] = max(0, int(p.get("level") or 1) - 1)
            eq["invalid_property_cnt"] = calc_invalid_property_cnt(props)
            eq["all_hit"] = eq["invalid_property_cnt"] == 0
            total_hit += calc_valid_hit_count(props)

        # 若全局缓存有该角色规则，优先用缓存规则覆盖 valid（更权威）
        rule = get_cached_plan_rule(char_id)
        if rule:
            effective_ids = get_effective_ids_from_rule(rule)
            total_hit = _apply_rule_to_equips(equips, effective_ids)
            data["equip_plan_info"] = build_equip_plan_info_from_rule(rule, total_hit)
        else:
            # 从 valid 反推简易 plan（无评级）
            prop_list = []
            for pid in sorted(effective_ids):
                # 找一个样本名
                name, full_name = str(pid), str(pid)
                for eq in equips:
                    for p in eq.get("properties") or []:
                        if int(p.get("property_id") or 0) == pid:
                            name = p.get("property_name") or name
                            full_name = name
                            break
                prop_list.append(
                    {
                        "id": pid,
                        "name": name,
                        "full_name": full_name,
                        "system_id": int(str(pid)[:3]) if len(str(pid)) >= 3 else pid,
                        "is_select": False,
                    }
                )
            data["equip_plan_info"] = {
                "type": 1,
                "game_default": {"property_list": []},
                "cultivate_info": {
                    "name": "legacy_valids",
                    "plan_id": "0",
                    "is_delete": False,
                    "old_plan": False,
                },
                "custom_info": {"property_list": []},
                "valid_property_cnt": total_hit,
                "plan_only_special_property": False,
                "equip_rating": "",
                "plan_effective_property_list": prop_list,
                "equip_rating_score": 0,
                "_score_source": "legacy_valids",
            }
        data["_official_score_applied"] = True
        return data

    # ---- 路径 C：全局规则缓存回算（Enka / 全 valid=false 旧数据）----
    rule = get_cached_plan_rule(char_id)
    if not rule:
        return data

    effective_ids = get_effective_ids_from_rule(rule)
    if not effective_ids:
        return data

    total_hit = _apply_rule_to_equips(equips, effective_ids)
    data["equip_plan_info"] = build_equip_plan_info_from_rule(rule, total_hit)
    data["_official_score_applied"] = True
    return data


def process_avatars_on_refresh(
    avatars: List[Dict[str, Any]],
    *,
    source: str,
) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for avatar in avatars:
        data = dict(avatar)
        if source == "MYS" and has_official_mys_plan(data):
            update_official_plan_cache(data.get("id"), data["equip_plan_info"])
        ensure_official_score(data, force_recompute=(source != "MYS"))
        result.append(data)
    return result


def merge_mys_avatar_score(
    local_avatar: Dict[str, Any],
    mys_avatar: Dict[str, Any],
) -> Dict[str, Any]:
    """把 MYS 的官方评分方案合并进本地角色数据（可保留 Enka 其它字段）。

    优先使用 MYS 的 equip + equip_plan_info（含服务端 valid / 评级 / 命中），
    保证刷新后本地 JSON 真正带上官方分。
    """
    data = dict(local_avatar)
    plan = mys_avatar.get("equip_plan_info")
    if isinstance(plan, dict) and plan:
        # 深拷贝，避免后续修改污染
        data["equip_plan_info"] = deepcopy(plan)
        # 清掉回算标记
        data["equip_plan_info"].pop("_score_source", None)
        update_official_plan_cache(data.get("id") or mys_avatar.get("id"), plan)

    # 驱动盘以 MYS 为准（官方 valid / 未命中字段完整）
    if mys_avatar.get("equip"):
        data["equip"] = deepcopy(mys_avatar["equip"])

    # 属性条也以 MYS 为准（更完整）
    if mys_avatar.get("properties"):
        data["properties"] = deepcopy(mys_avatar["properties"])

    if mys_avatar.get("weapon"):
        data["weapon"] = deepcopy(mys_avatar["weapon"])

    ensure_official_score(data, force_recompute=False)
    data["_official_score_applied"] = True
    data["_score_merged_from_mys"] = True
    return data


async def supplement_official_score_from_mys(
    uid: str,
    avatars: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """用米游社 Cookie 拉取 avatar/info，把官方评分合并进本地角色列表。

    - Enka/MiniGG 刷新成功但列表里没有 equip_plan_info 时的关键补丁
    - 查询面板时本地缺评分的兜底
    无 Cookie / 请求失败时原样返回。
    """
    if not avatars:
        return avatars

    # 已全部具备 MYS 原装 plan 则跳过
    need_ids: List[Any] = []
    for a in avatars:
        if not isinstance(a, dict):
            continue
        if has_official_mys_plan(a) and not _need_recompute_valids(a.get("equip") or []):
            continue
        if a.get("id") is not None:
            need_ids.append(a["id"])

    if not need_ids:
        return avatars

    try:
        from ..utils.zzzero_api import zzz_api
    except Exception as e:
        logger.warning(f"[官方评分] 无法导入 zzz_api: {e}")
        return avatars

    ck = await zzz_api.zzz_get_ck(str(uid), "OWNER")
    if not ck:
        logger.info(f"[官方评分] UID={uid} 无主人 Cookie，跳过 MYS 补分")
        return avatars

    # 去重保持顺序
    seen = set()
    id_list = []
    for i in need_ids:
        if i not in seen:
            seen.add(i)
            id_list.append(i)

    try:
        mys_list = await zzz_api.get_zzz_avatar_info(str(uid), id_list)
    except Exception as e:
        logger.warning(f"[官方评分] MYS avatar/info 请求异常: {e}")
        return avatars

    if isinstance(mys_list, int):
        logger.warning(f"[官方评分] MYS avatar/info 失败 retcode={mys_list}")
        return avatars

    # get_zzz_avatar_info 标注为 List[ZZZAvatarInfo]，运行时是普通 dict
    mys_map: Dict[int, Dict[str, Any]] = {}
    for item in mys_list:
        row: Dict[str, Any] = cast(Dict[str, Any], item)
        raw_id = row.get("id")
        if raw_id is None:
            continue
        mys_map[int(raw_id)] = row
    if not mys_map:
        return avatars

    result: List[Dict[str, Any]] = []
    for avatar in avatars:
        local: Dict[str, Any] = dict(avatar)
        raw_local_id = local.get("id")
        mid = int(raw_local_id) if raw_local_id is not None else 0
        mys_row = mys_map.get(mid)
        if mys_row is not None and mys_row.get("equip_plan_info"):
            result.append(merge_mys_avatar_score(local, mys_row))
            logger.info(f"[官方评分] 已合并 MYS 评分 char_id={mid}")
        else:
            ensure_official_score(local)
            result.append(local)
    return result
