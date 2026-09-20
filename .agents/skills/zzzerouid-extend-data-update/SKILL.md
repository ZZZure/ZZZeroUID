---
name: zzzerouid-extend-data-update
description: >
  当用户要求「更新 extend_data」「刷新 weapon_effect / equip_effect」
  「从 nanoka 拉音擎/驱动盘被动」「nanoka.cc 数据接口填 JSON」
  「更新套装效果/音擎精炼效果」「跑 data_to_map_by_nanoka」
  「hakush_resource / INTEND_RES_PATH」「更新 version.py / nanoka 版本」
  「更新 utils/map」时使用。
  Use when the user runs /zzzerouid-extend-data-update.
---

# 从 nanoka 更新版本数据

一次发版对齐四块：版本号与 CDN、`utils/map`、`INTEND_RES_PATH` 图标、`extend_data` 两份效果 JSON。

效果 DSL（`weapon_effect` / `equip_effect` 字段）见 [references/effect-dsl.md](./references/effect-dsl.md)。

## 版本发现

1. `GET https://zzz.nanoka.cc/`，正则 `static\.nanoka\.cc/zzz/([^/"']+)/`，得到 CDN 目录，如 `3.3.3+19110104`。
2. 插件 map 后缀 = 去掉 `+build`：`3.3.3+19110104` → `3.3.3`。
3. 只改 `ZZZeroUID/version.py`：

```python
ZZeroUID_version = "3.3.3"
ZZZero_version = "3.3.3"
NANOKA_DATA_VERSION = "3.3.3+19110104"
```

`utils/hakush_api/api.py` 的 `HAKUSH_BASE` 和 `tools/hakush_resource.py` 的邦布目录都读 `NANOKA_DATA_VERSION`，不要再手改 URL。

CDN：

| 用途 | URL |
|------|-----|
| 角色/音擎/驱动盘/邦布目录 | `https://static.nanoka.cc/zzz/<NANOKA_DATA_VERSION>/{character,weapon,equipment,bangboo}.json` |
| 角色/音擎详情 | `.../zh/character/<id>.json`、`.../zh/weapon/<id>.json` |
| 图标 webp | `https://static.nanoka.cc/assets/zzz/<code>.webp`（无版本号） |

`new.json` 在新 CDN 上 404，map 脚本不用它。

## 执行顺序（必须按序）

在**插件根**执行，解释器必须是 Core 根 `.venv`（本机 `F:\gsuid_core\.venv\Scripts\python.exe`）。插件目录里 `uv run` 往往没有 `fastapi`，会在 import `gsuid_core` 时炸掉。先 bump `version.py`，再跑脚本：`data_to_map_by_nanoka` 按 `ZZZero_version` 写 `utils/map/*_<ver>.json`；`hakush_resource` 从 `name_convert` 读这些 map，文件必须已经存在。

1. **改 `version.py`**（上表）。
2. **生成 map** → `ZZZeroUID/utils/map/`：

```text
F:\gsuid_core\.venv\Scripts\python.exe ZZZeroUID/tools/data_to_map_by_nanoka.py
```

写出 `PartnerId2Data_<ver>.json`、`PartnerId2SkillParam_<ver>.json`、`WeaponId2Data_<ver>.json`、`EquipId2Data_<ver>.json`。旧版本 json 留着，不要删。角色详情有 3s sleep，大约数分钟。若 `PROP_NAME_TO_ID` KeyError，把 nanoka `base_property.name2` / `rand_property.name2` 补进 `data_to_map_by_nanoka.py` 后再跑。
3. **下图标** → `ZZZeroUID/tools/INTEND_RES_PATH/`（已存在的文件会跳过）：

```text
F:\gsuid_core\.venv\Scripts\python.exe ZZZeroUID/tools/hakush_resource.py
```

写 `weapon/`、`suit/`、`3d_suit/`、`role/`、`role_circle/`、`role_general/`、`mind/`、`square_bangbo/`。已存在则跳过。邦布 `icon` 为空、或 webp 404（测试角色立绘 / 部分 3D 套装）打印失败后继续，不算整次失败。
4. **extend_data**（默认只追加 JSON 里还没有的名字，新的放最上面）：

```text
python .agents/skills/zzzerouid-extend-data-update/scripts/update_extend_data.py --self-test
python .agents/skills/zzzerouid-extend-data-update/scripts/update_extend_data.py
```

全量重编已有 effect 才加 `--rewrite-all`。DSL 与 REVIEW 规则见下。
5. 新角色补 `utils/alias/char_alias.json`。同步 `AGENTS.md` 里写的当前版本号。

## extend_data

- 音擎：键 = 中文名；`normal_effect` / `skill_effect` 各 `"1"`…`"5"`。
- 驱动盘：键 = 套装名；`desc1` = 2 件，`desc2` = 4 件。
- 详情用 `talents["1".."5"].desc` 和装备 `desc2`/`desc4`；中文名用详情 `name`。
- `energy-flat` / `daze` / `buildup` / `sheer` / 纯减伤 的 REVIEW 保持空串。
- 不要把中文写进 effect；必须 `Crit` 不是 `crit`。
- 没有新条目时脚本不改对应文件。

## 坑

- 先改 `version.py` 再跑 map：否则文件名还是旧后缀，插件加载的还是旧 map。
- map 没写完就跑 `hakush_resource`：`name_convert` 会找不到 `*_3.3.3.json`。
- 漏 `game_name="zzz"` 与这次无关，但别在同一任务里改绑定。
- `data_to_map_by_hakush.py` 不要用；nanoka 路径以 `data_to_map_by_nanoka.py` 为准。
