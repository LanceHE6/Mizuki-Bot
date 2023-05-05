# -*- coding = utf-8 -*-
# @File:skill.py
# @Author:Hycer_Lance
# @Time:2023/4/27 17:00
# @Software:PyCharm

from .operator import user_data
import json

"""
数据库技能表示例（只读
type:int    name:str       brief_description:str         base_rate1:real    base_rate2:real   base_rate1_plus:real    base_rate2_plus:real
    1         强力击            造成大量物理伤害                     2.5                 3.0                    0.03                    0.04
    
base_consumption int    base_persistence int    base_consumption_plus real    base_persistence_plus real
        25                       2                          1                             0.25
"""


async def new_instance_list(uid: str or int):
    with open(user_data, 'r', encoding='utf-8') as data:
        user = json.load(data)
        data.close()
    try:
        player_skills = user[f"{uid}"]["skills"]

    except KeyError:
        player_skills: dict = {
            "1": {
                "type": 1,
                "level": 1,
                "is_using": 1
            }
        }
        user[f"{uid}"]["skills"] = player_skills

    skill_list: list[Skill] = []
    for s in player_skills:
        skill_list.append(await new_instance(player_skills[s]))

    return skill_list


async def new_instance(skill: dict):
    return Skill(skill["type"], skill["level"], skill["is_using"])


class Skill:
    def __init__(self, skill_type: int, level: int, is_using: bool):
        self.skill_info = "暂无介绍"
        self.skill_name = "无"
        self.skill_quality = 0
        self.max_rate = 0
        self.min_rate = 0
        self.skill_type = skill_type
        self.skill_level = level
        self.is_using = is_using
        self.init_type(skill_type, level)

    def init_type(self, skill_type: int, level: int):
        # 三星技能
        if skill_type == 1:
            self.skill_name = "强力击"
            self.skill_quality = 3
            self.min_rate = 190 + 10 * level
            self.max_rate = 208 + 12 * level
            self.skill_info = f"对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的物理伤害"
        elif skill_type == 2:
            self.skill_name = "防御力增强"
            self.skill_quality = 3
            self.min_rate = self.max_rate = 56 + 4 * level
            self.skill_info = f"自身防御力提高{self.max_rate}%，持续{2 + int(self.skill_level / 5)}回合"
        elif skill_type == 3:
            self.skill_name = "攻击力增强"
            self.skill_quality = 3
            self.min_rate = self.max_rate = 37 + 3 * level
            self.skill_info = f"自身攻击力提高{self.max_rate}%，持续{2 + int(self.skill_level / 5)}回合"
        elif skill_type == 4:
            self.skill_name = "生命回复"
            self.skill_quality = 3
            self.min_rate = self.max_rate = 19 + 1 * level
            self.skill_info = f"立即回复{self.max_rate}%最大生命值"
        elif skill_type == 5:
            self.skill_name = "冲锋号令"
            self.skill_quality = 3
            self.min_rate = self.max_rate = 24 + 1 * level
            self.skill_info = f"自身暴击率增加{self.max_rate}%，持续{2 + int(self.skill_level / 6)}回合"
        # 四星技能
        elif skill_type == 6:
            self.skill_name = "三连击"
            self.skill_quality = 4
            self.min_rate = 110 + 5 * level
            self.max_rate = 119 + 6 * level
            self.skill_info = f"连续进行三次攻击，每次攻击对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的物理伤害"
        elif skill_type == 7:
            self.skill_name = "蛮力穿刺"
            self.skill_quality = 4
            self.min_rate = self.max_rate = 66 + 4 * level
            self.skill_info = f"自身暴击伤害增加{self.max_rate}%，并立即对对手发动一次普通攻击"
        elif skill_type == 8:
            self.skill_name = "碎甲击"
            self.skill_quality = 4
            self.min_rate = 142 + 8 * level
            self.max_rate = 150 + 10 * level
            self.skill_info = f"对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的物理伤害，且无视其{40 + int(self.skill_level / 4) * 10}%的防御"
        elif skill_type == 9:
            self.skill_name = "刺身拼盘"
            self.skill_quality = 4
            self.min_rate = 172 + 8 * level
            self.max_rate = 180 + 10 * level
            self.skill_info = f"对对手造成相当于自身攻击力{self.min_rate}%~{self.max_rate}%的物理伤害，并将所造成伤害的50%转换为自身生命值"
        # 五星技能
        elif skill_type == 10:
            self.skill_name = "亮剑"
            self.skill_quality = 5
            self.min_rate = self.max_rate = 75 + 5 * level
            self.skill_info = f"自身防御力降为0，立刻恢复30%最大生命，攻击力增加{self.max_rate}%，持续2回合"
        elif skill_type == 11:
            self.skill_name = "狼魂"
            self.skill_quality = 5
            self.min_rate = self.max_rate = 46 + 4 * level
            self.skill_info = f"攻击力增加{self.max_rate}%，伤害类型变为法术，持续2回合"
        elif skill_type == 12:
            self.skill_name = "肉斩骨断"
            self.skill_quality = 5
            self.min_rate = self.max_rate = 37 + 3 * level
            self.skill_info = f"攻击力增加{self.max_rate}%，并抵挡一次致命伤害(血量为1时无效)，持续1回合"
        elif skill_type == 13:
            self.skill_name = "居合斩"
            self.skill_quality = 5
            self.min_rate = 57 + 3 * level
            self.max_rate = 75 + 5 * level
            self.skill_info = f"攻击力增加{self.min_rate}%，防御力增加{self.max_rate}%，持续1回合"
        # 六星技能
        elif skill_type == 14:
            self.skill_name = "指令: 熔毁"
            self.skill_quality = 6
            self.min_rate = 76 + 4 * level
            self.max_rate = 57 + 3 * level
            self.skill_info = f"立即流失35%最大生命值+15%当前生命值，攻击力增加{self.min_rate}%，防御力增加{self.max_rate}%，伤害类型变为真实，持续2回合"
        elif skill_type == 15:
            self.skill_name = "判决"
            self.skill_quality = 6
            self.min_rate = 53 + 2 * level
            self.max_rate = 57 + 3 * level
            self.skill_info = f"连续进行12次攻击，每次对对手造成{self.min_rate}%~{self.max_rate}%的物理伤害且无视其50%的防御"
        elif skill_type == 16:
            self.skill_name = "绝影"
            self.skill_quality = 6
            self.min_rate = 72 + 3 * level
            self.max_rate = 76 + 4 * level
            self.skill_info = f"连续进行10次攻击，每次对对手造成{self.min_rate}%~{self.max_rate}%的物理伤害，且最后一击伤害翻倍"
        elif skill_type == 17:
            self.skill_name = "横扫架势"
            self.skill_quality = 6
            self.min_rate = self.max_rate = 47 + 3 * level
            self.skill_info = f"立刻回复10%最大生命值，防御力降低{50 - int(self.skill_level / 4) * 5}%，攻击力提高{self.max_rate}%，持续{2 + int(self.skill_level / 6)}回合"
        elif skill_type == 18:
            self.skill_name = "黄昏"
            self.skill_quality = 6
            self.min_rate = self.max_rate = 67 + 3 * level
            self.skill_info = f"攻击力提高{self.max_rate}%，伤害类型变为法术，每回合流失12%最大生命值，持续99回合"

    async def get_info(self) -> dict:
        skill_info = {
            "name": self.skill_name,
            "quality": self.skill_quality,
            "level": self.skill_level,
            "skill_info": self.skill_info
        }
        return skill_info
