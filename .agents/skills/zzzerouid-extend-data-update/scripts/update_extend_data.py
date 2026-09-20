"""Fetch nanoka weapon/equipment text and fill extend_data JSON."""

from __future__ import annotations

import re
import sys
import json
import argparse
import urllib.error
import urllib.request
from pathlib import Path

UA = {"User-Agent": "ZZZeroUID-extend-data/1.0"}
SITE = "https://zzz.nanoka.cc/"
CDN = "https://static.nanoka.cc/zzz"
PREFIX_ORDER = list("AXSBCWQPE")
SKILL_PATTERNS: list[tuple[str, str]] = [
    ("强化特殊技", "C"),
    ("普通攻击", "A"),
    ("冲刺攻击", "X"),
    ("闪避反击", "S"),
    ("特殊技", "B"),
    ("连携技", "W"),
    ("终结技", "Q"),
    ("快速支援", "P"),
    ("极限支援", "P"),
    ("招架支援", "P"),
    ("回避支援", "P"),
    ("追加攻击", "E"),
    ("支援突击", "E"),
    ("支援攻击", "PE"),
]
COLOR_RE = re.compile(r"</?color(?:=[^>]*)?>", re.I)
TRIGGER_RE = re.compile(
    r"发动|命中|触发|成为|位于后场|从背后|处于|入场|换入|开启|延长|对敌人施加|场上存在|装备者为|拥有|低于|每层"
)
PLACEHOLDER_NAME = re.compile(r"^(Item_|\[占位\]|\[Placeholder\])|测试音擎")

GOLD_CASES: list[tuple[str, str, str, str]] = [
    ("啄木鸟2", "暴击率+8%。", "Crit+800", ""),
    (
        "啄木鸟4",
        "[普通攻击]、[闪避反击]或[强化特殊技]命中敌人并触发暴击时，分别为装备者提供1层增益效果，每层增益效果使装备者的攻击力提升9%，持续6秒，不同招式分别结算持续时间。",
        "",
        "ASC:AttackAdd+2700",
    ),
    (
        "河豚4",
        "[终结技]造成的伤害提升20%；发动[终结技]时，装备者的攻击力提升15%，持续12秒。",
        "",
        "Q:DmgBonus+2000;AttackAdd+1500",
    ),
    ("拂晓2", "[普通攻击]造成的伤害提升15%。", "", "A:DmgBonus+1500"),
    ("如影2", "[追加攻击]和[冲刺攻击]造成的伤害提升15%。", "", "XE:DmgBonus+1500"),
    (
        "如影4",
        "[追加攻击]或[冲刺攻击]命中敌人时，若造成的伤害与装备者的属性一致，则获得1层增益效果，同一招式内最多触发一次；每拥有1层增益效果，装备者的攻击力提升4%，暴击率提升4%，最多叠加3层，持续15秒，重复触发时刷新持续时间。",
        "",
        "AttackAdd+1200;Crit+1200",
    ),
    (
        "极地4",
        "[普通攻击]和[冲刺攻击]造成的伤害提升20%，队伍中任意角色对敌人施加[冻结]或触发[碎冰]效果时，该增益效果额外提升20%，持续12秒。",
        "",
        "AX:DmgBonus+4000",
    ),
    (
        "花信",
        "攻击力提升6%，[强化特殊技]造成的伤害提升15%。",
        "AttackAdd+600",
        "C:DmgBonus+1500",
    ),
    ("月相望", "[普通攻击]、[冲刺攻击]、[闪避反击]造成的伤害提升12%。", "", "AXS:DmgBonus+1200"),
    ("月相晦", "发动[连携技]或[终结技]时，装备者造成的伤害提升15%，持续6秒。", "", "WQ:DmgBonus+1500"),
    (
        "月相弦",
        "发动[强化特殊技]时，[普通攻击]造成的伤害提升18%，持续10秒，重复触发时刷新持续时间。",
        "",
        "A:DmgBonus+1800",
    ),
    (
        "拘缚者",
        "攻击命中敌人时，[普通攻击]造成的伤害和失衡值提升6%，最多叠加5层，持续8秒，同一招式内最多触发一次，每层效果单独结算持续时间。",
        "",
        "A:DmgBonus+3000",
    ),
    (
        "钢铁",
        "物理伤害提升20%；从背后攻击命中敌人时，装备者造成的伤害提升25%。",
        "PhysDmgBonus+2000",
        "DmgBonus+2500",
    ),
    (
        "硫磺",
        "[普通攻击]、[冲刺攻击]或[闪避反击]命中敌人时，装备者的攻击力提升3.5%，最多叠加8层，持续8秒，0.5秒内最多触发一次，每层效果单独结算持续时间。",
        "",
        "AttackAdd+2800",
    ),
    (
        "残心",
        "暴击率提升10%；[冲刺攻击]造成的电属性伤害提升40%；队伍中任意角色对敌人施加属性异常效果或造成失衡时，装备者的暴击率额外提升10%，持续15秒。",
        "Crit+1000",
        "X:ThunderDmgBonus+4000;Crit+1000",
    ),
    (
        "拂晓4",
        "[普通攻击]造成的伤害提升20%，装备者为[强攻]角色时，发动[强化特殊技]或[终结技]会使[普通攻击]造成的伤害额外提升20%，持续25秒，重复触发时刷新持续时间。",
        "",
        "A:DmgBonus+4000",
    ),
    (
        "混沌金属4",
        "装备者的暴击伤害提升20%，队伍中任意角色触发[侵蚀]伤害时，该增益效果额外提升5.5%，最多叠加6层，持续8秒，重复触发时刷新持续时间。",
        "CritDmg+2000",
        "CritDmg+3300",
    ),
    (
        "血髓",
        "装备者暴击率大于100%时，每超出1%暴击率，使装备者造成的伤害提升0.48%，至多提升24%。",
        "DmgBonus+2400",
        "",
    ),
    (
        "烛光",
        "发动[强化特殊技]时，装备者暴击率提升8%，持续40秒；装备者对当前生命值低于最大值50%的敌人造成的伤害提高15%。",
        "",
        "Crit+800;DmgBonus+1500",
    ),
    (
        "无视抗",
        "造成的伤害无视目标16%风属性伤害抗性。",
        "WindResist+-1600",
        "",
    ),
]


