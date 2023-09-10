# -*- coding = utf-8 -*-
# @File:skland_sign.py
# @Author:Hycer_Lance
# @Time:2023/9/9 11:09
# @Software:PyCharm

from nonebot import on_command

from .SKLand import SKLand

from ..Utils.GroupAndGuildUtils import GroupAndGuildMessageEvent, GroupAndGuildMessageUtils, GroupAndGuildMessageSegment

arknights_sign_comm = on_command("skl_sign", aliases={"森空岛签到", "方舟签到"}, block=True, priority=2)


@arknights_sign_comm.handle()
async def _(event: GroupAndGuildMessageEvent):
    qid = str(await GroupAndGuildMessageUtils.get_event_user_id(event))
    skland = await SKLand().create_by_qid(qid)
    if skland == -1:
        await arknights_sign_comm.finish("您还未绑定森空岛账号")
    result = await skland.skland_sign()
    if 0 in result:
        reply = ''
        for resource in result[1]:
            reply = f"获得:\n{resource['resource']['name']} x {resource['count']}"
        await arknights_sign_comm.finish(GroupAndGuildMessageSegment.at(event) + "签到成功!\n" + reply)
    elif -1 in result:
        await arknights_sign_comm.finish(GroupAndGuildMessageSegment.at(event) + "您今天已经签过到了哦！")
    elif -3 in result:
        await arknights_sign_comm.finish(
            GroupAndGuildMessageSegment.at(event) + "您的token已过期，请使用绑定指令更换token")
    else:
        await arknights_sign_comm.finish(GroupAndGuildMessageSegment.at(event) + "签到失败！\n" + str(result[1]))
