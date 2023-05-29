# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/5 12:32
# @Software:PyCharm

from pathlib import Path
import json

from colorama import Fore

from ...database.utils import MDB
from nonebot.log import logger
from sqlite3 import DatabaseError

aliases_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'aliases.json'
operators_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'operators_data.json'
skills_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'skills_data.json'
maps_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'maps_data.json'
enemies_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'enemies_data.json'
enemy_skills_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'enemy_skills_data.json'
'''
"1": {
   "1": {
    "name": "芬",
    "health": 2700,
    "health_plus": 15,
    "atk": 336,
    "atk_plus": 1,
    "def": 152,
    "def_plus": 2,
    "res": 0,
    "res_plus": 0,
    "crit_r": 0.1,
    "crit_r_plus": 0.001,
    "crit_d": 1.0,
    "crit_d_plus": 0.005,
    "speed": 110,
    "speed_plus": 0.1,
    "atk_type": 0,
    "skills": [1]
    
    "1": {
    "name": "冲锋号令",
    "brief_d": "立刻回复一定的技力点",
    "detail": "立即回复 15 + ⌊0.5 * 技能等级⌋ 技力点",
    "rate1": 15,
    "rate1_plus": 0.5,
    "rate2": 0,
    "rate2_plus": 0,
    "consume": 0,
    "consume_plus": 0,
    "persistence": 0,
    "persistence_plus": 0
'''


class OPAttributeNotFoundError(Exception):
    def __init__(self, error_attribute):
        self.error_attribute = error_attribute

    def __str__(self):
        print("未知干员属性:" + self.error_attribute)


class SkillAttributeNotFoundError(Exception):
    def __init__(self, error_attribute):
        self.error_attribute = error_attribute

    def __str__(self):
        print("未知技能属性:" + self.error_attribute)


class OPAttribute:  # 干员属性类
    name = 'name'
    stars = 'stars'
    profession = 'profession'
    health = 'health'
    health_plus = 'health_plus'
    atk = 'atk'
    atk_plus = 'atk_plus'
    res = 'res'
    res_plus = 'res_plus'
    defence = 'def'
    defence_plus = 'def_plus'
    crit_r = 'crit_r'
    crit_r_plus = 'crit_r_plus'
    crit_d = 'crit_d'
    crit_d_plus = 'crit_d_plus'
    speed = 'speed'
    speed_plus = 'speed_plus'
    atk_type = 'atk_type'
    skills = 'skills'


class SkillAttribute:  # 技能属性类
    name = "name"
    brief_d = "brief_d"
    detail = "detail"
    rate1 = "rate1"
    rate1_plus = "rate1_plus"
    rate2 = "rate2"
    rate2_plus = "rate2_plus"
    rate3 = "rate3"
    rate3_plus = "rate3_plus"
    obj_type = "obj_type"
    consume = "consume"
    consume_plus = "consume_plus"
    persistence = "persistence"
    persistence_plus = "persistence_plus"


class MapAttribute:  # 地图属性类
    enemies = "enemies"
    reward = "reward"


async def get_op_attribute(oid: str or int, attribute: str, is_enemy: bool = False) -> any:
    if attribute not in ["name", "health", "health_plus", "atk", "atk_plus", "def", "def_plus", "crit_r", "crit_r_plus",
                         "crit_d", "crit_d_plus", "speed", "speed_plus", "atk_type", "skills", "res", "res_plus",
                         "profession", "stars"]:
        raise OPAttributeNotFoundError(attribute)
    with open(operators_data if not is_enemy else enemies_data, 'r', encoding='utf-8') as data:
        ops_data = json.load(data)
        data.close()
    return ops_data[f"{oid}"][f"{attribute}"]


