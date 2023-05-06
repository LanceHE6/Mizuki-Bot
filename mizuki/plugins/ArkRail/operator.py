# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm

from pathlib import Path
from .DB import get_user_playing_ops, get_op_attribute, OPAttribute
from skill import get_skills_list
from skill import Skill

user_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'user_data.json'

"""
数据库玩家表示例
uid:str         level:int           operators_all                               operators_playing
  123               10           {2:{level:10,skills:{1,2,3}},...}             {2:{level:10,skills:{1,2,3}},...} 
"""


class Operator:

    def __init__(self, name: str, level: int, health: int, atk: int,
                 defence: int, res: float, crit_r: float, crit_d: float, speed: float,
                 atk_type: int, skills_list: list[Skill]):
        self.name = name
        self.level = level
        self.health = health
        self.atk = atk
        self.defence = defence
        self.res = res
        self.crit_r = crit_r
        self.crit_d = crit_d
        self.speed = speed
        self.atk_type = atk_type
        self.skills_list = skills_list


async def new_instance(oid, level, skills_level):
    name = await get_op_attribute(oid, OPAttribute.name)
    health = (await get_op_attribute(oid, OPAttribute.health) +
              await get_op_attribute(oid, OPAttribute.health_plus) * level)
    atk = (await get_op_attribute(oid, OPAttribute.atk) +
           await get_op_attribute(oid, OPAttribute.atk_plus) * level)
    defence = (await get_op_attribute(oid, OPAttribute.defence) +
               await get_op_attribute(oid, OPAttribute.defence_plus) * level)
    res = (await get_op_attribute(oid, OPAttribute.res) +
           await get_op_attribute(oid, OPAttribute.res_plus) * level)
    crit_r = (await get_op_attribute(oid, OPAttribute.crit_r) +
              await get_op_attribute(oid, OPAttribute.crit_r_plus) * level)
    crit_d = (await get_op_attribute(oid, OPAttribute.crit_d) +
              await get_op_attribute(oid, OPAttribute.crit_d_plus) * level)
    speed = (await get_op_attribute(oid, OPAttribute.speed) +
             await get_op_attribute(oid, OPAttribute.speed_plus) * level)
    atk_type = await get_op_attribute(oid, OPAttribute.atk_type)
    sid_list = await get_op_attribute(oid, OPAttribute.skills)
    skills_list: list[Skill] = await get_skills_list(sid_list, skills_level)

    return Operator(name, level, health, atk, defence, res, crit_r, crit_d, speed, atk_type, skills_list)


async def get_operator_list(uid: str or int) -> list[Operator]:
    playing_ops_dict = await get_user_playing_ops(uid)
    playing_ops_list: list[Operator] = []

    for op in playing_ops_dict:
        oid = playing_ops_dict[op]["oid"]
        level = playing_ops_dict[op]["level"]
        skills_level = playing_ops_dict[op]["skills_level"]  # [0,1,1]
        op_instance = await new_instance(oid, level, skills_level)
        playing_ops_list.append(op_instance)

    return playing_ops_list
