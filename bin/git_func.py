"""GitHub 数据处理"""

from bin.base import fnBug, fnLineNo
from bin.git_func_issues import parse_and_save_issues_details
from bin.git_func_events import parse_and_save_event_details
from bin.git_func_create_cmt import process_json_files


# 主入口函数
def git_func_main():
    """主入口函数"""
    fnBug("git_func_main", fnLineNo())
    # 解析并保存 GitHub issues 和 events 的详细信息
    parse_and_save_issues_details()
    parse_and_save_event_details()
    # 处理 JSON 文件，生成评论等内容
    process_json_files()
