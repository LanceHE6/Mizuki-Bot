# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/11 10:56
# @Software:PyCharm

from colorama import Fore
from pathlib import Path
from nonebot.log import logger
import requests
import json

casual_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'src'
async def get_op_img(oid: int or str, is_big: int = 0):
    """
    从接口获取干员图片并保存到本地
    :param oid: 干员id
    :param is_big: 是否为大立绘
    :return: 图片地址
    """
    op_img_api = f'https://hycerlance.site/api/op_img/?oid={oid}&is_big={is_big}'
    result = json.loads(requests.get(op_img_api).content)
    if result["code"]!=1:
        logger.info(Fore.RED+"干员图片获取出错")
        return
    img = requests.get(result["msg"]).content
    img_path = f"{casual_path}/{oid}.png"
    with open(img_path, "wb") as data:
        data.write(img)
        data.close()
    return img_path
