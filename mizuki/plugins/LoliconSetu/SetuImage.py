# -*- coding = utf-8 -*-
# @File:SetuImage.py
# @Author:Hycer_Lance
# @Time:2023/6/12 20:41
# @Software:PyCharm

class SetuImage:

    __r18: bool = None,
    __pid: str = None,
    __uid: str = None,
    __title: str = None,
    __author: str = None,
    __width: int = None,
    __height: int = None,
    __tags: list = None,
    __ext: str = None,
    __aiType: bool = None,
    __uploadDate: int = None,
    __url: str = None

    def __init__(self,
                 r18: bool,
                 pid: str,
                 uid: str,
                 title: str,
                 author: str,
                 width: int,
                 height: int,
                 tags: list,
                 ext: str,
                 ai_type: bool,
                 upload_date: int,
                 url: str
                 ):
        """
        构造一个setu实例
        :param r18: 是否为r18
        :param pid: 作品pid
        :param uid: 作者uid
        :param title: 作品标题
        :param author: 作者名
        :param width: 图片宽度
        :param height: 图片高度
        :param tags: 图片tags
        :param ext: 图片格式
        :param ai_type: 是否为ai作品
        :param upload_date: 上传日期
        :param url: 图片地址
        """
        self.__r18 = r18
        self.__pid = pid
        self.__uid = uid
        self.__title = title
        self.__author = author
        self.__width = width
        self.__height = height
        self.__tags = tags
        self.__ext = ext
        self.__aiType = ai_type
        self.__uploadDate = upload_date
        self.__url = url

    async def get_r18(self) -> bool:
        return self.__r18

    async def get_pid(self) -> str:
        return self.__pid

    async def get_uid(self) -> str:
        return self.__uid

    async def get_title(self) -> str:
        return self.__title

    async def get_author(self) -> str:
        return self.__author

    async def get_width(self) -> int:
        return self.__width

    async def get_height(self) -> int:
        return self.__height

    async def get_tags(self) -> list:
        return self.__tags

    async def get_ext(self) -> str:
        return self.__ext

    async def get_ai_type(self) -> bool:
        return self.__aiType

    async def get_upload_date(self) -> int:
        return self.__uploadDate

    async def get_url(self) -> str:
        return self.__url
    