async def get_skill_attribute(sid: str or int, attribute: str, is_enemy: bool = False) -> any:
    if attribute not in ["name", "brief_d", "detail", "rate1", "rate1_plus", "rate2", "rate2_plus", "rate3", "rate3_plus",
                         "obj_type", "consume", "consume_plus", "persistence", "persistence_plus"]:
        raise SkillAttributeNotFoundError(attribute)
    with open(skills_data if not is_enemy else enemy_skills_data, 'r', encoding='utf-8') as data:
        ops_data = json.load(data)
        data.close()
    return ops_data[f"{sid}"][f"{attribute}"]


async def get_map_attribute(mid: str, attribute: str) -> any:
    if attribute not in ["enemies", "reward"]:
        raise SkillAttributeNotFoundError(attribute)
    with open(maps_data, 'r', encoding='utf-8') as data:
        m_data = json.load(data)
        data.close()
    e_data = m_data[f"{mid}"][f"{attribute}"]  # 关卡数据
    if attribute == "enemies":
        enemies_data_list: list[list[int]] = []  # 返回值,包含敌人id列表和敌人等级列表
        eid_list: list[int] = []  # 敌人id列表
        level_list: list[int] = []  # 敌人等级列表
        for n in e_data:
            eid_list.append(e_data[n]["eid"])
            level_list.append(e_data[n]["level"])
        enemies_data_list.append(eid_list)
        enemies_data_list.append(level_list)
        return enemies_data_list
    else:
        return [e_data["name"], e_data["amount"]]  # 返回值,包含报酬名称和报酬数量


async def get_user_level(uid: str or int) -> int:
    sql_sequence = f"Select level from ArkRail_User where uid={uid};"
    level = await MDB.db_query_single(sql_sequence)[0]
    return int(level)


async def get_user_all_ops(uid: str or int) -> dict:
    """
    获取用户所拥有的所有干员的字典
    :param uid: uid
    :return: 所拥有所有干员的字典
    """
    sql_sequence = f"Select operators_all from ArkRail_User where uid={uid};"
    ops = await MDB.db_query_single(sql_sequence)
    return eval(ops[0])


async def get_user_playing_ops(uid: str or int) -> dict:
    sql_sequence = f"Select operators_playing from ArkRail_User where uid={uid};"
    ops = await MDB.db_query_single(sql_sequence)
    return eval(ops[0])


async def is_in_table(uid: int) -> bool:
    uid_list = await MDB.db_query_single("select uid from ArkRail_User")
    if uid in uid_list:
        return True
    else:
        ops = {
            "1": {
                "oid": 1,
                "level": 1,
                "skills_level": [0, 0, 0]
            },
            "2": {
                "oid": 2,
                "level": 1,
                "skills_level": [0, 0, 0]
            },
            "3": {
                "oid": 3,
                "level": 1,
                "skills_level": [0, 0, 0]
            },
            "4": {
                "oid": 4,
                "level": 1,
                "skills_level": [0, 0, 0]
            }
        }
        # 初始化用户数据和抽卡数据和体力数据
        await MDB.db_execute(f'insert into ArkRail_User values({uid}, 1, "{ops}", "{ops}");')

        await MDB.db_execute(f'Insert Into ArkRail_GachaUser values ({uid},0,0,"[]","[]","[]","[]");')

        await MDB.db_execute(f'Insert Into ArkRail_AgarUser values ({uid},160,160,0,0);')
        return False


# 通过名字在所有干员数据中找oid,返回-1未找到
async def get_oid_by_name(name: str) -> int:
    """
    通过名字(别名)获取干员oid
    :param name: 名字(别名)
    :return: oid  -1为未找到
    """

    #先在别名中找
    with open(aliases_data, 'r', encoding='utf-8') as aliases_file:
        aliases_dict = json.load(aliases_file)
        aliases_file.close()
    for op_name in aliases_dict:
        if name in aliases_dict[op_name]:
            name = op_name#找到干员名字
    #在干员信息中查找oid
    with open(operators_data, 'r', encoding='utf-8') as data:
        ops_data = json.load(data)
        data.close()
    for oid in ops_data:
        if ops_data[f"{oid}"]["name"] == name:
            return int(oid)
    return -1


