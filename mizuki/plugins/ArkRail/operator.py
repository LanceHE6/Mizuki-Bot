# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm

from pathlib import Path
from .DB import get_user_playing_ops, get_op_attribute, OPAttribute
from .skill import get_skills_list
from .skill import Skill

user_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'user_data.json'

"""
数据库玩家表示例
uid:str         level:int           operators_all                               operators_playing
  123               10           {2:{level:10,skills:{1,2,3}},...}             {2:{level:10,skills:{1,2,3}},...} 
"""


class Operator:

    def __init__(self, name: str, level: int, stars: int, profession: str, health: int, atk: int,
                 defence: int, res: float, crit_r: float, crit_d: float, speed: float,
                 atk_type: int, skills_list: list[Skill]):
        """
        :param name: 干员名称
        :param level: 干员等级
        :param stars: 干员星级
        :param profession: 干员职业
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
        self.stars = stars
        self.profession = profession
        self.level = level
        self.max_health = self.health = health
        self.atk = atk
        self.defence = defence
        self.res = res
        self.crit_r = crit_r
        self.crit_d = crit_d
        self.speed = speed
        self.atk_type = atk_type
        self.atk_type_str = "-"
        self.skills_list = skills_list

        if atk_type == 0:
            self.atk_type_str = "物理单体"
        elif atk_type == 1:
            self.atk_type_str = "法术单体"
        elif atk_type == 2:
            self.atk_type_str = "物理群体"
        elif atk_type == 3:
            self.atk_type_str = "法术群体"
        elif atk_type == 4:
            self.atk_type_str = "单体治疗"
        elif atk_type == 5:
            self.atk_type_str = "群体治疗"
        elif atk_type == 6:
            self.atk_type_str = "真实单体"
        elif atk_type == 7:
            self.atk_type_str = "不进行普攻"

        """
        以下是干员战斗时特有的属性:
        
        health_add_f: 最大生命值百分比加成
        atk_add_f: 攻击力百分比加成
        def_add_f: 防御力百分比加成
        res_add_f: 法抗百分比加成
        crit_r_add_f: 暴击率百分比加成
        crit_d_add_f: 暴击伤害百分比加成
        speed_f: 速度百分比加成
        
        health_add_d: 最大生命值数值加成
        atk_add_d: 攻击力数值加成
        def_add_d: 防御力数值加成
        res_add_d: 法抗数值加成
        crit_r_add_d: 暴击率数值加成
        crit_d_add_d: 暴击伤害数值加成
        speed_d: 速度数值加成
        
        特殊状态(数值表示持续回合，大于0时生效，效果生效时每回合减1)
        immobile: 无法行动(无法普攻和使用技能，跳过该干员回合)
        silent: 沉默(无法使用技能)
        hidden: 隐匿(无法被敌方指向性技能选中)
        deathless: 不死(血量最多降为1)
        invincible: 无敌(无法受到任何伤害)
        mocked: 被嘲讽(攻击时只能攻击指定单位)
        mocking_obj: 嘲讽者(被嘲讽时只能攻击的单位)
        """

        self.health_add_f: float = 0.0
        self.atk_add_f: float = 0.0
        self.def_add_f: float = 0.0
        self.res_add_f: float = 0.0
        self.crit_r_add_f: float = 0.0
        self.crit_d_add_f: float = 0.0
        self.speed_add_f: float = 0.0

        self.health_add_d: int = 0
        self.atk_add_d: int = 0
        self.def_add_d: int = 0
        self.res_add_d: int = 0
        self.crit_r_add_d: int = 0
        self.crit_d_add_d: int = 0
        self.speed_add_d: int = 0

        self.immobile: int = 0
        self.silent: int = 0
        self.hidden: int = 0
        self.deathless: int = 0
        self.invincible: int = 0
        self.mocked: int = 0
        self.mocking_obj: Operator


async def new_instance(oid: int, level: int, skills_level: list[int]) -> Operator:
    """
    通过传入的干员id、干员等级以及干员技能等级列表生成一个干员实例

    :param oid: 干员id，详情见operators_data.json文件
    :param level: 干员等级
    :param skills_level: 干员技能等级列表
    :return: 返回一个干员实例
    """
    name = await get_op_attribute(oid, OPAttribute.name)
    stars = await get_op_attribute(oid, OPAttribute.stars)
    profession = await get_op_attribute(oid, OPAttribute.profession)
    health = (await get_op_attribute(oid, OPAttribute.health) +
              await get_op_attribute(oid, OPAttribute.health_plus) * (level - 1))
    atk = (await get_op_attribute(oid, OPAttribute.atk) +
           await get_op_attribute(oid, OPAttribute.atk_plus) * (level - 1))
    defence = (await get_op_attribute(oid, OPAttribute.defence) +
               await get_op_attribute(oid, OPAttribute.defence_plus) * (level - 1))
    res = (await get_op_attribute(oid, OPAttribute.res) +
           await get_op_attribute(oid, OPAttribute.res_plus) * (level - 1))
    crit_r = (await get_op_attribute(oid, OPAttribute.crit_r) +
              await get_op_attribute(oid, OPAttribute.crit_r_plus) * (level - 1))
    crit_d = (await get_op_attribute(oid, OPAttribute.crit_d) +
              await get_op_attribute(oid, OPAttribute.crit_d_plus) * (level - 1))
    speed = (await get_op_attribute(oid, OPAttribute.speed) +
             await get_op_attribute(oid, OPAttribute.speed_plus) * (level - 1))
    atk_type = await get_op_attribute(oid, OPAttribute.atk_type)
    sid_list = await get_op_attribute(oid, OPAttribute.skills)
    skills_list: list[Skill] = await get_skills_list(sid_list, skills_level)

    return Operator(name, level, stars, profession, health, atk, defence, res, crit_r, crit_d, speed, atk_type,
                    skills_list)


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
