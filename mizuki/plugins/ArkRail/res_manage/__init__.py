# -*- coding = utf-8 -*-
# @File:__init__.py.py
# @Author:Hycer_Lance
# @Time:2023/6/4 10:36
# @Software:PyCharm
import datetime
import json
import time
import zipfile

import requests
import os
from tqdm import tqdm
from pathlib import Path

from nonebot.log import logger

img_resources_path = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res'
res_version_data = Path() / 'mizuki' / 'plugins' / 'ArkRail' / 'res_manage' / 'res_version_data.json'


def check_release():
    """
    检查仓库release，获取asset信息
    :return: 成功则返回包含图片资源下载地址和版本信息的列表，失败
            则返回字符串信息
    """
    headers = {
        # "Authorization": "token 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",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57 "
    }
    release_api = 'https://api.github.com/repos/LanceHE6/Mizuki-Bot/releases'

    response = requests.get(release_api, headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        releases_data = response.json()
        if len(releases_data) > 0:
            latest_release = releases_data[0]
            version = latest_release['tag_name']
            assets = latest_release['assets']
            for asset in assets:
                download_url = asset['browser_download_url']
                return [download_url, version]
        else:
            return 'No releases found for the repository.'

    else:
        return 'Failed to retrieve release information'

def zip_extract(zip_file: Path, extract_path: Path, reserve_zip: bool = False):
    """
    解压文件
    :param zip_file: 压缩包
    :param extract_path: 解压路劲
    :param reserve_zip: 是否保留压缩包
    :return:
    """

    # 打开 ZIP 文件
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        # 获取 ZIP 文件中的文件列表
        file_list = zip_ref.namelist()
        # 设置进度条
        progress_bar = tqdm(total=len(file_list), unit="file")
        # 遍历 ZIP 文件中的每个文件
        for file_info in zip_ref.infolist():
            # 重新编码防止中文乱码
            file_info.filename = file_info.filename.encode('cp437').decode('gbk')
            # 解压文件到目标路径
            zip_ref.extract(file_info, extract_path)
            progress_bar.update(1)
        # 关闭进度条
        progress_bar.close()
    if not reserve_zip:
        os.remove(zip_file)
    logger.info(f'[ArkRail]资源解压完成')

def download(download_url: str, save_path: Path, version: str):
    """
    下载资源
    :param download_url: 下载地址
    :param save_path: 保存路劲
    :param version: 版本信息，保存于json文件中，用于检查更新
    :return:
    """
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    # 5秒超时，采用代理服务器下载
    response = requests.get(download_url, stream=True, timeout=5)
    # 检查响应状态码
    if response.status_code == 200:
        # 提取文件名
        filename = download_url.split('/')[-1]
        # 获取文件大小
        file_size = int(response.headers.get('Content-Length', 0))
        # 设置进度条
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, colour='blue')
        # 保存文件到本地
        with open(save_path / filename, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                # 更新进度条
                progress_bar.update(len(data))
                file.write(data)

        # 关闭进度条
        progress_bar.close()
        with open(res_version_data, 'w', encoding='utf-8') as data_file:
            now_time = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
            version_data = {
                "res_name": filename,
                "version": version,
                "download_time": now_time
            }
            json.dump(version_data, data_file, indent=4, ensure_ascii=False)

        logger.info(f'[ArkRail]Downloaded: {filename}')
        time.sleep(2)
        logger.info(f'[ArkRail]开始解压资源')
        zip_extract(img_resources_path/filename, img_resources_path)

    else:
        logger.warning('[ArkRail]资源下载超时，更换为代理服务器下载')
        proxy_url = 'https://ghproxy.com/'
        # 请求失败，添加代理服务器地址并重试
        retry_url = proxy_url + download_url
        response = requests.get(retry_url, stream=True)

        if response.status_code == 200:
            # 提取文件名
            filename = download_url.split('/')[-1]
            # 获取文件大小
            file_size = int(response.headers.get('Content-Length', 0))
            # 设置进度条
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, colour='blue')
            # 保存文件到本地
            with open(save_path / filename, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    # 更新进度条
                    progress_bar.update(len(data))
                    file.write(data)

            # 关闭进度条
            progress_bar.close()
            with open(res_version_data, 'w', encoding='utf-8') as data_file:
                now_time = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
                version_data = {
                    "res_name": filename,
                    "version": version,
                    "download_time": now_time
                }
                json.dump(version_data, data_file, indent=4, ensure_ascii=False)

            logger.info(f'[ArkRail]Downloaded: {filename}')
            time.sleep(2)
            logger.info(f'[ArkRail]开始解压资源')
            zip_extract(img_resources_path / filename, img_resources_path)
        else:
            logger.warning('[ArkRail]Failed to download the file')


def check_image_res():
    """
    检查图片资源
    :return:
    """
    logger.info('[ArkRail]开始检查图片资源')
    if os.path.exists(img_resources_path):
        logger.info('[ArkRail]图片资源已存在')
        release_data = check_release()
        if isinstance(release_data, str):
            logger.warning('[ArkRail]获取图片资源信息失败')
            return
        with open(res_version_data, 'r', encoding='utf-8') as data:
            local_data = json.load(data)
            data.close()
        if local_data["version"] != release_data[1]:
            logger.info('[ArkRail]图片资源存在更新，开始更新资源')
            os.remove(img_resources_path)
            download(release_data[0], img_resources_path, release_data[1])
            logger.info('[ArkRail]图片资源更新完成')

    else:
        logger.warning('[ArkRail]未检测到图片资源即将开始下载')
        release_data = check_release()
        if isinstance(release_data, str):
            logger.warning('[ArkRail]获取图片资源信息失败')
            return
        download(release_data[0], img_resources_path, release_data[1])

check_image_res()
    