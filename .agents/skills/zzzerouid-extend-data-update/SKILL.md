---
name: zzzerouid-extend-data-update
description: >
  当用户要求「更新 extend_data」「刷新 weapon_effect / equip_effect」
  「从 nanoka 拉音擎/驱动盘被动」「nanoka.cc 数据接口填 JSON」
  「更新套装效果/音擎精炼效果」时使用。
  Use when the user runs /zzzerouid-extend-data-update.
---

# 从 nanoka 更新 `extend_data`

把 [nanoka.cc](https://zzz.nanoka.cc/) 的音擎天赋、驱动盘 2/4 件套，编码进：

- `ZZZeroUID/utils/extend_data/weapon_effect.json`
- `ZZZeroUID/utils/extend_data/equip_effect.json`

字段含义、招式前缀、属性名、量纲见 [references/effect-dsl.md](./references/effect-dsl.md)。先读它再改 JSON。

源码消费：`enka_to_mys.py` 的 `get_normal_equip_buff` 目前只吃 **驱动盘 `normal_effect`**。`skill_effect` 与 `weapon_effect` 已加载，按同一 DSL 维护。

## 何时跑

新版本音擎/驱动盘。默认**只追加 JSON 里还没有的名字**，已有条目原样不动。已有条目要整份重解析时才用 `--rewrite-all`。

不要用这套流程改 `utils/map/*`（那是 `data_to_map_by_hakush.py` / nanoka 地图脚本）。

## 步骤

1. **自检解析器**（必须先过）：

```text
python .agents/skills/zzzerouid-extend-data-update/scripts/update_extend_data.py --self-test
```

2. **拉最新 nanoka 并写 JSON**：

```text
python .agents/skills/zzzerouid-extend-data-update/scripts/update_extend_data.py
# 仅当需要把已有条目也按 nanoka 重编时：
# python .agents/skills/zzzerouid-extend-data-update/scripts/update_extend_data.py --rewrite-all
```

版本发现：抓 `https://zzz.nanoka.cc/` HTML，取 `static.nanoka.cc/zzz/<ver>/`。覆盖用 `--version 3.3.3+19110104`。

CDN：

| 用途 | URL |
|------|-----|
| 音擎目录 | `https://static.nanoka.cc/zzz/<ver>/weapon.json` |
| 音擎详情 | `https://static.nanoka.cc/zzz/<ver>/zh/weapon/<id>.json` |
| 驱动盘目录 | `https://static.nanoka.cc/zzz/<ver>/equipment.json` |
| 驱动盘详情 | `https://static.nanoka.cc/zzz/<ver>/zh/equipment/<id>.json` |

详情里用 `talents["1".."5"].desc`（音擎）和 `desc2` / `desc4`（驱动盘 2/4 件）。中文名用详情 `name`，不要用目录里可能截断的 `zh`。

3. **看脚本打印的 REVIEW**。`energy-flat` / `daze` / `buildup` / `sheer` 是 DSL 故意不收的（能量点/秒、失衡、积蓄、贯穿），空串即可。`parsed-empty` 且文案只有减伤/喧响值的，也保持空串。其余打开 nanoka 详情按 DSL 手修：

- 一句里多种互斥条件（只取面板常用的满层期望）
- 测试音擎、`Item_Weapon_*` 占位名：保持空串

4. **抽查**新音擎 / 新套装，以及 `Crit` 大小写、前缀字母序（`AXSBCWQPE`）、万分比（8% → `800`）。

5. 不要把中文说明写进 effect 字符串。不要用 `crit`（必须 `Crit`）。

## 写入规则

- 音擎：键 = 中文名；`normal_effect` / `skill_effect` 各 `"1"`…`"5"`（精炼）。
- 驱动盘：键 = 套装中文名；`desc1` = 2 件，`desc2` = 4 件。无条件进 `normal_effect`，触发/招式伤进 `skill_effect`。
- 多条效果用 `;` 拼接，无效果用 `""`。
- 默认只写入**尚不存在的键**；已有键的值、顺序一律不改。
- 本轮新增的条目插到 JSON **最上面**（最新 id 在前）。
- 没有新条目时不改对应文件。
- 全量重解析（会改已有值、diff 会很大）才加 `--rewrite-all`。
