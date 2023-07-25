FROM python:3.10.0
EXPOSE 13570
WORKDIR /Mizuki
COPY . /Mizuki
#RUN pip config set global.index-url https://pypi.douban.com/simple
RUN pip install nb-cli
RUN pip install -r requirements.txt
RUN nb plugin install nonebot-plugin-gocqhttp
RUN playwright install
RUN playwright install-deps # 安装Linux playwright依赖
# 复制脚本文件
COPY entrypoint.sh /entrypoint.sh
# 设置脚本文件权限
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
