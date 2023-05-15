# -*- coding = utf-8 -*-
# @File:pool_config.json.py
# @Author:Hycer_Lance
# @Time:2023/5/8 20:08
# @Software:PyCharm

import json
import os
from ..DB import get_op_attribute, OPAttribute
from pathlib import Path
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message
from PIL import Image, ImageDraw, ImageFont
from ..utils import get_op_img
from ...Utils.PluginInfo import PluginInfo

config = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'pool_config.json'

change_up_6s_comm = on_command("修改up6星", aliases={"更改up6星", "up6星设置", "修改6星up"}, block=True, priority=3, permission=SUPERUSER)
change_up_5s_comm = on_command("修改up5星", aliases={"更改up5星", "up5星设置", "修改5星up"}, block=True, priority=3, permission=SUPERUSER)
pool_info = on_command("pool_info", aliases={"卡池信息", "卡池"}, block=True, priority=3)

__plugin_info__ = [PluginInfo(
    plugin_name="ArkRail_gacha_pool_info",
    name="卡池信息",
    description="查看当前卡池内容",
    usage="卡池信息 ——查看当前卡池内容",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 3
    }
), PluginInfo(
    plugin_name="ArkRail_gacha_pool_config",
    name="卡池配置",
    description="修改池子up干员",
    usage=("更改6星up",
           "更改5星up"),
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 3,
        "permission": "SUPERUSER"
    }
)]

# change_prob_improvement = on_command("")
class Pool:
    """卡池配置"""

    def __init__(self):
        with open(config, 'r', encoding='utf-8') as file:
            all_config = json.load(file)
            file.close()
        self.stars_values_lmc = all_config["stars_values_lmc"]
        self.up_6s: list = all_config["up_6s"]
        self.up_5s: list = all_config["up_5s"]
        self.prob_improvement = all_config["prob_improvement"]

    async def change_up_6s(self, new_up: list):
        """更改6星up"""
        self.up_6s = new_up
        with open(config, 'r', encoding='utf-8') as file:
            all_config = json.load(file)
            file.close()
        all_config["up_6s"] = self.up_6s
        with open(config, 'w', encoding='utf-8') as file:
            json.dump(all_config, file)

    async def change_up_5s(self, new_up: list):
        """更改5星up"""
        self.up_5s = new_up
        with open(config, 'r', encoding='utf-8') as file:
            all_config = json.load(file)
            file.close()
        all_config["up_5s"] = self.up_5s
        with open(config, 'w', encoding='utf-8') as file:
            json.dump(all_config, file)

    async def change_prob_improvement(self, new_times: int):
        """概率提升的抽数"""
        self.prob_improvement = new_times
        with open(config, 'r', encoding='utf-8') as file:
            all_config = json.load(file)
            file.close()
        all_config["prob_improvement"] = self.prob_improvement
        with open(config, 'w', encoding='utf-8') as file:
            json.dump(all_config, file)


PoolConfig = Pool()


