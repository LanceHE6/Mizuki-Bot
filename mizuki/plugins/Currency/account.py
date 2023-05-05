# -*- coding = utf-8 -*-
# @File:account.py
# @Author:Hycer_Lance
# @Time:2023/5/5 16:49
# @Software:PyCharm

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent,MessageSegment
from colorama import Fore
from ...database.utils import MDB
from .utils import is_user_in_table

my_account = on_command("account", aliases={"龙门币","lmb","我的账户","我的龙门币"}, block=True, priority=2)

@my_account.handle()
async def _(event: GroupMessageEvent):


    uid = event.get_user_id()

    #用户首次使用指令，添加信息进数据库
    if not await is_user_in_table(uid):
        sql_sequence = f"Insert Into Currency_UserAccount(uid, account_num) values('{uid}',0);"
        if await  MDB.db_execute(sql_sequence) == 'ok':
            logger.info(Fore.BLUE + "[Currency_Account]新用户数据已添加")
            await my_account.finish(MessageSegment.at(uid) + f"你的账户中共有0龙门币")
        else:
            await my_account.finish("新账户数据添加失败")
    else:
        # 获取用户在数据库中的信息
        sql_sequence = f"Select account_num from Currency_UserAccount where uid={uid};"
        account_num = await MDB.db_query(sql_sequence)
        await my_account.finish(MessageSegment.at(uid)+f"你的账户中共有{account_num[0]}龙门币")