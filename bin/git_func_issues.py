"""GitHub Issues 数据处理"""

import inspect
import json
import re
import yaml

from bin.base import config_info, debug_info, fnBug
from bin.http_func import http_git_issues, http_git_issues_comments
from bin.md_func import save_md


# 抓取 issues 或 issue comments 封装
def git_func_issues(comments_url=None):
    """抓取 issues 或 issue comments 封装"""
    if comments_url is None:
        res = http_git_issues(
            config_info["PICK_LABEL"],
            config_info["GIT_REPO"],
            config_info["GIT_TOKEN"],
        )
    else:
        res = http_git_issues_comments(comments_url, config_info["GIT_TOKEN"])
    if "error" in res.keys() and res["error"]:
        fnBug(res["message"], inspect.currentframe().f_lineno)
        fnBug(res["data"])
        return []
    return res["data"]


pick_keys_info = {
    "issues": ["url", "html_url", "title", "body", "comments_url", "user"],
    "comments": ["url", "html_url", "body", "user"],
}

# 选出需要的字段
def git_func_issues_details(list_data, list_type="issues"):
    """选出需要的字段"""
    list_result = []
    for item_data in list_data:
        item_result = {}
        for key in pick_keys_info[list_type]:
            item_result[key] = item_data[key]
        list_result.append(item_result)
    return list_result


# 从 issue 的 body 中提取信息并合并到字典
def extract_and_append_info(body, info_dict):
    """从 issue 的 body 中提取信息"""
    # 匹配 ```yml ... ``` 中的内容
    yaml_str = re.search(r"```yml(.*?)```", body, re.S)
    if not yaml_str:
        return info_dict
    # 将 yaml 字符串转换为字典
    note_info = yaml.safe_load(yaml_str.group(1))
    info_dict.append(note_info)
    return info_dict


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
    fnBug(f"保存文件：{file_path}", inspect.currentframe().f_lineno)


def parse_and_save_issues_details():
    """解析并保存 issues 详情"""
    # 抓取 issues
    issues = git_func_issues()
    # 筛选数据
    details = git_func_issues_details(issues)
    # 对于每个 issue，提取信息
    for issue in details:
        new_item = {}
        new_item["issues_title"] = issue["title"]
        new_item["issues_url"] = issue["html_url"]
        new_item["issues_user"] = issue["user"]["login"]
        new_item["comments_url"] = issue["comments_url"]
        new_item["note_data"] = extract_and_append_info(issue["body"], [])
        # 抓取 issue comments
        comments = git_func_issues(issue["comments_url"])
        # 筛选数据
        comments = git_func_issues_details(comments, "comments")
        # 对于每个 issue comment，提取信息
        for comment in comments:
            # 评论用户必须是 issues 用户
            if comment["user"]["login"] == issue["user"]["login"]:
                new_item["note_data"] = extract_and_append_info(comment["body"], new_item["note_data"])
        # 计数
        new_item["note_count"] = len(new_item["note_data"])
        # 保存数据到文件
        save_data(new_item, "yml")
        save_data(new_item, "json")
        save_md(new_item, config_info["MD_PATH"], debug_info["debug"])
