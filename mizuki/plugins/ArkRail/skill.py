# -*- coding = utf-8 -*-
# @File:skill.py
# @Author:Hycer_Lance
# @Time:2023/4/27 17:00
# @Software:PyCharm

from .DB import get_skill_attribute, SkillAttribute

"""
数据库技能表示例（只读
type:int    name:str       brief_description:str         base_rate1:real    base_rate2:real   base_rate1_plus:real    base_rate2_plus:real
    1         强力击            造成大量物理伤害                     2.5                 3.0                    0.03                    0.04
    
base_consumption int    base_persistence int    base_consumption_plus real    base_persistence_plus real
        25                       2                          1                             0.25
"""


class Skill:
    def __init__(self, sid: int, name: str, level: int,
                 brief_d: str, detail: str, rate1: float,
                 rate2: float, consume: int, persistence: int):
        """
        :param sid: 技能id
        :param name: 技能名称
        :param level: 技能等级
        :param brief_d: 技能简述
        :param detail: 技能详述
        :param rate1: 技能倍率1(对于某些不需要用到这个值的技能，这个值为0)
        :param rate2: 技能倍率2(对于某些不需要用到这个值的技能，这个值为0)
        :param consume: 释放技能的消耗
        :param persistence: 技能持续回合(对于非持续性技能，这个值为0)
        """
        self.sid = sid
        self.name = name
        self.level = level
        self.brief_d = brief_d
        self.detail = detail
        self.rate1 = rate1
        self.rate2 = rate2
        self.consume = consume
        self.persistence = persistence


async def get_skills_list(sid_list: list[int], skills_level: list[int]) -> list[Skill]:
    """
    获取单个干员的技能列表的函数

    :param sid_list: 技能id的列表，格式为[1]、[3,4]、[1,5,8]等
    :param skills_level: 技能等级的列表，大小应该与技能id列表相同，与技能id列表的格式相同
    :return: 返回一个Skill类型的列表，表示干员可以使用的技能
    """
    j = 0
    skills_list: list[Skill] = []
    for i in sid_list:
        skill_instance = await new_instance(i, skills_level[j])
        skills_list.append(skill_instance)
        j += 1
    return skills_list


