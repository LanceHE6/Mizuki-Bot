# -*- coding = utf-8 -*-
# @File:show_info.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:52
# @Software:PyCharm
import asyncio

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.log import logger
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .DB import is_in_table, get_user_playing_ops, get_user_all_ops, get_oid_by_name, is_map_exist, get_map_attribute, \
    MapAttribute, get_op_attribute, OPAttribute, is_op_owned
from .operator import Operator, new_instance
from .utils import get_op_img, get_op_model, line_break
from ..Help.PluginInfo import PluginInfo
from ..Utils.GroupAndGuildMessageEvent import GroupAndGuildMessageEvent, GuildMessageEvent
from ..Utils.GroupAndGuildMessageSegment import GroupAndGuildMessageSegment
from ..GuildBinding.utils import get_uid_by_guild_id

op_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / 'op_images'
info_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / 'op_info'
stars_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / 'stars'
profession_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / 'profession'
skill_img_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / 'skills'
res_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res'

op_info = on_command("出战", aliases={"出战干员"}, block=True, priority=2)
op_info_all = on_command("ops", aliases={"所有角色", "所有干员", "info all", "我的干员", "干员"}, block=True, priority=2)
op_detail = on_command("detail", aliases={"d", "干员信息", "干员详情"}, block=True, priority=2)
map_info = on_command("level", aliases={"关卡", "关卡信息", "map"}, block=True, priority=2)

__plugin_info__ = [PluginInfo(
    plugin_name="ArkRail_show_op_info",
    name="出战干员信息展示",
    description="查看出战干员",
    usage="出战干员 ——查看出战干员",
    extra={
        "author": "Silence",
        "version": "0.1.0",
        "priority": 2,
        "guild_adapted": True
    }
    ),
    PluginInfo(
        plugin_name="ArkRail_show_all_op_info",
        name="所有干员信息展示",
        description="查看自身拥有的所有干员",
        usage="ops ——查看自身拥有的所有干员",
        extra={
            "author": "Silence",
            "version": "0.1.0",
            "priority": 2,
            "guild_adapted": True
        }
    ),
    PluginInfo(
        plugin_name="ArkRail_show_detail_info",
        name="干员详细信息展示",
        description="查看干员详细信息",
        usage="detail <干员名称> ——查看干员详细信息",
        extra={
            "author": "Silence",
            "version": "0.1.0",
            "priority": 2
        }
    ),
    PluginInfo(
        plugin_name="ArkRail_show_level_info",
        name="关卡信息展示",
        description="查看关卡信息",
        usage="level <关卡编号> ——查看关卡信息",
        extra={
            "author": "Silence",
            "version": "0.1.0",
            "priority": 2
        }
    )
]


@op_info.handle()
async def _(event: GroupAndGuildMessageEvent):
    if isinstance(event, GuildMessageEvent):
        uid = int(await get_uid_by_guild_id(event.get_user_id()))
        if uid == 0:
            await op_info.finish("您还没有在频道中绑定QQ账号！")
    else:
        uid = int(event.get_user_id())
    if not await is_in_table(uid):
        await op_info.send(GroupAndGuildMessageSegment.at(event) + "欢迎加入方舟铁道，您已获得新手礼包(包含4名强力干员)！")
    playing_ops = await get_user_playing_ops(uid)
    reply = GroupAndGuildMessageSegment.at(event) + "您的出战干员为："
    i = 1
    for op in playing_ops:
        oid = playing_ops[op]["oid"]
        level = playing_ops[op]["level"]
        name = await get_op_attribute(oid, OPAttribute.name)
        reply += f"\n{i}.{name}  等级：{level}"
        i += 1

    await op_info.finish(reply)