async def is_op_owned(uid: int or str, oid: int) -> bool:
    """
    通过oid判断用户是否拥有该干员
    :param uid: uid
    :param oid: oid
    :return: 布尔类型，True为拥有
    """
    user_ops = await get_user_all_ops(uid)
    for number in user_ops:
        if int(user_ops[number]["oid"]) == oid:
            return True
    return False


async def is_map_exist(mid: str) -> bool:
    with open(maps_data, 'r', encoding='utf-8') as data:
        m_data = json.load(data)
        data.close()
    for m in m_data:
        if m == mid:
            return True
    return False


# 获取指定星级的干员id列表
async def get_ops_list_by_stars(stars: int = 3 or 4 or 5 or 6) -> list:
    """
    获取指定星级的干员id列表
    :param stars: 星级
    :return: 干员oid列表
    """
    with open(operators_data, 'r', encoding='utf-8') as data:
        ops_data = json.load(data)
        data.close()
    ops_list = []
    for oid in ops_data:
        if int(ops_data[oid]["stars"]) == stars:
            ops_list.append(oid)
    return ops_list


async def add_op_to_user(uid: int or str, oid: int or str):
    uid = int(uid)
    oid = int(oid)
    owned_ops_list = await get_user_all_ops(uid)
    number = 1
    for _ in owned_ops_list:
        number += 1
    owned_ops_list[f"{number}"] = {
        "oid": oid,
        "level": 1,
        "skills_level": [0, 0, 0]
    }
    await MDB.db_execute(f'Update ArkRail_User set operators_all="{owned_ops_list}" Where uid="{uid}";')

async def change_user_op_level(uid: int or str, oid :int, target_level: int):
    """
    更改用户干员等级
    :param uid: qq
    :param oid: oid
    :param target_level: 目标等级
    :return: none
    """
    user_ops_list = await get_user_all_ops(uid)
    for op_no in user_ops_list:
        if user_ops_list[op_no]["oid"] == oid:
            user_ops_list[op_no]["level"] = target_level
    #判断该干员是否为出战干员
    user_playing_ops_list = await get_user_playing_ops(uid)
    for op_no in user_playing_ops_list:
        if user_playing_ops_list[op_no]["oid"] == oid:
            user_playing_ops_list[op_no]["level"] = target_level
            #同步更新出战干员的等级
            await MDB.db_execute(f'Update ArkRail_User set operators_playing="{user_playing_ops_list}" Where uid="{uid}";')
    await MDB.db_execute(f'Update ArkRail_User set operators_all="{user_ops_list}" Where uid="{uid}";')

async def change_user_op_skill_level(uid: int or str, oid :int, skill_number:int, target_level: int):
    """
    更改用户干员技能等级
    :param uid: qq
    :param oid: oid
    :param skill_number: 技能序号 0 1 2
    :param target_level: 目标等级
    :return: none
    """
    user_ops_list = await get_user_all_ops(uid)
    for op_no in user_ops_list:
        if user_ops_list[op_no]["oid"] == oid:
            user_ops_list[op_no]["skills_level"][skill_number] = target_level
    # 判断该干员是否为出战干员
    user_playing_ops_list = await get_user_playing_ops(uid)
    for op_no in user_playing_ops_list:
        if user_playing_ops_list[op_no]["oid"] == oid:
            user_playing_ops_list[op_no]["skills_level"][skill_number] = target_level
            # 同步更新出战干员的等级
            await MDB.db_execute(
                f'Update ArkRail_User set operators_playing="{user_playing_ops_list}" Where uid="{uid}";')
    await MDB.db_execute(f'Update ArkRail_User set operators_all="{user_ops_list}" Where uid="{uid}";')