def plugin_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "ZZZeroUID" / "utils" / "extend_data").is_dir():
            return parent
    raise SystemExit("cannot find plugin root (ZZZeroUID/utils/extend_data)")


def extend_dir() -> Path:
    return plugin_root() / "ZZZeroUID" / "utils" / "extend_data"


def http_get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def discover_version() -> str:
    html = http_get(SITE, timeout=20).decode("utf-8", errors="replace")
    found = re.findall(r"static\.nanoka\.cc/zzz/([^/\"']+)/", html)
    if not found:
        raise SystemExit("cannot discover nanoka version from homepage")
    return found[0]


def strip_color(s: str) -> str:
    return COLOR_RE.sub("", s)


def pct_val(n: float) -> int:
    return int(round(n * 100))


def find_skills(text: str) -> str:
    found: list[str] = []
    seen: set[str] = set()
    i = 0
    while i < len(text):
        hit: tuple[str, str] | None = None
        for name, code in SKILL_PATTERNS:
            if text.startswith(name, i) or text.startswith(f"[{name}]", i):
                hit = (name, code)
                break
        if hit:
            name, code = hit
            for ch in code:
                if ch not in seen:
                    seen.add(ch)
                    found.append(ch)
            i += len(name)
            continue
        i += 1
    found.sort(key=lambda c: PREFIX_ORDER.index(c) if c in PREFIX_ORDER else 99)
    return "".join(found)


def max_stacks(text: str) -> int:
    m = re.search(r"最多叠加\s*(\d+)\s*层", text)
    n = int(m.group(1)) if m else 1
    if "分别为" in text:
        skills = find_skills(text)
        if skills:
            n = max(n, len(skills))
    return n


def extra_full_stack(text: str) -> float | None:
    m = re.search(r"叠满[^。；;]{0,20}?提升\s*(\d+(?:\.\d+)?)\s*%", text)
    return float(m.group(1)) if m else None