async def draw_pool_info(up_6s: list, up_5s: list) -> Path:
    """
    绘制卡池信息图片
    :param up_6s: up6星列表
    :param up_5s: up5星列表
    :return: 图片地址
    """
    profession_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / 'profession'
    stars_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / 'stars'
    pool_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / 'gacha_pool'
    bg_img = Image.open(f"{pool_img_path}/bg.png").resize((1720, 1080))
    img = Image.new("RGBA", (1920, 1080), (255, 255, 255, 255))
    img.paste(bg_img, (100, 0))
    draw = ImageDraw.Draw(img)
    # 6星双up
    if len(up_6s) == 2:

        # 6星双up
        op_img = await get_op_img(up_6s[0], is_big=1)
        profession = await get_op_attribute(up_6s[0], OPAttribute.profession)
        name = await get_op_attribute(up_6s[0], OPAttribute.name)
        up_6s1_img = Image.open(op_img).resize((1536, 1536))
        stars_img = Image.open(f"{stars_img_path}/6.png").resize((350, 92))
        profession_img = Image.open(f"{profession_img_path}/{''.join(list(profession)[0:2])}.png").resize((80, 80))
        img.paste(up_6s1_img, (-350, -160), mask=up_6s1_img)  # 干员
        os.remove(op_img)
        img.paste(stars_img, (250, 500), mask=stars_img)  # 星级
        img.paste(profession_img, (260, 590))  # 职业
        font = ImageFont.truetype('simhei', 64)
        draw.text((350, 600), f"{name}", font=font, fill='white')  # 名字

        op_img = await get_op_img(up_6s[1], is_big=1)
        profession = await get_op_attribute(up_6s[1], OPAttribute.profession)
        name = await get_op_attribute(up_6s[1], OPAttribute.name)
        up_6s2_img = Image.open(op_img).resize((1536, 1536))
        profession_img = Image.open(f"{profession_img_path}/{''.join(list(profession)[0:2])}.png").resize((80, 80))
        img.paste(up_6s2_img, (800, -160), mask=up_6s2_img)
        os.remove(op_img)
        img.paste(stars_img, (1300, 500), mask=stars_img)  # 星级
        img.paste(profession_img, (1310, 590))  # 职业
        draw.text((1400, 600), f"{name}", font=font, fill='white')

        # 5星up
        i = 0
        for up in up_5s:
            op_img = await get_op_img(up)
            up_5s_img = Image.open(op_img).resize((150, 300))
            img.paste(up_5s_img, (715 + 160 * i, 650), mask=up_5s_img)  # 每个5星之间间隔10像素
            os.remove(op_img)
            i +=1
        stars_img = Image.open(f"{stars_img_path}/5.png").resize((350, 92))
        img.paste(stars_img, (750, 850), mask=stars_img)

        prob_up_img = Image.open(f"{pool_img_path}/prob_up.png").resize((1050, 150))
        img.paste(prob_up_img, (200, 900), mask=prob_up_img)
        save_path = pool_img_path / 'gacha_info.png'
        img.save(save_path)
        return save_path
    else:
        # 5星up
        op_img1 = await get_op_img(up_5s[0], is_big=1)
        op_img2 = await get_op_img(up_5s[1], is_big=1)
        op_img3 = await get_op_img(up_5s[2], is_big=1)
        up_5s1_img = Image.open(op_img1).resize((1024, 1024))
        up_5s2_img = Image.open(op_img2).resize((1024, 1024))
        up_5s3_img = Image.open(op_img3).resize((1024, 1024))
        profession1 = await get_op_attribute(up_5s[0], OPAttribute.profession)
        profession2 = await get_op_attribute(up_5s[1], OPAttribute.profession)
        profession3 = await get_op_attribute(up_5s[2], OPAttribute.profession)
        profession_img1 = Image.open(f"{profession_img_path}/{''.join(list(profession1)[0:2])}.png").resize((45, 45))
        profession_img2 = Image.open(f"{profession_img_path}/{''.join(list(profession2)[0:2])}.png").resize((45, 45))
        profession_img3 = Image.open(f"{profession_img_path}/{''.join(list(profession3)[0:2])}.png").resize((45, 45))
        op_name1 = await get_op_attribute(up_5s[0], OPAttribute.name)
        op_name2 = await get_op_attribute(up_5s[1], OPAttribute.name)
        op_name3 = await get_op_attribute(up_5s[2], OPAttribute.name)
        stars_img = Image.open(f"{stars_img_path}/5.png").resize((263, 69))

        img.paste(up_5s1_img, (750, -150), mask=up_5s1_img)
        img.paste(up_5s2_img, (1250, 0), mask=up_5s2_img)
        img.paste(up_5s3_img, (800, 450), mask=up_5s3_img)
        img.paste(stars_img, (1080, 200), mask=stars_img)
        img.paste(stars_img, (1625, 400), mask=stars_img)
        img.paste(stars_img, (1150, 850), mask=stars_img)
        img.paste(profession_img1, (1120, 270))
        img.paste(profession_img2, (1665, 470))
        img.paste(profession_img3, (1190, 920))

        font = ImageFont.truetype('simhei', 36)
        draw.text((1168, 273), f"{op_name1}", font=font, fill='white')
        draw.text((1713, 473), f"{op_name2}", font=font, fill='white')
        draw.text((1238, 923), f"{op_name3}", font=font, fill='white')
        # 6星up
        op_img = await get_op_img(up_6s[0], is_big=1)
        profession = await get_op_attribute(up_6s[0], OPAttribute.profession)
        name = await get_op_attribute(up_6s[0], OPAttribute.name)
        up_6s1_img = Image.open(op_img).resize((1536, 1536))
        stars_img = Image.open(f"{stars_img_path}/6.png").resize((350, 92))
        profession_img = Image.open(f"{profession_img_path}/{''.join(list(profession)[0:2])}.png").resize((80, 80))
        img.paste(up_6s1_img, (-350, -160), mask=up_6s1_img)  # 干员
        os.remove(op_img)
        img.paste(stars_img, (250, 500), mask=stars_img)  # 星级
        img.paste(profession_img, (260, 590))  # 职业
        font = ImageFont.truetype('simhei', 64)
        draw.text((350, 600), f"{name}", font=font, fill='white')  # 名字

        prob_up_img = Image.open(f"{pool_img_path}/prob_up.png").resize((1050, 150))
        img.paste(prob_up_img, (200, 800), mask=prob_up_img)
        save_path = pool_img_path / 'gacha_info.png'
        img.save(save_path)
        return save_path
