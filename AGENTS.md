# AGENTS.md

> 本文件遵循 [AGENTS.md](https://agents.md/)：给编码 Agent 的仓库说明（README for agents）。
> 人类用户说明见 [README.md](./README.md)。**源码是唯一事实源**。
>
> 模块 / 面板 / Bind：按需读
> [`.agents/skills/zzzerouid-development/SKILL.md`](.agents/skills/zzzerouid-development/SKILL.md)，
> **不要**一次把所有 `references/` 塞进上下文。

本仓库是 **GsCore 业务插件**，独立 git。放到 `gsuid_core/plugins/ZZZeroUID/` 安装。插件开发文档把它当作嵌套加载参考之一。

## Project overview

绝区零查询：UID、电量便签、角色面板、式舆防卫战 / 零号空洞 / 危局强袭战 / 临界推演、抽卡、签到、攻略图。

- `Plugins(name="ZZZeroUID", force_prefix=["zzz", "绝区零", "ZZZ"], allow_empty_prefix=False)`。
- UID：框架 **`GsBind`**，必须 **`game_name="zzz"`**（`ZZZ_GAME_NAME`）。不要用原神默认槽。
- Cookie：框架 `GsUser`。刷新顺序配置 `RefreshDataList`：`ENKA` → `MINIGG` → `MYS`。
- **没有** `to_ai` / `@ai_tools` / `ai_return`。接 AI 走 Core 插件技能 §10 / §18，不要先堆 `@ai_tools`。
- 版本：`ZZZeroUID/version.py` 的 `ZZeroUID_version` / `ZZZero_version`（当前 `3.1.0`，与 `utils/map/*_3.1.0.json` 对齐）。`pyproject.toml` 的 `[project]` / poetry 可能滞后。

## Repository map

```
.
├── AGENTS.md / README.md / LICENSE / ICON.png
├── pyproject.toml / ruff.toml / pyrightconfig.json
├── __init__.py / __nest__.py
├── docs/                               # API与官方评分说明.md
├── test/                               # HAR / 评分脚本（不是完整 pytest）
├── .agents/skills/zzzerouid-development/
└── ZZZeroUID/
    ├── __init__.py                     # 仅 Plugins(...)
    ├── __full__.py / version.py
    ├── zzzerouid_*/                    # 功能子包（下表）
    ├── utils/                          # api / hakush_api / database / resource / alias
    └── tools/                          # 地图生成 + INTEND_RES_PATH 图标
```

| 子包 | 职责 |
|------|------|
| `zzzerouid_user` | 绑定/切换/删除 UID |
| `zzzerouid_roleinfo` | `查询` 总览 |
| `zzzerouid_char_detail` | 角色面板、刷新、伤害、`official_score.py` |
| `zzzerouid_char_list` | 练度统计 |
| `zzzerouid_stamina` | 便签 / 电量推送 |
| `zzzerouid_abyss` | 零号空洞 |
| `zzzerouid_challenge` | 式舆防卫战 |
| `zzzerouid_mem` | 危局强袭战 |
| `zzzerouid_void` | 临界推演 |
| `zzzerouid_gachalog` | 抽卡记录 |
| `zzzerouid_month_info` | 绳网月报 |
| `zzzerouid_wiki` | 攻略/图鉴（若干函数体 `pass`） |
| `zzzerouid_code` / `_sign` / `_ann` | 兑换码、签到、清红 |
| `zzzerouid_config` / `_help` / `_resource` / `_start` | 配置、帮助、下载、启动 |
| `zzzerouid_webconsole` + `web/` | Hub 插件页：全体用户抽卡 / 角色卡 + PIL 预览 |

`utils/database/model.py`：`ZzzPush`（电量阈值）。UID 仍在 `GsBind`。

## Skills

| 任务 | 读 |
|------|-----|
| 本插件 | [zzzerouid-development](.agents/skills/zzzerouid-development/SKILL.md) |
| 补 `to_ai` | Core [gscore-plugin-development](../../../.agents/skills/gscore-plugin-development/SKILL.md) §10 / §18 |
| 代码红线 | Core 根 [`AGENTS.md`](../../../AGENTS.md) §1–§4、§1.9 |

单独 clone 时打开宿主 Core 的 `AGENTS.md`。

## Setup commands

在**本插件目录**执行。解释器指向 Core 根 `.venv`。

```sh
uv run ruff check ZZZeroUID
uv run ruff format --check ZZZeroUID
```

`ruff.toml`：`line-length = 120`。以它为准；不要跟 `pyproject.toml` 里遗留 black 79 / 单引号走。
`pyrightconfig.json` 写死了 `F:/gsuid_core` 的 `venvPath`——换机器会坏。改配置用相对 `extraPaths`。
`test/` 主要是 HAR 与 `verify_official_score.py`，不是 `pytest tests/`。

## Code style

新代码与 Core 根 `AGENTS.md` **编号一致**，正反例以那份为准。

| 编号 | 要求 |
|------|------|
| §1.1 | 禁止 try-except 兜底。例外：米游社/Enka JSON；资源下载失败打日志 |
| §1.2–1.4 | 禁止 `cast` / 自身 `type: ignore` / `getattr`·`dict.get` 兜底 |
| §1.6 | `#` 最多两行、每行 ≤88 字 |
| §1.7 | 不改 Core `system_prompt` |
| §1.8 | 禁止 `Any` |
| §1.9 | 绝区零垂直词只写本插件；接 AI 时 `covers` / `aliases` 带「绝区零·」前缀 |
| §2 | 函数全标注；PEP 604 |
| §3 | `ZzzPush`：无 `__tablename__`，`@with_session`，`col()`。UID 用 `GsBind` + `game_name="zzz"` |
| §4 | 全异步 |

行宽 120。UID 只通过 `utils/uid.py::get_uid`。未绑定用 `utils/hint.py::BIND_UID_HINT`。错误码 `hint.error_reply`。
`ZZZIgnoreAt`：改命令名要同步配置默认列表。历史代码脏则**改到哪修到哪**。

## Testing

- 改驱动盘 / 角色评分：先读 `docs/API与官方评分说明.md` 和 `test/verify_official_score.py`，再动 `official_score.py`。
- 不要提交真人 Cookie 或 HAR 里的敏感头。

## 本仓库结构约定

- 嵌套加载：`__nest__.py` + `__full__.py`。内层 `__init__.py` 不要手工 import 子包。
- `get_uid` 正则 `\d{8,10}`。命令在 `ZZZIgnoreAt` 且存在 `ev.at` 时 **raise Exception**（会先 `bot.send`）。
- 订阅：`gs_subscribe`，任务名 `[绝区零] 推送` / `体力` / `自动签到` / `自动清红`。
- 攻略：`ZZZGuideProvide` = `猫冬` \| `听雨惊花`。wiki 里角色图鉴 / 音擎 / 驱动盘 / 武器 / 邦布 / 突破材料目前是 `pass`。
- 路径：`utils/resource/RESOURCE_PATH.py`。别名：`utils/alias/char_alias.json`。

## 坑点

1. 漏 `game_name="zzz"` → 写进原神 UID 槽。
2. 禁止 `@` 的命令不要把 raise 当 `None`。
3. `zzzerouid_mem` 与 `zzzerouid_void` 都用过局部名 `sv_get_mem`，SV 中文名不同。
4. 发版对齐 `version.py` 与 `utils/map/` 后缀。
5. `WidgetResin` 开了电量可能不准。

## Security notes

- Cookie 禁止进 git、禁止日志全文。
- `pm=2` 下载资源、`pm=1` 强制推送 / 全部重签。
- 公网 Core：`WS_TOKEN`。
