# -*- coding = utf-8 -*-
# @File:boot_script.py
# @Author:Hycer_Lance
# @Time:2023/7/8 16:51
# @Software:PyCharm

import json
import sys
import os
import psutil
import time


class Reboot:
    # NoneBot 程序的名称
    nonebot_process_name = 'python.exe'

    def __init__(self):
        self.boot_data = self.get_bot_boot_data()
        self.pid = self.get_nonebot_pid()

    def reboot(self):
        """
        重启函数
        :return: None
        """
        if self.pid:
            # 终止 NoneBot 程序
            self.terminate_nonebot()
            time.sleep(1)  # 等待一段时间确保进程终止
        # 重新启动 NoneBot 程序
        self.restart_nonebot()

    @classmethod
    def get_bot_boot_data(cls) -> dict:
        """
        获取保存的启动参数
        :return: 带有参数的字典
        """
        with open("./boot_data/boot_data.json", "r", encoding="utf-8") as data:
            return json.load(data)

    @classmethod
    def get_nonebot_pid(cls) -> int or None:
        """
        获取bot进程id
        :return: pid
        """
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            if process.name() == 'python.exe' and process.cwd() == cls.get_bot_boot_data()["cwd"]:
                return process.pid
        return None

    def terminate_nonebot(self):
        """
        关闭bot
        :return: None
        """
        try:
            process = psutil.Process(self.pid)
            process.terminate()
            process.wait()
            print("已关闭nonebot进程")
        except psutil.NoSuchProcess:
            pass

    def restart_nonebot(self):
        """
        重启bot
        :return: None
        """
        # 重新写入文件，将回复标签打为false
        with open("./boot_data/boot_data.json", "w", encoding="utf-8") as data:
            self.boot_data["reply"] = False
            json.dump(self.boot_data, data)
            data.close()
        # 执行启动命令
        os.system(f"{sys.executable} {self.boot_data['cwd']}\\bot.py")


if __name__ == '__main__':
    reboot = Reboot()
    reboot.reboot()
