# -*- coding = utf-8 -*-
# @File:MBot.py
# @Author:Hycer_Lance
# @Time:2023/6/13 15:42
# @Software:PyCharm

from nonebot.adapters.onebot.v11 import Bot

class MBot:
    """
    通过go-cqhttp api 实现的Bot功能拓展类

    func:

    get_online_clients
    获取当前账号在线客户端列表

    delete_friend
    删除好友

    get_forward_msg
    获取转发消息内容

    send_group_forward_msg
    发送群转发消息

    send_private_forward_msg
    发送私聊转发消息

    get_group_msg_history
    获取群历史消息

    get_group_system_msg
    获取群系统消息

    get_essence_msg_list
    获取群精华消息列表

    get_group_at_all_remain
    获取群 @全体成员 剩余次数

    set_essence_msg
    设置精华消息

    delete_essence_msg
    删除精华消息

    send_group_sign
    发送群打卡

    send_group_notice
    发送群公告

    get_group_notice
    获取群公告

    upload_group_file
    上传群文件

    delete_group_file
    删除群文件

    create_group_file_folder
    创建群文件夹

    delete_group_folder
    删除群文件夹

    get_group_file_system_info
    获取群文件系统信息

    get_group_root_files
    获取群文件根目录列表

    get_group_files_by_folder
    获取群子目录文件列表

    get_group_file_url
    获取群文件资源链接

    upload_private_file
    上传私聊文件

    check_url_safely
    检查链接安全性
    """

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
        file 和 folder属性详情请参考 https://docs.go-cqhttp.org/api/
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
        file 和 folder属性详情请参考 https://docs.go-cqhttp.org/api/
        :param group_id: 群号
        :param file_id: 文件ID
        :param bus_id: 文件类型
        :return: None
        """
        await self.__bot__.call_api("delete_group_file", group_id=group_id, file_id=file_id, busid=bus_id)

    async def create_group_file_folder(self, group_id: int, name: str):
        """
        创建群文件夹
        :param group_id: 群号
        :param name: 文件夹名字
        :return: None
        """
        await self.__bot__.call_api("create_group_file_folder", group_id=group_id, name=name, parent_id="/")

    async def delete_group_folder(self, group_id: int, folder_id: int):
        """
        删除群文件夹
        file 和 folder属性详情请参考 https://docs.go-cqhttp.org/api/
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :return: None
        """
        await self.__bot__.call_api("delete_group_folder", group_id=group_id, folder_id=folder_id)

    async def get_group_file_system_info(self, group_id: int):
        """
        获取群文件系统信息
        :param group_id: 群号
        :return:
        file_count	int32	文件总数
        limit_count	int32	文件上限
        used_space	int64	已使用空间
        total_space	int64	空间上限
        """
        return await self.__bot__.call_api("get_group_file_system_info", group_id=group_id)

    async def get_group_root_files(self, group_id):
        """
        获取群根目录文件列表
        :param group_id: 群号
        :return:
        files	File[]	文件列表
        folders	Folder[]	文件夹列表
        """
        return await self.__bot__.call_api("get_group_root_files", group_id=group_id)

    async def get_group_files_by_folder(self, group_id: int, folder_id: int):
        """
        获取群子目录文件列表
        file 和 folder属性详情请参考 https://docs.go-cqhttp.org/api/
        :param group_id: 群号
        :param folder_id: 文件夹ID
        :return:
        files	File[]	文件列表
        folders	Folder[]	文件夹列表
        """
        return await self.__bot__.call_api("get_group_files_by_folder", group_id=group_id, folder_id=folder_id)

    async def get_group_file_url(self, group_id: int, file_id: int, bus_id: int) -> str:
        """
        获取群文件资源链接
        file 和 folder属性详情请参考 https://docs.go-cqhttp.org/api/
        :param group_id: 群号
        :param file_id: 文件ID
        :param bus_id: 文件类型
        :return: url 文件下载链接
        """
        return await self.__bot__.call_api("get_group_file_url", group_id=group_id, file_id=file_id, busid=bus_id)

    async def upload_private_file(self, user_id: int, file: str, name: str):
        """
        上传私聊文件
        :param user_id: 对方QQ
        :param file: 本地文件路径
        :param name: 文件名称
        :return: None
        """
        await self.__bot__.call_api("upload_private_file", user_id=user_id, file=file, name=name)

    # async def get_cookies(self, domain: str = None) -> str:
    #     """
    #     获取 Cookies
    #     :param domain: 需要获取 cookies 的域名
    #     :return: Cookies
    #     """
    #     return await self.__bot__.call_api("get_cookies", domain=domain)

    async def check_url_safely(self, url: str) -> int:
        """
        检查链接安全性
        :param url: 需要检查的链接
        :return: 安全等级, 1: 安全 2: 未知 3: 危险
        """
        return await self.__bot__.call_api("check_url_safely", url=url)
