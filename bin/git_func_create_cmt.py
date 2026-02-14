"""将 GitHub 仓库动态作为评论添加到指定的 issue 中"""

import inspect
import os
import json
from datetime import datetime

from bin.base import config_info, fnBug, fnLog
from bin.http_func import http_git_create_comment, http_git_repo, http_git_create_issue


# 封装 res 判断
def check_response(res_info, lineno=-1):
    """检查 HTTP 响应是否包含错误"""
    if "error" in res_info.keys() and res_info["error"]:
        fnBug(res_info["message"], lineno)
        fnBug(res_info["data"])
        return False
    return True


def construct_and_post_comment(issue_data, event_data):
    """构造评论并发布到指定的 issue，必要时创建新 issue"""
    if not event_data:
        fnLog("No event data available.", inspect.currentframe().f_lineno)
        return

    tpl = """```yml
Title: GitHub - {Title}
Desc: {Desc}
Source: "[url=https://github.com/wdssmq]wdssmq (沉冰浮水)@github[/url]"
Tags: GitHub
Type: 代码
Url: {Url}

```"""

    for event in event_data:
        repo_url = f'https://github.com/{event["repo"]["name"]}'
        # 判断是否已经存在相同的 Url
        if issue_data and any(
            note.get("Url") == repo_url for note in issue_data.get("note_data", [])
        ):
            continue
        repo_info = http_git_repo(event["repo"]["name"], config_info["GIT_TOKEN"])
        if not check_response(repo_info, inspect.currentframe().f_lineno):
            continue
        repo_desc = repo_info["data"].get("description", "无描述")
        repo_title = repo_info["data"].get("full_name", "无标题")

        note_info = {
            "Title": repo_title,
            "Desc": repo_desc,
            "Url": repo_url,
        }
        note_body = tpl.format(**note_info)
        if issue_data and issue_data.get("comments_url"):
            res = http_git_create_comment(
                issue_data["comments_url"], note_body, config_info["GIT_TOKEN"]
            )
            if not check_response(res, inspect.currentframe().f_lineno):
                continue
        else:
            issue_title = datetime.now().strftime("%Y-%m")
            res = http_git_create_issue(
                config_info["GIT_REPO"],
                issue_title,
                note_body,
                [config_info["PICK_LABEL"]],
                config_info["GIT_TOKEN"],
            )
            if not check_response(res, inspect.currentframe().f_lineno):
                continue
        break


# 解析 JSON 文件
def parse_json_file(file_path):
    """解析 JSON 文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# 遍历文件夹下的所有 json 文件
def list_json_files():
    """列出目录下的所有 JSON 文件"""
    json_files = []
    for root, _, files in os.walk(config_info["DATA_PATH"]):
        for file in files:
            if file.endswith(".json"):
                file_info = {"file_name": file, "file_path": os.path.join(root, file)}
                json_files.append(file_info)
    return json_files


# 基于 JSON 文件的内容进行处理
def process_json_files():
    """处理所有 JSON 文件"""
    json_files = list_json_files()
    events_data = []
    issues_data = None
    for json_file in json_files:
        if json_file["file_name"] == "github_events.json":
            events_data = parse_json_file(json_file["file_path"])
        elif issues_data is not None:
            continue
        else:
            cur_data = parse_json_file(json_file["file_path"])
            if cur_data["note_count"] + 1 <= config_info["MAX_NOTES"]:
                issues_data = cur_data
        if issues_data and events_data:
            break
    construct_and_post_comment(issues_data, events_data)
