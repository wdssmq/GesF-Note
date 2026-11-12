"""GitHub Events 数据来源。"""

import json

from bin.base import config_info, fnBug, fnErr, fnLineNo
from bin.http_func import http_git_events, http_git_repo


def git_func_events():
    """获取 events 列表。"""
    result = http_git_events(config_info["GIT_USER"], config_info["GIT_TOKEN"])
    if result.get("error"):
        fnErr(result["message"], fnLineNo())
        fnErr(result["data"])
        raise RuntimeError(f"GitHub Events API request failed: {result['message']}")
    return result["data"]


def git_func_event_details(event_list):
    """提取并合并 PushEvent 的提交信息。"""

    def extract_commit_info(payload):
        return [
            {"message": commit.get("message", "")}
            for commit in payload.get("commits", [])
        ]

    details = []
    for event in event_list:
        if event.get("type") != "PushEvent":
            continue
        event_repo = event.get("repo", {})
        existing = next(
            (detail for detail in details if detail["repo"] == event_repo),
            None,
        )
        if existing:
            existing["commits"].extend(
                extract_commit_info(event.get("payload", {}))
            )
        else:
            details.append({
                "type": "PushEvent",
                "repo": event_repo,
                "commits": extract_commit_info(event.get("payload", {})),
            })
    return details


def save_event_details(details):
    """保存整理后的 Events 数据。"""
    file_path = config_info["DATA_PATH"] + "github_events.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(details, file, ensure_ascii=False, indent=4)
    fnBug(f"保存文件：{file_path}", fnLineNo())


def parse_and_save_event_details():
    """获取、整理并保存 Events 数据。"""
    details = git_func_event_details(git_func_events())
    if not details:
        fnBug("未获取到 event 详情数据", fnLineNo())
        return []
    save_event_details(details)
    return details


def github_event_note(source, excluded_urls):
    """从 PushEvent 中选取尚未收录的仓库。"""
    for event in parse_and_save_event_details():
        name = event["repo"]["name"]
        url = f"https://github.com/{name}"
        if url in excluded_urls:
            continue
        result = http_git_repo(name, config_info["GIT_TOKEN"])
        if result.get("error"):
            raise RuntimeError(f"GitHub API request failed: {result['message']}")
        repo = result["data"]
        return {
            "Title": repo.get("full_name", "无标题"),
            "Desc": repo.get("description", "无描述"),
            "Source": source["source"],
            "Tags": source["tags"],
            "Type": source["type"],
            "Url": url,
        }
    return None
