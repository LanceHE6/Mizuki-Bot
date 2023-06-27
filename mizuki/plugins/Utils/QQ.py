# -*- coding = utf-8 -*-
# @File:QQ.py
# @Author:Hycer_Lance
# @Time:2023/6/20 19:29
# @Software:PyCharm
import re

import requests
from pathlib import Path

temp_path = Path() / "mizuki" / "plugins" / "Utils"

class QQ:
    """
    实现获取QQ信息的一些常用功能
    """
    __qq_api = 'https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins='
    '''
    接口返回数据
    portraitCallBack({"2765543491":["http://qlogo4.store.qq.com/qzone/2765543491/2765543491/100",3993,-1,0,0,0,"Hycer",0]})
    '''

    def __init__(self, uid: int):
        self.qid = uid
        self.__qq_api += str(uid)
        try:
            data = requests.get(self.__qq_api).content
        except requests.exceptions.SSLError:
            data = requests.get(self.__qq_api, verify=False).content
        # 匹配返回的json数据
        pattern = r'portraitCallBack\((.*)\)'
        match = re.search(pattern, str(data))
        if match:
            self.dictionary_data: dict = eval(match.group(1))

    async def get_avatar(self) -> Path:
        """
        获取用户头像
        使用图片后记得删除
        :return: 图片的Path地址
        """
        try:
            img_data = requests.get(self.get_avatar_url()).content
        except requests.exceptions.SSLError:
            img_data = requests.get(self.get_avatar_url(), verify=False).content

        save_path = temp_path / f"{self.qid}_avatar.png"
        with open(save_path, 'wb') as data:
            data.write(img_data)
            data.close()
        return save_path

    def get_avatar_url(self) -> str:
        """
        获取头像网络地址
        :return: url
        """
        return self.dictionary_data[f'{self.qid}'][0]

    def get_nickname(self) -> str:
        """
        获取用户昵称
        :return: 昵称
        """
        return self.dictionary_data[f'{self.qid}'][-2]