@pool_info.handle()
async def _():
    logger.info("[pool_config]开始绘制卡池信息图片")
    await pool_info.send("开始绘制卡池信息，请稍等")
    try:
        img = await draw_pool_info(PoolConfig.up_6s, PoolConfig.up_5s)
        logger.info("[pool_config]卡池信息绘制完成")
        await pool_info.send(MessageSegment.image(img))
        os.remove(img)
    except TimeoutError as e:
        await pool_info.finish(f"卡池信息绘制出错:{e}\n请联系管理员")
    await pool_info.finish()

@change_up_6s_comm.handle()
async def _(args: Message = CommandArg()):
    """修改up6星 管理员发送的参数为up6星oid的列表"""
    try:
        up_list = eval(args.extract_plain_text().replace(' ', ''))  # 获取命令后面跟着的纯文本内容
        if len(up_list) > 2:
            await change_up_6s_comm.finish("超过最大up6星数量")
    except NameError:
        up_list = None
        await change_up_6s_comm.finish("非法指令格式，请在指令后跟up6星oid的列表")
    await PoolConfig.change_up_6s(up_list)
    reply = f"当前up6星已改为"
    for oid in up_list:
        name = await get_op_attribute(oid, OPAttribute.name)
        reply += ' ' + name
    await change_up_6s_comm.finish(reply)


@change_up_5s_comm.handle()
async def _(args: Message = CommandArg()):
    """修改up6星 管理员发送的参数为up5星oid的列表"""
    try:
        up_list = eval(args.extract_plain_text().replace(' ', ''))  # 获取命令后面跟着的纯文本内容
        if len(up_list) > 3:
            await change_up_6s_comm.finish("超过最大up5星数量")
    except NameError:
        up_list = None
        await change_up_5s_comm.finish("非法指令格式，请在指令后跟up5星oid的列表")
    await PoolConfig.change_up_5s(up_list)
    reply = f"当前up5星已改为"
    for oid in up_list:
        name = await get_op_attribute(oid, OPAttribute.name)
        reply += ' ' + name
    await change_up_5s_comm.finish(reply)


