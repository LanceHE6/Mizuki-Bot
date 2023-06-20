# -*- coding = utf-8 -*-
# @File:account.py
# @Author:Hycer_Lance
# @Time:2023/5/5 16:49
# @Software:PyCharm

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Bot

import os
from colorama import Fore
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from .utils import is_user_in_table, get_user_lmc_num, get_user_sj_num
from ..Utils.PluginInfo import PluginInfo
from ..Utils.QQ import QQ

src_path = Path() / 'mizuki' / 'plugins' / 'Currency' / 'res'
my_account = on_command("account", aliases={"我的账户", "账户"}, block=True, priority=2)

__plugin_info__ = PluginInfo(
    plugin_name="Currency_account",
    name="账户系统",
    description="显示用户货币数据",
    usage="account ——查看龙门币和合成玉数量",
    extra={
        "author": "Hycer_Lance",
        "version": "1.0.0",
        "priority": 2
    }
)


def circle_corner(img: Image, radii: int) -> Image:
    """
    将图片圆角化
    :param img: Image对象
    :param radii: 圆角度
    :return: 处理后的Image对象
    """
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建黑色方形
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 黑色方形内切白色圆形

    img = img.convert("RGBA")
    w, h = img.size

    # 创建一个alpha层，存放四个圆角，使用透明度切除圆角外的图片
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)),
                (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)),
                (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)),
                (0, h - radii))  # 左下角
    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见

    # 添加圆角边框
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(img.getbbox(), outline="black", width=3, radius=radii)
    return img


async def draw_img(uid: int, user_nick_name: str) -> Path:
    """
    绘制回复图片
    :param uid: 用户qq号
    :param user_nick_name: 用户昵称
    :return 绘制好的图片地址
    """
    # 获取头像
    qq = QQ(uid)
    avatar_path = await qq.get_avatar()

    lmc_num = await get_user_lmc_num(uid)
    sj_num = await get_user_sj_num(uid)
    bg_img = Image.open(src_path / 'bg.png').convert("RGBA")  # 背景图片
    img = Image.new("RGBA", bg_img.size)  # 新建画板
    box = Image.open(src_path / "box.png")  # 内框
    user_avatar = circle_corner(Image.open(avatar_path).resize((200, 200)), 100)  # 用户头像
    os.remove(avatar_path)  # 删除临时头像文件
    lmc_img = Image.open(src_path / "lmc.png").resize((300, 300))
    sj_img = Image.open(src_path / "sj.png").resize((300, 300))

    img.paste(bg_img, (0, 0), mask=bg_img)
    img.paste(box, (248, 180), mask=box)
    img.paste(user_avatar, (400, 300), mask=user_avatar)
    img.paste(lmc_img, (480, 520), mask=lmc_img)
    img.paste(sj_img, (480, 880), mask=sj_img)

    draw = ImageDraw.Draw(img)
    draw_font = ImageFont.truetype("simhei", 80)
    draw.text((640, 360), f"{user_nick_name}", font=draw_font)  # 用户昵称

    draw_font = ImageFont.truetype("simhei", 48)
    draw.text((560, 815), "龙门币", font=draw_font)
    draw.text((560, 1170), "合成玉", font=draw_font)

    draw_font = ImageFont.truetype("simhei", 120)
    draw.text((840, 620), f"X  {lmc_num}", font=draw_font, fill=(0, 179, 245))
    draw.text((840, 970), f"X  {sj_num}", font=draw_font, fill='red')
    draw_font = ImageFont.truetype("simhei", 36)
    draw.text((1210, 1220), "Create By Mizuki-Bot", font=draw_font, fill=(0, 162, 255))
    save_path = Path() / 'mizuki' / 'plugins' / 'Currency' / f'{uid}_account.png'
    img.save(save_path)
    return save_path


@my_account.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uid = int(event.get_user_id())
    user_info = await bot.get_stranger_info(user_id=uid)
    nickname = user_info["nickname"]
    # 用户首次使用指令，添加信息进数据库
    check = await is_user_in_table(uid)
    if not check:
        logger.info(Fore.BLUE + "[Currency_Account]新用户数据已添加")
    logger.info("[Currency]开始绘制账户信息图片")
    img = await draw_img(uid, nickname)
    logger.info("[Currency]账户信息图片绘制完成")
    await my_account.send(MessageSegment.at(uid) + MessageSegment.image(img))
    os.remove(img)
    await my_account.finish()
