# -*- coding = utf-8 -*-
# @File:player.py
# @Author:Hycer_Lance
# @Time:2023/4/27 16:55
# @Software:PyCharm

from pathlib import Path
import json

user_data=Path() / 'mizuki' / 'plugins' / 'test' / 'user_data.json'

class Player:
    def __init__(self,uid: str | int):
        with open(user_data, 'r', encoding='utf-8') as data:
            user=json.load(data)
            data.close()
        self.player_level: int =user[uid]["level"]
        self.player_skills: dict=user[uid]["skills"]
        pass
