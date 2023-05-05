# -*- coding = utf-8 -*-
# @File:DB.py
# @Author:Hycer_Lance
# @Time:2023/5/4 17:21
# @Software:PyCharm

from ..database.utils import MDB
from nonebot.log import logger
from colorama import Fore


# 检查所有所需表
async def check_tables():
    if not MDB.check_table("ArkRail_User"):
        logger.info(Fore.RED + "[ArkRail]ArkRail_User表不存在 准备创建新数据表")
        result = await MDB.db_execute(
            "Create Table ArkRail_User(uid integer primary key Not Null,"
            "                          level integer default 1 check ( level between 1 and 120),"
            "                          operators_all text,"
            "                          operators_playing text);")
        if result == 'ok':
            logger.info(Fore.RED + "[ArkRail]ArkRail_User表创建成功")
        else:
            logger.info(Fore.RED + f"[ArkRail]ArkRail_User表创建失败:{result}")

    if not MDB.check_table("ArkRail_Operators"):
        logger.info(Fore.RED + "[ArkRail]ArkRail_Operators表不存在 准备创建新数据表")
        result = await MDB.db_execute(
            "Create Table ArkRail_Operators(type integer primary key Not Null,"
            "                          name text,"
            "                          atk_type int,"
            "                          base_health int,"
            "                          base_atk int,"
            "                          base_def int,"
            "                          base_resistance real,"
            "                          base_crit_rate real,"
            "                          base_crit_damage real,"
            "                          base_speed real,"
            "                          base_health_plus int,"
            "                          base_atk_plus int,  "
            "                          base_def_plus int,"
            "                          base_resistance_plus real,"
            "                          base_crit_rate_plus real,"
            "                          base_crit_damage_plus real,"
            "                          base_speed_plus real,"
            "                          skills text"
            "                          );")
        if result == 'ok':
            logger.info(Fore.RED + "[ArkRail]ArkRail_Operators表创建成功")
        else:
            logger.info(Fore.RED + f"[ArkRail]ArkRail_Operators表创建失败:{result}")

    if not MDB.check_table("ArkRail_Skills"):
        logger.info(Fore.RED + "[ArkRail]ArkRail_Skills表不存在 准备创建新数据表")
        result = await MDB.db_execute(
            "Create Table ArkRail_Skills(type int primary key NOT NULL ,"
            "                          name text,"
            "                          brief_description text,"
            "                          base_rate1 real,"
            "                          base_rate2 real,"
            "                          base_consumption int,"
            "                          base_persistence int,"            
            "                          base_rate1_plus real,"
            "                          base_rate2_plus real,"
            "                          base_consumption_plus real,"
            "                          base_persistence_plus real,"
            "                          );")
        if result == 'ok':
            logger.info(Fore.RED + "[ArkRail]ArkRail_Skills表创建成功")
        else:
            logger.info(Fore.RED + f"[ArkRail]ArkRail_Skills表创建失败:{result}")
