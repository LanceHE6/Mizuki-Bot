from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment as GroupMessageSegment
from nonebot.adapters.qqguild import MessageSegment as GuildMessageSegment
from nonebot.adapters.qqguild import MessageEvent as GuildMessageEvent
from nonebot.adapters.onebot.v11 import GroupMessageEvent as GroupMessageEvent

from .GroupAndGuildMessageEvent import GroupAndGuildMessageEvent


class GroupAndGuildMessageSegment:

    @staticmethod
    def at(event: GroupAndGuildMessageEvent, uid: int = 0):
        """
        @成员消息生成

        :param event: 事件，用于判断是群事件还是频道事件
        :param uid: 用户id(不填默认@event发起者)
        :return: MessageSegment
        """
        if uid == 0:
            uid = event.get_user_id()
        if isinstance(event, GuildMessageEvent):
            message = GuildMessageSegment.mention_user(uid)
        else:
            message = GroupMessageSegment.at(uid)

        return message

    @staticmethod
    def image(event, path, is_url: bool = False):
        """
        图片消息生成

        :param event: 事件，用于判断是群事件还是频道事件
        :param path: 图片路径或图片url
        :param is_url: 是否为网络图片，默认为False
        :return: MessageSegment
        """
        if isinstance(event, GuildMessageEvent):
            img = GuildMessageSegment.file_image(path) if not is_url else GuildMessageSegment.image(path)
        else:
            img = GroupMessageSegment.image(path)

        return img
