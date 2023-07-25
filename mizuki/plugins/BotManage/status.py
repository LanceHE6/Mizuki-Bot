# -*- coding = utf-8 -*-
# @File:status.py
# @Author:Hycer_Lance
# @Time:2023/7/25 11:24
# @Software:PyCharm

from nonebot import on_command

from datetime import datetime
from ..Utils.GroupAndGuildMessageEvent import GroupAndGuildMessageEvent
from ..Help.PluginInfo import PluginInfo
import psutil

__plugin_info__ = PluginInfo(
    plugin_name="Status",
    name="Status",
    description="查询系统状态",
    usage="status ——查询系统状态",
    extra={
        "author": "Hycer_Lance",
        "version": "0.1.0",
        "priority": 5
    }
)


class SystemInfo:
    @classmethod
    def b_to_gb(cls, b: int):
        """
        将B转化为GB
        :param b:
        :return: GB float
        """
        return round(b / 1024 / 1024 / 1024, 2)

    @staticmethod
    def get_cpu_percent() -> str:
        """
        返回cpu占用率
        :return: xx%
        """
        return str(psutil.cpu_percent(interval=5)) + "%"

    @classmethod
    def get_memory_info(cls):
        """
        返回内存信息对象
        :return: 内存信息对象
        """

        class MemoryInfo:
            total: float
            free: float
            used: float
            percent: str

            def __init__(self, t, f, u, p):
                self.total = t
                self.free = f
                self.percent = p
                self.used = u

        memory = psutil.virtual_memory()
        total = cls.b_to_gb(memory.total)
        free = cls.b_to_gb(memory.free)
        used = cls.b_to_gb(memory.used)
        percent = str(memory.percent) + "%"
        return MemoryInfo(total, free, used, percent)

    @staticmethod
    def get_run_time():
        """
        返回系统运行时间
        :return: 时间
        """
        boot_time = datetime.fromtimestamp(round(psutil.boot_time()))
        now_time = datetime.fromtimestamp(round(datetime.now().timestamp()))
        return now_time - boot_time


poke = on_command("status", aliases={"系统状态"}, priority=5, block=True)


@poke.handle()
async def _(event: GroupAndGuildMessageEvent):
    cpu_percent = SystemInfo.get_cpu_percent()
    memory_info = SystemInfo.get_memory_info()
    run_time = SystemInfo.get_run_time()
    reply = f"CPU:{cpu_percent}\n" \
            f"内存:{memory_info.percent}  {memory_info.used}/{memory_info.total}\n" \
            f"运行时间:{run_time}"
    await poke.finish(reply)
