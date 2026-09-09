# 一、架构与模块全景

> 返回 [SKILL.md](../SKILL.md)

嵌套加载：外层 `__nest__.py` + 内层 `__full__.py`。

```python
Plugins(
    name="ZZZeroUID",
    force_prefix=["zzz", "绝区零", "ZZZ"],
    allow_empty_prefix=False,
)
```

## 子包

| 子包 | 职责 |
|------|------|
| `zzzerouid_user` | 绑定/切换/删除 UID |
| `zzzerouid_roleinfo` | `查询` 角色总览图 |
| `zzzerouid_char_detail` | 角色面板、刷新、伤害、官方评分 |
| `zzzerouid_char_list` | 练度统计 |
| `zzzerouid_stamina` | 便签 / 电量 + 定时推送 |
| `zzzerouid_abyss` | 零号空洞 |
| `zzzerouid_challenge` | 式舆防卫战（深渊） |
| `zzzerouid_mem` | 危局强袭战 |
| `zzzerouid_void` | 临界推演 |
| `zzzerouid_gachalog` | 抽卡记录 |
| `zzzerouid_month_info` | 绳网月报 |
| `zzzerouid_wiki` | 攻略/图鉴（部分未实现） |
| `zzzerouid_webconsole` | Hub 插件页：全体用户抽卡 / 角色卡 + PIL 预览 |
| `zzzerouid_code` | 前瞻兑换码 |
| `zzzerouid_sign` | 米游社签到 |
| `zzzerouid_ann` | 公告清红 |
| `zzzerouid_config` | 用户开关 |
| `zzzerouid_help` | 帮助图 |
| `zzzerouid_resource` | 下载全部资源 |
| `zzzerouid_start` | `on_core_start` |
| `utils/` | API、Bind 封装、资源路径、别名、字体 |
| `tools/` | 从 hakush/nanoka 生成 map JSON |

`utils/api/api.py` 定义米游社 Record / Enka / MiniGG / 抽卡 URL。
`utils/hakush_api/` 图鉴资源。`utils/enka_to_mys.py` 面板结构转换。
