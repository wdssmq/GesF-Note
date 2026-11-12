"""主入口函数"""

import os

# 从 bin/base.py 中导入通用函数
from bin.base import fnInit, fnBug, fnLog, fnLineNo
from bin.git_func import git_func_main
from config import ENV_CONFIG_KEYS, load_runtime_config

# pylint: disable=global-statement,consider-using-f-string


def init():
    """初始化"""
    fnLog("## init")
    config = load_runtime_config()
    debug = {"debug": bool(config.get("DEBUG")), "log": ""}
    fnInit(config, debug)
    if not all(os.environ.get(key) for key in ENV_CONFIG_KEYS):
        fnLog("无法获 github 的 secrets 配置信息，开始使用本地变量")
    if debug["debug"]:
        fnBug("debug 已开启: %s" % debug["debug"], fnLineNo())
    fnLog(
        "config 内拥有以下值: %s" % str(config.keys()),
        fnLineNo(),
    )


# 初始化调用
init()
git_func_main()
