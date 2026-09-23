"""Regression tests for issue/comment YAML note handling."""

import unittest

from bin.git_func_create_cmt import build_note_body
from bin.git_func_issues import extract_and_append_info


class IssueYamlHandlingTests(unittest.TestCase):
    """Validate malformed and generated note YAML handling."""

    def test_extract_and_append_info_handles_legacy_desc_with_colons(self):
        body = """```yml
Title: GitHub - example/repo
Desc: :lollipop: Wow, such a lovely HTML5 danmaku engine.
Source: "[url=https://github.com/wdssmq]wdssmq (沉冰浮水)@github[/url]"
Tags: GitHub
Type: 代码
Url: https://github.com/example/repo
```"""

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


if __name__ == "__main__":
    unittest.main()
