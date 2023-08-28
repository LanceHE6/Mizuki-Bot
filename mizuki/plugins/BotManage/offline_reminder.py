# -*- coding = utf-8 -*-
# @File:offline_reminder.py
# @Author:Hycer_Lance
# @Time:2023/8/24 15:25
# @Software:PyCharm

import yaml
import requests

from nonebot import get_driver, get_bots
from nonebot.log import logger

driver = get_driver()

@driver.on_bot_disconnect
async def _():
    """
    基于企业微信群bot的下线提醒
    :return:
    """
    bot_type_list = []
    bots = get_bots()
    for bid in bots:
        bot_type_list.append(bots[bid].type)
    # 只用当go-cqhttp下线时才会通知
    if "OneBot V11" not in bot_type_list:
        with open("mizuki/plugins/BotManage/config.yaml", "r", encoding="utf-8") as f:
            webhook = yaml.load(f.read(), Loader=yaml.FullLoader)["WeComWebhook"]
        data = {
            "msgtype": "text",
            "text": {
                "content": "您的bot已下线，请留意。"
            }
        }
        headers = {
            "Content-Type": "application/json"
        }
        logger.info("[BotManage]go-cqhttp连接断开，发送下线提醒")
        response = requests.post(url=webhook, headers=headers, json=data)
        if response.status_code == 200:
            logger.info("[BotManage]发送提醒成功")
        else:
            logger.info(f"[BotManage]提醒发送失败 response:{response.content}")
