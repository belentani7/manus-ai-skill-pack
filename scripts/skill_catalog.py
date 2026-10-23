#!/usr/bin/env python3
"""Discover reusable SKILL.md packages without network access or dependencies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def discover(root: Path) -> list[dict[str, str]]:
    """Build a stable index of top-level skill directories."""
    result = []
    for folder in sorted(root.iterdir(), key=lambda path: path.name.casefold()):
        if not folder.is_dir() or folder.is_symlink() or folder.name.startswith("."):
            continue
        manifest = folder / "SKILL.md"
        if not manifest.is_file() or manifest.is_symlink():
            continue
        text = manifest.read_text(encoding="utf-8-sig")
        heading = next((line.lstrip("# ").strip() for line in text.splitlines()
                        if line.startswith("# ") and line[2:].strip()), folder.name)
        result.append({"id": folder.name, "title": heading, "path": f"{folder.name}/SKILL.md"})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="List reusable skills in this repository")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--filter", default="", help="Case-insensitive substring of skill ID or title")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"Not a directory: {args.root}")
    items = [item for item in discover(args.root)
             if args.filter.casefold() in (item["id"] + " " + item["title"]).casefold()]
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        for item in items:
            print(f'{item["id"]}\t{item["title"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
