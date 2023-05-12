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

    async def round(self):
        """
        回合前的准备，大概吧
        """
        move_op = self.all_ops_list[len(self.all_ops_list) - 1]  # 当前行动者
        if move_op in self.player_ops_list:
            pass
        else:  # 如果未被嘲讽则随机选一个目标
            while True:
                obj: Operator = self.player_ops_list[random.randint(0, len(self.player_ops_list) - 1)] \
                    if not move_op.mocked else move_op.mocking_obj
                if not obj.hidden:  # 如果所有干员都处于隐匿状态就糟咯awa
                    break

            if not len(move_op.skills_list) and random.randint(1, 100) <= 20 + (5 * move_op.stars) and \
                    self.enemy_skill_count >= move_op.skills_list[0].consume:  # 条件达成则使用技能

                for i in range(len(move_op.skills_list) - 1, -1, -1):
                    if self.enemy_skill_count >= move_op.skills_list[i].consume:
                        await self.turn(move_op, i + 1, obj)
                        break

            else:  # 否则进行普攻
                await self.turn(move_op, 0, obj)

    async def turn(self, sub: Operator, operate: int, obj1: Operator, obj2: Operator = None):
        """
        干员的一个回合

        :param sub: 行动者
        :param operate: 操作序号 0普攻 1-3技能
        :param obj1: 目标对象1
        :param obj2: 目标对象2(可选)
        """
        if sub in self.player_ops_list:  # 我方干员回合
            if operate == 0:
                await self.attack(sub, obj1)
                self.player_skill_count += 5  # 普攻回复5技力点
            elif operate in [1, 2, 3]:
                await sub.use_skill(sub.skills_list[operate - 1], obj1, obj2)
                self.player_skill_count -= sub.skills_list[operate - 1].consume  # 使用技能消耗技力点
        else:  # 敌方干员回合
            if operate == 0:
                await self.attack(sub, obj1)
                self.enemy_skill_count += 10  # 普攻回复10技力点
            elif operate in [1, 2, 3]:
                await sub.use_skill(sub.skills_list[operate - 1], obj1, obj2)
                self.enemy_skill_count -= sub.skills_list[operate - 1].consume  # 使用技能消耗技力点
        quick_sort(self.all_ops_list, 0, len(self.all_ops_list) - 1)

    async def attack(self, sub: Operator, obj: Operator) -> str:
        """
        干员进行普攻的函数，会根据atk_type来进行不同的操作

        :param sub: 对象
        :param obj: 目标
        :return: 信息字符串
        """
        message: str = ""
        is_crit: bool = random.randint(1, 10000) <= sub.crit_r_p * 10000  # 是否暴击
        is_crit_str: str = "暴击并" if is_crit else ""
        if sub.atk_type == 0:  # 单体物理
            damage = (sub.atk_p - obj.defence_p) \
                if (sub.atk_p - obj.defence_p > sub.atk_p * 0.05) \
                else (sub.atk_p * 0.05)  # 5%攻击力的保底伤害
            damage += damage * is_crit * (1.0 + sub.crit_d_p)
            message = f"{sub.name}对{obj.name}发动了普通攻击，{is_crit_str}对其造成了{damage}点物理伤害！"  # 返回的字符串
            if sub.profession == "重装-中坚" and random.randint(1, 100) < 50:  # 中坚重装普攻有概率嘲讽敌方单位
                message += f"\n{sub.name}嘲讽了{obj.name}！"
                obj.mocked = 1
                obj.mocking_obj = sub
            if not obj.invincible:
                obj.health -= damage
                if await obj.is_die():
                    message += f"\n{obj.name}被{sub.name}击倒了！"
                    if obj in self.map_enemies_list:
                        self.map_enemies_list.remove(obj)
                    else:
                        self.player_ops_list.remove(obj)
                self.all_ops_list.remove(obj)
        elif sub.atk_type == 1:  # 单体法术
            damage = (sub.atk_p * ((100 - obj.res_p) / 100))  # 法抗90封顶
            damage += damage * is_crit * (1.0 + sub.crit_d_p)
            message = f"{sub.name}对{obj.name}发动了普通攻击，{is_crit_str}对其造成了{damage}点法术伤害！"  # 返回的字符串

            if not obj.invincible:
                obj.health -= damage
                if await obj.is_die():
                    message += f"\n{obj.name}被{sub.name}击倒了！"
                    if obj in self.map_enemies_list:
                        self.map_enemies_list.remove(obj)
                    else:
                        self.player_ops_list.remove(obj)
                self.all_ops_list.remove(obj)
        elif sub.atk_type == 2:  # 群体物理
            message = f"{sub.name}对"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_damage: str = ""  # 各个目标受到的伤害
            die_objs: str = ""  # 被击倒的目标名字
            for op in obj.next_operators:
                objs_name += f" {op.name}"
                damage = (sub.atk_p - op.defence_p) \
                    if (sub.atk_p - op.defence_p > sub.atk_p * 0.05) \
                    else (sub.atk_p * 0.05)
                damage += damage * is_crit * (1.0 + sub.crit_d_p)
                objs_damage += f" {damage}"
                if not op.invincible:
                    op.health -= damage
                    if await op.is_die():
                        die_objs += f" {op.name}"
                        if op in self.map_enemies_list:
                            self.map_enemies_list.remove(op)
                        else:
                            self.player_ops_list.remove(op)
                    self.all_ops_list.remove(op)
            message += f"{objs_name} 发动了普通攻击，{is_crit_str}分别对他们造成了{objs_damage} 点物理伤害！\n{die_objs} 被击倒了！"
        elif sub.atk_type == 3:  # 群体法术
            message = f"{sub.name}对"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_damage: str = ""  # 各个目标受到的伤害
            die_objs: str = ""  # 被击倒的目标名字
            for op in obj.next_operators:
                objs_name += f" {op.name}"
                damage = (sub.atk_p * ((100 - op.res_p) / 100))
                damage += damage * is_crit * (1.0 + sub.crit_d_p)
                objs_damage += f" {damage}"
                if not op.invincible:
                    op.health -= damage
                    if await op.is_die():
                        die_objs += f" {op.name}"
                        if op in self.map_enemies_list:
                            self.map_enemies_list.remove(op)
                        else:
                            self.player_ops_list.remove(op)
                    self.all_ops_list.remove(op)
            message += f"{objs_name} 发动了普通攻击，{is_crit_str}分别对他们造成了{objs_damage} 点法术伤害！\n{die_objs} 被击倒了！"
        elif sub.atk_type == 4:  # 单体治疗
            health_amount = sub.atk_p
            obj.health += health_amount
            if obj.health > obj.max_health_p:
                obj.health = obj.max_health_p
                health_amount = sub.atk_p + (obj.max_health_p - obj.health - sub.atk_p)

            message = f"{sub.name}治疗了{obj.name}，恢复其{health_amount}生命值！"  # 返回的字符串
        elif sub.atk_type == 5:  # 群体治疗
            message = f"{sub.name}治疗了"  # 返回的字符串
            objs_name: str = ""  # 所有目标名字
            objs_health: str = ""  # 各个目标恢复的生命值
            health_amount = sub.atk_p
            for op in obj.next_operators:
                objs_name += f" {op.name}"
                op.health += health_amount
                if op.health > op.max_health_p:
                    op.health = op.max_health_p
                    health_amount = sub.atk_p + (op.max_health_p - op.health - sub.atk_p)
                objs_health += f"{health_amount} "
            message += f"{objs_name}，分别恢复他们{objs_health} 的生命值！"
        elif sub.atk_type == 6:  # 单体真实
            damage = sub.atk_p
            damage += damage * is_crit * (1.0 + sub.crit_d_p)
            message = f"{sub.name}对{obj.name}发动了普通攻击，{is_crit_str}对其造成了{damage}点真实伤害！"  # 返回的字符串
            if not obj.invincible:
                obj.health -= damage
                if await obj.is_die():
                    message += f"\n{obj.name}被{sub.name}击倒了！"
                    if obj in self.map_enemies_list:
                        self.map_enemies_list.remove(obj)
                    else:
                        self.player_ops_list.remove(obj)
                self.all_ops_list.remove(obj)
        elif sub.atk_type == 7:  # 不攻击
            message = f"{sub.name}无动于衷..."
            pass
        sub.speed_p = 0
        return message


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
