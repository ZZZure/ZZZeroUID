from gsuid_core.utils.api.mys.api import NEW_URL, OLD_URL

ZZZ_API = f'{NEW_URL}/event/game_record_zzz/api/zzz'
ZZZ_INDEX_API = f'{ZZZ_API}/index'
ZZZ_NOTE_API = f'{ZZZ_API}/note'
ZZZ_BUDDY_INFO_API = f'{ZZZ_API}/buddy/info'
ZZZ_AVATAR_BASIC_API = f'{ZZZ_API}/avatar/basic'
ZZZ_AVATAR_INFO_API = f'{ZZZ_API}/avatar/info'
ZZZ_CHALLENGE_API = f'{ZZZ_API}/challenge'

ZZZ_BIND_API = f'{OLD_URL}/binding/api'
ZZZ_GAME_INFO_API = f'{ZZZ_BIND_API}/getUserGameRolesByCookie?game_biz=nap_cn'


# Resource
ZZZ_RES = 'https://act-webstatic.mihoyo.com/game_record/zzz'
ZZZ_SQUARE_AVATAR = f'{ZZZ_RES}/role_square_avatar'
ZZZ_SQUARE_BANGBOO = f'{ZZZ_RES}/bangboo_rectangle_avatar'