async def change_user_playing_ops(uid: int or str, playing_oid_list: list):
    """
    更改用户出战干员
    :param uid: qq
    :param playing_oid_list: 出战干员oid列表
    :return:
    """

    all_ops = await get_user_all_ops(uid)
    i = 1
    new_playing_ops = {}
    for oid in playing_oid_list:
        for op_no in all_ops:
            if all_ops[op_no]["oid"] == oid:
                new_playing_ops[i] = all_ops[op_no]
                break
        i += 1
    await MDB.db_execute(f'Update ArkRail_User set operators_playing="{new_playing_ops}" Where uid="{uid}";')


async def get_user_all_pool_num(uid: int or str) -> int:
    """返回用户所有池子的抽数"""
    uid = int(uid)
    num = await MDB.db_query_single(f'Select all_pool_num From ArkRail_GachaUser Where uid="{uid}";')
    return int(num[0])


async def get_user_cur_pool_num(uid: int or str) -> int:
    """返回用户当前池子的抽数"""
    uid = int(uid)
    num = await MDB.db_query_single(f'Select cur_pool_num From ArkRail_GachaUser Where uid="{uid}";')
    return int(num[0])


async def get_user_all_pool_ops(uid: int or str, stars: int = 6 or 5) -> list:
    """返回用户所有池子抽到的6星或者5星的列表"""
    uid = int(uid)
    list_text = await MDB.db_query_single(f'Select all_pool_{stars}s From ArkRail_GachaUser Where uid="{uid}";')
    return eval(list_text[0])


async def get_user_cur_pool_ops(uid: int or str, stars: int = 6 or 5) -> list:
    """返回用户当前池子抽到的6星或者5星的列表"""
    uid = int(uid)
    list_text = await MDB.db_query_single(f'Select cur_pool_{stars}s From ArkRail_GachaUser Where uid="{uid}";')
    return eval(list_text[0])


async def add_op_to_user_db(uid: int or str, oid: int or str, stars: int = 6 or 5):
    """
    将6/5星干员id添加进用户的获取干员的数据库中
    :param uid
    :param oid 干员id
    :param stars 干员星级
    """
    uid = int(uid)
    oid = int(oid)
    stars = int(stars)
    owned_list_cur = await get_user_cur_pool_ops(uid, stars)
    owned_list_cur.append(oid)
    owned_list_all = await get_user_all_pool_ops(uid, stars)
    owned_list_all.append(oid)

    try:
        sql_sequence = f'Update ArkRail_GachaUser Set cur_pool_{stars}s="{owned_list_cur}" Where uid="{uid}";'
        await MDB.db_execute(sql_sequence)
        sql_sequence = f'Update ArkRail_GachaUser Set all_pool_{stars}s="{owned_list_all}" Where uid="{uid}";'
        await MDB.db_execute(sql_sequence)
        logger.info("[Gacha]获取记录添加进用户数据库")
    except DatabaseError as e:
        logger.info(Fore.RED + f"[Gacha]获取记录添加失败:{e}")


async def add_user_pool_num(uid: int or str, num: int):
    """用户获取记录增加num抽"""
    sql_sequence = f'Update ArkRail_GachaUser Set cur_pool_num=cur_pool_num+{num} Where uid="{uid}";'
    await MDB.db_execute(sql_sequence)
    sql_sequence = f'Update ArkRail_GachaUser Set all_pool_num=all_pool_num+{num} Where uid="{uid}";'
    await MDB.db_execute(sql_sequence)


async def reset_user_cur_pool_num(uid: int or str):
    """重置用户当前池子抽数-用于保底判断"""
    sql_sequence = f'Update ArkRail_GachaUser Set cur_pool_num=0 Where uid="{uid}";'
    await MDB.db_execute(sql_sequence)

async def get_user_ops_num_of_gacha(uid: int or str, stars: int =5 or 6) -> int:
    """获取用户抽卡获得的5星或6星干员总数"""
    ops_list = await get_user_all_pool_ops(uid, stars)
    return len(ops_list)