from gsuid_core.logger import logger
from gsuid_core.server import on_core_start

from ..zzzerouid_resource import startup


@on_core_start
async def all_start():
    try:
        await startup()
    except Exception as e:
        logger.exception(e)
