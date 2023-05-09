# -*- coding = utf-8 -*-
# @File:gacha.py
# @Author:Hycer_Lance
# @Time:2023/5/6 21:14
# @Software:PyCharm

import os
import time
from colorama import Fore
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.log import logger
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from .DB import get_op_attribute, get_ops_list_by_stars, OPAttribute, is_op_owned, add_op_to_user, add_op_to_user_db
from .DB import add_user_pool_num
from .pool_config import PoolConfig
from ..Currency.utils import change_user_sj_num, sj_is_enough, change_user_lmc_num
import random

"""
概率：
6* 2%
5* 8%
4* 50%
3* 40%
"""



op_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'ops_img'
new_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'new.png'
profession_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'profession'
stars_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'stars'

single = on_command("单抽", aliases={"抽卡", "寻访"}, block=True, priority=3)
ten = on_command("十连", aliases={"十连抽", "十连寻访"}, block=True, priority=3)


async def gacha(ten_type: bool = False) -> list:
    if ten_type:
        num = 10
    else:
        num = 1
    oid_list = []
    for i in range(0, num):
        flag = random.randint(0, 1001)
        if flag <= 20:
            """6*"""
            _6s_ops_list = await get_ops_list_by_stars(6)
            for up in PoolConfig.up_6s:
                _6s_ops_list.remove(f'{up}')
            up_flag = random.choice([0, 1])
            if up_flag == 1:
                oid_list.append(random.choice(PoolConfig.up_6s))
            else:
                if not _6s_ops_list:
                    oid_list.append(random.choice(PoolConfig.up_6s))
                else:
                    oid_list.append(random.choice(_6s_ops_list))

        elif flag <= 100:
            """5*"""
            _5s_ops_list = await get_ops_list_by_stars(5)
            for up in PoolConfig.up_5s:
                _5s_ops_list.remove(f'{up}')
            up_flag = random.choice([0, 1])
            if up_flag == 1:
                oid_list.append(random.choice(PoolConfig.up_5s))
            else:
                if not _5s_ops_list:
                    oid_list.append(random.choice(PoolConfig.up_5s))
                else:
                    oid_list.append(random.choice(_5s_ops_list))

        elif flag <= 600:
            """4*"""
            oid_list.append(random.choice(await get_ops_list_by_stars(4)))
        else:
            """3*"""
            oid_list.append(random.choice(await get_ops_list_by_stars(3)))
    return oid_list


# 绘制抽卡图片，返回图片地址
async def draw_img_ten(oid_list: list, uid: int or str) -> Path:
    bg_img = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'gacha_bg_ten.png'
    bg = Image.open(bg_img)  # bg
    image = Image.new('RGB', bg.size, (255, 0, 0))
    image.paste(bg, (0, 0))  # 创建新画板

    draw = ImageDraw.Draw(image)
    i = 0
    for oid in oid_list:
        op_img = Image.open(op_img_path / f"{oid}.png")
        profession = await get_op_attribute(oid, OPAttribute.profession)
        pro_img = Image.open(profession_img_path / f"{''.join(list(profession)[0:2])}.png")
        stars = await get_op_attribute(oid, OPAttribute.stars)
        stars_img = Image.open(stars_img_path / f'{stars}.png')

        image.paste(op_img, (172 + i * 200, 230))  # 干员
        flash_img = Image.open(stars_img_path / f'{stars}flash.png')
        image.paste(flash_img, (172 + i * 200, -10))  # 上光效
        if stars == 5 or stars == 6:
            await add_op_to_user_db(uid, oid, stars)  # 写入获取记录表中
        if not await is_op_owned(int(uid), int(oid)):  # new标识
            font = ImageFont.truetype('simhei', 48)
            draw.text((238 + i * 200, 180), "NEW", font=font, fill='red')
            await add_op_to_user(uid, oid)  # 写入数据库
        else:
            # 转换为龙门币
            await change_user_lmc_num(uid, PoolConfig.stars_values_lmc[f"{stars}"])
        image.paste(flash_img.rotate(180), (172 + i * 200, 630))  # 下光效
        image.paste(pro_img, (224 + i * 200, 600))  # 职业
        image.paste(stars_img, (185 + i * 200, 220), mask=stars_img)  # 星级
        i += 1

    # 文字样式（微软雅黑），可以自定义ttf格式文字样式
    font = ImageFont.truetype('simhei', 22)
    draw.text((2200, 730), f"{uid}", font=font)
    draw.text((2190, 750), f'{time.strftime("%m-%d %H:%M:%S", time.localtime())}', font=font)
    draw.text((2205, 770), "Create By", font=font, fill=(0, 162, 255))
    draw.text((2200, 790), "Mizuki-Bot", font=font, fill=(0, 162, 255))

    now_time = int(time.time())
    image.save(Path() / 'mizuki' / 'plugins' / 'ArkRail' / f'gacha_{now_time}.png')
    # image.show()
    return Path() / 'mizuki' / 'plugins' / 'ArkRail' / f'gacha_{now_time}.png'


