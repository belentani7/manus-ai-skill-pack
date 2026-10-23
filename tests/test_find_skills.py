"""Regression tests for the skill finder."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from scripts.find_skills import discover, search, main, parse_metadata


class FinderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def skill(self, folder, text):
        path = self.root / folder
        path.mkdir()
        (path / "SKILL.md").write_text(text, encoding="utf-8")

    def test_metadata(self):
        self.assertEqual(parse_metadata("---\nname: Video\n---\n"), {"name": "Video"})
        self.assertEqual(parse_metadata("---\nname: incomplete"), {})

    def test_discovery(self):
        self.skill("zeta", "# Plain")
        self.skill("alpha", "---\nname: Alpha\n---\n")
        self.assertEqual([x["path"] for x in discover(self.root)], ["alpha", "zeta"])

    def test_matching(self):
        self.skill("camera", "---\nname: Camera\ndescription: Video tools\n---\n")
        self.assertEqual(len(search(self.root, "CAMERA video")), 1)
        self.assertEqual(len(search(self.root, "camera audio")), 0)

    def test_cli_json_and_no_match(self):
        self.skill("camera", "---\nname: Camera\n---\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["camera", "--root", str(self.root), "--json"]), 0)
        self.assertEqual(json.loads(out.getvalue())["count"], 1)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["absent", "--root", str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()
