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
2. 插件 map 后缀 = `ZZZero_version`（**不是** CDN 版本去掉 `+build`）。两者是两个独立变量：

   | 变量 | 决定什么 | 谁读它 |
   |------|---------|--------|
   | `ZZZero_version` | `utils/map/*_<ver>.json` 文件名 | `tools/data_to_map.py` 拼文件名 → `utils/name_convert.py` / `utils/zzz_map.py` 按同名字段读 |
   | `NANOKA_DATA_VERSION` | CDN 数据目录 | `utils/hakush_api/api.py` 的 `HAKUSH_BASE`、`tools/hakush_resource.py` 的邦布目录 |

   所以插件版本号**不必等于** CDN 版本号：用户要 `3.4` 而 CDN 只有 `3.3.12+19566749` 时，
   `ZZZero_version = "3.4"` + `NANOKA_DATA_VERSION = "3.3.12+19566749"` 完全成立，
   只要 `utils/map/*_3.4.json` 生成了就能跑。CDN 上没有的版本号一律 404，别硬凑 `+build`。
3. 只改 `ZZZeroUID/version.py`：

```python
ZZeroUID_version = "3.4"
ZZZero_version = "3.4"
NANOKA_DATA_VERSION = "3.3.12+19566749"
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
2. **清缓存 + 生成 map** → `ZZZeroUID/utils/map/`：

```text
F:\gsuid_core\.venv\Scripts\python.exe ZZZeroUID/tools/data_to_map_by_nanoka.py
```

脚本按顺序做三件事：

1. **先删缓存**（`clear_stale_cache()`）。`gsuid_core` 的 `cache_data` 只按 id 落盘到
   `DATA_CACHE_PATH\get_hakush_char_data\` 与 `get_hakush_weapon_data\`，**没有 TTL、没有数据版本键**，
   磁盘里可能还留着角色上线前的测试快照（名字带 `(Test1)` 前缀、数值是 beta 值）。
   不清掉的话，**运行时的伤害计算也会读到旧快照**（`zzzerouid_char_detail/mono/damage_cal.py`
   → `utils/data.py::get_hakush_char` → 带 `@cache_data` 的 `get_hakush_char_data`），
   算出来的伤害是 beta 数值。脚本只删这两个 hakush 目录，`DATA_CACHE_PATH` 下别的插件的缓存别动。
2. **直连 CDN 取详情**（`fetch_detail`），不走缓存接口，并剥掉 `(TestN)` 占位前缀。
3. **写完新 map 后删旧版本**（`remove_old_map_files()`）：`utils/map/` 只保留 `*_<ZZZero_version>.json`，
   旧版本 json **删掉，不要留**（`PartnerScore.json` 不带版本，保留）。

写出 `PartnerId2Data_<ver>.json`、`PartnerId2SkillParam_<ver>.json`、`WeaponId2Data_<ver>.json`、`EquipId2Data_<ver>.json`。
角色详情有 3s sleep，大约数分钟。若 `PROP_NAME_TO_ID` KeyError，把 nanoka `base_property.name2` / `rand_property.name2` 补进 `data_to_map_by_nanoka.py` 后再跑。

**必须用现网数据**：别再改回用 `get_hakush_char_data` / `get_hakush_weapon_data`（它们带 `@cache_data`，只会拿磁盘快照）。
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

**`--rewrite-all` 不要盲目跑**：2026-10-19 实测它会改 43 个音擎 + 14 个驱动盘，里面既有真 bug（`crit` 小写、effect 混中文）也有**解析器回归**（例：`BreakStunAdd+50000`、`CritDmg+9000`、`DmgBonus+170`）。要重编先 `--dry-run` 看 diff，再逐条对着现网原文 review。
**默认的「只追加」不会更新已有条目**：游戏改了数值（例如 3.3 上线把「禁罪囚笼」从暴击 24% 改成 20%、把「涅槃初翎」精通 104/117/131/144 改成 99/108/117/126）时，脚本会因为名字已存在而跳过，**必须手工重编那几条**。

5. 新角色补 `utils/alias/char_alias.json`。同步 `AGENTS.md` 里写的当前版本号。

## 运行时到底读哪些字段

- `equip_effect`：运行时**只读 `normal_effect`**（`enka_to_mys.py::get_normal_equip_buff` 唯一调用点用默认值），`skill_effect` 目前无人读取。
- `weapon_effect`：`zzz_map.py` 载入但**没有任何运行时模块消费**，属于备用数据集。
- 消费方 `add_buff_props` 用 `float()` 解析数值，effect 里混中文（例 `异常精通+30点。`）会抛 `ValueError`；属性名大小写必须严格（`props['crit']` 与 `props['Crit']` 是两个键，小写会静默失效）。


## extend_data

- 音擎：键 = 中文名；`normal_effect` / `skill_effect` 各 `"1"`…`"5"`。
- 驱动盘：键 = 套装名；`desc1` = 2 件，`desc2` = 4 件。
- 详情用 `talents["1".."5"].desc` 和装备 `desc2`/`desc4`；中文名用详情 `name`。
- `energy-flat` / `daze` / `buildup` / `sheer` / 纯减伤 的 REVIEW 保持空串。
- 不要把中文写进 effect；必须 `Crit` 不是 `crit`。
- 没有新条目时脚本不改对应文件。

## 坑

- 先改 `version.py` 再跑 map：否则文件名还是旧后缀，插件加载的还是旧 map。
- map 没写完就跑 `hakush_resource`：`name_convert` 会找不到 `*_<ZZZero_version>.json`。
- 漏 `game_name="zzz"` 与这次无关，但别在同一任务里改绑定。
- `data_to_map_by_hakush.py` 不要用；nanoka 路径以 `data_to_map_by_nanoka.py` 为准。
- `char_alias.json` 的**键必须是 `PartnerId2Data` 里的短名**（`真斗`），不是全名（`狛野真斗`）。
  `alias_to_char_name` 命中后返回的是**键**，键不在 map 里 → `char_name_to_char_id` 返回 `None` → 查不到角色。
  全名要放进值列表里当别名。2026-10-19 修过一次这种回归（commit `20af0b7` 把键从 `真斗` 改成了 `狛野真斗`）。
- `INTEND_RES_PATH` 是 gitignore 的暂存区，且**子目录不会自动建**，跑 `hakush_resource.py` 前先手工建
  `weapon/ suit/ 3d_suit/ role/ role_circle/ role_general/ mind/ square_bangbo/`，否则 `img.save` 报 FileNotFoundError。
- 3D 套装（`3Dxxx.webp`）和部分角色冥想（`Mindscape_<id>_<t>.webp`）上游**就是 404**，脚本会打印失败并继续；
  插件实际用的 2D 套装（`xxx.webp`）能下全。别把这些当成整次失败。
- `utils/nanoka/urls.py::WIKI_DATA_VERSION` 单独锁版本，**不要**跟着 `NANOKA_DATA_VERSION` 动。
- nanoka 现网数据里 3.3 新角色的 `partner_info.full_name` 还是占位符 `...`，`data_to_map_by_nanoka.py` 用
  `FULL_NAME_OVERRIDE` 补成官方全名（赛维里安·洛威尔 / 菲欧妮·蕾法爱菈）——角色面板卡直接显示 `full_name`。
- **更新时必须删缓存**：`DATA_CACHE_PATH\get_hakush_char_data\` / `get_hakush_weapon_data\` 里的快照没有 TTL，
  会同时污染 map 生成**和运行时的伤害计算**。`data_to_map_by_nanoka.py` 已自动清理这两个目录。
- **旧版本 map json 要删掉**：`utils/map/` 只保留 `*_<ZZZero_version>.json`（`PartnerScore.json` 不带版本，保留）。
  留着旧版本既占仓库体积，又会让人误以为插件还在用旧数据。脚本生成完会自动删。
- 别用缓存里的旧快照判断「数据有没有变」：缓存是上线前的 beta 快照，会让你以为现网没变化。
  「重跑产物和上一版字节一致」有两种解释——上游真没变，**或者**两次都吃了同一份陈旧缓存。
  要下「上游没更新」的结论，先把缓存源和现网源做一次同 URL 对比。
