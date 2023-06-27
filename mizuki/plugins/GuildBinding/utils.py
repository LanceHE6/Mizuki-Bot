# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/6/26 17:09
# @Software:PyCharm

from ...database.utils import MDB


async def get_uid_by_guild_id(guid_id: str) -> int:
    """
    通过频道中的id获取用户QQ号
    :param guid_id:
    :return: uid
    """
    sql = f'Select uid From Guild_QQ_Binding Where guild_id="{guid_id}";'
    result = await MDB.db_query_single(sql)
    if not result:
        return 0
    else:
        return int(result[0])


async def set_guild_bind(uid: int or str, gid: str):
    """
    设置用户频道id与qq号绑定
    :param uid: uid
    :param gid: guild_id
    :return: None
    """
    uid = int(uid)
    sql = f"Select count(*) From Guild_QQ_Binding Where guild_id='{gid}';"
    exists = await MDB.db_query_single(sql)
    exists = int(exists[0])
    if exists:
        change_sql = f"Update Guild_QQ_Binding Set uid={uid} Where guild_id={gid};"
        await MDB.db_execute(change_sql)
    else:
        add_sql = f'Insert Into Guild_QQ_Binding Values("{gid}", {uid});'
        await MDB.db_execute(add_sql)
