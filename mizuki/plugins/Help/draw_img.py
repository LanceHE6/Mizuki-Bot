# -*- coding = utf-8 -*-
# @File:draw_img.py
# @Author:Hycer_Lance
# @Time:2023/5/15 12:23
# @Software:PyCharm

from PIL import Image, ImageDraw, ImageFont
from ..Utils.PluginInfo import PluginsInfoList
from pathlib import Path
from nonebot import get_driver

bg_img_path = Path() / 'mizuki' / 'plugins' / 'Help' / 'res' / 'bg.png'
casual_img_path = Path() / 'mizuki' / 'plugins' / 'Help'

async def draw_help_img() -> Path:
    plugins_info_list = PluginsInfoList().plugins_list
    bg_img = Image.open(bg_img_path)
    img = Image.new("RGB", bg_img.size, (255, 255, 255))
    img.paste(bg_img, (0,0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("simhei", 64)
    draw.text((650, 100), "指令列表",font=font, fill='black')
    font = ImageFont.truetype("simhei", 32)
    draw.text((1150, 160), "[]为必填,<>为选填", font=font, fill='red')
    font = ImageFont.truetype("simhei", 24)
    draw.text((1150, 1120), "Create By Mizuki-bot", font=font, fill=(0, 162, 255))
    command_start = list(get_driver().config.command_start)[0]
    i = 0
    for plugin in plugins_info_list:
        x = 200
        base_y =180
        font_size = 32
        font = ImageFont.truetype("simhei", font_size)
        content = ''
        if isinstance(plugin.usage, list):#判断用法是否为列表
            for per in plugin.usage:
                if str(per).startswith("@"):#判断是否为@bot
                    content = per
                else:
                    content = command_start + per
                i += 1
        else:
            if str(plugin.usage).startswith("@"):  # 判断是否为@bot
                content = plugin.usage
            else:
                content = command_start + plugin.usage
            i += 1
        if "permission" in plugin.extra.keys() and plugin.extra["permission"] == "SUPERUSER":
            content += " (bot管理员)"

        if base_y + i * (font_size + 6) > 1080:#左边排满了往右边排
            x = 1000
            i = 0
        draw.text((x, base_y + i * (font_size + 6)), f"{content}", font=font, fill='white')

    save_path = casual_img_path / 'help.png'
    img.save(save_path)
    return save_path