@op_info_all.handle()
async def _(event: GroupAndGuildMessageEvent):
    if isinstance(event, GuildMessageEvent):
        uid = int(await get_uid_by_guild_id(event.get_user_id()))
        if uid == 0:
            await op_info.finish("您还没有在频道中绑定QQ账号！")
    else:
        uid = int(event.get_user_id())
    if not await is_in_table(uid):
        await op_info_all.send(
            GroupAndGuildMessageSegment.at(event) + "欢迎加入方舟铁道，您已获得新手礼包(包含4名强力干员)！")
    all_ops = await get_user_all_ops(uid)

    img = Image.new("RGBA", (1080, (int(len(all_ops) / 8) + 1) * 240 + 50), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    i = 1
    basic_y = 50
    for op in all_ops:
        oid = all_ops[op]["oid"]
        level = all_ops[op]["level"]
        name = await get_op_attribute(oid, OPAttribute.name)
        profession = ''.join(list(await get_op_attribute(oid, OPAttribute.profession))[0:2])
        stars = await get_op_attribute(oid, OPAttribute.stars)

        op_img = Image.open(op_img_path / f"{oid}.png").resize((100, 200))
        x = (i - 1) * 120 + 70
        img.paste(op_img, (x, basic_y))
        # 名字
        if len(name) > 4:
            font = ImageFont.truetype("simhei", 16)
            name_bg = Image.new("RGB", (len(name) * 16, 18), (0, 0, 0))
        else:
            font = ImageFont.truetype("simhei", 20)
            name_bg = Image.new("RGB", (len(name) * 21, 22), (0, 0, 0))
        img.paste(name_bg, (x + 5, basic_y + 175))
        draw.text((x + 5, basic_y + 175), name, fill="white", font=font)

        # 等级
        level_img = Image.open(info_img_path / "level.png").resize((50, 50))
        img.paste(level_img, (x + 25, basic_y + 120), mask=level_img)
        font = ImageFont.truetype("simhei", 36)
        if len(str(level)) == 2:
            draw.text((x + 32, basic_y + 128), str(level), font=font, fill="white", stroke_fill="black", stroke_width=2)
        else:
            draw.text((x + 42, basic_y + 128), str(level), font=font, fill="white", stroke_fill="black", stroke_width=2)

        # 职业
        profession_img = Image.open(profession_img_path / f"{profession}_big.png"). resize((25, 25))
        img.paste(profession_img, (x + 5, basic_y + 5))

        # 星级
        stars_img = Image.open(stars_img_path / f"{stars}.png").resize((77, 21))
        if stars == 3:
            img.paste(stars_img, (x + 18, basic_y + 5), mask=stars_img)
        if stars == 4:
            img.paste(stars_img, (x + 20, basic_y + 5), mask=stars_img)
        if stars == 5:
            img.paste(stars_img, (x + 22, basic_y + 5), mask=stars_img)
        if stars == 6:
            img.paste(stars_img, (x + 25, basic_y + 5), mask=stars_img)

        if i % 8 == 0:
            basic_y += 240
            i = 0
        i += 1

    save_path = res_path / f"{uid}_ops.png"
    img.save(save_path)
    await op_info_all.send(GroupAndGuildMessageSegment.image(event, save_path), at_sender=True)
    os.remove(save_path)
    await op_info_all.finish()


@op_detail.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    uid = int(event.get_user_id())
    if not await is_in_table(uid):
        await op_info.send(GroupAndGuildMessageSegment.at(event) + "欢迎加入方舟铁道，您已获得新手礼包(包含4名强力干员)！")

    name = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容
    oid = await get_oid_by_name(name)
    if oid == -1:
        await op_detail.finish(GroupAndGuildMessageSegment.at(event) + f"没有名为{name}的干员")

    op: Operator
    if await is_op_owned(uid, oid):
        # 玩家拥有该干员
        tip = ''
        user_all_ops = await get_user_all_ops(uid)
        index = "1"
        for i in user_all_ops:
            if user_all_ops[i]["oid"] == oid:
                index = i
                break

        select_op = user_all_ops[index]
        oid = select_op["oid"]
        level = select_op["level"]
        skills_level = select_op["skills_level"]
        op = await new_instance(oid, level, skills_level)
    else:
        tip = '\n你未拥有该干员，以下为干员初始状态'
        level = 1
        op = await new_instance(oid, level, [0, 0, 0])
        # 玩家未拥有该干员
    await op_info.send("开始绘制干员信息图片，请稍等。。。")
    logger.info("[op_info]开始绘制干员信息图片")
    img_path = await draw_op_info_img(oid, level, op, uid)
    logger.info("[op_info]干员信息图片完成")
    await op_info.send(GroupAndGuildMessageSegment.at(event) + tip + GroupAndGuildMessageSegment.image(event, img_path))
    os.remove(img_path)
    await op_info.finish()


@map_info.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    uid = int(event.get_user_id())
    mid = args.extract_plain_text().replace(' ', '')  # 获取命令后面跟着的纯文本内容

    if not await is_map_exist(mid):
        await op_detail.finish(GroupAndGuildMessageSegment.at(event) + f"没有{mid}这张地图！")

    reply = GroupAndGuildMessageSegment.at(event) + f"{mid}\n敌人数据"
    enemies_data_list = await get_map_attribute(mid, MapAttribute.enemies)
    reward_list = await get_map_attribute(mid, MapAttribute.reward)
    consume = await get_map_attribute(mid, MapAttribute.consume)
    for i in range(len(enemies_data_list[0])):
        e_name = await get_op_attribute(enemies_data_list[0][i], OPAttribute.name, True)
        reply += f"\n{e_name}    等级：{enemies_data_list[1][i]}"
    reply += f"\n\n关卡报酬：\n{reward_list[0]}\n数量：{reward_list[1]}\n领取奖励所需琼脂：{consume}"

    await op_info_all.finish(reply)


async def draw_op_info_img(oid: int, level: int, op: Operator, uid: int or str) -> Path:
    bg_img = Image.open(f"{info_img_path}/bg.png")
    op_img_path = await get_op_img(oid, is_big=1)
    op_img = Image.open(op_img_path)
    max_health_img = Image.open(f"{info_img_path}/max_health.png")
    atk_img = Image.open(f"{info_img_path}/atk.png")
    def_img = Image.open(f"{info_img_path}/def.png")
    crit_d_img = Image.open(f"{info_img_path}/crit_d.png")
    crit_r_img = Image.open(f"{info_img_path}/crit_r.png")
    res_img = Image.open(f"{info_img_path}/res.png")
    speed_img = Image.open(f"{info_img_path}/speed.png")

    img = Image.new("RGBA", bg_img.size, (255, 255, 255, 0))  # 新建画板
    draw = ImageDraw.Draw(img)

    img.paste(bg_img, (0, 0))
    img.paste(op_img, (1450, 100), mask=op_img)
    level_img = Image.open(f"{info_img_path}/level.png")
    img.paste(level_img, (50, 200), mask=level_img)
    # 七种属性图标
    img.paste(max_health_img, (50, 520))
    img.paste(atk_img, (50, 580))
    img.paste(def_img, (50, 640))
    img.paste(res_img, (50, 700))
    img.paste(speed_img, (400, 520))
    img.paste(crit_r_img, (400, 580))
    img.paste(crit_d_img, (400, 640))
    # 属性值
    font = ImageFont.truetype("simhei", 100)
    if len(str(level)) == 2:  # 判断等级位数
        draw.text((95, 245), f"{level}", font=font, fill='white', stroke_fill='black', stroke_width=2)
    else:
        draw.text((120, 245), f"{level}", font=font, fill='white', stroke_fill='black', stroke_width=2)
    font = ImageFont.truetype("simhei", 50)
    draw.text((50, 460), "属性>>", font=font, fill='black')
    draw.text((250, 515), f"{op.max_health}", font=font, fill="black")  # max_health
    draw.text((250, 575), f"{op.atk}", font=font, fill="black")  # atk
    draw.text((250, 635), f"{op.defence}", font=font, fill="black")  # def
    draw.text((250, 695), f"{op.res}", font=font, fill="black")  # res
    draw.text((600, 515), f"{round(op.max_speed, 1)}", font=font, fill="black")  # speed
    draw.text((600, 575), f"{round(100 * op.crit_r, 1)}%", font=font, fill="black")  # crit_r
    draw.text((600, 635), f"{round(100 * op.crit_d, 1)}%", font=font, fill="black")  # crit_d

    # 干员模型
    box = Image.new("RGBA", (480, 395), (0, 0, 0, 150))
    op_model_path = await get_op_model(oid)
    op_model = Image.open(op_model_path).resize((500, 500))
    img.paste(box, (280, 105), mask=box)
    img.paste(op_model, (250, -50), mask=op_model)

    # 干员信息
    stars = await get_op_attribute(oid, OPAttribute.stars)
    stars_img = Image.open(f"{stars_img_path}/{stars}.png").resize((350, 92))  # 星级
    img.paste(stars_img, (40, 760), mask=stars_img)
    font = ImageFont.truetype("simhei", 150)
    draw.text((50, 860), f"{op.name}", font=font, fill='white', stroke_fill='black', stroke_width=2)  # name

    profession = ''.join(list(op.profession)[0:2])
    feature = ''.join(list(op.profession)[-2:])
    pro_img = Image.open(f"{profession_img_path}/{profession}_big.png")
    img.paste(pro_img, (50, 1020))
    font = ImageFont.truetype("simhei", 60)
    draw.text((240, 1020), f"{profession}", font=font, fill='white', stroke_fill='black', stroke_width=1)
    draw.text((240, 1090), f"{feature}", font=font, fill='white', stroke_fill='black', stroke_width=1)

    # 技能详情
    box = Image.open(f"{info_img_path}/box.png")
    img.paste(box, (650, 200), mask=box)

    draw.text((800, 220), "技能", font=font, fill='white', stroke_fill='black', stroke_width=1)
    draw.text((1180, 220), "描述", font=font, fill='white', stroke_fill='black', stroke_width=1)
    draw.text((1410, 220), "技力", font=font, fill='white', stroke_fill='black', stroke_width=1)

    op_skills_list = op.skills_list

    i = 0
    for skill in op_skills_list:
        font = ImageFont.truetype("simhei", 36)
        sid = skill.sid
        skill_img = Image.open(skill_img_path / f"{sid}.png").resize((120, 120))
        img.paste(skill_img, (810, 340 + i * 300), mask=skill_img)
        str_half_len = len(skill.name) if len(skill.name) < 5 else 5
        draw.text((870-(str_half_len/2)*36, 460 + i * 300), f"{skill.name}", font=font, fill='white', stroke_fill='black', stroke_width=2)
        font = ImageFont.truetype("simhei", 48)
        draw.text((940, 415 + i * 300), f"LV.{skill.level + 1}", font=font, fill="white")
        font = ImageFont.truetype("simhei", 30)
        skill_detail = await line_break(skill.detail, 10)
        draw.text((1100, 360 + i * 300), f"{skill_detail}", font=font, fill='white', stroke_fill='black',
                  stroke_width=2)
        font = ImageFont.truetype("simhei", 64)
        draw.text((1435, 380 + i * 300), f"{int(skill.consume)}", font=font, fill='white', stroke_fill='black',
                  stroke_width=2)
        i += 1
    save_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / f'{uid}_info.png'
    img.save(save_path)
    # img.show()
    return save_path
