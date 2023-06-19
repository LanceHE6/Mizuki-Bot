# -*- coding = utf-8 -*-
# @File:utils.py
# @Author:Hycer_Lance
# @Time:2023/5/16 21:32
# @Software:PyCharm


async def get_cost_op(start_level: int, end_level: int) -> int:
    """
    获取从一个等级升级到另一个等级所需消耗的货币
    :param start_level: 开始等级
    :param end_level: 目标等级
    :return: 总共消耗货币数
    """
    lmc_cost_per_level = [341, 512, 683, 854, 1025, 1196, 1367, 1538, 1709, 1880, 2051, 2222, 2393, 2564, 2735, 2905,
                          3076, 3247, 3418, 3589, 3760, 3931, 4102, 4273, 4444, 4615, 4786, 4957, 5128, 5299, 5470,
                          5641, 5811, 5982, 6153, 6324, 6495, 6666, 6837, 7008, 7179, 7350, 7521, 7692, 7863, 8034,
                          8205, 8376, 8547, 8717, 8888, 9059, 9230, 9401, 9572, 9743, 9914, 10085, 10256, 10427, 10598,
                          10769, 10940, 11111, 11282, 11452, 11623, 11794, 11965, 12136, 12307, 12478, 12649, 12820,
                          12991, 13162, 13333, 13504, 13675, 13846, 14017, 14188, 14358, 14529, 14700, 14871, 15042,
                          15213, 15601]
    total_cost = 0
    for i in range(start_level - 1, end_level - 1):
        total_cost += lmc_cost_per_level[i]

    return total_cost


async def get_cost_skill(start_level: int, end_level: int) -> int:
    """
    获取从一个技能等级升级到另一个技能等级所需消耗的货币
    :param start_level: 开始等级
    :param end_level: 目标等级
    :return: 总共消耗货币数
    """
    lmc_cost_per_level = [5000, 10000, 18000, 28000, 40000, 55000, 70000]
    total_cost = 0
    for i in range(start_level, end_level + 1):
        total_cost += lmc_cost_per_level[i]

    return total_cost


async def str_to_list(string: str) -> list:
    """
    将包含空格的字符串拆分成列表
    :param string: 目标字符串
    :return: 得到的列表
    """
    the_list = []
    word = ''
    for char in string:
        if char != ' ':
            word += char
        else:
            # 去除前后多余空格
            if word == '':
                continue
            the_list.append(word)
            word = ''
    # 处理最后一个单词
    if word != '':
        the_list.append(word)
    return the_list