def is_threshold_stat(text: str, keyword: str) -> bool:
    idx = text.find(keyword)
    if idx < 0:
        return False
    window = text[idx : idx + len(keyword) + 12]
    return any(s in window for s in ("大于", "超过", "不低于"))


def last_pct_after(text: str, keyword: str) -> float | None:
    idx = text.find(keyword)
    if idx < 0:
        return None
    window = text[idx : idx + 28]
    point = window.find("点")
    pct = window.find("%")
    if point != -1 and (pct == -1 or point < pct):
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*%", window)
    if m:
        return max(float(m.group(1)), float(m.group(2)))
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", window)
    return float(m.group(1)) if m else None


def last_flat_after(text: str, keyword: str) -> float | None:
    idx = text.find(keyword)
    if idx < 0:
        return None
    window = text[idx : idx + 36]
    m = re.search(r"(\d+(?:\.\d+)?)\s*点", window)
    if m:
        return float(m.group(1))
    m = re.search(r"提升\s*(\d+(?:\.\d+)?)", window)
    if m and "%" not in window[: window.find(m.group(1)) + 6]:
        return float(m.group(1))
    return None


def extract_effects(clause: str, stack_src: str = "") -> list[tuple[str, int]]:
    t = clause
    out: list[tuple[str, int]] = []
    stacks = max_stacks(t)
    if any(k in t for k in ("每层", "每拥有", "该增益", "分别为")):
        stacks = max(stacks, max_stacks(stack_src))
    extra = extra_full_stack(t)

    if "防御力降低" in t or ("无视" in t and "防御" in t):
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", t)
        if m:
            out.append(("D", -pct_val(float(m.group(1)))))

    resist_map = [
        ("火属性伤害抗性", "FireResist"),
        ("冰属性伤害抗性", "IceResist"),
        ("电属性伤害抗性", "ThunderResist"),
        ("以太伤害抗性", "EtherResist"),
        ("物理伤害抗性", "PhysResist"),
        ("风属性伤害抗性", "WindResist"),
        ("火属性抗性", "FireResist"),
        ("冰属性抗性", "IceResist"),
        ("电属性抗性", "ThunderResist"),
    ]
    for kw, stat in resist_map:
        if kw in t:
            m = re.search(r"(\d+(?:\.\d+)?)\s*%", t)
            if m:
                out.append((stat, -pct_val(float(m.group(1)))))

    if "暴击伤害" in t and not is_threshold_stat(t, "暴击伤害"):
        n = last_pct_after(t, "暴击伤害")
        if n is not None:
            v = pct_val(n) * stacks
            if extra:
                v += pct_val(extra)
            out.append(("CritDmg", v))
    if "暴击率" in t and not is_threshold_stat(t, "暴击率"):
        n = last_pct_after(t, "暴击率")
        if n is not None:
            v = pct_val(n) * stacks
            if extra:
                v += pct_val(extra)
            out.append(("Crit", v))

    if "异常精通" in t:
        n = last_flat_after(t, "异常精通")
        if n is not None:
            out.append(("ElementMystery", int(round(n * stacks))))
    if "异常掌控" in t:
        n = last_pct_after(t, "异常掌控")
        if n is not None:
            out.append(("ElementAbnormalPowerAdd", pct_val(n) * stacks))
        else:
            n = last_flat_after(t, "异常掌控")
            if n is not None:
                out.append(("ElementAbnormalPower", int(round(n * stacks))))

    if "穿透率" in t:
        n = last_pct_after(t, "穿透率")
        if n is not None:
            out.append(("PenRate", pct_val(n) * stacks))

    energy_at = t.find("能量自动回复")
    if energy_at >= 0 and "点" not in t[energy_at : energy_at + 24]:
        n = last_pct_after(t, "能量自动回复")
        if n is not None:
            out.append(("SpRecoverAdd", pct_val(n) * stacks))

    if "护盾" in t:
        n = last_pct_after(t, "护盾")
        if n is not None:
            out.append(("ShieldAdd", pct_val(n) * stacks))

    if "冲击力" in t:
        n = last_pct_after(t, "冲击力")
        if n is not None:
            v = pct_val(n) * stacks
            if extra:
                v += pct_val(extra)
            out.append(("BreakStunAdd", v))
        else:
            n = last_flat_after(t, "冲击力")
            if n is not None:
                out.append(("BreakStunBase", int(round(n * stacks))))

    if "攻击力" in t:
        n = last_pct_after(t, "攻击力")
        if n is not None:
            v = pct_val(n) * stacks
            if extra:
                v += pct_val(extra)
            out.append(("AttackAdd", v))

    if "防御力" in t and "降低" not in t and "无视" not in t and not is_threshold_stat(t, "防御力"):
        n = last_pct_after(t, "防御力")
        if n is not None:
            out.append(("DefenceAdd", pct_val(n) * stacks))

    if "生命值" in t and "低于" not in t:
        n = last_pct_after(t, "生命值")
        if n is not None:
            out.append(("HpAdd", pct_val(n) * stacks))

    elem_map = [
        ("物理伤害", "PhysDmgBonus"),
        ("火属性伤害", "FireDmgBonus"),
        ("冰属性伤害", "IceDmgBonus"),
        ("电属性伤害", "ThunderDmgBonus"),
        ("以太伤害", "EtherDmgBonus"),
        ("以太属性伤害", "EtherDmgBonus"),
        ("风属性伤害", "WindDmgBonus"),
    ]
    for kw, stat in elem_map:
        if kw not in t:
            continue
        idx = t.find(kw)
        if t[idx + len(kw) : idx + len(kw) + 1] == "时":
            continue
        n = last_pct_after(t, kw)
        if n is not None:
            v = pct_val(n) * stacks
            if extra:
                v += pct_val(extra)
            out.append((stat, v))

    cap = last_pct_after(t, "至多提升") or last_pct_after(t, "最多提升")
    has_elem = any(s.endswith("DmgBonus") and s != "DmgBonus" for s, _ in out)
    ignore_generic = "无视" in t or "每超出" in t or cap is not None
    generic = (not ignore_generic) and (
        "造成的伤害" in t
        or "造成伤害" in t
        or ("伤害提高" in t and "暴击伤害" not in t)
        or (re.search(r"(?<![属理火冰电太风击])伤害提升", t) is not None and "暴击伤害" not in t)
    )
    if cap is not None:
        out.append(("DmgBonus", pct_val(cap)))
    elif (not has_elem) and generic:
        n: float | None = None
        for kw in ("造成的伤害", "造成伤害", "伤害提升", "伤害提高"):
            n = last_pct_after(t, kw)
            if n is not None:
                break
        if n is None:
            m = re.search(r"(\d+(?:\.\d+)?)\s*%", t)
            if m:
                n = float(m.group(1))
        if n is not None:
            v = pct_val(n) * stacks
            if extra:
                v += pct_val(extra)
            out.append(("DmgBonus", v))

    m_extra = re.search(
        r"(?:该增益效果额外提升|造成的伤害额外提升|暴击伤害额外提升|攻击力额外提升)\s*(\d+(?:\.\d+)?)\s*%",
        t,
    )
    if m_extra and "最多叠加" not in t:
        extra_n = pct_val(float(m_extra.group(1)))
        hit = False
        for i in range(len(out) - 1, -1, -1):
            if "DmgBonus" in out[i][0] or out[i][0] in ("AttackAdd", "Crit", "CritDmg"):
                s, v = out[i]
                out[i] = (s, v + extra_n)
                hit = True
                break
        if not hit:
            out.append(("__INHERIT__", extra_n))
    elif m_extra and "最多叠加" in t and not out:
        out.append(("__INHERIT__", pct_val(float(m_extra.group(1))) * stacks))
    elif not out:
        m2 = re.search(r"该增益效果额外提升\s*(\d+(?:\.\d+)?)\s*%", t)
        if m2:
            out.append(("__INHERIT__", pct_val(float(m2.group(1))) * stacks))
    return out


