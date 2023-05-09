# -*- coding = utf-8 -*-
# @File:account.py
# @Author:Hycer_Lance
# @Time:2023/5/5 16:49
# @Software:PyCharm
import json
from string import Template
from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from colorama import Fore
import requests
from .utils import is_user_in_table, get_user_lmc_num, get_user_sj_num

my_account = on_command("account", aliases={"我的账户", "账户"}, block=True, priority=2)

#获取用户qq头像地址及昵称    ——糖豆子api
qq_info_api =Template("http://api.tangdouz.com/qq.php?qq=${uid}")

@my_account.handle()
async def _(event: GroupMessageEvent):
    uid = int(event.get_user_id())
    headers = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0 Win64; x64)"
    }
    # 用户首次使用指令，添加信息进数据库
    check = await is_user_in_table(uid)
    if not check:
        logger.info(Fore.BLUE + "[Currency_Account]新用户数据已添加")

    # 获取用户在数据库中的信息
    qq_info = json.loads(requests.get(url=qq_info_api.substitute(uid= uid), headers=headers).content)
    if qq_info["code"] != 1:
        await my_account.finish("获取用户信息失败，请稍后再试")
    print(qq_info)
    nick_name = qq_info["name"]
    qq_img = qq_info["imgurl"]
    lmc_num = await get_user_lmc_num(uid)
    sj_num = await get_user_sj_num(uid)

    await my_account.finish(MessageSegment.at(uid) + f"\n{nick_name}的账户\n\n龙门币:{lmc_num}\n合成玉:{sj_num}")

