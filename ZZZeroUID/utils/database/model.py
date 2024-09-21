from typing import Optional

from sqlmodel import Field
from gsuid_core.webconsole import site
from gsuid_core.utils.database.base_models import Push
from gsuid_core.webconsole.mount_app import GsAdminModel
from fastapi_amis_admin.amis.components import PageSchema


class ZzzPush(Push, table=True):
    __table_args__ = {'extend_existing': True}
    bot_id: str = Field(title='平台')
    zzz_uid: str = Field(default=None, title='绝区零UID')

    energy_push: Optional[str] = Field(
        title='绝区零体力推送',
        default='off',
        schema_extra={'json_schema_extra': {'hint': 'zzz开启体力推送'}},
    )
    energy_value: Optional[int] = Field(title='电量阈值', default=180)
    energy_is_push: Optional[str] = Field(
        title='电量是否已推送', default='off'
    )


@site.register_admin
class ZzzPushAdmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='绝区零推送管理',
        icon='fa fa-bullhorn',
    )  # type: ignore

    # 配置管理模型
    model = ZzzPush
