# -*- coding = utf-8 -*-
# @File:draw_img.py
# @Author:Hycer_Lance
# @Time:2023/5/15 12:23
# @Software:PyCharm

from PIL import Image, ImageDraw, ImageFont
from ..Help.PluginInfo import PluginsInfoList
from pathlib import Path
from nonebot import get_driver

bg_img_path = Path() / 'mizuki' / 'plugins' / 'Help' / 'res' / 'bg.png'
mizuki_img_path = Path() / 'mizuki' / 'plugins' / 'Help' / 'res' / 'mizuki.png'
casual_img_path = Path() / 'mizuki' / 'plugins' / 'Help'
FONT = 'mizuki/plugins/Resource/GEETYPE.ttf'


async def draw_help_img(guild_command: bool = False) -> Path:
    """
    绘制help菜单图片
    :param guild_command: 是否为频道help菜单
    :return: 菜单图片Path
    """
    plugins_info_list = PluginsInfoList().plugins_list
    bg_img = Image.open(bg_img_path)
    mizuki_img = Image.open(mizuki_img_path)
    img = Image.new("RGB", bg_img.size, (255, 255, 255))
    img.paste(bg_img, (0, 0))
    img.paste(mizuki_img, (900, 700), mask=mizuki_img)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 64)
    draw.text((650, 100), "指令列表", font=font, fill='black')
    font = ImageFont.truetype(FONT, 32)
    draw.text((1150, 140), "<>为必填,[]为选填", font=font, fill='red')
    font = ImageFont.truetype(FONT, 24)
    draw.text((1150, 1120), "Create By Mizuki-bot", font=font, fill=(0, 162, 255))
    command_start = list(get_driver().config.command_start)[0]
    i = 0
    x = 200
    for plugin in plugins_info_list:
        base_y = 180
        font_size = 32
        font = ImageFont.truetype(FONT, font_size)
        if isinstance(plugin.usage, list):  # 判断用法是否为列表
            for per in plugin.usage:
                if str(per).startswith("@"):  # 判断是否为@bot
                    content = per
                else:
                    content = command_start + per
                if "permission" in plugin.extra.keys() and plugin.extra["permission"] == "SUPERUSER":
                    content += " (bot管理员)"
                # 只输出频道指令
                if not (guild_command and "guild_adapted" in plugin.extra.keys() and plugin.extra["guild_adapted"]):
                    continue
                draw.text((x, base_y + i * (font_size + 6)), f"{content}", font=font, fill='white')
                i += 1
        else:
            if str(plugin.usage).startswith("@"):  # 判断是否为@bot
                content = plugin.usage
            else:
                content = command_start + plugin.usage
            if "permission" in plugin.extra.keys() and plugin.extra["permission"] == "SUPERUSER":
                content += " (bot管理员)"
            if not guild_command:
                draw.text((x, base_y + i * (font_size + 6)), f"{content}", font=font, fill='white')
                i += 1
            else:
                if "guild_adapted" in plugin.extra.keys() and plugin.extra["guild_adapted"]:
                    draw.text((x, base_y + i * (font_size + 6)), f"{content}", font=font, fill='white')
                    i += 1
        if base_y + i * (font_size + 6) > 1080:  # 左边排满了往右边排
            x = 850
            i = 0

    save_path = casual_img_path / 'help.png'
    img.save(save_path)
    return save_path
