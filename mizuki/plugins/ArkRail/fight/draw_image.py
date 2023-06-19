# -*- coding = utf-8 -*-
# @File:draw_image.py
# @Author:Hycer_Lance
# @Time:2023/6/4 21:54
# @Software:PyCharm
import json

from PIL import Image, ImageFont, ImageDraw

from .playing_manager import PlayingManager, new_instance
from pathlib import Path

res_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res'


async def draw_player_fight_image(pm: PlayingManager, message_list, uid):
    """
    绘制战斗图像的方法(我方干员行动)

    :param pm: 战斗数据
    :param message_list: 消息(显示在图像下方)
    :param uid: 用户id
    """
    player_skill_count = pm.player_skill_count  # 我方初始技力点
    enemy_skill_count = pm.enemy_skill_count
    all_list = pm.all_list
    all_ops_list = pm.all_ops_list
    all_enemies_list = pm.all_enemies_list

    if all_list[0] not in all_ops_list:
        return

    bg_img = Image.open(res_path / "atk_places/1_f.png")  # 背景
    bg_img_size = bg_img.size  # 背景原尺寸
    message_str = ""  # 消息内容
    if message_list is not None:  # 获取消息内容列表并处理成字符串
        message_str = "\n".join(message_list)
        row = message_str.count("\n")
        bg_size = (bg_img_size[0], bg_img_size[1] + 32 * (row + 1))  # 背景尺寸根据消息内容的多少动态变化
    else:
        bg_size = bg_img_size
    image = Image.new("RGBA", bg_size, (127, 199, 255, 255))  # 背景颜色
    draw = ImageDraw.ImageDraw(image)
    image.paste(bg_img)

    oid = all_list[0].oid
    atk_type = all_list[0].atk_type_p
    skills = all_list[0].skills_list

    # 怪物模型
    i = 0
    for enemy in all_enemies_list:
        eid = enemy.oid

        # 确定敌人位置和大小
        if i == 0:
            point = (600, 210)
            size = (260, 260)
        elif i == 1:
            point = (917, 127)
            size = (300, 300)
        elif i == 2:
            point = (1031, 270)
            size = (280, 280)
        else:
            point = (1330, 282)
            size = (260, 260)

        if enemy.stars >= 7:
            size = (int(size[0] * 1.5), int(size[1] * 1.5))

        # 绘制敌人模型
        enemy_model_img = Image.open(res_path / f"enemies/{eid}.png").resize(size)
        image.paste(enemy_model_img, point, mask=enemy_model_img)

        # 获取血条坐标
        x = point[0] + 43
        y = point[1] + 270

        # 根据敌人是否是boss确定血条颜色和高度(长度是一样的)
        if enemy.stars < 5:  # 大于等于5星的敌人算作boss
            color = (218, 105, 54, 204)
            height = 10
        else:
            color = (220, 40, 40, 204)
            height = 12

            # 绘制boss图标
            boss_symbol_img = Image.open(res_path / "atk_info/boss.png").resize((38, 38))
            image.paste(boss_symbol_img, (x + 71, y - 13), mask=boss_symbol_img)

        # 满血条
        max_width = 180
        # 从左往右
        draw.rectangle((x, y, max_width + x, y + height), fill=color)
        # 扣血条
        now_health = enemy.health
        max_health = enemy.max_health_p
        width = int(max_width * (max_health - now_health) / max_health)
        if x + max_width - width < max_width + x:
            draw.rectangle((x + max_width - width, y, max_width + x, y + height), fill=(0, 0, 0, 100))

        alpha = 255  # 透明度
        j = 0
        for damage in enemy.damage_list:  # 绘制敌人受到的伤害/治疗(等于0的数值不绘制)
            font = ImageFont.truetype("simhei", 30)
            if damage > 0:
                damage_str = f"+{damage}"
                draw.text((x + 62, y - 250 - j * 32), f"{damage_str}", font=font, fill=(0, 255, 80, alpha))
                alpha -= 80
                j += 1
            elif damage < 0:
                damage_str = f"{damage}"
                draw.text((x + 62, y - 250 - j * 32), f"{damage_str}", font=font, fill=(255, 0, 0, alpha))
                alpha -= 80
                j += 1

        k = 0
        for e in enemy.effect_list:  # 绘制敌人效果
            k += 1
            if k >= 6:  # 只绘制前五个效果，超过5个效果加省略号
                font = ImageFont.truetype("simhei", 14)
                draw.text((x + 162, y + 14), "...", font=font)
                break
            e_bg_img = Image.open(res_path / "effects/effect_bg.png").resize((22, 22))
            e_id = e.effect_type
            effect_img = Image.open(res_path / f"effects/{e_id}.png").resize((20, 20))
            image.paste(e_bg_img, (x + (k - 1) * 27, y + 13), mask=e_bg_img)
            image.paste(effect_img, (x + 1 + (k - 1) * 27, y + 14), mask=effect_img)

            font = ImageFont.truetype("simhei", 10)  # 绘制持续回合
            persistence_str = int(e.persistence) if e.persistence >= 0 else "∞"  # 小于0的话持续时间无限
            draw.text((x - 2 + (k - 1) * 27, y + 29), f"{persistence_str}", font=font)

            if e.effect_level > 0:  # 绘制效果层数
                font = ImageFont.truetype("simhei", 14)
                draw.text((x + 17 + (k - 1) * 27, y + 26), f"{int(e.effect_level)}", font=font)

            if e.effect_degree != 0:  # 绘制效果箭头，用于判断是增益还是削弱
                arrow_str = "" if e.effect_degree > 0 else "de"
                e_arrow = Image.open(res_path / f"effects/{arrow_str}buff.png").resize((9, 11))
                image.paste(e_arrow, (x - 4 + (k - 1) * 27, y + 10), mask=e_arrow)
        i += 1

    # 干员模型
    op_model_img = Image.open(res_path / f"op_models/{oid}_back.png").resize((660, 660))
    image.paste(op_model_img, (130, 0), mask=op_model_img)

    # speed_bar
    i = 0
    for obj in all_list:  # 应改为all_list 循环5次
        if i == 5:
            break
        oid = obj.oid
        movement_bg_img = Image.open(res_path / "atk_info/movement_bg.png")
        image.paste(movement_bg_img, (27, 5 + i * 89), mask=movement_bg_img)
        avatar_path = "op_heads" if obj in all_ops_list else "enemies"
        head_size = (90, 90) if obj.stars < 7 else (135, 135)
        op_avatar = Image.open(res_path / avatar_path / f"{oid}.png").resize(head_size)
        image.paste(op_avatar, (32, 5 + i * 89), mask=op_avatar)
        # 速度
        speed = obj.speed
        font = ImageFont.truetype("simhei", 14)
        draw.text((128, 80 + i * 89), f"{speed}", font=font)
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
        draw.rectangle((26 + i * 224, 693, max_width + 26 + i * 224, 711), fill="#00ffff", outline="#757575", width=3)
        # 扣血条
        now_health = op.health
        max_health = op.max_health_p
        width = int(max_width * (max_health - now_health) / max_health)
        if max_width + 26 + i * 224 - width < 26 + i * 224 + max_width - 3:
            draw.rectangle((max_width + 26 + i * 224 - width, 696, 26 + i * 224 + max_width - 3, 708), fill="#252525")
        # 显示血量
        font = ImageFont.truetype("simhei", 14)
        draw.text((159 + i * 224, 676), f"{int(now_health)}/{int(max_health)}", font=font)

        alpha = 255  # 透明度
        j = 0
        for damage in op.damage_list:  # 绘制干员受到的伤害/治疗(等于0的数值不绘制)
            font = ImageFont.truetype("simhei", 36)
            if damage > 0:
                damage_str = f"+{damage}"
                draw.text((144 + i * 224, 633 - j * 35), f"{damage_str}", font=font, fill=(0, 255, 80, alpha))
                alpha -= 80
                j += 1
            elif damage < 0:
                damage_str = f"{damage}"
                draw.text((144 + i * 224, 633 - j * 35), f"{damage_str}", font=font, fill=(255, 0, 0, alpha))
                alpha -= 80
                j += 1

        k = 0
        for e in op.effect_list:  # 绘制效果
            k += 1
            if k >= 5:  # 只绘制前四个效果，超过4个效果加省略号
                font = ImageFont.truetype("simhei", 16)
                draw.text((206 + i * 224, 719), "...", font=font)
                break
            e_bg_img = Image.open(res_path / "effects/effect_bg.png").resize((40, 40))
            e_id = e.effect_type
            effect_img = Image.open(res_path / f"effects/{e_id}.png").resize((35, 35))
            image.paste(e_bg_img, (23 + (k - 1) * 47 + i * 224, 711), mask=e_bg_img)
            image.paste(effect_img, (25 + (k - 1) * 47 + i * 224, 713), mask=effect_img)

            font = ImageFont.truetype("simhei", 12)  # 绘制持续回合
            persistence_str = int(e.persistence) if e.persistence >= 0 else "∞"  # 小于0的话持续时间无限
            draw.text((21 + (k - 1) * 47 + i * 224, 742), f"{persistence_str}", font=font)

            if e.effect_level > 0:  # 绘制效果层数
                font = ImageFont.truetype("simhei", 18)
                draw.text((56 + (k - 1) * 47 + i * 224, 737), f"{int(e.effect_level)}", font=font)

            if e.effect_degree != 0:  # 绘制效果箭头，用于判断是增益还是削弱
                arrow_str = "" if e.effect_degree > 0 else "de"
                e_arrow = Image.open(res_path / f"effects/{arrow_str}buff.png").resize((16, 20))
                image.paste(e_arrow, (17 + (k - 1) * 47 + i * 224, 709), mask=e_arrow)
        i += 1

    # skills
    i = 0
    for skill in skills:  # 应改为当前干员skills 循环
        bg_img = Image.open(res_path / "atk_type/atk_bg.png").resize((150, 150))
        description_img = Image.open(res_path / "atk_type/atk_type_bg.png").resize((104, 24))
        sid = skill.sid
        skill_img = Image.open(res_path / f"skills/{sid}_b.png").resize((100, 100))
        image.paste(bg_img, (1275 - i * 166, 596), mask=bg_img)
        image.paste(skill_img, (1300 - i * 166, 620), mask=skill_img)
        image.paste(description_img, (1298 - i * 166, 718), mask=description_img)

        is_enough = "player" if pm.player_skill_count >= skill.consume else "enemy"
        consume_img = Image.open(res_path / f"atk_info/{is_enough}_skill_count.png").resize((10, 12))
        image.paste(consume_img, (1387 - i * 166, 724), mask=consume_img)

        if skill.obj_type in [1, 2, 3]:
            d_color = (245, 100, 100)
        elif skill.obj_type in [0, 4, 5, 6]:
            d_color = (0, 160, 255)
        else:
            d_color = (175, 100, 245)

        font = ImageFont.truetype("simhei", 16)
        draw.text((1310 - i * 166, 723), f"{skill.obj_type_str}", font=font, fill=d_color)

        font = ImageFont.truetype("simhei", 14)
        draw.text((1385 - i * 166, 736), f"{int(skill.consume)}", font=font, anchor="rs")

        i += 1

    player_skill_count_img = Image.open(res_path / "atk_info/player_skill_count.png")
    image.paste(player_skill_count_img, (1494, 13), mask=player_skill_count_img)
    enemy_skill_count_img = Image.open(res_path / "atk_info/enemy_skill_count.png")
    image.paste(enemy_skill_count_img, (1494, 80), mask=enemy_skill_count_img)
    font = ImageFont.truetype("simhei", 48)
    draw.text((1562, 23), f"{player_skill_count}", font=font)
    draw.text((1562, 92), f"{enemy_skill_count}", font=font)

    # 攻击图标
    atk_img = Image.open(res_path / f"atk_type/atk_bg_{atk_type}.png").resize((180, 180))
    image.paste(atk_img, (1464, 520), mask=atk_img)

    # 战斗信息
    if message_list is not None:
        font = ImageFont.truetype("simhei", 28)
        draw.text((8, 764), f"{message_str}", font=font, fill=(0, 0, 0))

    save_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res' / f'{uid}_play_info.png'
    image.save(save_path)
    # image.show()

    return save_path
