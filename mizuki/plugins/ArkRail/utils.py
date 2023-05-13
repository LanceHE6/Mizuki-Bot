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

async def get_op_model(oid: int or str, is_back: int = 0):
    """
    从接口获取干员m模型并保存到本地
    :param oid: 干员id
    :param is_back: 是否为背面
    :return: 图片地址
    """
    op_model_api = f'https://hycerlance.site/api/op_models/?oid={oid}&is_back={is_back}'
    result = json.loads(requests.get(op_model_api).content)
    if result["code"]!=1:
        logger.info(Fore.RED+"干员模型获取出错")
        return
    img = requests.get(result["msg"]).content
    img_path = f"{casual_path}/{oid}.png"
    with open(img_path, "wb") as data:
        data.write(img)
        data.close()
    return img_path

async def line_break(line: str, line_count: int)-> str:
    """
    实现在字符串固定字符数后添加换行符
    :param line: 待处理字符串
    :param line_count: 在line_count个字后换行
    :return: 处理后的字符串
    """
    line_char_count = line_count * 2  # 每行字符数：12个中文字符
    table_width = 4
    ret = ''
    width = 0
    for c in line:
        if len(c.encode('utf8')) == 3:  # 中文
            if line_char_count == width + 1:  # 剩余位置不够一个汉字
                width = 2 #挪到下一行
                ret += '\n' + c
            else: # 中文宽度加2，注意换行边界
                width += 2
                ret += c
        else:
            if c == '\t':
                space_c = table_width - width % table_width  # 已有长度对TABLE_WIDTH取余
                ret += ' ' * space_c
                width += space_c
            elif c == '\n':
                width = 0
                ret += c
            else:
                width += 1
                ret += c
        if width >= line_char_count:
            ret += '\n'
            width = 0
    if ret.endswith('\n'):
        return ret
    return ret + '\n'