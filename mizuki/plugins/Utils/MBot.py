# -*- coding = utf-8 -*-
# @File:MBot.py
# @Author:Hycer_Lance
# @Time:2023/6/13 15:42
# @Software:PyCharm

from nonebot.adapters.onebot.v11 import Bot

class MBot:

    def __init__(self, bot: Bot):
        self.__bot__ = bot

    def get_bot(self) -> Bot:
        return self.__bot__

    async def get_online_clients(self, no_cache: bool = True):
        """
        获取当前账号在线客户端列表
        :param no_cache: 无视缓存
        :return: clients	Device[]	在线客户端列表
        """
        return await self.__bot__.call_api("get_online_clients", no_cache=no_cache)

    async def delete_friend(self, uid: int or str):
        """
        删除好友
        :param uid: qq号
        :return: None
        """
        await self.__bot__.call_api("delete_friend", user_id=int(uid))

    async def get_forward_msg(self, message_id: str):
        """
        获取合并转发内容
        :param message_id: 消息ID
        :return: messages	forward message[]	消息列表
        """
        return await self.__bot__.call_api("get_forward_msg", message_id=message_id)

    async def send_group_forward_msg(self, group_id: int, messages: list):
        """
        发送合并转发 ( 群聊 )
        :param group_id:目标群号
        :param messages: 自定义转发消息，详情请看CQ码
        :return:
        message_id	int64	消息 ID
        forward_id	string	转发消息 ID
        """
        return await self.__bot__.call_api("send_group_forward_msg", group_id=group_id, messages=messages)

    async def send_private_forward_msg(self, user_id: int, messages: list):
        """
        发送合并转发 ( 群聊 )
        :param user_id:目标群号
        :param messages: 自定义转发消息，详情请看CQ码
        :return:
        message_id	int64	消息 ID
        forward_id	string	转发消息 ID
        """
        return await self.__bot__.call_api("send_private_forward_msg", user_id=user_id, messages=messages)

    async def get_group_msg_history(self, message_seq: int, group_id: int):
        """
        获取群消息历史记录
        不提供起始序号将默认获取最新的消息
        :param message_seq: 起始消息序号, 可通过 get_msg 获得
        :param group_id: 群号
        :return: Message[]	从起始序号开始的前19条消息
        """
        return await self.__bot__.call_api("get_group_msg_history", message_seq=message_seq, group_id=group_id)

    async def get_group_system_msg(self):
        """
        获取群系统消息
        :return:
        invited_requests	InvitedRequest[]	邀请消息列表
        join_requests	JoinRequest[]	进群消息列表
        如果列表不存在任何消息, 将返回 null
        """
        return await self.__bot__.call_api("get_group_system_msg")

    async def get_essence_msg_list(self, group_id: int):
        """
        获取精华消息列表
        :param group_id: 群号
        :return: 响应内容为 JSON 数组
        """
        await self.__bot__.call_api("get_essence_msg_list", group_id=group_id)

    async def get_group_at_all_remain(self, group_id: int):
        """
        获取群 @全体成员 剩余次数
        :param group_id: 群号
        :return:
        can_at_all	bool	是否可以 @全体成员
        remain_at_all_count_for_group	int16	群内所有管理当天剩余 @全体成员 次数
        remain_at_all_count_for_uin	int16	Bot 当天剩余 @全体成员 次数
        """
        return await self.__bot__.call_api("get_group_at_all_remain", group_id=group_id)

    async def set_essence_msg(self, message_id: int):
        """
        设置精华消息
        :param message_id: 消息ID
        :return: None
        """
        await self.__bot__.call_api("set_essence_msg", message_id=message_id)

    async def delete_essence_msg(self, message_id: int):
        """
        移除精华消息
        :param message_id: 消息ID
        :return: None
        """
        await self.__bot__.call_api("delete_essence_msg", message_id=message_id)

    async def send_group_sign(self, group_id: int):
        """
        群打卡
        :param group_id: 群号
        :return: None
        """
        await self.__bot__.call_api("send_group_sign", group_id=group_id)

    async def send_group_notice(self, group_id: int, content: str, image: str = None):
        """
        发送群公告
        :param group_id: 群号
        :param content: 公告内容
        :param image: 图片地址（可选）
        :return: None
        """
        await self.__bot__.call_api("_send_group_notice", group_id=group_id, content=content, image=image)

    async def get_group_notice(self, group_id: int):
        """
        获取群公告
        :param group_id: 群号
        :return:
        响应内容为 json 数组，每个元素内容如下：
        """
        return await self.__bot__.call_api("_get_group_notice", group_id=group_id)

    async def upload_group_file(
            self,
            group_id: int,
            file: str,
            name: str,
            folder: str = None
    ):
        """
        上传群文件
        在不提供 folder 参数的情况下默认上传到根目录
        :param group_id: 群号
        :param file: 本地文件路径
        :param name: 储存名称
        :param folder: 父目录ID
        :return: None
        """
        await self.__bot__.call_api(
            "upload_group_file",
            group_id=group_id,
            file=file,
            name=name,
            folder=folder
        )

    async def delete_group_file(self, group_id: int, file_id: str, bus_id: int):
        """
        删除群文件
        :param group_id: 群号
        :param file_id: 文件ID
        :param bus_id: 文件类型
        :return: None
        """
        await self.__bot__.call_api("delete_group_file", group_id=group_id, file_id=file_id, busid=bus_id)