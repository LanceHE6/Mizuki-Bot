# -*- coding = utf-8 -*-
# @File:gacha_record.py
# @Author:Hycer_Lance
# @Time:2023/5/14 11:44
# @Software:PyCharm

import os
from colorama import Fore
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, Bot
from nonebot.log import logger
from pathlib import Path
from .utils import draw_gacha_record
from ...Utils.PluginInfo import PluginInfo

src_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'gacha' / 'res'

gacha_record = on_command("抽卡记录", aliases={"抽卡分析"}, block=True, priority=3)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_gacha_record",
    name="抽卡记录分析",
    description="查看方舟铁道的抽卡分析",
    usage="抽卡记录 ——查看方舟铁道的抽卡分析",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 3
    }
)

@gacha_record.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uid = event.get_user_id()
    user_info = await bot.get_stranger_info(user_id=int(uid))
    nickname = user_info["nickname"]
    logger.info(f"[gacha_recode]开始绘制用户{uid}的抽卡记录")
    try:
        img_path = await draw_gacha_record(uid, nickname)
        logger.info(f"[gacha_recode]用户{uid}的抽卡记录绘制成功")
    except IndexError:
        img_path = None
        logger.info(Fore.RED+f"[gacha_recode]用户{uid}的抽卡记录绘制失败")
        await gacha_record.finish(MessageSegment.at(uid)+"抽卡记录绘制出错，请联系管理员")
    await gacha_record.send(MessageSegment.at(uid)+MessageSegment.image(img_path))
    os.remove(img_path)
    await gacha_record.finish()