async def new_instance(sid: int, level: int) -> Skill:
    """
    通过传入的技能id和技能等级生成一个Skill实例，通常不需要直接调用这个方法

    :param sid: 技能id，详见skills_data.json文件
    :param level: 技能等级
    :return: 返回一个Skill实例
    """
    name = await get_skill_attribute(sid, SkillAttribute.name)
    brief_d = await get_skill_attribute(sid, SkillAttribute.brief_d)
    detail = await get_skill_attribute(sid, SkillAttribute.detail)
    rate1 = (await get_skill_attribute(sid, SkillAttribute.rate1) +
             await get_skill_attribute(sid, SkillAttribute.rate1_plus) * level)
    rate2 = (await get_skill_attribute(sid, SkillAttribute.rate2) +
             await get_skill_attribute(sid, SkillAttribute.rate2_plus) * level)
    consume = (await get_skill_attribute(sid, SkillAttribute.consume) +
               await get_skill_attribute(sid, SkillAttribute.consume_plus) * level)
    persistence = (await get_skill_attribute(sid, SkillAttribute.persistence) +
                   await get_skill_attribute(sid, SkillAttribute.persistence_plus) * level)
    return Skill(sid, name, level, brief_d, detail, rate1, rate2, consume, persistence)

    # def init_type(self, skill_type: int, level: int):
    #     # 三星技能
    #     if skill_type == 1:
    #         self.skill_name = "强力击"
    #         self.skill_quality = 3
    #         self.min_rate = 190 + 10 * level
    #         self.max_rate = 208 + 12 * level
    #         self.skill_info = f"对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的物理伤害"
    #     elif skill_type == 2:
    #         self.skill_name = "防御力增强"
    #         self.skill_quality = 3
    #         self.min_rate = self.max_rate = 56 + 4 * level
    #         self.skill_info = f"自身防御力提高{self.max_rate}%，持续{2 + int(self.skill_level / 5)}回合"
    #     elif skill_type == 3:
    #         self.skill_name = "攻击力增强"
    #         self.skill_quality = 3
    #         self.min_rate = self.max_rate = 37 + 3 * level
    #         self.skill_info = f"自身攻击力提高{self.max_rate}%，持续{2 + int(self.skill_level / 5)}回合"
    #     elif skill_type == 4:
    #         self.skill_name = "生命回复"
    #         self.skill_quality = 3
    #         self.min_rate = self.max_rate = 19 + 1 * level
    #         self.skill_info = f"立即回复{self.max_rate}%最大生命值"
    #     elif skill_type == 5:
    #         self.skill_name = "冲锋号令"
    #         self.skill_quality = 3
    #         self.min_rate = self.max_rate = 24 + 1 * level
    #         self.skill_info = f"自身暴击率增加{self.max_rate}%，持续{2 + int(self.skill_level / 6)}回合"
    #     # 四星技能
    #     elif skill_type == 6:
    #         self.skill_name = "三连击"
    #         self.skill_quality = 4
    #         self.min_rate = 110 + 5 * level
    #         self.max_rate = 119 + 6 * level
    #         self.skill_info = f"连续进行三次攻击，每次攻击对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的物理伤害"
    #     elif skill_type == 7:
    #         self.skill_name = "蛮力穿刺"
    #         self.skill_quality = 4
    #         self.min_rate = self.max_rate = 66 + 4 * level
    #         self.skill_info = f"自身暴击伤害增加{self.max_rate}%，并立即对对手发动一次普通攻击"
    #     elif skill_type == 8:
    #         self.skill_name = "碎甲击"
    #         self.skill_quality = 4
    #         self.min_rate = 142 + 8 * level
    #         self.max_rate = 150 + 10 * level
    #         self.skill_info = f"对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的物理伤害，且无视其{40 + int(self.skill_level / 4) * 10}%的防御"
    #     elif skill_type == 9:
    #         self.skill_name = "刺身拼盘"
    #         self.skill_quality = 4
    #         self.min_rate = 172 + 8 * level
    #         self.max_rate = 180 + 10 * level
    #         self.skill_info = f"对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的物理伤害，并将所造成伤害的50%转换为自身生命值"
    #     # 五星技能
    #     elif skill_type == 10:
    #         self.skill_name = "亮剑"
    #         self.skill_quality = 5
    #         self.min_rate = self.max_rate = 75 + 5 * level
    #         self.skill_info = f"自身防御力降为0，立刻恢复30%最大生命，攻击力增加{self.max_rate}%，持续2回合"
    #     elif skill_type == 11:
    #         self.skill_name = "狼魂"
    #         self.skill_quality = 5
    #         self.min_rate = self.max_rate = 46 + 4 * level
    #         self.skill_info = f"攻击力增加{self.max_rate}%，伤害类型变为法术，持续2回合"
    #     elif skill_type == 12:
    #         self.skill_name = "肉斩骨断"
    #         self.skill_quality = 5
    #         self.min_rate = self.max_rate = 37 + 3 * level
    #         self.skill_info = f"攻击力增加{self.max_rate}%，并抵挡一次致命伤害(血量为1时无效)，持续1回合"
    #     elif skill_type == 13:
    #         self.skill_name = "居合斩"
    #         self.skill_quality = 5
    #         self.min_rate = 57 + 3 * level
    #         self.max_rate = 75 + 5 * level
    #         self.skill_info = f"攻击力增加{self.min_rate}%，防御力增加{self.max_rate}%，持续1回合"
    #     # 六星技能
    #     elif skill_type == 14:
    #         self.skill_name = "指令: 熔毁"
    #         self.skill_quality = 6
    #         self.min_rate = 76 + 4 * level
    #         self.max_rate = 57 + 3 * level
    #         self.skill_info = f"立即流失35%最大生命值+15%当前生命值，攻击力增加{self.min_rate}%，防御力增加{self.max_rate}%，伤害类型变为真实，持续2回合"
    #     elif skill_type == 15:
    #         self.skill_name = "判决"
    #         self.skill_quality = 6
    #         self.min_rate = 53 + 2 * level
    #         self.max_rate = 57 + 3 * level
    #         self.skill_info = f"连续进行12次攻击，每次对对手造成{self.min_rate}%~{self.max_rate}%的物理伤害且无视其50%的防御"
    #     elif skill_type == 16:
    #         self.skill_name = "绝影"
    #         self.skill_quality = 6
    #         self.min_rate = 72 + 3 * level
    #         self.max_rate = 76 + 4 * level
    #         self.skill_info = f"连续进行10次攻击，每次对对手造成{self.min_rate}%~{self.max_rate}%的物理伤害，且最后一击伤害翻倍"
    #     elif skill_type == 17:
    #         self.skill_name = "横扫架势"
    #         self.skill_quality = 6
    #         self.min_rate = self.max_rate = 47 + 3 * level
    #         self.skill_info = f"立刻回复10%最大生命值，防御力降低{50 - int(self.skill_level / 4) * 5}%，攻击力提高{self.max_rate}%，持续{2 + int(self.skill_level / 6)}回合"
    #     elif skill_type == 18:
    #         self.skill_name = "黄昏"
    #         self.skill_quality = 6
    #         self.min_rate = self.max_rate = 67 + 3 * level
    #         self.skill_info = f"攻击力提高{self.max_rate}%，伤害类型变为法术，每回合流失12%最大生命值，持续99回合"
