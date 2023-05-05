# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/5 12:32
# @Software:PyCharm

from pathlib import Path
import json

operators_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'operators_data.json'
skills_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'skills_data.json'

async def get_op_name(oid:str or int)->str:
    with open(operators_data, 'r', encoding='utf-8') as data:
        ops_data=json.load(data)
        data.close()
    return ops_data[f"{oid}"]["name"]
