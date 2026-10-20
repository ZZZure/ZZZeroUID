# 六、坑点与规范

> 返回 [SKILL.md](../SKILL.md)

## 规范

新代码：Core `AGENTS.md` §1。行宽 120。注释短。UID 只通过 `get_uid`。
本插件还没有 AI 桥接；加的时候 `to_ai` 第一行写「绝区零」，`covers`/`aliases` 带领域前缀。

## 坑

1. 漏 `game_name="zzz"` → 污染原神绑定。
2. `ZZZIgnoreAt` 命令遇到 `@` 会 **raise**，不是返回提示字符串。
3. `sv_get_mem` 变量名在 `mem` 与 `void` 各有一份，SV 中文名不同。
4. wiki 里多条 `pass`：不要对外声称「已支持角色图鉴」。
5. `pyrightconfig.json` 绝对路径 `F:/gsuid_core` 不可移植。
6. `pyproject.toml` 与 `ruff.toml` 行宽/引号冲突：以 `ruff.toml` 120 + double 为准。
7. 评分口径以官方接口为准，见 `docs/API与官方评分说明.md`。
8. 地图 JSON 文件名带版本；升 `ZZZero_version` 必须成套更新 `utils/map/`，**并删掉旧版本 json**（只留当前版本）。
9. `gsuid_core` 的 `cache_data` 缓存没有 TTL/数据版本键；重新生成数据前必须删 `DATA_CACHE_PATH\get_hakush_*`，
   否则会拿到上线前的 beta 快照（map 和运行时伤害计算都会中招）。详见 [zzzerouid-extend-data-update](../../zzzerouid-extend-data-update/SKILL.md)。

## 改完自查

- [ ] Bind 调用带 `ZZZ_GAME_NAME`
- [ ] 未绑定走 `BIND_UID_HINT`
- [ ] 新路径进 `RESOURCE_PATH.py`
- [ ] `ruff check ZZZeroUID`
