"""Regression tests for issue/comment YAML note handling."""

import unittest
from unittest.mock import Mock, patch

from bin.base import config_info
from bin.git_func_create_cmt import build_note_body
from bin.git_func_create_cmt import construct_and_post_comment
from bin.git_func_create_cmt import process_json_files
from bin.http_func import http_git_create_issue
from bin.git_func_issues import extract_and_append_info
from bin.md_func import fix_ellipsis
from bin import git_func_create_cmt
from bin import http_func


class IssueYamlHandlingTests(unittest.TestCase):
    """Validate malformed and generated note YAML handling."""

    def test_fix_ellipsis_handles_missing_description(self):
        self.assertEqual(fix_ellipsis(None), "")

    def test_extract_and_append_info_handles_legacy_desc_with_colons(self):
        body = """```yml
Title: GitHub - example/repo
Desc: :lollipop: Wow, such a lovely HTML5 danmaku engine.
Source: "[url=https://github.com/wdssmq]wdssmq (沉冰浮水)@github[/url]"
Tags: GitHub
Type: 代码
Url: https://github.com/example/repo
```"""

        with patch.dict(config_info, {"DEBUG": False}):
            notes = extract_and_append_info(body, [])

        self.assertEqual(len(notes), 1)
        self.assertEqual(
            notes[0]["Desc"], ":lollipop: Wow, such a lovely HTML5 danmaku engine."
        )
        self.assertEqual(notes[0]["Url"], "https://github.com/example/repo")

    def test_generated_note_body_round_trips_desc_with_colons(self):
        note_info = {
            "Title": "GitHub - example/repo",
            "Desc": ":lollipop: Wow, such a lovely HTML5 danmaku engine.",
            "Source": "[url=https://github.com/wdssmq]wdssmq (沉冰浮水)@github[/url]",
            "Tags": "GitHub",
            "Type": "代码",
            "Url": "https://github.com/example/repo",
        }

        notes = extract_and_append_info(build_note_body(note_info), [])

        self.assertEqual(notes, [note_info])

    @patch.object(git_func_create_cmt, "construct_and_post_comment")
    @patch.object(git_func_create_cmt, "parse_json_file")
    @patch.object(git_func_create_cmt, "list_json_files")
    def test_process_creates_issue_when_existing_issue_is_full(
        self, list_json_files, parse_json_file, construct_and_post_comment
    ):
        full_issue = {"note_count": 14}
        events = [{"repo": {"name": "example/repo"}}]
        list_json_files.return_value = [
            {"file_name": "2026-10.json", "file_path": "2026-10.json"},
            {"file_name": "github_events.json", "file_path": "github_events.json"},
        ]
        parse_json_file.side_effect = [full_issue, events]

        with patch.dict(
            git_func_create_cmt.config_info,
            {"MAX_NOTES": 14, "DEBUG": False},
            clear=True,
        ):
            process_json_files()

        construct_and_post_comment.assert_called_once_with(None, full_issue, events)

    @patch.object(http_func, "http")
    def test_create_issue_reports_github_http_error(self, http_request):
        response = Mock(status_code=403, ok=False)
        response.json.return_value = {
            "message": "Resource not accessible by integration"
        }
        http_request.return_value = response

        result = http_git_create_issue(
            "owner/repo", "2026-10", "body", ["pick"], "token"
        )

        self.assertTrue(result["error"])
        self.assertEqual(result["message"], "Resource not accessible by integration")

    @patch("bin.git_func_create_cmt.http_git_create_issue")
    @patch("bin.git_func_create_cmt.http_git_repo")
    def test_construct_posts_new_issue_when_no_current_issue(
        self, get_repo, create_issue
    ):
        get_repo.return_value = {
            "error": False,
            "data": {"description": "Example", "full_name": "example/repo"},
        }
        create_issue.return_value = {"error": False, "data": {}}

        with patch.dict(
            config_info,
            {
                "GIT_TOKEN": "token",
                "GIT_REPO": "owner/repo",
                "PICK_LABEL": "pick",
            },
            clear=True,
        ):
            construct_and_post_comment(
                None, None, [{"repo": {"name": "example/repo"}}]
            )

        self.assertEqual(create_issue.call_args[0][0], "owner/repo")
        self.assertEqual(create_issue.call_args[0][3], ["pick"])


if __name__ == "__main__":
    unittest.main()
