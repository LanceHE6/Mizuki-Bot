# -*- coding = utf-8 -*-
# @File:auto_sign.py
# @Author:Hycer_Lance
# @Time:2023/9/10 15:45
# @Software:PyCharm

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot import get_bot
from nonebot.log import logger
from nonebot.adapters.onebot.v11.exception import ActionFailed

from nonebot_plugin_apscheduler import scheduler

from .database import SKLandDB
from .SKLand import SKLand
from ..Utils.GroupAndGuildUtils import (GroupAndGuildMessageSegment,
                                        GroupAndGuildMessageEvent,
                                        GroupAndGuildMessageUtils,
                                        GroupAndGuildMessage)
from ..Help.PluginInfo import PluginInfo

auto_sign = on_command("森空岛自动签到", aliases={"skl自动签到"}, block=True, priority=3)

__plugin_info__ = PluginInfo(
    plugin_name="SKLand_auto_sign",
    name="森空岛自动签到",
    description="森空岛自动签到",
    usage="森空岛自动签到 [on/off] ——打开/关闭自动签到",
    extra={
        "author": "Hycer_Lance",
        "version": "1.0.0",
        "priority": 2,
        "guild_adapted": True
    }
)


async def get_user_auto_sign_status(qid: int):
    """
    获取用户的自动签到开关状态
    :param qid: uid
    :return: 1为开启自动签到, 0为关闭自动签到, -1为不存在此用户
    """
    if await SKLandDB.is_user_exist(str(qid)):
        sql_sequence = f"select is_auto_sign from SKLand_User where qid={qid};"
        result = (await SKLandDB.db_query_single(sql_sequence))[0]
        if result == 1:
            return 1
        else:
            return 0
    else:
        return -1


async def set_user_auto_sign_status(qid: int, status: bool):
    """
    设置用户自动签到开关状态
    :param qid: uid
    :param status: True 开启自动签到 False 关闭自动签到
    :return: 0 更改失败 1 更改成功 -1 不存在此用户  2状态未改变
    """
    current_status = await get_user_auto_sign_status(qid)
    if not current_status == -1:
        status = 1 if status else 0
        if status == current_status:
            return 2
        sql_sequence = f"update SKLand_User set is_auto_sign={status} where qid={qid};"
        result = await SKLandDB.db_execute(sql_sequence)
        if result == 'ok':
            return 1
        else:
            return 0
    else:
        return -1


@auto_sign.handle()
async def _(event: GroupAndGuildMessageEvent, status: GroupAndGuildMessage = CommandArg()):
    status = status.extract_plain_text()
    qid = await GroupAndGuildMessageUtils.get_event_user_id(event)
    if status == "":
        current_status = await get_user_auto_sign_status(qid)
        if current_status == -1:
            await auto_sign.finish(GroupAndGuildMessageSegment.at(event) + "您还未绑定森空岛账号哦！")
        await auto_sign.finish(GroupAndGuildMessageSegment.at(event) +
                               f"您的森空岛自动签到{'已' if current_status == 1 else '未'}开启")
    elif status in ["on", "开"]:
        status = True
    elif status in ["off", "关"]:
        status = False
    else:
        await auto_sign.finish(GroupAndGuildMessageSegment.at(event) + "未知参数")
    result = await set_user_auto_sign_status(qid, status)
    if result == -1:
        await auto_sign.finish(GroupAndGuildMessageSegment.at(event) + "您还未绑定森空岛账号哦！")
    elif result == 0:
        await auto_sign.finish(GroupAndGuildMessageSegment.at(event) + "更改失败,请检查报错信息")
    elif result == 2 or 1:
        await auto_sign.finish(
            GroupAndGuildMessageSegment.at(event) + f"森空岛自动签到已{'开启' if status else '关闭'}")


@scheduler.scheduled_job("cron", hour="*/23")
async def _():
    logger.info("[SKLand_auto_sign]开始执行自动签到")
    bot = get_bot()
    qid_list = await SKLandDB.find_tb_by_column(table_name="SKLand_User", column="qid")
    for qid in qid_list:
        if await get_user_auto_sign_status(int(qid)) == 1:
            await bot.send_private_msg(user_id=qid, message="正在为您执行森空岛自动签到")
            skland = await SKLand().create_by_qid(qid)
            result = await skland.skland_sign()
            try:
                if 0 in result:
                    reply = ''
                    for resource in result[1]:
                        reply = f"获得:\n{resource['resource']['name']} x {resource['count']}"
                    await bot.send_private_msg(user_id=qid, message="签到成功!\n" + reply)
                elif -1 in result:
                    await bot.send_private_msg(user_id=qid, message="您今天已经签过到了哦！")
                elif -3 in result:
                    await bot.send_private_msg(
                        user_id=qid, message="您的token已过期，请使用绑定指令更换token")
                else:
                    await bot.send_private_msg(user_id=qid, message="签到失败！\n" + str(result[1]))
            except ActionFailed:
                logger.info("[SKLand_auto_sign]非bot好友不发送私聊提醒消息")
    logger.info("[SKLand_auto_sign]自动签到执行完成")
