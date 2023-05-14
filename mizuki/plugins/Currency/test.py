# -*- coding = utf-8 -*-
# @File:test.py
# @Author:Hycer_Lance
# @Time:2023/5/9 20:54
# @Software:PyCharm
import requests
import json
from PIL import Image, ImageDraw, ImageOps, ImageFont


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

    #创建一个alpha层，存放四个圆角，使用透明度切除圆角外的图片
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

bg_img = Image.open('src/bg.png').convert("RGBA")#背景图片
img = Image.new("RGBA", bg_img.size)#新建画板
box = Image.open("src/box.png")#内框
user_avatar = circle_corner(Image.open('src/qq.png').resize((200,200)), 100)#用户头像
lmc_img = Image.open("src/lmc.png").resize((200, 200))
sj_img = Image.open("src/sj.png").resize((200, 200))

img.paste(bg_img, (0, 0), mask=bg_img)
img.paste(box, (248, 180), mask=box)
img.paste(user_avatar, (400, 300), mask=user_avatar)
img.paste(lmc_img, (640, 540), mask=lmc_img)
img.paste(sj_img, (640, 840), mask=sj_img)

draw = ImageDraw.Draw(img)
draw_font = ImageFont.truetype("simhei", 80)

draw.text((640, 360), "Hycer", font= draw_font)#用户昵称

draw_font = ImageFont.truetype("simhei", 48)
draw.text((670, 750), "龙门币", font= draw_font)
draw.text((670, 1050), "合成玉", font= draw_font)

draw_font = ImageFont.truetype("simhei", 120)
draw.text((880, 600), "X  5000", font= draw_font, fill=(0, 179, 245))
draw.text((880, 900), "X  6000", font= draw_font, fill='red')

img.show()

