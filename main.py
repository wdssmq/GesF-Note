"""主入口函数"""

import os
import json
import inspect


# import sys
# import time

# 从 bin/base.py 中导入通用函数
from bin.base import config_info, debug_info, fnInit, fnBug, fnLog
from bin.git_func import git_func_main

# pylint: disable=global-statement,consider-using-f-string


def init():
    """初始化"""
    global config_info
    fnLog("## init")

    # GIT_REPO: wdssmq/GesF-Note
    # GIT_TOKEN: https://github.com/settings/tokens

    try:
        if os.environ["GIT_REPO"]:
            config_info["GIT_REPO"] = os.environ["GIT_REPO"]

        if os.environ["GIT_TOKEN"]:
            config_info["GIT_TOKEN"] = os.environ["GIT_TOKEN"]

        if os.environ["GIT_USER"]:
            config_info["GIT_USER"] = os.environ["GIT_USER"]

        if os.environ["PICK_LABEL"]:
            config_info["PICK_LABEL"] = os.environ["PICK_LABEL"]

    except KeyError:
        fnLog("无法获 github 的 secrets 配置信息，开始使用本地变量")

    # 读取配置文件
    if os.path.exists("dev_config.json") is True:
        with open("dev_config.json", "rb") as config_file:
            config_info = json.loads(config_file.read())

    # data 路径
    config_info["DATA_PATH"] = os.path.join(os.getcwd(), "data/")
    # md 路径
    config_info["MD_PATH"] = os.path.join(os.getcwd(), "blog-astro/src/content/blog/")

    # 读取 debug 配置
    if "DEBUG" in config_info.keys() and config_info["DEBUG"]:
        debug_info["debug"] = True
        fnBug("debug 已开启: %s" % debug_info["debug"], inspect.currentframe().f_lineno)

    if debug_info["debug"]:
        config_info["DATA_PATH"] = os.path.join(os.getcwd(), "dev_data/")
        config_info["MD_PATH"] = os.path.join(os.getcwd(), "dev_data/")
    fnLog(
        "config 内拥有以下值: %s" % str(config_info.keys()),
        inspect.currentframe().f_lineno,
    )


# 初始化调用
init()
# 将配置传递给全局变量
fnInit(config_info, debug_info)
git_func_main()
