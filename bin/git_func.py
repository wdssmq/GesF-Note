""" GitHub 数据处理 """

import inspect
import re
import json
import yaml

from bin.base import fnBug
from bin.md_func import save_md
from bin.http_func import http_git_issues, http_git_issues_comments

# 全局变量
config_info = {}
debug_info = {"debug": False, "log": ""}

# pylint: disable=global-statement


def git_func_init(config, debug):
    """初始化"""
    global config_info, debug_info
    config_info = config
    debug_info = debug


# 抓取 issues 或 issue comments 封装
def git_func_issues(comments_url=None):
    """抓取 issues 或 issue comments 封装"""
    if comments_url is None:
        issues = http_git_issues(
            config_info["PICK_LABEL"],
            config_info["GIT_REPO"],
            config_info["GIT_TOKEN"],
        )
    else:
        issues = http_git_issues_comments(comments_url, config_info["GIT_TOKEN"])
    return issues


pick_keys_info = {
    "issues": ["url", "html_url", "title", "body", "comments_url", "user"],
    "comments": ["url", "html_url", "body", "user"],
}


# 选出需要的字段
def filter_issues(list_data, list_type="issues"):
    """选出需要的字段"""
    list_result = []
    for item_data in list_data:
        item_result = {}
        for key in pick_keys_info[list_type]:
            item_result[key] = item_data[key]
        list_result.append(item_result)
    return list_result


# 从 issue 的 body 中提取信息
def extract_info(body):
    """从 issue 的 body 中提取信息"""
    # 匹配 ```yml ... ``` 中的内容
    yaml_str = re.search(r"```yml(.*?)```", body, re.S).group(1)
    # 将 yaml 字符串转换为字典
    dict_info = yaml.safe_load(yaml_str)
    return dict_info


# 保存数据到文件
def save_data(data, file_type="yml"):
    """保存数据到文件"""
    file_name = data["issues_title"].replace(" ", "_") + f".{file_type}"
    file_path = config_info["DATA_PATH"] + file_name
    # 保存到文件
    with open(file_path, "w", encoding="utf-8") as file:
        if file_type == "yml":
            yaml.dump(data, file, allow_unicode=True)
        elif file_type == "json":
            json.dump(data, file, ensure_ascii=False, indent=4)
    fnBug(
        f"保存文件：{file_path}", inspect.currentframe().f_lineno, debug_info["debug"]
    )


# 主入口函数
def git_func_main():
    """主入口函数"""
    # 抓取 issues
    issues = git_func_issues()
    # 检查错误
    if "error" in issues.keys() and issues["error"]:
        fnBug(issues["message"], inspect.currentframe().f_lineno)
        fnBug(issues["data"])
        return
    # 筛选数据
    items = filter_issues(issues)
    # 对于每个 issue，提取信息
    for item in items:
        new_item = {}
        new_item["issues_title"] = item["title"]
        new_item["issues_url"] = item["html_url"]
        new_item["issues_user"] = item["user"]["login"]
        new_item["note_data"] = [extract_info(item["body"])]
        # 抓取 issue comments
        comments = git_func_issues(item["comments_url"])
        # 筛选数据
        comments = filter_issues(comments, "comments")
        # 对于每个 issue comment，提取信息
        for comment in comments:
            # 评论用户必须是 issues 用户
            if comment["user"]["login"] == item["user"]["login"]:
                new_item["note_data"].append(extract_info(comment["body"]))
        # 计数
        new_item["note_count"] = len(new_item["note_data"])
        # 保存数据到文件
        save_data(new_item, "yml")
        save_data(new_item, "json")
        save_md(new_item, config_info["MD_PATH"], debug_info["debug"])
