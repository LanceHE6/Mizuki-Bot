# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/14 15:28
# @Software:PyCharm

import os
import time
import requests
import json
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from ...Currency.utils import change_user_lmc_num
from ..gacha.pool_config import PoolConfig
from ..utils import get_op_img
import random
from ..DB import (
    add_user_pool_num,
    get_user_cur_pool_num,
    reset_user_cur_pool_num,
    get_op_attribute,
    get_ops_list_by_stars,
    OPAttribute,
    is_op_owned,
    add_op_to_user,
    add_op_to_user_db,
    get_user_ops_num_of_gacha,
    get_user_all_pool_num
    )

src_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src'
gacha_record_src_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'gacha' / 'src'
new_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'new.png'
profession_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'profession'
stars_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src' / 'stars'


async def gacha(uid, ten_type: bool = False) -> list:
    if ten_type:
        num = 10
    else:
        num = 1
    oid_list = []
    for i in range(0, num):
        flag = random.randint(0, 1001)
        now_pool_num = await get_user_cur_pool_num(uid)
        if now_pool_num > 50:
            prob_imp = (now_pool_num-PoolConfig.prob_improvement)*20
        else:
            prob_imp = 0
        if flag <= 20+prob_imp:
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
            await reset_user_cur_pool_num(uid)#重置保底数
        elif 20 + prob_imp < flag <= 100 + prob_imp:
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

        elif 100 + prob_imp< flag <= 600+ prob_imp:
            """4*"""
            oid_list.append(random.choice(await get_ops_list_by_stars(4)))
        else:
            """3*"""
            oid_list.append(random.choice(await get_ops_list_by_stars(3)))
        await add_user_pool_num(uid, 1)  # 记录抽数
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
        op_img_path =await get_op_img(int(oid))
        op_img = Image.open(op_img_path)
        profession = await get_op_attribute(oid, OPAttribute.profession)
        pro_img = Image.open(profession_img_path / f"{''.join(list(profession)[0:2])}.png")
        stars = await get_op_attribute(oid, OPAttribute.stars)
        stars_img = Image.open(stars_img_path / f'{stars}.png')

        image.paste(op_img, (172 + i * 200, 230))  # 干员
        os.remove(op_img_path)#删除临时干员图片文件
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
    op_img_path =await get_op_img(int(oid), is_big=1)
    op_img = Image.open(op_img_path)
    new_img = Image.open(new_img_path)
    profession = await get_op_attribute(oid, OPAttribute.profession)
    pro_img = Image.open(profession_img_path / f"{''.join(list(profession)[0:2])}_big.png")
    stars = await get_op_attribute(oid, OPAttribute.stars)
    name = await get_op_attribute(oid, OPAttribute.name)
    stars_img = Image.open(stars_img_path / f'{stars}_big.png')

    image.paste(op_img, (80, 10), mask=op_img)  # 干员
    os.remove(op_img_path)  # 删除临时干员图片文件
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

async def get_user_info(uid: int or str) -> list:
    """
    通过网络api获取用户的qq昵称以及头像
    :param uid: qq号
    :return: 包含用户昵称和头像本地地址的列表[nick_name, avatar_path]
    """
    headers = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0 Win64; x64)"
    }

    # # 获取用户qq头像地址及昵称    ——糖豆子api（暂时不能用）
    # qq_info_api = f"http://api.tangdouz.com/qq.php?qq={uid}"
    # qq_info = json.loads(requests.get(url=qq_info_api, headers=headers).content)
    # if qq_info["code"] != 1:
    #     await my_account.finish("获取用户信息失败，请稍后再试")
    # nick_name = qq_info["name"]
    # img_data = requests.get(qq_info["imgurl"]).content
    # with open(src_path/"user_avatar.png", 'wb') as data:
    #     data.write(img_data)
    #     data.close()

    # 获取用户qq头像地址及昵称备用api
    qq_info_api = f"https://api.usuuu.com/qq/{uid}"
    qq_info = json.loads(requests.get(url=qq_info_api, headers=headers).content)
    if qq_info["code"] != "200":
        return []
    nick_name = qq_info["data"]["name"]
    img_data = requests.get(qq_info["data"]["avatar"]).content
    with open(src_path / "user_avatar.png", 'wb') as data:
        data.write(img_data)
        data.close()

    return [nick_name, src_path / "user_avatar.png"]

async def circle_corner(img: Image, radii: int) -> Image:
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

async def transverse_text_center_locate(text: str, img_width: int or float, font_size: int):
    """
    定位字符串在图片中间的x坐标
    :param text: 字符串
    :param img_width: 图片宽度
    :param font_size: 字体大小
    :return: 字符串的x坐标
    """
    count = 0
    for char in text:
        if len(char) == 2:#判断中文
            count += 2
        else:
            count += 1
    return img_width/2-count/2*font_size/2

async def draw_gacha_record(uid: int or str) -> Path:
    """
    绘制抽卡记录分析
    :param uid: qq
    :return 图片本地地址
    """
    bg_img = Image.open(f"{gacha_record_src_path}/bg.png")

    img = Image.new("RGBA", bg_img.size)
    img.paste(bg_img, (0, 0))
    draw = ImageDraw.Draw(img)
    user_info =await get_user_info(uid)
    nick_name = user_info[0]
    avatar_path = user_info[1]
    avatar = await circle_corner(Image.open(avatar_path).resize((200, 200)), 100)
    img.paste(avatar, (688, 100), mask=avatar)
    font = ImageFont.truetype("simhei", 80)
    draw.text((await transverse_text_center_locate(nick_name, img.width, 80), 320), f"{nick_name}", font=font,
              fill='white')
    draw.text((450, 500), "总计抽数:", font=font, fill='white', stroke_fill='black', stroke_width=1)
    draw.text((450, 590), "总5星数:", font=font, fill='white', stroke_fill='black', stroke_width=1)
    draw.text((450, 670), "总6星数:", font=font, fill='white', stroke_fill='black', stroke_width=1)
    draw.text((450, 750), "5星出率:", font=font, fill='white', stroke_fill='black', stroke_width=1)
    draw.text((450, 830), "6星出率:", font=font, fill='white', stroke_fill='black', stroke_width=1)
    draw.text((450, 920), "已累计未出6星抽数:", font=font, fill='white', stroke_fill='black', stroke_width=1)

    total_num = await get_user_all_pool_num(uid)
    s5_num = await get_user_ops_num_of_gacha(uid, 5)
    s6_num = await get_user_ops_num_of_gacha(uid, 6)
    s5_radio = round(s5_num/total_num*100, 2)
    s6_radio = round(s6_num / total_num*100, 2)
    cur_num = await get_user_cur_pool_num(uid)
    draw.text((850, 500), f"{total_num}", font=font, fill='white')
    draw.text((850, 590), f"{s5_num}", font=font, fill=(254, 254, 58))
    draw.text((850, 670), f"{s6_num}", font=font, fill=(254, 163, 27))
    draw.text((850, 750), f"{s5_radio}%", font=font, fill=(254, 254, 58))
    draw.text((850, 830), f"{s6_radio}%", font=font, fill=(254, 163, 27))
    draw.text((1200, 920), f"{cur_num}", font=font, fill='white')
    os.remove(avatar_path)

    save_path = gacha_record_src_path / f'{uid}_recode.png'
    img.save(save_path)
    return save_path