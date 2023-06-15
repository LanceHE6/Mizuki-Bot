# -*- coding = utf-8 -*-
# @File:Lolicon.py
# @Author:Hycer_Lance
# @Time:2023/6/12 19:46
# @Software:PyCharm

import json
import os

import requests
import time

from pathlib import Path
from .SetuImage import SetuImage

setu_path = Path() / os.path.abspath(os.path.dirname(__file__)) / 'setu'

class Lolicon:
    __LOLICON_API: str = "https://api.lolicon.app/setu/v2"
    __HEADERS: dict = {
        "Content-Type": "application/json"
    }

    def __init__(self,
                 r18: bool = False,
                 num: int = 1,
                 tag: list = None,
                 keyword: str = None,
                 size: list = None,
                 proxy: str = "i.pixiv.re"
                 ):
        """
        根据参数构造一个lolicon实例
        :param r18: r18开关
        :param num: 获取的图片数量
        :param tag: tag["猫娘","可爱"]
        :param keyword: 关键字
        :param size: 图片大小
        :param proxy: 代理地址
        """
        if size is None:
            size = ["original"]
        self.__data: dict = {
            "r18": 1 if r18 else 0,
            "num": num,
            "keyword": keyword,
            "tag": tag,
            "size": size,
            "proxy": proxy
        }
        self.__setu_list: list[SetuImage] = []

    async def get_image(self) -> list[SetuImage] or str:
        """
        依据构造的数据获取图片
        :return: 包含SetuImage对象的列表， 若为str则发生请求错误
        """
        self.__setu_list = []
        response = json.loads(requests.post(
            url=self.__LOLICON_API,
            headers=self.__HEADERS,
            data=json.dumps(self.__data)
        ).content)
        # 请求出错
        if response["error"] != "":
            return response["error"]
        for img_data in response["data"]:
            r18 = img_data["r18"]
            pid = img_data["pid"]
            uid = img_data["uid"]
            title = img_data["title"]
            author = img_data["author"]
            width = img_data["width"]
            height = img_data["height"]
            tags = img_data["tags"]
            ext = img_data["ext"]
            ai_type = img_data["aiType"]
            upload_date = img_data["uploadDate"]
            url = img_data["urls"]["original"]
            setu_image = SetuImage(
                r18,
                pid,
                uid,
                title,
                author,
                width,
                height,
                tags,
                ext,
                ai_type,
                upload_date,
                url
            )
            self.__setu_list.append(setu_image)
        return self.__setu_list

    async def get_path(self) -> list[Path] or str:
        """
        下载图片并返回本地地址
        :return: 包含Path对象的列表， 若为str则发生请求错误
        """
        setu_path_list: list[Path] = []
        if len(self.__setu_list) == 0:
            self.__setu_list = await self.get_image()
            if isinstance(self.__setu_list, str):
                return self.__setu_list
        for setu in self.__setu_list:
            now_time = int(time.time())
            setu_image_path = setu_path / f"{now_time}.{await setu.get_ext()}"
            setu_data = requests.get(url=await setu.get_url()).content
            with open(setu_image_path, "wb") as data:
                data.write(setu_data)
                data.close()
            setu_path_list.append(setu_image_path)
        return setu_path_list