async def draw_img_single(oid_list: list, uid: int or str) -> Path:
    bg_img = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'gacha_bg_single.png'
    bg = Image.open(bg_img)  # bg
    image = Image.new('RGB', bg.size, (255, 0, 0))
    image.paste(bg, (0, 0))  # 创建新画板

    draw = ImageDraw.Draw(image)
    oid = oid_list[0]
    op_img = Image.open(op_img_path / f"{oid}_big.png")
    new_img = Image.open(new_img_path)
    profession = await get_op_attribute(oid, OPAttribute.profession)
    pro_img = Image.open(profession_img_path / f"{''.join(list(profession)[0:2])}_big.png")
    stars = await get_op_attribute(oid, OPAttribute.stars)
    name = await get_op_attribute(oid, OPAttribute.name)
    stars_img = Image.open(stars_img_path / f'{stars}_big.png')

    image.paste(op_img, (80, 10), mask=op_img)  # 干员
    image.paste(stars_img, (160, 550), mask=stars_img)  # 星级
    image.paste(pro_img, (320, 750))  # 职业标志

    font = ImageFont.truetype('simsun', 100)
    draw.text((110, 790), f"{''.join(list(profession)[0:2])}", font=font, fill=(0, 0, 0), stroke_fill=(0, 0, 0), stroke_width=2)  # 职业文字
    font = ImageFont.truetype('simsun', 120)
    draw.text((460, 765), name, font=font, stroke_fill='gray', stroke_width=1)  # 干员名字
    if stars == 5 or stars == 6:
        await add_op_to_user_db(uid, oid, stars)  # 写入获取记录表中
    if not await is_op_owned(int(uid), int(oid)):  # new标识
        image.paste(new_img, (320, 886), mask=new_img)
        await add_op_to_user(uid, oid)

    else:
        # 转换为龙门币
        await change_user_lmc_num(uid, PoolConfig.stars_values_lmc[f"{stars}"])
    # 文字样式（微软雅黑），可以自定义ttf格式文字样式
    font = ImageFont.truetype('simhei', 22)
    draw.text((950, 990), f"{uid}", font=font)
    draw.text((940, 1010), f'{time.strftime("%m-%d %H:%M:%S", time.localtime())}', font=font)
    draw.text((955, 1030), "Create By", font=font, fill=(0, 162, 255))
    draw.text((950, 1050), "Mizuki-Bot", font=font, fill=(0, 162, 255))

    now_time = int(time.time())
    image.save(Path() / 'mizuki' / 'plugins' / 'ArkRail' / f'gacha_{now_time}.png')
    # image.show()
    return Path() / 'mizuki' / 'plugins' / 'ArkRail' / f'gacha_{now_time}.png'


# 单抽
@single.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    if not await sj_is_enough(uid, num=600):
        await single.finish(MessageSegment.at(uid) + "你的合成玉余额不足600")

    logger.info("[Gacha]开始抽卡制图")
    oid_list = await gacha()
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
    oid_list = await gacha(True)
    try:
        gacha_img = await draw_img_ten(oid_list, uid)
        logger.info("[Gacha]抽卡制图完成")
    except IndexError:
        gacha_img = None
        logger.info(Fore.RED + "[Gacha]抽卡制图出错")
        await ten.finish(MessageSegment.at(uid) + "请先发送/干员初始化你的数据")
    await ten.send(MessageSegment.at(uid) + MessageSegment.image(file=gacha_img))
    await change_user_sj_num(uid, -6000)
    await add_user_pool_num(uid, 10)  # 记录抽数
    os.remove(gacha_img)
    await ten.finish()
