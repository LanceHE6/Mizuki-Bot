# -*- coding = utf-8 -*-
# @File:draw_image.py
# @Author:Hycer_Lance
# @Time:2023/6/4 21:54
# @Software:PyCharm
import json

from PIL import Image, ImageFont, ImageDraw

from .playing_manager import PlayingManager
from pathlib import Path


res_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res'


async def draw_fight_image(pm: PlayingManager):
    player_skill_count = pm.player_skill_count  # 我方初始技力点
    enemy_skill_count = pm.enemy_skill_count
    all_list = pm.all_list
    all_ops_list = pm.all_ops_list
    all_enemies_list = pm.all_enemies_list

    bg_img = Image.open(res_path / "atk_places/1_f.png")  # 背景
    image = Image.new("RGBA", bg_img.size, (0, 0, 0))
    draw = ImageDraw.ImageDraw(image)
    image.paste(bg_img)

    oid = all_list[0].oid
    atk_type = all_list[0].atk_type_p
    skills = all_list[0].skills_list
    # 干员模型
    op_model_img = Image.open(res_path / f"op_models/{oid}_back.png")
    image.paste(op_model_img, (-50, -180), mask=op_model_img)

    # 怪物模型
    i = 0
    for enemy in all_enemies_list:
        eid = enemy.oid
        if i == 0:
            enemy_model_img = Image.open(res_path / f"enemies/{eid}.png").resize((240, 240))
            image.paste(enemy_model_img, (600, 210), mask=enemy_model_img)
        if i == 1:
            enemy_model_img = Image.open(res_path / f"enemies/{eid}.png").resize((300, 300))
            image.paste(enemy_model_img, (917, 127), mask=enemy_model_img)
        if i == 2:
            enemy_model_img = Image.open(res_path / f"enemies/{eid}.png").resize((240, 240))
            image.paste(enemy_model_img, (1031, 294), mask=enemy_model_img)
        if i == 3:
            enemy_model_img = Image.open(res_path / f"enemies/{eid}.png").resize((240, 240))
            image.paste(enemy_model_img, (1330, 282), mask=enemy_model_img)
        i += 1

    # speed_bar
    i = 0
    for obj in all_list:  # 应改为all_list 循环4次
        if i == 4:
            break
        oid = obj.oid
        movement_bg_img = Image.open(res_path / "atk_info/movement_bg.png")
        image.paste(movement_bg_img, (27, 5+i*89), mask=movement_bg_img)
        avatar_path = "op_heads" if obj in all_ops_list else "enemies"
        op_avatar = Image.open(res_path / avatar_path / f"{oid}.png").resize((90, 90))
        image.paste(op_avatar, (27, 5+i*89), mask=op_avatar)
        # 速度
        speed = obj.speed_p
        font = ImageFont.truetype("simhei", 14)
        draw.text((128, 80+i*89), f"{speed}", font=font)
        i += 1
    # status_bar
    i = 0
    for op in all_ops_list:
        oid = op.oid
        op_avatar = Image.open(res_path / f"op_heads/{oid}.png").resize((120, 120))
        image.paste(op_avatar, (26 + i * 224, 573), mask=op_avatar)
        # 满血条
        max_width = 197
        # 从左往右
        draw.rectangle((26+i*224, 693, max_width+26+i*224, 711), fill="#00ffff", outline="#757575", width=3)
        # 扣血条
        now_health = op.health
        max_health = op.max_health_p
        width = int(max_width*(max_health - now_health)/max_health)
        if width != 0:
            draw.rectangle((max_width + 26 + i * 224 - width, 696, 26 + i * 224 + max_width - 3, 708), fill="#252525")
        # 显示血量
        font = ImageFont.truetype("simhei", 14)
        draw.text((159 + i * 224, 676), f"{now_health}/{max_health}", font=font)
        i += 1

    # skills
    i = 0
    for skill in skills:  # 应改为当前干员skills 循环
        bg_img = Image.open(res_path / "atk_type/atk_bg.png").resize((150, 150))
        sid = skill.sid
        skill_img = Image.open(res_path / f"skills/{sid}_b.png")
        image.paste(bg_img, (1275 - i * 166, 596), mask=bg_img)
        image.paste(skill_img, (1287 - i * 166, 606), mask=skill_img)
        i += 1

    # 攻击图标

    atk_img = Image.open(res_path / f"atk_type/atk_bg_{atk_type}.png").resize((180, 180))
    image.paste(atk_img, (1464, 520), mask=atk_img)

    image.show()