def is_conditional(clause: str) -> bool:
    return TRIGGER_RE.search(clause) is not None or re.search(r"\[[^]]+\]造成的", clause) is not None


def damage_source_prefix(clause: str) -> str:
    m = re.search(r"((?:\[[^]]+\][、或和与]*)+)造成的(?:\S{0,6})?伤害", clause)
    return find_skills(m.group(1)) if m else ""


def format_tok(prefix: str, stat: str, value: int) -> str:
    p = f"{prefix}:" if prefix else ""
    return f"{p}{stat}+{value}"


def _split_percent_comma(part: str) -> list[str]:
    bits = [b.strip() for b in re.split(r"(?<=%)[，,]", part) if b.strip()]
    if len(bits) <= 1:
        return [part]
    glued: list[str] = [bits[0]]
    for bit in bits[1:]:
        if re.match(r"最多叠加", bit) or not re.search(
            r"暴击|攻击力|防御力|生命值|伤害|精通|掌控|冲击力|穿透|护盾|该增益|额外提升",
            bit,
        ):
            glued[-1] = glued[-1] + "，" + bit
        else:
            glued.append(bit)
    if len(glued) <= 1:
        return glued
    merged: list[str] = [glued[0]]
    for bit in glued[1:]:
        extra_only = "该增益效果额外" in bit or ("额外提升" in bit and "最多叠加" not in bit)
        if extra_only and "最多叠加" not in bit:
            merged[-1] = merged[-1] + "，" + bit
            continue
        if "叠满" in bit:
            merged[-1] = merged[-1] + "，" + bit
            continue
        merged.append(bit)
    return [s.strip() for s in merged if s.strip()]


