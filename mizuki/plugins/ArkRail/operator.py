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
        """
        :param name: 干员名称
        :param level: 干员等级
        :param health: 干员生命值(初始赋值给干员的最大生命值max_health和当前生命值health)
        :param atk: 干员攻击力
        :param defence: 干员防御力
        :param res: 干员法抗
        :param crit_r: 干员暴击率
        :param crit_d: 干员暴击伤害倍率
        :param speed: 干员速度
        :param atk_type: 干员攻击方式
        :param skills_list: 干员的技能列表
        """
        self.name = name
        self.level = level
        self.max_health = self.health = health
        self.atk = atk
        self.defence = defence
        self.res = res
        self.crit_r = crit_r
        self.crit_d = crit_d
        self.speed = speed
        self.atk_type = atk_type
        self.skills_list = skills_list


async def new_instance(oid, level, skills_level):
    """
    通过传入的干员id、干员等级以及干员技能等级列表生成一个干员实例

    :param oid: 干员id
    :param level: 干员等级
    :param skills_level: 干员技能等级列表
    :return: 返回一个干员实例
    """
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
    """
    通过传入的用户id，返回该用户当前出战干员的列表

    :param uid: 用户id
    :return: 返回用户当前出战干员的列表
    """
    playing_ops_dict = await get_user_playing_ops(uid)
    playing_ops_list: list[Operator] = []

    for op in playing_ops_dict:
        oid = playing_ops_dict[op]["oid"]
        level = playing_ops_dict[op]["level"]
        skills_level = playing_ops_dict[op]["skills_level"]  # [0,1,1]
        op_instance = await new_instance(oid, level, skills_level)
        playing_ops_list.append(op_instance)

    return playing_ops_list
