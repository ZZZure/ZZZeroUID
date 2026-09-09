---
name: zzzerouid-development
description: >
  当用户要求"维护/开发 ZZZeroUID"、"绝区零插件怎么加命令"、"zzz绑定 UID"、
  "电量/便签/面板"、"式舆防卫战/零号空洞/危局/临界推演"、"抽卡记录"、
  "RefreshDataList ENKA/MINIGG/MYS"、"ZzzPush"、"攻略猫冬/听雨惊花"、
  "game_name=zzz"、"改 ZZZeroUID 有哪些坑"时触发此 SKILL。
  凡是改动 `gsuid_core/plugins/ZZZeroUID` 的任务都应优先读取此 SKILL。
---

# ZZZeroUID 插件开发与维护指南（核心入口）

> 源码是唯一事实源。按表打开**一篇** `references/`，不要一次读完。

## 谁该读

| 任务 | 文档 |
|------|------|
| 改本插件 | **本 SKILL** |
| 给本插件补 `to_ai` | 本 SKILL + Core `gscore-plugin-development` §10 / §18 |
| 代码红线 | [`AGENTS.md`](../../../AGENTS.md) + Core 根 `AGENTS.md` |

## 文档目录索引

| 章节 | 主题 | 链接 |
|------|------|------|
| 一 | 架构与模块 | [references/01-architecture-and-modules.md](./references/01-architecture-and-modules.md) |
| 二 | 命令与触发器 | [references/02-commands-and-triggers.md](./references/02-commands-and-triggers.md) |
| 三 | 绑定、API、面板数据 | [references/03-bind-api-and-data.md](./references/03-bind-api-and-data.md) |
| 四 | 渲染与资源 | [references/04-rendering-and-resources.md](./references/04-rendering-and-resources.md) |
| 五 | 配置、订阅、启动 | [references/05-config-lifecycle.md](./references/05-config-lifecycle.md) |
| 六 | 坑点与规范 | [references/06-pitfalls-and-conventions.md](./references/06-pitfalls-and-conventions.md) |
| 七 | Web 控制台页（抽卡 / 角色卡片 / PIL 预览） | [references/07-web-console.md](./references/07-web-console.md) |

## 关键概念速记

- 前缀 `zzz` / `绝区零` / `ZZZ`。
- `GsBind` **必须** `game_name="zzz"`。UID 正则 `\d{8,10}`。
- 面板刷新：`RefreshDataList` = ENKA / MINIGG / MYS。
- 尚无 AI 桥接；加的话优先 `to_ai` + `ai_return`。
- 若干 wiki 触发器函数体是 `pass`。
- 官方评分：`zzzerouid_char_detail/official_score.py` + `docs/API与官方评分说明.md`。
- Hub 插件页：`zzzerouid_webconsole` + `web/`，`register_plugin_page(page_id="console")`。预览走 PIL `draw_card` / `draw_char_detail_img`。