def split_clauses(desc: str) -> list[tuple[str, bool, str]]:
    desc = strip_color(desc).replace("\n", "")
    raw = [p.strip() for p in re.split(r"[；;]", desc) if p.strip()]
    parts: list[str] = []
    prev_stack = ""
    for p in raw:
        m_stack = re.search(r"最多叠加\s*\d+\s*层", p)
        if m_stack:
            prev_stack = m_stack.group(0)
        if parts and m_stack and not re.search(r"提升|降低|提高", p):
            parts[-1] = parts[-1] + "，" + p
            continue
        if prev_stack and "每层" in p and "最多叠加" not in p:
            p = p + "，" + prev_stack
        parts.append(p)
    out: list[tuple[str, bool, str]] = []
    for part in parts:
        parent_cond = is_conditional(part)
        subs = _split_percent_comma(part)
        for i, sub in enumerate(subs):
            if "最多叠加" not in sub:
                m = re.search(r"最多叠加\s*\d+\s*层", part)
                if m and (i > 0 or "每层" in sub or "每拥有" in sub or "分别为" in sub):
                    sub = sub + "，" + m.group(0)
            if "分别为" in part and "分别为" not in sub:
                sub = "分别为" + sub
            inherit = parent_cond if i > 0 else False
            out.append((sub, inherit, part))
    return out


def parse_desc(desc: str) -> tuple[list[str], list[str]]:
    parts = split_clauses(desc)
    normal: list[str] = []
    skill: list[str] = []
    last_stat = ""
    last_prefix = ""
    for clause, parent_cond, parent in parts:
        effects = extract_effects(clause, parent)
        if not effects:
            continue
        cond = is_conditional(clause) or parent_cond
        src = damage_source_prefix(clause) or damage_source_prefix(parent)
        fenbie = "分别为" in clause or "分别为" in parent
        trig = find_skills(parent if fenbie else clause) if cond else ""
        for stat, value in effects:
            if stat == "__INHERIT__":
                stat = last_stat or "DmgBonus"
                prefix = last_prefix
            else:
                prefix = ""
                if src and ("DmgBonus" in stat):
                    prefix = src
                elif fenbie:
                    prefix = trig
                elif stat == "DmgBonus" and trig and not src:
                    prefix = trig
            last_stat, last_prefix = stat, prefix
            tok = format_tok(prefix, stat, value)
            (skill if cond else normal).append(tok)
    return normal, skill


