# -*- coding = utf-8 -*-
# @File:gacha.py
# @Author:Hycer_Lance
# @Time:2023/5/6 21:14
# @Software:PyCharm
import datetime
import time

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from .DB import get_op_attribute, get_ops_list_by_stars, OPAttribute
import random
"""
概率：
6* 2%
5* 8%
4* 50%
3* 40%
"""

bg_img = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'gacha_bg.png'
op_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'ops_img'

single = on_command("单抽", aliases={"抽卡","寻访"}, block=True, priority=3)
ten = on_command("十连", aliases={"十连抽","十连寻访"}, block=True, priority=3)

async def gacha(ten_type: bool = False)->list:
    if ten_type:
        num = 10
    else:
        num = 1
    oid_list = []
    for i in range(0, num):
        flag = random.randint(0, 1001)
        if flag <= 20:
            """6*"""
            oid_list.append(random.choice(await get_ops_list_by_stars(6)))
        elif flag <= 100:
            """5*"""
            oid_list.append(random.choice(await get_ops_list_by_stars(5)))
        elif flag <= 600:
            """4*"""
            oid_list.append(random.choice(await get_ops_list_by_stars(4)))
        else:
            """3*"""
            oid_list.append(random.choice(await get_ops_list_by_stars(3)))
    return oid_list

#绘制抽卡图片，返回图片地址
async def draw_img_ten(oid_list: list, uid: int or str)-> str:
    bg = Image.open(bg_img)
    image = Image.new('RGB', bg.size, (255, 0, 0))
    image.paste(bg, (0, 0))
    font = ImageFont.truetype('simhei', 32)
    draw = ImageDraw.Draw(image)
    i = 0
    for oid in oid_list:
        op_img = Image.open(op_img_path/f"{oid}.png")
        profession = await get_op_attribute(oid , OPAttribute.profession)
        stars = await get_op_attribute(oid, OPAttribute.stars)
        image.paste(op_img, (248 + i * 185, 80))
        draw.text((248 + i * 185, 420), profession, font=font, color=(102, 102, 256))
        i += 1

    # 文字样式（微软雅黑），可以自定义ttf格式文字样式
    font = ImageFont.truetype('simhei', 32)

    draw.text((2100, 430), f"{uid}", font=font)
    draw.text((2100, 460), f'{time.strftime("%m-%d %H:%M:%S",time.localtime())}', font=font)
    image.show()
#单抽
@single.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    oid_list = await gacha()

#十连
@ten.handle()
async def _(event: GroupMessageEvent):
    uid = event.get_user_id()
    oid_list = await gacha(True)


