# -*- coding = utf-8 -*-
# @File:gacha.py
# @Author:Hycer_Lance
# @Time:2023/5/6 21:14
# @Software:PyCharm

import os
from colorama import Fore

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.log import logger

from ...Currency.utils import change_user_sj_num, sj_is_enough
from .utils import gacha, draw_img_ten, draw_img_single
from ...Utils.PluginInfo import PluginInfo
from ...Utils.CDManager import CDManager

"""
概率：
6* 2%
5* 8%
4* 50%
3* 40%
"""

single = on_command("单抽", aliases={"抽卡", "寻访"}, block=True, priority=3)
ten = on_command("十连", aliases={"十连抽", "十连寻访"}, block=True, priority=3)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_gacha",
    name="抽卡",
    description="方舟铁道抽卡",
    usage=(
        "抽卡",
        "十连"
    ),
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 3
    }
)

user_cd_manager = CDManager(10)

# 单抽
@single.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    if await user_cd_manager.is_in_cd(uid):
        remain_time = await user_cd_manager.get_remaining_time(uid)
        await single.finish(f"抽卡冷却中！\n剩余CD:{remain_time}s")
    if not await sj_is_enough(uid, num=600):
        await single.finish(MessageSegment.at(uid) + "你的合成玉余额不足600")

    logger.info("[Gacha]开始抽卡制图")
    oid_list = await gacha(uid)
    try:
        gacha_img = await draw_img_single(oid_list, uid)
        logger.info("[Gacha]抽卡制图完成")
    except IndexError:
        gacha_img = None
        logger.info(Fore.RED + "[Gacha]抽卡制图出错")
        await single.finish(MessageSegment.at(uid) + "请先发送/干员初始化你的数据")

    await single.send(MessageSegment.at(uid) + MessageSegment.image(file=gacha_img))
    await change_user_sj_num(uid, -600)
    await user_cd_manager.add_user(uid)
    os.remove(gacha_img)
    await single.finish()


# 十连
@ten.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    if await user_cd_manager.is_in_cd(uid):
        remain_time = await user_cd_manager.get_remaining_time(uid)
        await ten.finish(f"抽卡冷却中！\n剩余CD:{remain_time}s")
    if not await sj_is_enough(uid, num=6000):
        await ten.finish(MessageSegment.at(uid) + "你的合成玉余额不足6000")

    logger.info("[Gacha]开始抽卡制图")
    oid_list = await gacha(uid, True)
    try:
        gacha_img = await draw_img_ten(oid_list, uid)
        logger.info("[Gacha]抽卡制图完成")
    except IndexError:
        gacha_img = None
        logger.info(Fore.RED + "[Gacha]抽卡制图出错")
        await ten.finish(MessageSegment.at(uid) + "请先发送/干员初始化你的数据")
    await ten.send(MessageSegment.at(uid) + MessageSegment.image(file=gacha_img))
    await change_user_sj_num(uid, -6000)
    await user_cd_manager.add_user(uid)
    os.remove(gacha_img)
    await ten.finish()
