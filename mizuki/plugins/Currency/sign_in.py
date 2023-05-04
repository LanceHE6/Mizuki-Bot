# -*- coding = utf-8 -*-
# @File:sign_in.py
# @Author:Hycer_Lance
# @Time:2023/5/3 16:26
# @Software:PyCharm

import datetime
from ..database.utils import MDB
from nonebot.log import logger
from nonebot import on_command, on_keyword
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent,MessageSegment
import time
from colorama import Fore

"""
数据库签到表示例
uid:str         last_sign_in_time:int            continuous_sign-in:int
  123            167515463151(时间戳)                       1
"""

sign_in_by_command = on_command("签到", aliases={"打卡"}, block=True, priority=2)
sign_kw=["签到","打卡"]
sign_in_by_message = on_keyword(sign_kw,block=True, rule=to_me(), priority=1)

async def time_to_strftime(stamp_time):
    return time.strftime("%Y-%m-%d", time.localtime(stamp_time))


async def sign_func(event: GroupMessageEvent):
    if not MDB.check_table("UserSignIn"):
        logger.info(Fore.RED + "[Currency]用户数据表不存在 准备创建新数据表")
        result = await MDB.db_execute(
            "Create Table UserSignIn(uid integer primary key Not Null,last_sign_in_time integer,continuous_sign_in integer);")
        if result == 'ok':
            logger.info(Fore.RED + "[Currency]UserSignIn表创建成功")
        else:
            logger.info(Fore.RED + f"[Currency]UserSignIn表创建失败:{result}")

    uid = event.get_user_id()
    uid_list = await MDB.find_tb_by_column("UserSignIn", "uid")
    print(list(uid_list))
    now_time = int(time.time())

    if int(uid) not in uid_list:
        sql_sequence = f"Insert Into UserSignIn(uid, last_sign_in_time, continuous_sign_in) values('{uid}',{now_time},1);"
        if await  MDB.db_execute(sql_sequence) == 'ok':
            logger.info(Fore.BLUE + "[Currency_Sign_in]新用户数据已添加")
            reply = MessageSegment.at(uid) + "签到成功！"
            return reply
        else:
            return "签到出错"
    else:
        # 获取用户在数据库中的信息
        sql_sequence = f"Select * from UserSignIn where uid={uid};"
        user_data = await MDB.db_query(sql_sequence)
        # 获取当前时间和用户上次签到的时间
        last_sign_in_time = await time_to_strftime(user_data[1])
        time_now = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')
        time_last = datetime.datetime.strptime(last_sign_in_time, '%Y-%m-%d')
        # print(time_now, time_last, (time_now - time_last).days)
        sign_days = user_data[2]
        if time_now <= time_last:
            return "你今天已经签到过了哦！明天再来吧！"
        if (time_now - time_last).days == 1:  # 连续签到
            sign_days += 1
        else:  # 断签
            sign_days = 1
        sql_sequence = f"Update UserSignIn Set last_sign_in_time={now_time},continuous_sign_in={sign_days} where uid={uid};"
        if await  MDB.db_execute(sql_sequence) == 'ok':
            logger.info(Fore.BLUE + "[Currency_Sign_in]用户数据已更新")
        else:
            return "签到出错"
        reply = MessageSegment.at(uid) + "签到成功！"
        if sign_days >= 3:
            reply += f"你已连续签到{sign_days}天！"
        return reply

@sign_in_by_message.handle()
async def _(event:GroupMessageEvent):
    reply=await sign_func(event)
    await sign_in_by_message.finish(reply)
@sign_in_by_command.handle()
async def _(event:GroupMessageEvent):
    reply=await sign_func(event)
    await sign_in_by_command.finish(reply)




