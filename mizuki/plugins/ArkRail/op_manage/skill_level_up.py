# -*- coding = utf-8 -*-
# @File:skill_level_up.py
# @Author:Hycer_Lance
# @Time:2023/5/26 19:14
# @Software:PyCharm

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State

from ...Utils.PluginInfo import PluginInfo
from ..DB import (get_oid_by_name,
                  get_user_all_ops,
                  is_op_owned,
                  change_user_op_skill_level,
                  get_op_attribute,
                  OPAttribute,
                  get_skill_attribute,
                  SkillAttribute)
from ...Currency.utils import get_user_lmc_num, change_user_lmc_num
from .utils import get_cost_skill

skill_level_up = on_command("skill_up", aliases={"技能升级", "升级技能"}, block=True, priority=1)

__plugin_info__ = PluginInfo(
    plugin_name="ArkRail_skill_level_up",
    name="技能升级",
    description="技能升级",
    usage="技能升级<干员名> ——给干员升级技能",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 1
    }
)

@skill_level_up.handle()
async def _(event: GroupMessageEvent, state: T_State, args: Message = CommandArg()):
    name = args.extract_plain_text().replace(' ', '')
    if name == '':
        await skill_level_up.finish("请在指令后跟干员名称", at_sender = True)
    uid = event.get_user_id()
    oid = await get_oid_by_name(name)
    op_name = await get_op_attribute(oid, OPAttribute.name)
    state["op_name"] = op_name
    state["uid"] = uid
    state["oid"] = oid
    #判断干员是否存在
    if oid == -1:
        await skill_level_up.finish(MessageSegment.at(uid)+f"没有找到名为 {name} 的干员")
    #判断用户是否拥有该干员
    if not await is_op_owned(uid, oid):
        await skill_level_up.finish(MessageSegment.at(uid)+"您未拥有该干员")
    user_all_ops = await get_user_all_ops(uid)
    for no in user_all_ops:
        if user_all_ops[no]["oid"] == oid:
            skill_level_list = user_all_ops[no]["skills_level"]
            op_level = user_all_ops[no]["level"]
            skills_list = await get_op_attribute(oid, OPAttribute.skills)
    count = 0
    for skill_level in skill_level_list:
        if skill_level==6:
            count += 1
    if len(skill_level_list) == count:
        await skill_level_up.finish("该干员所有技能均已满级", at_sender = True)
    #插入绘制干员等级图片函数
    user_lmc_num = await get_user_lmc_num(uid)
    state["user_lmc_num"] = user_lmc_num
    state["skill_level_list"] = skill_level_list
    reply = f"{op_name}\n等级:{op_level}\n"
    count = 1
    skill_name_list = []
    for skill_level, skill_type in zip(skill_level_list, skills_list):
        skill_name = await get_skill_attribute(skill_type, SkillAttribute.name)
        skill_name_list.append(skill_name)
        reply += f"\n技能{count}:{skill_name} LV.{skill_level+1}"
        if skill_level == 6:
            reply += "\n已满级"
        else:
            next_cost = await get_cost_skill(skill_level, skill_level)
            reply += f"\n下一级所需龙门币:{next_cost}"
        count += 1
    state["skill_name_list"] = skill_name_list
    await skill_level_up.send(reply+"\n\n请发送需要升级的技能序号以及目标等级", at_sender = True)


@skill_level_up.got("data" ,prompt="")
async def got_level(state: T_State, response = Arg("data")):
    skill_number = 0
    skill_dest_level = 0
    try:
        if isinstance(response, Message):
            skill_number = int(response.extract_plain_text().split(' ')[0])
            skill_dest_level = int(response.extract_plain_text().split(' ')[1])
    except ValueError:
        await skill_level_up.finish("指令参数不全", at_sender = True)
    uid = (state["uid"])
    if skill_number>len(state["skill_level_list"]) or skill_number < 1:
        await skill_level_up.finish("非法技能序号", at_sender = True)
    if skill_dest_level <= int(state["skill_level_list"][skill_number-1]) or skill_dest_level > 7:
        await skill_level_up.finish("非法等级", at_sender = True)
    if int(state["skill_level_list"][skill_number-1]) == 6:
        await skill_level_up.finish("该技能已满级", at_sender = True)
    cost = await get_cost_skill(state["skill_level_list"][skill_number-1], skill_dest_level-1)
    if cost > state["user_lmc_num"]:
        await skill_level_up.finish("龙门币余额不足", at_sender = True)

    await change_user_op_skill_level(uid, state["oid"], skill_number-1, skill_dest_level-1)
    await change_user_lmc_num(uid, -cost)
    await skill_level_up.finish(f"已将 {state['skill_name_list'][skill_number-1]} 升到{skill_dest_level}级\n消耗龙门币:{cost}", at_sender = True)
