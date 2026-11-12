"""运行配置和期刊数据来源。"""

import json
import os


TYPE_ORDER = ("代码", "视频")

DATA_SOURCES = [
    {
        "type": "代码",
        "kind": "github_events",
        "source": "[url=https://github.com/wdssmq]wdssmq (沉冰浮水)@github[/url]",
        "tags": "GitHub",
    },
    {
        "type": "视频",
        "kind": "rss",
        "url": "https://demo.wdssmq.com/feed.php?oddLater&uid=44744006",
        "source": "[url=https://space.bilibili.com/44744006]沉冰浮水@bilibili[/url]",
        "tags": "哔哩哔哩",
    },
]

ENV_CONFIG_KEYS = ("GIT_REPO", "GIT_TOKEN", "GIT_USER", "PICK_LABEL")

def load_runtime_config():
    """按现有顺序合并环境变量、本地配置和运行路径。"""
    config = {
        "DEBUG": False,
        "MIN_TIME_DIFF": 3600,
        "MAX_NOTES": 14
    }

    for key in ENV_CONFIG_KEYS:
        value = os.environ.get(key)
        if value:
            config[key] = value

    if os.path.exists("dev_config.json"):
        with open("dev_config.json", "rb") as config_file:
            config.update(json.loads(config_file.read()))

    config["DATA_PATH"] = os.path.join(os.getcwd(), "data/")
    config["MD_PATH"] = os.path.join(
        os.getcwd(), "blog-astro/src/content/blog/"
    )

    if config.get("DEBUG"):
        config["DATA_PATH"] = os.path.join(os.getcwd(), "dev_data/")
        config["MD_PATH"] = os.path.join(os.getcwd(), "dev_data/")

    return config
