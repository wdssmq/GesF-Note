"""GitHub Events 数据处理"""

import inspect
import json

from bin.base import config_info, fnBug
from bin.http_func import http_git_events


def git_func_events():
    """获取 events 列表"""
    res = http_git_events(config_info["GIT_USER"], config_info["GIT_TOKEN"])
    if "error" in res.keys() and res["error"]:
        fnBug(res["message"], inspect.currentframe().f_lineno)
        fnBug(res["data"])
        return []
    return res["data"]


def git_func_event_details(event_list):
    """获取 event 详情"""

    # 定义一个函数，用于提取提交信息
    def extract_commit_info(payload):
        commits = []
        if "commits" not in payload.keys():
            return commits
        for commit in payload["commits"]:
            commits.append(
                {
                    "message": commit.get("message", ""),
                }
            )
        return commits

    details = []
    for event in event_list:
        event_type = event.get("type", "")
        if event_type != "PushEvent":
            continue
        event_repo = event.get("repo", {}).get("name", "")
        # 判断是否存在同名的 repo 在 details ,存在则合并 commits
        if any(d["repo"] == event_repo for d in details):
            for d in details:
                if d["repo"] == event_repo:
                    d["commits"].extend(extract_commit_info(event.get("payload", {})))
                    break
        else:
            details.append(
                {
                    "type": event_type,
                    "repo": event_repo,
                    "commits": extract_commit_info(event.get("payload", {})),
                }
            )
    return details


def save_event_details(details):
    """保存 event 详情到文件"""
    file_name = "github_events.json"
    file_path = config_info["DATA_PATH"] + file_name
    # 保存到文件
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(details, file, ensure_ascii=False, indent=4)
    fnBug(f"保存文件：{file_path}", inspect.currentframe().f_lineno)


# 解析并保存 event details
def parse_and_save_event_details():
    """解析并保存 event details"""
    # 抓取 events
    events = git_func_events()
    # 获取 event 详情
    details = git_func_event_details(events)
    if not details:
        fnBug("未获取到 event 详情数据", inspect.currentframe().f_lineno)
        return
    # 保存 event 详情到文件
    save_event_details(details)
