# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm
import random
from pathlib import Path
from .DB import get_user_playing_ops, get_op_attribute, OPAttribute, get_map_attribute, MapAttribute
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
        :param health: 干员初始生命值(初始赋值给干员的最大生命值max_health和当前生命值health)
        :param atk: 干员初始攻击力
        :param defence: 干员初始防御力
        :param res: 干员初始法抗
        :param crit_r: 干员初始暴击率
        :param crit_d: 干员初始暴击伤害倍率
        :param speed: 干员初始速度
        :param atk_type: 干员攻击方式
        :param skills_list: 干员的技能列表

        后面有_p的变量表示干员战斗时该变量的实际值(xxx_p = xxx * (1 + xxx_add_f) + xxx_add_d)
        """
        self.name = name
        self.stars = stars
        self.profession = profession
        self.level = level
        self.max_health = self.health = self.max_health_p = health
        self.atk = self.atk_p = atk
        self.defence = self.defence_p = defence
        self.res = self.res_p = res
        self.crit_r = self.crit_r_p = crit_r
        self.crit_d = self.crit_d_p = crit_d
        self.speed = self.speed_p = speed
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
        
        next_operators: 身边的干员(包括自己)
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

        self.next_operators: list[Operator] = [self]

    async def attack(self, obj, is_crit: bool):
        """
        干员进行普攻的函数，会根据atk_type来进行不同的操作

        :param obj: 目标
        :param is_crit: 是否暴击
        """
        if self.atk_type == 0:
            damage = (self.atk_p - obj.defence_p) \
                if (self.atk_p - obj.defence_p > self.atk_p * 0.05) \
                else (self.atk_p * 0.05)  # 5%攻击力的保底伤害
            damage += damage * is_crit * (1.0 + self.crit_d_p)
            if not obj.invincible:
                obj.health -= damage
        elif self.atk_type == 1:
            damage = (self.atk_p * ((100 - obj.res_p) / 100))  # 法抗90封顶
            damage += damage * is_crit * (1.0 + self.crit_d_p)
            if not obj.invincible:
                obj.health -= damage
        elif self.atk_type == 2:
            for op in obj.next_operators:
                damage = (self.atk_p - op.defence_p) \
                    if (self.atk_p - op.defence_p > self.atk_p * 0.05) \
                    else (self.atk_p * 0.05)
                damage += damage * is_crit * (1.0 + self.crit_d_p)
                if not op.invincible:
                    op.health -= damage
        elif self.atk_type == 3:
            for op in obj.next_operators:
                damage = (self.atk_p * ((100 - op.res_p) / 100))
                damage += damage * is_crit * (1.0 + self.crit_d_p)
                if not op.invincible:
                    op.health -= damage
        elif self.atk_type == 4:
            obj.health += self.atk_p
            if obj.health > obj.max_health_p:
                obj.health = obj.max_health_p
        elif self.atk_type == 5:
            for op in obj.next_operators:
                op.health += self.atk_p
                if op.health > op.max_health_p:
                    op.health = op.max_health_p
        elif self.atk_type == 6:
            damage = self.atk_p
            damage += damage * is_crit * (1.0 + self.crit_d_p)
            if not obj.invincible:
                obj.health -= damage
        elif self.atk_type == 7:
            pass

    async def is_crit(self) -> bool:
        """
        判断干员是否暴击的函数

        :return: 干员是否暴击
        """
        num = random.randint(1, 10000)
        return num <= self.crit_r_p * 10000

    async def die(self) -> bool:
        """
        干员血量小于0时调用的函数

        :return: 干员是否被击倒(如果干员处于不死状态则不会被击倒)
        """
        if self.deathless:  # 如果干员处于不死状态，则将其血量恢复为1
            self.health = 1
            return False
        for op in self.next_operators:
            op.next_operators.remove(self)
        return True


async def new_instance(oid: int, level: int, skills_level: list[int], is_enemy: bool = False) -> Operator:
    """
    通过传入的干员id、干员等级以及干员技能等级列表生成一个干员实例

    :param oid: 干员id，详情见operators_data.json文件
    :param level: 干员等级
    :param skills_level: 干员技能等级列表
    :param is_enemy: 是否是敌人，默认为False
    :return: 返回一个干员实例
    """
    name = await get_op_attribute(oid, OPAttribute.name, is_enemy)
    stars = await get_op_attribute(oid, OPAttribute.stars, is_enemy)
    profession = await get_op_attribute(oid, OPAttribute.profession, is_enemy)
    health = (await get_op_attribute(oid, OPAttribute.health, is_enemy) +
              await get_op_attribute(oid, OPAttribute.health_plus, is_enemy) * (level - 1))
    atk = (await get_op_attribute(oid, OPAttribute.atk, is_enemy) +
           await get_op_attribute(oid, OPAttribute.atk_plus, is_enemy) * (level - 1))
    defence = (await get_op_attribute(oid, OPAttribute.defence, is_enemy) +
               await get_op_attribute(oid, OPAttribute.defence_plus, is_enemy) * (level - 1))
    res = (await get_op_attribute(oid, OPAttribute.res, is_enemy) +
           await get_op_attribute(oid, OPAttribute.res_plus, is_enemy) * (level - 1))
    crit_r = (await get_op_attribute(oid, OPAttribute.crit_r, is_enemy) +
              await get_op_attribute(oid, OPAttribute.crit_r_plus, is_enemy) * (level - 1))
    crit_d = (await get_op_attribute(oid, OPAttribute.crit_d, is_enemy) +
              await get_op_attribute(oid, OPAttribute.crit_d_plus, is_enemy) * (level - 1))
    speed = (await get_op_attribute(oid, OPAttribute.speed, is_enemy) +
             await get_op_attribute(oid, OPAttribute.speed_plus, is_enemy) * (level - 1))
    atk_type = await get_op_attribute(oid, OPAttribute.atk_type, is_enemy)
    sid_list = await get_op_attribute(oid, OPAttribute.skills, is_enemy)
    skills_list: list[Skill] = await get_skills_list(sid_list, skills_level, is_enemy)

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


async def get_enemies_list(mid: str) -> list[Operator]:
    """
    通过传入的地图id，返回地图敌人列表

    :param mid: 地图id
    :return: 返回地图中的敌人列表
    """
    map_enemies_data_list = await get_map_attribute(mid, MapAttribute.enemies)
    map_enemies_list: list[Operator] = []

    for i in range(len(map_enemies_data_list[0])):
        op_instance = await new_instance(map_enemies_data_list[0][i], map_enemies_data_list[1][i], [0, 0, 0], True)
        map_enemies_list.append(op_instance)

    return map_enemies_list
