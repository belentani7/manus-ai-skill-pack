"""Offline regression tests for the two safe Drive import entry points."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    ROOT / "abcnuts-autonomous-github-sync/scripts/gdrive_to_repo_sync.py",
    ROOT / "abcnuts-autonomous-sync-script/scripts/gdrive_to_repo_sync.py",
]


class SafeSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "checkout"
        self.repo.mkdir()
        self.source = self.root / "source"
        self.source.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True)
        subprocess.run(["git", "config", "user.name", "Offline Tester"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "offline@example.invalid"], cwd=self.repo, check=True)
        (self.repo / "README.md").write_text("initial\n")
        subprocess.run(["git", "add", "README.md"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=self.repo, check=True)
        (self.source / "skill.txt").write_text("new skill\n")

    def module(self, path):
        spec = importlib.util.spec_from_file_location("safe_sync", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def cli(self, mod, *extra):
        return mod.main(["safe-folder", str(self.repo), "feat: import",
                         "--source-dir", str(self.source), *extra])

    def branch(self):
        subprocess.run(["git", "checkout", "-qb", "factory/offline"], cwd=self.repo, check=True)

    def test_entry_points_identical(self):
        self.assertEqual(SCRIPTS[0].read_bytes(), SCRIPTS[1].read_bytes())

    def test_preview_does_not_write(self):
        for path in SCRIPTS:
            with self.subTest(path=path):
                self.assertEqual(self.cli(self.module(path)), 0)
                self.assertFalse((self.repo / "skill.txt").exists())

    def test_apply_requires_feature_branch(self):
        self.assertEqual(self.cli(self.module(SCRIPTS[0]), "--apply"), 1)

    def test_apply_imports_without_commit(self):
        self.branch()
        self.assertEqual(self.cli(self.module(SCRIPTS[0]), "--apply"), 0)
        self.assertEqual((self.repo / "skill.txt").read_text(), "new skill\n")
        self.assertIn("?? skill.txt", subprocess.check_output(
            ["git", "status", "--short"], cwd=self.repo, text=True))

    def test_explicit_commit_only_new_file(self):
        self.branch()
        self.assertEqual(self.cli(self.module(SCRIPTS[0]), "--apply", "--commit"), 0)
        self.assertEqual(subprocess.check_output(
            ["git", "show", "--format=", "--name-only", "HEAD"],
            cwd=self.repo, text=True).strip(), "skill.txt")

    def test_existing_file_is_not_overwritten(self):
        self.branch()
        (self.repo / "skill.txt").write_text("keep me")
        with self.assertRaises(FileExistsError):
            self.module(SCRIPTS[0]).preflight(self.source, self.repo)
        self.assertEqual((self.repo / "skill.txt").read_text(), "keep me")

    def test_source_inside_checkout_rejected(self):
        self.branch()
        nested = self.repo / "nested"
        nested.mkdir()
        with self.assertRaises(ValueError):
            self.module(SCRIPTS[0]).preflight(nested, self.repo)

    def test_symlink_source_rejected(self):
        self.branch()
        (self.source / "link.txt").symlink_to(self.source / "skill.txt")
        self.assertEqual(self.cli(self.module(SCRIPTS[0]), "--apply"), 1)
        self.assertFalse((self.repo / "skill.txt").exists())

    def test_secrets_rejected(self):
        self.branch()
        (self.source / ".env.local").write_text("SECRET=x")
        self.assertEqual(self.cli(self.module(SCRIPTS[0]), "--apply"), 1)

    def test_invalid_remote_folder_rejected(self):
        mod = self.module(SCRIPTS[0])
        for path in ("../secret", "-help", "other:folder", "a//b", "a\\b", "/root"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                mod.validate_folder(path)

    def test_push_requires_commit(self):
        self.branch()
        self.assertEqual(self.cli(self.module(SCRIPTS[0]), "--apply", "--push"), 1)

    def test_dirty_checkout_rejected(self):
        self.branch()
        (self.repo / "local.txt").write_text("do not touch")
        self.assertEqual(self.cli(self.module(SCRIPTS[0]), "--apply"), 1)

    def test_source_root_symlink_rejected(self):
        self.branch()
        link = self.root / "source-link"
        link.symlink_to(self.source, target_is_directory=True)
        mod = self.module(SCRIPTS[0])
        result = mod.main(["safe-folder", str(self.repo), "feat: import",
                           "--source-dir", str(link), "--apply"])
        self.assertEqual(result, 1)
        self.assertFalse((self.repo / "skill.txt").exists())

    def test_sensitive_names_are_case_insensitive(self):
        mod = self.module(SCRIPTS[0])
        for name in (".GIT", ".ENV.PROD", "Credentials.JSON"):
            with self.subTest(name=name):
                path = self.source / name
                path.write_text("sensitive")
                try:
                    with self.assertRaises(ValueError):
                        mod.preflight(self.source, self.repo)
                finally:
                    path.unlink()

    def test_source_symlink_swap_after_preflight_rejected(self):
        mod = self.module(SCRIPTS[0])
        planned = mod.preflight(self.source, self.repo)
        secret = self.root / "private.txt"
        secret.write_text("private data")
        (self.source / "skill.txt").unlink()
        (self.source / "skill.txt").symlink_to(secret)
        with self.assertRaises(ValueError):
            mod.copy_new_files(planned)
        self.assertFalse((self.repo / "skill.txt").exists())

    def test_destination_parent_symlink_swap_rejected(self):
        mod = self.module(SCRIPTS[0])
        nested = self.source / "nested"
        nested.mkdir()
        (nested / "lesson.txt").write_text("lesson")
        planned = mod.preflight(self.source, self.repo)
        external = self.root / "external"
        external.mkdir()
        (self.repo / "nested").symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            mod.copy_new_files(planned)
        self.assertFalse((external / "lesson.txt").exists())
        self.assertFalse((self.repo / "skill.txt").exists())

    def test_temp_file_cleaned_if_copy_raises(self):
        mod = self.module(SCRIPTS[0])
        planned = mod.preflight(self.source, self.repo)
        with patch.object(mod.shutil, "copyfileobj", side_effect=OSError("copy failed")):
            with self.assertRaises(OSError):
                mod.copy_new_files(planned)
        self.assertFalse((self.repo / "skill.txt").exists())
        self.assertEqual(sorted(p.name for p in self.repo.iterdir()), [".git", "README.md"])


if __name__ == "__main__":
    unittest.main()
