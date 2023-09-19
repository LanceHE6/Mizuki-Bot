# -*- coding = utf-8 -*-
# @File:token_verification.py
# @Author:Hycer_Lance
# @Time:2023/9/10 15:16
# @Software:PyCharm

from nonebot.log import logger
from nonebot import get_bot
from nonebot_plugin_apscheduler import scheduler

from .SKLand import SKLand
from .database import SKLandDB


@scheduler.scheduled_job("cron", hour="*/23")
async def _():
    logger.info("[SKLand_token_verification]开始检查token有效性")
    bot = get_bot()
    qid_list = await SKLandDB.find_tb_by_column(table_name="SKLand_User", column="qid")
    for qid in qid_list:
        skland = await SKLand().create_by_qid(qid)
        if not skland.token_verification():
            await bot.send_private_msg(user_id=int(qid), message="您的鹰角网络凭证(token)已过期，请留意")
    logger.info("[SKLand_token_verification]检查完成")
