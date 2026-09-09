# 七、Web 控制台页

> 返回 [SKILL.md](../SKILL.md)

`zzzerouid_webconsole` 在 import 时：

```python
register_plugin_page(..., page_id="console", static_dir=ZZZeroUID/web)
PluginAPI()  # /api/zzzerouid/...
```

Hub：`/plugins` → ZZZeroUID 标题右侧按钮 → 确认（可不再提示）→ iframe `/plugin-pages/zzzerouid/console/`。

| 路径 | 作用 |
|------|------|
| `GET /api/zzzerouid/players` | 扫描 `PLAYER_PATH` 下 UID 目录 |
| `GET /api/zzzerouid/players/{uid}/gacha` | `gacha_logs.json` |
| `GET /api/zzzerouid/players/{uid}/gacha/preview` | 调 `draw_card`，PNG |
| `GET /api/zzzerouid/players/{uid}/characters` | `####.json` 角色缓存 |
| `GET /api/zzzerouid/players/{uid}/characters/{id}/preview` | 调 `draw_char_detail_img`，PNG |
| `DELETE ...` | 只删本地 JSON 缓存 |

预览就是聊天里那套 PIL，不是 CSS 仿制。页面文案在 `web/locales/{zh-CN,en-US,ja-JP}.json`。

表面色跟随 Hub 亮暗：`web/app.css` 用 `hsl(var(--background))` 等 token；SDK 接收 `gshub:theme`。金/青强调色仅在 `html.dark` 下加亮。
