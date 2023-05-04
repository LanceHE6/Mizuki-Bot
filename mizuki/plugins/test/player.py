# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm

from pathlib import Path
import json

user_data = Path() / 'mizuki' / 'plugins' / 'test' / 'user_data.json'

"""
数据库玩家表示例
uid:str         level:int           operators_all                               operators_playing
  123               10           {2:{level:10,skills:{1,2,3}},...}             {2:{level:10,skills:{1,2,3}},...} 
  
数据库干员表示例（只读
type:int    name:str       base_health:int  base_atk:int  base_def:int  base_resistance:int  base_crit_rate:double  base_crit_damage:double   skills
    10          芬                1200           200           150              10                    5.0                     50.0             [1,3]

数据库技能表示例（只读
type:int    name:str       brief_description:str         base_rate1:double    base_rate2:double
    1         强力击            造成大量物理伤害                     2.5                 3.0
"""

async def new_instance(uid: str or int):
    with open(user_data, 'r', encoding='utf-8') as data:
        user = json.load(data)
        data.close()
    try:
        player_level: int = user[f"{uid}"]["level"]
        player_name: str = user[f"{uid}"]["name"]
        player_skills: dict = user[f"{uid}"]["skills"]
    except KeyError:
        player_level: int = 0
        player_name: str = ''
        player_skills: dict = {
            "1": {
                "type": 1,
                "level": 1,
                "is_using": 1
            }
        }
        user[f"{uid}"] = {
            "name": player_name,
            "level": player_level,
            "skills": player_skills
        }
        with open(user_data, 'w', encoding='utf-8') as data:
            json.dump(user, data)
            data.close()

    return Player(player_level, player_name, player_skills)


class Player:

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
