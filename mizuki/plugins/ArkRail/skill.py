# -*- coding = utf-8 -*-
# @File:skill.py
# @Author:Hycer_Lance
# @Time:2023/4/27 17:00
# @Software:PyCharm

from .DB import get_skill_attribute, SkillAttribute
from .effect import Effect


class Skill:
    def __init__(self, sid: int, name: str, level: int,
                 brief_d: str, detail: str, rate1: float,
                 rate2: float, rate3: float, obj_type: int,
                 consume: int, persistence: int):
        """
        :param sid: 技能id
        :param name: 技能名称
        :param level: 技能等级
        :param brief_d: 技能简述
        :param detail: 技能详述
        :param rate1: 技能倍率1(对于某些不需要用到这个值的技能，这个值为0)
        :param rate2: 技能倍率2(对于某些不需要用到这个值的技能，这个值为0)
        :param rate3: 技能倍率3(对于某些不需要用到这个值的技能，这个值为0)
        :param obj_type: 目标类型(详见下面)
        :param consume: 释放技能的消耗
        :param persistence: 技能持续回合(对于非持续性技能，这个值为0)

        目标类型列表
        0:自身  1:单个敌人  2:两个敌人  3:所有敌人  4:单个我方  5:两个我方  6:所有我方  7:单个敌方和单个我方
        """
        self.sid = sid
        self.name = name
        self.level = level
        self.brief_d = brief_d
        self.detail = detail
        self.rate1 = rate1
        self.rate2 = rate2
        self.rate3 = rate3
        self.obj_type = obj_type
        self.consume = consume
        self.persistence = persistence

        self.count = 0  # 技能持续回合(持续性技能用)

    async def get_skill_effect(self) -> list[Effect]:
        effect_list: list[Effect] = []
        eid = sid
        ep = self.persistence + 1
        if sid == 2:
            effect_list.append(Effect(eid, ep, 0, self.rate2))
        return effect_list


async def get_skills_list(sid_list: list[int], skills_level: list[int], is_enemy: bool) -> list[Skill]:
    """
    获取单个干员的技能列表的函数

    :param sid_list: 技能id的列表，格式为[1]、[3,4]、[1,5,8]等
    :param skills_level: 技能等级的列表，大小应该与技能id列表相同，与技能id列表的格式相同
    :param is_enemy: 是否为敌人的技能列表，默认为False
    :return: 返回一个Skill类型的列表，表示干员可以使用的技能
    """
    j = 0
    skills_list: list[Skill] = []
    for sid in sid_list:
        skill_instance = await new_instance(sid, skills_level[j], is_enemy)
        skills_list.append(skill_instance)
        j += 1
    return skills_list


async def new_instance(sid: int, level: int, is_enemy: bool) -> Skill:
    """
    通过传入的技能id和技能等级生成一个Skill实例，通常不需要直接调用这个方法

    :param sid: 技能id，详见skills_data.json文件和enemy_skills_data.json文件，敌人技能id从-1开始往下减
    :param level: 技能等级
    :param is_enemy: 是否为敌人的技能，默认为False
    :return: 返回一个Skill实例
    """
    name: str = await get_skill_attribute(sid, SkillAttribute.name, is_enemy)
    brief_d: str = await get_skill_attribute(sid, SkillAttribute.brief_d, is_enemy)
    rate1: float = (await get_skill_attribute(sid, SkillAttribute.rate1, is_enemy) +
                    await get_skill_attribute(sid, SkillAttribute.rate1_plus, is_enemy) * level)
    rate2: float = (await get_skill_attribute(sid, SkillAttribute.rate2, is_enemy) +
                    await get_skill_attribute(sid, SkillAttribute.rate2_plus, is_enemy) * level)
    rate3: float = (await get_skill_attribute(sid, SkillAttribute.rate3, is_enemy) +
                    await get_skill_attribute(sid, SkillAttribute.rate3_plus, is_enemy) * level)
    obj_type: int = await get_skill_attribute(sid, SkillAttribute.obj_type, is_enemy)
    consume: int = (await get_skill_attribute(sid, SkillAttribute.consume, is_enemy) -
                    await get_skill_attribute(sid, SkillAttribute.consume_plus, is_enemy) * level)
    persistence: int = (await get_skill_attribute(sid, SkillAttribute.persistence, is_enemy) +
                        await get_skill_attribute(sid, SkillAttribute.persistence_plus, is_enemy) * level)
    detail: str = await get_skill_attribute(sid, SkillAttribute.detail, is_enemy)
    detail = detail.replace("${r1_int}", str(int(rate1)))\
        .replace("${r2_int}", str(int(rate2)))\
        .replace("${r3_int}", str(int(rate3)))\
        .replace("${r1_float}", str(round(rate1 * 100.0, 1)) + "%")\
        .replace("${r2_float}", str(round(rate2 * 100.0, 1)) + "%") \
        .replace("${r3_float}", str(round(rate3 * 100.0, 1)) + "%") \
        .replace("${persistence}", str(int(persistence)) if int(persistence) >= 0 else "∞")
    if is_enemy:
        sid *= -1
    return Skill(sid, name, level, brief_d, detail, rate1, rate2, rate3, obj_type, consume, persistence)
