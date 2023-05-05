# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm

from pathlib import Path
import json

user_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'user_data.json'

"""
数据库玩家表示例
uid:str         level:int           operators_all                               operators_playing
  123               10           {2:{level:10,skills:{1,2,3}},...}             {2:{level:10,skills:{1,2,3}},...} 
"""


async def new_instance_list(uid: str or int):

    return


class Operator:

    def __init__(self, level: int, name: str, skills: dict):
        self.player_name = name
        self.player_level = level
        self.max_health = 2000 + 30 * level
        self.health = self.max_health
        self.attack = 200 + 4 * level
        self.defence = 150 + 3 * level
        self.critical_rate = 10 + int(level / 10)
        self.critical_damage = 50 + level
        self.player_skills = skills

    async def get_info(self) -> dict:
        player_info = {
            "name": self.player_name,
            "level": self.player_level,
            "max_health": self.max_health,
            "attack": self.attack,
            "defence": self.defence,
            "crit_rate": self.critical_rate,
            "crit_damage": self.critical_damage
        }
        return player_info