def join_toks(toks: list[str]) -> str:
    acc: dict[str, int] = {}
    order: list[str] = []
    for t in toks:
        name, sep, rest = t.partition("+")
        if not sep:
            continue
        val = int(float(rest))
        if name not in acc:
            order.append(name)
            acc[name] = 0
        acc[name] += val
    return ";".join(f"{name}+{acc[name]}" for name in order)


def empty_weapon() -> dict[str, dict[str, str]]:
    keys = {str(i): "" for i in range(1, 6)}
    return {"normal_effect": dict(keys), "skill_effect": dict(keys)}


def empty_equip() -> dict[str, dict[str, str]]:
    blank = {"desc1": "", "desc2": ""}
    return {"normal_effect": dict(blank), "skill_effect": dict(blank)}


def needs_review(desc: str, normal: str, skill: str) -> list[str]:
    reasons: list[str] = []
    plain = strip_color(desc)
    if PLACEHOLDER_NAME.search(plain):
        reasons.append("placeholder")
    interesting = "提升" in plain or "提高" in plain or "+" in plain or "降低" in plain or "无视" in plain
    if interesting and not normal and not skill:
        reasons.append("parsed-empty")
    if "点/秒" in plain or "点能量" in plain:
        reasons.append("energy-flat")
    if "失衡值" in plain:
        reasons.append("daze")
    if "积蓄" in plain:
        reasons.append("buildup")
    if "贯穿" in plain:
        reasons.append("sheer")
    return reasons


