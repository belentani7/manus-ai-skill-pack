#!/usr/bin/env python3
"""Safely preview or import a Drive folder into a Git feature branch.

Read-only preview is the default. No shell interpolation, force push, or
implicit commit/push. --source-dir supports offline review and tests.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_FILES = 1000
SENSITIVE_NAMES = {".git", ".ssh", "id_rsa", "id_ed25519", "credentials.json", "token.json"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


def command(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def validate_folder(folder: str) -> str:
    if (not folder or folder.startswith(("-", "/")) or "\\" in folder
            or ":" in folder or any(ord(ch) < 32 for ch in folder)
            or any(part in {"", ".", ".."} for part in folder.split("/"))):
        raise ValueError("Invalid Drive folder path")
    return folder


def git_root(repo: Path) -> Path:
    if not repo.is_dir():
        raise ValueError("Repository directory does not exist")
    root = Path(command(["git", "rev-parse", "--show-toplevel"], cwd=repo)).resolve()
    if root != repo.resolve():
        raise ValueError("Repository path must be the Git checkout root")
    return root


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def preflight(source: Path, repo: Path) -> list[tuple[Path, Path, str]]:
    if not source.is_dir() or source.is_symlink():
        raise ValueError("Source must be a real directory")
    if source.resolve() == repo or repo in source.resolve().parents or source.resolve() in repo.parents:
        raise ValueError("Source must not contain the repository")
    planned: list[tuple[Path, Path, str]] = []
    for base, dirs, files in os.walk(source, followlinks=False):
        base_path = Path(base)
        for name in dirs + files:
            path = base_path / name
            if path.is_symlink():
                raise ValueError("Symlink refused: " + str(path.relative_to(source)))
            if name in SENSITIVE_NAMES or name.startswith(".env") or path.suffix.lower() in SENSITIVE_SUFFIXES:
                raise ValueError("Sensitive path refused: " + str(path.relative_to(source)))
        for name in sorted(files):
            src = base_path / name
            if not src.is_file() or src.stat().st_size > MAX_FILE_BYTES:
                raise ValueError("Non-regular or oversized file: " + str(src.relative_to(source)))
            relative = src.relative_to(source)
            dest = repo / relative
            if dest.is_symlink() or any(p.is_symlink() for p in dest.parents if p != repo.parent):
                raise ValueError("Destination symlink refused: " + str(relative))
            if dest.exists():
                if not dest.is_file():
                    raise ValueError("Destination is not a regular file: " + str(relative))
                if sha256(src) == sha256(dest):
                    continue
                raise FileExistsError("Existing file differs (no overwrite): " + str(relative))
            planned.append((src, dest, relative.as_posix()))
            if len(planned) > MAX_FILES:
                raise ValueError("Too many files; split the import into smaller batches")
    if not planned:
        print("No new files to import.")
    return planned


def copy_new_files(planned: list[tuple[Path, Path, str]]) -> None:
    created: list[Path] = []
    try:
        for src, dest, _ in planned:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() or dest.is_symlink():
                raise FileExistsError("Destination appeared during import: " + str(dest))
            with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as tmp:
                temp_path = Path(tmp.name)
                with src.open("rb") as reader:
                    shutil.copyfileobj(reader, tmp)
            try:
                if sha256(src) != sha256(temp_path):
                    raise OSError("Copy checksum mismatch")
                os.link(temp_path, dest)  # atomic create-only; never replace existing files
                created.append(dest)
            finally:
                temp_path.unlink(missing_ok=True)
    except Exception:
        for dest in reversed(created):
            dest.unlink(missing_ok=True)
        raise


def run_import(args: argparse.Namespace) -> int:
    folder = validate_folder(args.gdrive_folder)
    repo = git_root(Path(args.repo_path).expanduser())
    if args.push and not args.commit:
        raise ValueError("--push requires --commit")
    if args.commit and not args.apply:
        raise ValueError("--commit requires --apply")
    if args.apply:
        if command(["git", "status", "--porcelain", "--untracked-files=all"], cwd=repo):
            raise ValueError("Checkout must be clean before applying changes")
        branch = command(["git", "branch", "--show-current"], cwd=repo)
        if not branch or branch in {"main", "master"}:
            raise ValueError("Apply is permitted only on an explicit feature branch")
    with tempfile.TemporaryDirectory(prefix="gdrive-skill-sync-") as tmp:
        if args.source_dir:
            source = Path(args.source_dir).expanduser().resolve()
        else:
            source = Path(tmp)
            command(["rclone", "copy", "manus_google_drive:" + folder, str(source),
                     "--max-size", "25M", "--max-transfer", "250M"])
        planned = preflight(source, repo)
        for _, _, relative in planned:
            print(("IMPORT " if args.apply else "PREVIEW ") + relative)
        if not args.apply:
            print(f"Dry run: {len(planned)} new files; no repository changes, commits or pushes.")
            return 0
        copy_new_files(planned)
        print(f"Imported {len(planned)} new files to feature branch (no overwrite).")
        if args.commit and planned:
            command(["git", "add", "--", *[rel for _, _, rel in planned]], cwd=repo)
            command(["git", "commit", "-m", args.commit_message], cwd=repo)
            print("Local commit created.")
            if args.push:
                command(["git", "push", "origin", "HEAD"], cwd=repo)
                print("Feature branch pushed without force.")
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gdrive_folder", help="Drive folder path relative to configured remote")
    parser.add_argument("repo_path", help="Path to a clean local Git checkout")
    parser.add_argument("commit_message", help="Message used only with --commit")
    parser.add_argument("--source-dir", help="Offline source folder instead of rclone")
    parser.add_argument("--apply", action="store_true", help="Copy new files on a feature branch")
    parser.add_argument("--commit", action="store_true", help="Commit only newly imported files")
    parser.add_argument("--push", action="store_true", help="Push feature branch; requires --commit")
    args = parser.parse_args(argv)
    try:
        return run_import(args)
    except (ValueError, FileExistsError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Sync blocked: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
