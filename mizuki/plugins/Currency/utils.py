# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/5 17:10
# @Software:PyCharm

from ...database.utils import MDB


# 判断用户是否在Currency_UserAccount表中
async def is_user_in_table(uid: int or str) -> bool:
    uid_list = await MDB.find_tb_by_column("Currency_UserAccount", "uid")
    # 初始6000合成玉
    if int(uid) not in uid_list:
        sql_sequence = f"Insert Into Currency_UserAccount(uid, LongMenCoin, Synthetic_Jade) values('{uid}',0,6000);"
        await MDB.db_execute(sql_sequence)
        return False
    else:
        return True


# 返回用户账户龙门币数量
async def get_user_lmc_num(uid: int or str) -> int:
    if not await is_user_in_table(uid):
        return 0
    sql_sequence = f"Select LongMenCoin from Currency_UserAccount where uid={uid};"
    account_num = await MDB.db_query_single(sql_sequence)
    return int(account_num[0])


async def lmc_is_enough(uid: int or str, num: int) -> bool:
    account_num = await get_user_lmc_num(uid)
    if account_num >= num:
        return True
    else:
        return False


# 更改用户账户中龙门币数量，返回更改状态结果,正数为增加，负数为减少
async def change_user_lmc_num(uid: int or str, num: int) -> str:
    # 判断是否有用户数据
    if await is_user_in_table(uid):
        # 判断是否为消费货币
        if num < 0:
            if not await lmc_is_enough(uid, -num):
                return "账户余额不足"
        # account_num = await get_user_lmc_num(uid) + num
        sql_sequence = f"Update Currency_UserAccount Set LongMenCoin=LongMenCoin+{num} where uid={uid};"
        result = await MDB.db_execute(sql_sequence)
    else:
        if num < 0:
            return "账户余额不足"
        # account_num = await get_user_lmc_num(uid) + num
        sql_sequence = f"Update Currency_UserAccount Set LongMenCoin=LongMenCoin+{num} where uid={uid};"
        result = await MDB.db_execute(sql_sequence)
    return result


# 返回用户账户合成玉数量
async def get_user_sj_num(uid: int or str) -> int:
    if not await is_user_in_table(uid):
        return 0
    sql_sequence = f"Select Synthetic_Jade from Currency_UserAccount where uid={uid};"
    account_num = await MDB.db_query_single(sql_sequence)
    return int(account_num[0])


async def sj_is_enough(uid: int or str, num: int) -> bool:
    account_num = await get_user_sj_num(uid)
    if account_num >= num:
        return True
    else:
        return False


# 更改用户账户中合成玉数量，返回更改状态结果,正数为增加，负数为减少
async def change_user_sj_num(uid: int or str, num: int) -> str:
    # 判断是否有用户数据
    if await is_user_in_table(uid):
        # 判断是否为消费货币
        if num < 0:
            if not await sj_is_enough(uid, -num):
                return "账户余额不足"
        # account_num = await get_user_lmc_num(uid) + num
        sql_sequence = f"Update Currency_UserAccount Set Synthetic_Jade=Synthetic_Jade+{num} where uid={uid};"
        result = await MDB.db_execute(sql_sequence)
    else:
        if num < 0:
            return "账户余额不足"
        # account_num = await get_user_lmc_num(uid) + num
        sql_sequence = f"Update Currency_UserAccount Set Synthetic_Jade=Synthetic_Jade+{num} where uid={uid};"
        result = await MDB.db_execute(sql_sequence)
    return result
