"""RSS 数据来源。"""

from urllib.parse import urlparse
from xml.etree import ElementTree

import requests


def rss_notes(source):
    """按订阅原始顺序转换条目。"""
    response = requests.get(source["url"], timeout=10)
    response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    channel = root.find("channel")
    if root.tag != "rss" or channel is None:
        raise ValueError(f"RSS 格式不正确: {source['url']}")

    notes = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        parsed_url = urlparse(url)
        if (
            not title
            or parsed_url.scheme not in ("http", "https")
            or not parsed_url.netloc
        ):
            raise ValueError(f"RSS 条目标题或链接无效: {source['url']}")
        notes.append({
            "Title": title,
            "Desc": "",
            "Source": source["source"],
            "Tags": source["tags"],
            "Type": source["type"],
            "Url": url,
        })
    return notes


def rss_note(source, excluded_urls):
    """按订阅原始顺序选择尚未收录的条目。"""
    return next(
        (note for note in rss_notes(source) if note["Url"] not in excluded_urls),
        None,
    )
