"""HTTP 请求"""

import sys
import inspect
import requests

# import json

from bin.base import fnErr


def http(req_arg=None, data_arg=None, json_arg=None, headers_arg=None):
    """HTTP 请求"""
    if data_arg is None:
        data_arg = {}
    if headers_arg is None:
        headers_arg = {}
    # ----------------------------------------
    url = req_arg["url"]

    try:
        if req_arg["method"] == "get":
            res_info = requests.get(
                url, params=data_arg, headers=headers_arg, timeout=10
            )
        elif req_arg["method"] == "post":
            res_info = requests.post(
                url, data=data_arg, json=json_arg, headers=headers_arg, timeout=10
            )
        elif req_arg["method"] == "patch":
            res_info = requests.patch(
                url, data=data_arg, json=json_arg, headers=headers_arg, timeout=10
            )
        else:
            fnErr("不支持的请求方法", inspect.currentframe().f_lineno)
            sys.exit(0)
    except KeyError:
        fnErr("网络错误", inspect.currentframe().f_lineno)
        sys.exit(0)

    return res_info


def http_git_headers(token=""):
    """GitHub 请求头"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token " + token,
    }
    return headers


def http_git_check(res_data):
    """判断抓取信息是否报错"""
    # 检查 dict 类型的返回值
    error_message = ""
    if isinstance(res_data, dict) and "status" in res_data.keys():
        if res_data["status"] != 200:
            error_message = res_data.get("message", "未知错误")

    if error_message != "":
        return {"error": True, "message": error_message, "data": res_data}

    return {"error": False, "data": res_data}


def http_git_events(user="", token=""):
    """获取 events 列表"""
    url = f"https://api.github.com/users/{user}/events/public?per_page=100"
    headers = http_git_headers(token)
    res_data = http({"url": url, "method": "get"}, headers_arg=headers)
    return http_git_check(res_data.json())


def http_git_repo(repo="", token=""):
    """获取 repo 详情"""
    url = f"https://api.github.com/repos/{repo}"
    headers = http_git_headers(token)
    res_data = http({"url": url, "method": "get"}, headers_arg=headers)
    return http_git_check(res_data.json())


def http_git_issues(labels="pick", repo="", token=""):
    """获取 issues 列表"""
    url = f"https://api.github.com/repos/{repo}/issues?labels={labels}"
    headers = http_git_headers(token)
    res_data = http({"url": url, "method": "get"}, headers_arg=headers)
    return http_git_check(res_data.json())


def http_git_issues_comments(comments_url, token=""):
    """获取 issue comments 列表"""
    url = comments_url
    headers = http_git_headers(token)
    res_data = http({"url": url, "method": "get"}, headers_arg=headers)
    return http_git_check(res_data.json())


def http_git_create_comment(comments_url, comment, token):
    headers = http_git_headers(token)
    data = {"body": comment}
    res_data = http(
        {"url": comments_url, "method": "post"}, json_arg=data, headers_arg=headers
    )
    return http_git_check(res_data.json())
