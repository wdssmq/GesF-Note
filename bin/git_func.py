"""GitHub 数据处理"""

import json

from bin.base import fnBug, fnLineNo
from bin.git_func_issues import parse_and_save_issues_details
from bin.git_func_create_cmt import process_json_files


# 主入口函数
def git_func_main():
    """主入口函数"""
    fnBug("git_func_main", fnLineNo())
    # 解析并保存 GitHub issues
    issues = issues = parse_and_save_issues_details()
    fnBug("issues count: " + str(len(issues)), fnLineNo())
    # 选择并获取本轮数据来源，生成评论等内容
    process_json_files(issues)
