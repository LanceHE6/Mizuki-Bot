#!/bin/bash
rm -f /etc/hosts  # 删除原有hosts文件
cp hosts /etc/  # 拷贝已准备的hosts
python bot.py
