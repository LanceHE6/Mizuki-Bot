# -*- coding = utf-8 -*-
# @File:draw_gacha.py
# @Author:Hycer_Lance
# @Time:2023/5/6 21:14
# @Software:PyCharm

import os
from colorama import Fore
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.log import logger
from ..DB import add_user_pool_num
from ...Currency.utils import change_user_sj_num, sj_is_enough
from .utils import gacha, draw_img_ten, draw_img_single

"""
概率：
6* 2%
5* 8%
4* 50%
3* 40%
"""

single = on_command("单抽", aliases={"抽卡", "寻访"}, block=True, priority=3)
ten = on_command("十连", aliases={"十连抽", "十连寻访"}, block=True, priority=3)

# 单抽
@single.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
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
    await add_user_pool_num(uid, 1)  # 记录抽数
    os.remove(gacha_img)
    await single.finish()


# 十连
@ten.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
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

    os.remove(gacha_img)
    await ten.finish()
