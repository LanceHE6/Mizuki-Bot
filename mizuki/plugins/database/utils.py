# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/3 15:53
# @Software:PyCharm

import sqlite3
from pathlib import Path
from nonebot.log import logger
from colorama import Fore

database = Path() / 'database' / 'Mizuki_DB.db'


def check_database():
    logger.info(Fore.BLUE+"[DB]开始检查数据库")
    try:
        connection = sqlite3.Connection(database)
        logger.info(Fore.BLUE+"[DB]数据库连接正常")
        connection.close()
    except sqlite3.DatabaseError as e:
        logger.info(Fore.RED+f"[DB]数据库连接失败:{e}")


class MDataBase:

    def __init__(self, db_file: Path or str):
        check_database()
        self.connection = sqlite3.Connection(db_file)
        self.cur = self.connection.cursor()
        logger.info(Fore.BLUE+"[DB]数据库已连接")

    #检查表是否存在
    def check_table(self, table_name: str)->bool:

        sql_sequence = f"select tbl_name  from sqlite_master where type='table' and name = '{table_name}';"
        try:
            self.cur.execute(sql_sequence)
            db_list = self.cur.fetchall()
            if not db_list==[]:
                return True
            else:
                return False
        except sqlite3.DatabaseError as e:
            logger.info(Fore.RED+f"[DB-check_table]{e}")
            return False

    #数据库执行
    async def db_execute(self, sql_sentence: str)->str:
        try:
            self.cur.execute(sql_sentence)
            self.connection.commit()
            return "ok"
        except sqlite3.DatabaseError as e:
            self.connection.rollback()
            return str(e)

    async def get_cur(self):
        return self.cur
    # sql查询,单行
    async def db_query(self, sql_sequence: str):
        result = self.cur.execute(sql_sequence)
        return result.fetchone()

    #sql查询语句，condition为判断条件语句，返回一个字段中符合条件的所有值的列表
    async def find_tb_by_column(self, table_name: str, column: str):
        sql_sequence = f"select {column}  from {table_name};"
        result=self.cur.execute(sql_sequence)
        result_list = [row[0] for row in result.fetchall()]
        return result_list
    def __del__(self):
        self.connection.close()
        logger.info(Fore.BLUE+"[DB]数据库连接已断开")

#全局数据库对象
MDB = MDataBase(database)