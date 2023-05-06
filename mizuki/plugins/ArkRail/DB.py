# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/5 12:32
# @Software:PyCharm

from pathlib import Path
import json
from ...database.utils import MDB

operators_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'operators_data.json'
skills_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'data' / 'skills_data.json'
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
    consume = "consume"
    consume_plus = "consume_plus"
    persistence = "persistence"
    persistence_plus = "persistence_plus"


async def get_op_attribute(oid: str or int, attribute: str) -> any:
    if attribute not in ["name", "health", "health_plus", "atk", "atk_plus", "def", "def_plus", "crit_r", "crit_r_plus",
                         "crit_d", "crit_d_plus", "speed", "speed_plus", "atk_type", "skills", "res", "res_plus", "profession", "stars"]:
        raise OPAttributeNotFoundError(attribute)
    with open(operators_data, 'r', encoding='utf-8') as data:
        ops_data = json.load(data)
        data.close()
    return ops_data[f"{oid}"][f"{attribute}"]


async def get_skill_attribute(sid: str or int, attribute: str) -> any:
    if attribute not in ["name", "brief_d", "detail", "rate1", "rate1_plus", "rate2", "rate2_plus", "consume",
                         "consume_plus", "persistence", "persistence_plus"]:
        raise SkillAttributeNotFoundError(attribute)
    with open(skills_data, 'r', encoding='utf-8') as data:
        ops_data = json.load(data)
        data.close()
    return ops_data[f"{sid}"][f"{attribute}"]


async def get_user_level(uid: str or int) -> int:
    sql_sequence = f"Select level from ArkRail_User where uid={uid};"
    level = await MDB.db_query_column(sql_sequence)[0]
    return int(level)


async def get_user_all_ops(uid: str or int) -> dict:
    sql_sequence = f"Select operators_all from ArkRail_User where uid={uid};"
    ops = await MDB.db_query_column(sql_sequence)
    return eval(ops[0])


async def get_user_playing_ops(uid: str or int) -> dict:
    sql_sequence = f"Select operators_playing from ArkRail_User where uid={uid};"
    ops = await MDB.db_query_column(sql_sequence)
    return eval(ops[0])


async def is_in_table(uid: int) -> bool:
    uid_list = await MDB.db_query_column("select uid from ArkRail_User")
    if uid in uid_list:
        return True
    else:
        ops = {
            "1": {
                "oid": 1,
                "level": 1,
                "skills_level": [0]
            },
            "2": {
                "oid": 2,
                "level": 1,
                "skills_level": [0]
            },
            "3": {
                "oid": 3,
                "level": 1,
                "skills_level": [0]
            },
            "4": {
                "oid": 4,
                "level": 1,
                "skills_level": [0]
            }
        }
        await MDB.db_execute(f'insert into ArkRail_User values({uid}, 1, "{ops}", "{ops}")')
        return False


# 通过名字在所有干员数据中找oid,返回-1未找到
async def get_oid_by_name(name: str) -> int:
    with open(operators_data, 'r', encoding='utf-8') as data:
        ops_data = json.load(data)
        data.close()
    for oid in ops_data:
        if ops_data[f"{oid}"]["name"] == name:
            return int(oid)
    return -1


async def is_op_owned(uid: int or str, oid: int) -> bool:
    user_ops = await get_user_all_ops(uid)
    for number in user_ops:
        if int(user_ops[number]["oid"]) == oid:
            return True
    return False

#获取指定星级的干员id列表
async def get_ops_list_by_stars(stars: int = 3 or 4 or 5 or 6)->list:
    with open(operators_data, 'r', encoding='utf-8') as data:
        ops_data = json.load(data)
        data.close()
    ops_list = []
    for oid in ops_data:
        if int(ops_data[oid]["stars"]) == stars:
            ops_list.append(oid)
    return ops_list