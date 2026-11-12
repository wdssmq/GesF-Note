"""将来源内容添加到期刊 issue。"""

from datetime import datetime

import yaml

from config import DATA_SOURCES, TYPE_ORDER
from bin.base import config_info, fnBug, fnLineNo, fnLog, fnTimeDiffByTimeStr
from bin.http_func import http_git_create_comment, http_git_create_issue
from bin.sources.github_events import github_event_note
from bin.sources.rss import rss_note


SOURCE_HANDLERS = {
    "github_events": github_event_note,
    "rss": rss_note,
}


def build_note_body(note_info):
    """将条目序列化为 issue 使用的 YAML。"""
    return "```yml\n%s```\n" % yaml.safe_dump(
        note_info, allow_unicode=True, sort_keys=False
    )


def checked_data(result):
    """返回 GitHub 响应数据，失败时中断处理。"""
    if result.get("error"):
        raise RuntimeError(f"GitHub API request failed: {result['message']}")
    return result["data"]


def next_type(issues):
    """根据最近期的最后一条决定本次类型。"""
    if not TYPE_ORDER or len(set(TYPE_ORDER)) != len(TYPE_ORDER):
        raise ValueError("Type 轮换配置为空或存在重复")
    if not issues or not issues[0]["note_data"]:
        return TYPE_ORDER[0]
    last_type = issues[0]["note_data"][-1].get("Type")
    if last_type not in TYPE_ORDER:
        raise ValueError(f"最新条目的 Type 未配置: {last_type!r}")
    return TYPE_ORDER[(TYPE_ORDER.index(last_type) + 1) % len(TYPE_ORDER)]


def choose_note(note_type, excluded_urls):
    """仅处理轮到的类型。"""
    sources = [source for source in DATA_SOURCES if source["type"] == note_type]
    if len(sources) != 1:
        raise ValueError(f"Type {note_type!r} 需要配置一个数据来源")
    source = sources[0]
    handler = SOURCE_HANDLERS.get(source["kind"])
    if handler is None:
        raise ValueError(f"数据来源类型未配置: {source['kind']!r}")
    return handler(source, excluded_urls)


def process_json_files(issues):
    """按期刊状态选取并追加最多一条记录。"""
    latest = issues[0] if issues else None
    if latest:
        diff = fnTimeDiffByTimeStr(latest["updated_at"])
        if diff < config_info.get("MIN_TIME_DIFF", 3600):
            fnBug(f"时间差为 {diff} 秒, 小于最小时间差", fnLineNo())
            return
    if config_info["DEBUG"]:
        fnBug("debug 模式跳过提交新 issue 或 comment", fnLineNo())
        return

    excluded_urls = {
        note["Url"]
        for issue in issues[:2]
        for note in issue["note_data"]
        if note.get("Url")
    }
    note_type = next_type(issues)
    note = choose_note(note_type, excluded_urls)
    if note is None:
        fnLog(f"Type {note_type} 没有可追加的条目", fnLineNo())
        return

    body = build_note_body(note)
    if latest and latest["note_count"] < config_info["MAX_NOTES"]:
        result = http_git_create_comment(
            latest["comments_url"], body, config_info["GIT_TOKEN"]
        )
    else:
        title = datetime.now().strftime("%Y-%m")
        if any(issue["issues_title"] == title for issue in issues):
            raise ValueError(f"期刊 issue 标题已存在: {title}")
        result = http_git_create_issue(
            config_info["GIT_REPO"], title, body,
            [config_info["PICK_LABEL"]], config_info["GIT_TOKEN"]
        )
    checked_data(result)
