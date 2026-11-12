"""运行配置入口"""

import json
import os

ENV_CONFIG_KEYS = ("GIT_REPO", "GIT_TOKEN", "GIT_USER", "PICK_LABEL")
MAX_NOTES = 14


def load_runtime_config():
    """按现有顺序合并环境变量、本地配置和运行路径。"""
    config = {
        "DEBUG": False,
        "MIN_TIME_DIFF": 3600,
    }

    for key in ENV_CONFIG_KEYS:
        value = os.environ.get(key)
        if value:
            config[key] = value

    if os.path.exists("dev_config.json"):
        with open("dev_config.json", "rb") as config_file:
            config = json.loads(config_file.read())

    config["DATA_PATH"] = os.path.join(os.getcwd(), "data/")
    config["MD_PATH"] = os.path.join(
        os.getcwd(), "blog-astro/src/content/blog/"
    )
    config["MAX_NOTES"] = MAX_NOTES

    if config.get("DEBUG"):
        config["DATA_PATH"] = os.path.join(os.getcwd(), "dev_data/")
        config["MD_PATH"] = os.path.join(os.getcwd(), "dev_data/")

    return config
