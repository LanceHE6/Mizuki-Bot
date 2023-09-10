# -*- coding = utf-8 -*-
# @File:database.py 
# @Author:Hycer_Lance
# @Time:2023/9/7 20:12
# @Software:PyCharm

import os
import sqlite3
from pathlib import Path
from nonebot.log import logger
from colorama import Fore

database_path = Path() / 'mizuki' / 'plugins' / 'SKLand' / 'data'
database = database_path / 'SKLand.db'


def check_database():
    logger.info(Fore.BLUE + "[SKLandDB]检查数据库...")
    if not os.path.exists(database_path):
        os.mkdir(database_path)
    try:
        connection = sqlite3.Connection(database)
        logger.info(Fore.BLUE + "[SKLandDB]数据库连接正常")
        connection.close()
    except sqlite3.DatabaseError as e:
        logger.info(Fore.RED + f"[SKLandDB]数据库连接失败:{e}")


class SKLandDataBase:

    def __init__(self, db_file: Path or str):
        check_database()
        self.connection = sqlite3.Connection(db_file)
        self.cur = self.connection.cursor()
        logger.info(Fore.BLUE + "[SKLandDB]数据库已连接")

        logger.info(Fore.BLUE + "[SKLandDB]检查数据表...")

        if not self.check_table("SKLand_User"):
            """
            森空岛相关数据表
            """
            logger.info(Fore.RED + "[SKLand_User]森空岛用户数据表不存在 准备创建新数据表")
            try:
                self.cur.execute(
                    "Create Table SKLand_User(qid integer primary key Not Null, token text, cred text, binding text, "
                    "arknights_roles text, binding_arknights_role text, is_auto_sign int default 0);")
                self.connection.commit()
                logger.info(Fore.GREEN + "[SKLand_User]SKLand_User表创建成功")
            except sqlite3.DatabaseError as e:
                self.connection.rollback()
                logger.info(Fore.RED + f"[SKLand_User]SKLand_User:{e}")

        logger.info(Fore.BLUE + "[SKLandDB]数据表检查完成")

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
            logger.info(Fore.RED + f"[SKLandDB-check_table]{e}")
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

    async def is_user_exist(self, uid: str):
        """
        判断用户是否在用户表中
        :param uid: 用户qq号
        :return: True 存在
        """
        sql_sequence = f"select count(*) from SKLand_User where qid={uid};"
        result = await self.db_query_single(sql_sequence)
        if result[0] == 0:
            return False
        return True

    def __del__(self):
        self.connection.close()
        logger.info(Fore.BLUE + "[SKLandDB]数据库连接已断开")


# 全局数据库对象
SKLandDB = SKLandDataBase(database)
