# -*- coding = utf-8 -*-
# @File:QQ.py
# @Author:Hycer_Lance
# @Time:2023/6/20 19:29
# @Software:PyCharm

import requests
from pathlib import Path

temp_path = Path() / "mizuki" / "plugins" / "Utils"

class QQ:
    """
    实现QQ的一些常用功能
    """
    __qq_avatar_api = 'https://q1.qlogo.cn/g?b=qq&nk={uid}&s=640'

    def __init__(self, uid: int):
        self.qid = uid
        self.__qq_avatar_api = self.__qq_avatar_api.replace("{uid}", str(uid))

    async def get_avatar(self) -> Path:
        """
        获取用户头像
        使用图片后记得删除
        :return: 图片的Path地址
        """
        try:
            img_data = requests.get(self.__qq_avatar_api).content
        except requests.exceptions.SSLError:
            img_data = requests.get(self.__qq_avatar_api, verify=False).content
        save_path = temp_path / f"{self.qid}_avatar.png"
        with open(save_path, 'wb') as data:
            data.write(img_data)
            data.close()
        return save_path
