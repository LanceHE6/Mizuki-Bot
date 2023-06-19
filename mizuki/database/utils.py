# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/3 15:53
# @Software:PyCharm

import os
import sqlite3
from pathlib import Path
from nonebot.log import logger
from colorama import Fore

database_path = Path() / 'database'
database = database_path / 'Mizuki_DB.db'


def check_database():
    logger.info(Fore.BLUE + "[DB]检查数据库...")
    if not os.path.exists(database_path):
        os.mkdir(database_path)
    try:
        connection = sqlite3.Connection(database)
        logger.info(Fore.BLUE + "[DB]数据库连接正常")
        connection.close()
    except sqlite3.DatabaseError as e:
        logger.info(Fore.RED + f"[DB]数据库连接失败:{e}")


class MDataBase:

    def __init__(self, db_file: Path or str):
        check_database()
        self.connection = sqlite3.Connection(db_file)
        self.cur = self.connection.cursor()
        logger.info(Fore.BLUE + "[DB]数据库已连接")

        logger.info(Fore.BLUE + "[DB]检查数据表...")

        if not self.check_table("Currency_UserAccount"):
            logger.info(Fore.RED + "[Currency]用户账户数据表不存在 准备创建新数据表")
            try:
                self.cur.execute(
                    "Create Table Currency_UserAccount(uid integer primary key Not Null,LongMenCoin integer check ("
                    "LongMenCoin >=0), Synthetic_Jade integer check (Synthetic_Jade >=0));")
                self.connection.commit()
                logger.info(Fore.RED + "[Currency]Currency_UserAccount表创建成功")
            except sqlite3.DatabaseError as e:
                self.connection.rollback()
                logger.info(Fore.RED + f"[Currency]Currency_UserAccount表创建失败:{e}")

        if not self.check_table("Currency_UserSignIn"):
            logger.info(Fore.RED + "[Currency]用户签到数据表不存在 准备创建新数据表")
            try:
                self.cur.execute(
                    "Create Table Currency_UserSignIn(uid integer primary key Not Null,last_sign_in_time integer,"
                    "continuous_sign_in integer);")
                self.connection.commit()
                logger.info(Fore.RED + "[Currency]Currency_UserSignIn表创建成功")
            except sqlite3.DatabaseError as e:
                self.connection.rollback()
                logger.info(Fore.RED + f"[Currency]Currency_UserSignIn表创建失败:{e}")

        if not self.check_table("ArkRail_User"):
            logger.info(Fore.RED + "[ArkRail]ArkRail_User表不存在 准备创建新数据表")
            try:
                self.cur.execute(
                    "Create Table ArkRail_User(uid integer primary key Not Null,"
                    "                          level integer default 1 check ( level between 1 and 120),"
                    "                          operators_all text,"
                    "                          operators_playing text,"
                    "                          level_progress text"
                    ");")
                self.connection.commit()
                logger.info(Fore.RED + "[ArkRail]ArkRail_User表创建成功")

            except sqlite3.DatabaseError as e:
                self.connection.rollback()
                logger.info(Fore.RED + f"[ArkRail]ArkRail_User表创建失败:{e}")

        if not self.check_table("ArkRail_GachaUser"):
            logger.info(Fore.RED + "[ArkRail]ArkRail_GachaUser表不存在 准备创建新数据表")
            try:
                self.cur.execute(
                    "Create Table ArkRail_GachaUser(uid integer primary key Not Null,"
                    "                          all_pool_num integer,"
                    "                          cur_pool_num integer,"
                    "                          all_pool_6s text,"
                    "                          cur_pool_6s text,"
                    "                          all_pool_5s text,"
                    "                          cur_pool_5s text);")
                self.connection.commit()
                logger.info(Fore.RED + "[ArkRail]ArkRail_GachaUser表创建成功")

            except sqlite3.DatabaseError as e:
                self.connection.rollback()
                logger.info(Fore.RED + f"[ArkRail]ArkRail_GachaUser表创建失败:{e}")

        if not self.check_table("ArkRail_AgarUser"):
            logger.info(Fore.RED + "[ArkRail]ArkRail_AgarUser表不存在 准备创建新数据表")
            try:
                self.cur.execute(
                    "Create Table ArkRail_AgarUser(uid integer primary key Not Null,"
                    "                          agar_num integer,"
                    "                          agar_max_num integer default 160,"
                    "                          is_full integer check ( is_full==0 or is_full==1 ),"
                    "                          full_time integer);")
                self.connection.commit()
                logger.info(Fore.RED + "[ArkRail]ArkRail_AgarUser表创建成功")

            except sqlite3.DatabaseError as e:
                self.connection.rollback()
                logger.info(Fore.RED + f"[ArkRail]ArkRail_AgarUser表创建失败:{e}")
        logger.info(Fore.BLUE + "[DB]数据表检查完成")

    # 检查表是否存在
    def check_table(self, table_name: str) -> bool:

        sql_sequence = f"select tbl_name  from sqlite_master where type='table' and name = '{table_name}';"
        try:
            self.cur.execute(sql_sequence)
            db_list = self.cur.fetchall()
            if not db_list == []:
                return True
            else:
                return False
        except sqlite3.DatabaseError as e:
            logger.info(Fore.RED + f"[DB-check_table]{e}")
            return False

    # 数据库执行
    async def db_execute(self, sql_sentence: str) -> str:
        try:
            self.cur.execute(sql_sentence)
            self.connection.commit()
            return "ok"
        except sqlite3.DatabaseError as e:
            self.connection.rollback()
            return str(e)

    # sql查询,单行
    async def db_query_single(self, sql_sequence: str) -> list:
        result = self.cur.execute(sql_sequence)
        result_list = [row[0] for row in result.fetchall()]
        if not result_list:
            return []
        return list(result_list)

    async def db_query_column(self, sql_sequence: str) -> list:
        result = self.cur.execute(sql_sequence)
        result_list = [row for row in result.fetchall()]
        if not result_list:
            return []
        return list(result_list)[0]

    # sql查询语句，condition为判断条件语句，返回一个字段中符合条件的所有值的列表
    async def find_tb_by_column(self, table_name: str, column: str):
        sql_sequence = f"select {column}  from {table_name};"
        result = self.cur.execute(sql_sequence)
        result_list = [row[0] for row in result.fetchall()]
        return result_list

    def __del__(self):
        self.connection.close()
        logger.info(Fore.BLUE + "[DB]数据库连接已断开")


# 全局数据库对象
MDB = MDataBase(database)
