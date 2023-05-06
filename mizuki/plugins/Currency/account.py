# -*- coding = utf-8 -*-
# @File:account.py
# @Author:Hycer_Lance
# @Time:2023/5/5 16:49
# @Software:PyCharm

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from colorama import Fore
from ...database.utils import MDB
from .utils import is_user_in_table

my_account = on_command("account", aliases={"我的账户", "账户"}, block=True, priority=2)


@my_account.handle()
async def _(event: GroupMessageEvent):
    uid = int(event.get_user_id())

    # 用户首次使用指令，添加信息进数据库
    check = await is_user_in_table(uid)
    if not check:
        logger.info(Fore.BLUE + "[Currency_Account]新用户数据已添加")

    # 获取用户在数据库中的信息
    sql_sequence1 = f"Select LongMenCoin from Currency_UserAccount where uid={uid};"
    lmc_num = await MDB.db_query_column(sql_sequence1)
    sql_sequence2 = f"Select Synthetic_Jade from Currency_UserAccount where uid={uid};"
    sj_num = await MDB.db_query_column(sql_sequence2)
    await my_account.finish(MessageSegment.at(uid) + f"\n你的账户\n\n龙门币:{lmc_num[0]}\n合成玉:{sj_num[0]}")

