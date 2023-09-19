# -*- coding = utf-8 -*-
# @File:regular_check.py
# @Author:Hycer_Lance
# @Time:2023/5/30 17:12
# @Software:PyCharm

from nonebot_plugin_apscheduler import scheduler
from ..DB import agar_natural_recover
from nonebot.log import logger


@scheduler.scheduled_job("cron", minute="*/6")
async def recover():
    logger.info("[ArkRail_agar]检查琼脂")
    await agar_natural_recover()
