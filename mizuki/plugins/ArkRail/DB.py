# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/5 12:32
# @Software:PyCharm

from pathlib import Path
import json

operators_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'operators_data.json'
skills_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'skills_data.json'
'''
"1": {
    "name": "芬",
    "health": 2700,
    "health_plus": 15,
    "atk": 336,
    "atk_plus": 1,
    "def": 152,
    "def_plus": 2,
    "crit_r": 0.1,
    "crit_r_plus": 0.001,
    "crit_d": 1.0,
    "crit_d_plus": 0.005,
    "speed": 110,
    "speed_plus": 0.1,
    "atk_type": 0,
    "skills": [1]
'''
class OPAttributeNotFoundError(Exception):
    def __init__(self, error_attribute):
        self.error_attribute=error_attribute

    def __str__(self):
        print("未知干员属性:"+self.error_attribute)

class OPAttribute:#干员属性类
    name='name'
    health='health'
    health_plus='health_plus'
    atk='atk'
    atk_plus='atk_plus'
    defence='def'
    defence_plus='def_plus'
    crit_r='crit_r'
    crit_r_plus='crit_r_plus'
    crit_d='crit_d'
    crit_d_plus='crit_d_plus'
    speed='speed'
    speed_plus='speed_plus'
    atk_type='atk_type'
    skills='skills'
async def get_op_attribute(oid:str or int, attribute: str)->any:
    if attribute not in ["name","health","health_plus","atk","atk_plus","def","def_plus","crit_r","crit_r_plus","crit_d","crit_d_plus","speed","speed_plus","atk_type","skills"]:
        raise OPAttributeNotFoundError(attribute)
    with open("operators_data.json", 'r', encoding='utf-8') as data:
        ops_data=json.load(data)
        data.close()
    return ops_data[f"{oid}"][f"{attribute}"]
