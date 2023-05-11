import random

from .operator import Operator, get_operator_list, get_enemies_list


class PlayingManager:

    def __init__(self, player_ops_list: list[Operator], map_enemies_list: list[Operator]):
        self.player_ops_list = player_ops_list  # 玩家干员列表
        self.map_enemies_list = map_enemies_list  # 敌方干员列表
        self.all_ops_list = player_ops_list + map_enemies_list  # 所有干员列表，用于计算干员出手顺序
        quick_sort(self.all_ops_list, 0, len(self.all_ops_list) - 1)  # 根据速度做快速排序

        self.player_skill_count = 20  # 我方初始技力点
        self.enemy_skill_count = 10  # 敌方初始技力点

    async def count(self, sub: Operator, operate: int, obj1: Operator, obj2: Operator = None):
        """
        干员的一个回合

        :param sub: 行动者
        :param operate: 操作序号 0普攻 1-3技能
        :param obj1: 目标对象1
        :param obj2: 目标对象2(可选)
        """
        if sub in self.player_ops_list:  # 我方干员回合
            if operate == 0:
                await sub.attack(obj1)
                self.player_skill_count += 5  # 普攻回复5技力点
            elif operate in [1, 2, 3]:
                await sub.use_skill(sub.skills_list[operate - 1], obj1, obj2)
                self.player_skill_count -= sub.skills_list[operate - 1].consume  # 使用技能消耗技力点
        else:  # 敌方干员回合
            if operate == 0:
                await sub.attack(obj1)
                self.enemy_skill_count += 5  # 普攻回复5技力点
            elif operate in [1, 2, 3]:
                await sub.use_skill(sub.skills_list[operate - 1], obj1, obj2)
                self.enemy_skill_count -= sub.skills_list[operate - 1].consume  # 使用技能消耗技力点
        quick_sort(self.all_ops_list, 0, len(self.all_ops_list) - 1)


async def new_instance(uid: str or int, mid: str) -> PlayingManager:
    player_ops_list: list[Operator] = await get_operator_list(uid)
    map_enemies_list: list[Operator] = await get_enemies_list(mid)
    return PlayingManager(player_ops_list, map_enemies_list)


# 快速排序函数
def quick_sort(arr: list[Operator], low, high):
    if low < high:
        pi = partition(arr, low, high)

        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)


def partition(arr: list[Operator], low, high):
    i = (low - 1)  # 最小元素索引
    pivot = arr[high].speed

    for j in range(low, high):

        # 当前元素小于或等于 pivot
        if arr[j].speed <= pivot:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