def run_self_test() -> int:
    failed = 0
    for name, desc, exp_n, exp_s in GOLD_CASES:
        n, s = parse_desc(desc)
        got_n, got_s = join_toks(n), join_toks(s)
        if got_n == exp_n and got_s == exp_s:
            print(f"[OK] {name}")
        else:
            failed += 1
            print(f"[FAIL] {name}")
            print(f"  got n={got_n!r} s={got_s!r}")
            print(f"  exp n={exp_n!r} s={exp_s!r}")
    print(f"{len(GOLD_CASES) - failed}/{len(GOLD_CASES)}")
    return 1 if failed else 0


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def dump_json(path: Path, data: dict) -> None:
    # 与仓库里旧文件一致：indent=2，再给除首行外每行加 2 空格。
    raw = json.dumps(data, indent=2, ensure_ascii=False)
    lines = raw.splitlines()
    out = [lines[0]]
    for line in lines[1:]:
        out.append("  " + line if line else line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def parse_weapon_detail(detail: dict) -> tuple[dict[str, dict[str, str]], list[str], str]:
    item = empty_weapon()
    talents = detail.get("talents") or {}
    reviews: list[str] = []
    name = str(detail["name"]).strip()
    for star in ("1", "2", "3", "4", "5"):
        desc = (talents.get(star) or {}).get("desc") or ""
        n, s = parse_desc(desc)
        item["normal_effect"][star] = join_toks(n)
        item["skill_effect"][star] = join_toks(s)
        for reason in needs_review(desc, item["normal_effect"][star], item["skill_effect"][star]):
            reviews.append(f"R{star} {reason}")
    return item, reviews, name


def parse_equip_detail(detail: dict) -> tuple[dict[str, dict[str, str]], list[str], str]:
    item = empty_equip()
    name = str(detail["name"]).strip()
    d2 = detail.get("desc2") or ""
    d4 = detail.get("desc4") or ""
    n2, s2 = parse_desc(d2)
    n4, s4 = parse_desc(d4)
    item["normal_effect"]["desc1"] = join_toks(n2)
    item["skill_effect"]["desc1"] = join_toks(s2)
    item["normal_effect"]["desc2"] = join_toks(n4)
    item["skill_effect"]["desc2"] = join_toks(s4)
    reviews: list[str] = []
    for reason in needs_review(d2, item["normal_effect"]["desc1"], item["skill_effect"]["desc1"]):
        reviews.append(f"2pc {reason}")
    for reason in needs_review(d4, item["normal_effect"]["desc2"], item["skill_effect"]["desc2"]):
        reviews.append(f"4pc {reason}")
    return item, reviews, name


def merge_new_on_top(old: dict, new_items: dict) -> dict:
    """新条目按传入顺序放最前，已有条目原样、原顺序保留。"""
    out: dict = {}
    for name, item in new_items.items():
        out[name] = item
    for name, item in old.items():
        if name not in out:
            out[name] = item
    return out


def update_weapons(ver: str, old: dict, rewrite_all: bool) -> tuple[dict, list[str], bool]:
    idx = json.loads(http_get(f"{CDN}/{ver}/weapon.json"))
    reviews: list[str] = []
    added: dict[str, dict] = {}
    for wid in idx:
        hint = str((idx[wid] or {}).get("zh") or "").strip()
        if not rewrite_all and hint in old:
            continue
        detail = json.loads(http_get(f"{CDN}/{ver}/zh/weapon/{wid}.json"))
        item, item_reviews, name = parse_weapon_detail(detail)
        if PLACEHOLDER_NAME.search(name) or name.startswith("Item_"):
            reviews.append(f"SKIP weapon {wid} {name}")
            continue
        if not rewrite_all and name in old:
            continue
        added[name] = item
        print(f"weapon {wid} {name}")
        for r in item_reviews:
            reviews.append(f"REVIEW weapon {wid} {name} {r}")
    # 目录是旧→新，倒过来让最新的在最上面
    added = {k: added[k] for k in reversed(list(added))}
    if rewrite_all:
        out = merge_new_on_top(old, added)
        return out, reviews, True
    if not added:
        return old, reviews, False
    out = merge_new_on_top(old, added)
    if "半糖雪兔" in added and "半糖冰雹" in out:
        del out["半糖冰雹"]
        reviews.append("DROP stale weapon 半糖冰雹")
    reviews.append("NEW weapons: " + ", ".join(added))
    return out, reviews, True


def update_equips(ver: str, old: dict, rewrite_all: bool) -> tuple[dict, list[str], bool]:
    idx = json.loads(http_get(f"{CDN}/{ver}/equipment.json"))
    reviews: list[str] = []
    added: dict[str, dict] = {}
    for eid in idx:
        hint = ""
        meta = idx[eid] or {}
        zh = meta.get("zh")
        if isinstance(zh, dict):
            hint = str(zh.get("name") or "").strip()
        elif zh:
            hint = str(zh).strip()
        if not rewrite_all and hint in old:
            continue
        detail = json.loads(http_get(f"{CDN}/{ver}/zh/equipment/{eid}.json"))
        item, item_reviews, name = parse_equip_detail(detail)
        if not rewrite_all and name in old:
            continue
        added[name] = item
        print(f"equip {eid} {name}")
        for r in item_reviews:
            reviews.append(f"REVIEW equip {eid} {name} {r}")
    added = {k: added[k] for k in reversed(list(added))}
    if rewrite_all:
        return merge_new_on_top(old, added), reviews, True
    if not added:
        return old, reviews, False
    reviews.append("NEW equips: " + ", ".join(added))
    return merge_new_on_top(old, added), reviews, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--version", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--rewrite-all",
        action="store_true",
        help="重解析全部条目（默认只追加 JSON 里还没有的）",
    )
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()

    ver = args.version or discover_version()
    print(f"nanoka version {ver}")
    root = extend_dir()
    weapon_path = root / "weapon_effect.json"
    equip_path = root / "equip_effect.json"
    old_w = load_json(weapon_path)
    old_e = load_json(equip_path)
    weapons, wr, w_changed = update_weapons(ver, old_w, args.rewrite_all)
    equips, er, e_changed = update_equips(ver, old_e, args.rewrite_all)
    if args.dry_run:
        print("dry-run, not writing")
    else:
        if w_changed:
            dump_json(weapon_path, weapons)
            print(f"wrote {weapon_path}")
        else:
            print(f"unchanged {weapon_path}")
        if e_changed:
            dump_json(equip_path, equips)
            print(f"wrote {equip_path}")
        else:
            print(f"unchanged {equip_path}")
    print(f"weapons {len(weapons)} equips {len(equips)}")
    for line in wr + er:
        print(line)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as e:
        print("http error", e, file=sys.stderr)
        raise SystemExit(2)
