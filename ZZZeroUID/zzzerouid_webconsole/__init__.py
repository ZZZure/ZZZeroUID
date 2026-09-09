"""ZZZeroUID Web 控制台页：抽卡记录 + 角色详情卡片。"""

from pathlib import Path

from gsuid_core.webconsole.plugin_page import register_plugin_page

WEB_DIR = Path(__file__).parent.parent / "web"

register_plugin_page(
    title="抽卡与角色管理",
    static_dir=WEB_DIR,
    page_id="console",
    description="管理全体用户的抽卡记录与角色详情卡片，并可预览与聊天中一致的 PIL 渲染图。",
    confirm_message="即将打开 ZZZeroUID 提供的抽卡与角色管理页面。确认后侧边栏会收起，页面以嵌入方式打开。",
    title_i18n={
        "zh-CN": "抽卡与角色管理",
        "en-US": "Gacha & Agents",
        "ja-JP": "ガチャとエージェント",
    },
    description_i18n={
        "zh-CN": "管理全体用户的抽卡记录与角色详情卡片，并可预览与聊天中一致的 PIL 渲染图。",
        "en-US": "Manage every player's gacha logs and agent cards, with PIL previews matching chat renders.",
        "ja-JP": "全ユーザーのガチャ記録とエージェント詳細を管理し、チャットと同じ PIL 画像をプレビューできます。",
    },
    confirm_message_i18n={
        "zh-CN": "即将打开 ZZZeroUID 提供的抽卡与角色管理页面。确认后侧边栏会收起，页面以嵌入方式打开。",
        "en-US": "Open the ZZZeroUID gacha and agent manager. The sidebar will collapse and the page will be embedded.",
        "ja-JP": "ZZZeroUID のガチャ／エージェント管理を開きます。サイドバーは折りたたまれ埋め込み表示されます。",
    },
    icon="layout-dashboard",
)

from . import api as _api  # noqa: E402, F401
