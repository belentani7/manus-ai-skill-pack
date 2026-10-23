#!/usr/bin/env python3
"""Search local SKILL.md directories without installing dependencies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return values
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key in ("name", "description"):
            values[key] = value.strip().strip('"').strip("'")
    return {}


def discover(root: Path) -> list[dict[str, str]]:
    result = []
    for folder in sorted(root.iterdir(), key=lambda p: p.name.casefold()):
        if not folder.is_dir() or folder.is_symlink():
            continue
        manifest = folder / "SKILL.md"
        if not manifest.is_file() or manifest.is_symlink():
            continue
        fields = parse_metadata(manifest.read_text(encoding="utf-8", errors="replace"))
        result.append({"name": fields.get("name") or folder.name,
                       "path": folder.name,
                       "description": fields.get("description", "")})
    return result


def search(root: Path, query: str) -> list[dict[str, str]]:
    terms = query.casefold().split()
    return [skill for skill in discover(root)
            if all(term in " ".join(skill.values()).casefold() for term in terms)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find skills by name and description")
    parser.add_argument("query", nargs="*")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error("root directory does not exist")
    if args.limit < 1:
        parser.error("--limit must be positive")
    matches = search(args.root, " ".join(args.query))
    shown = matches[:args.limit]
    if args.json:
        print(json.dumps({"count": len(matches), "shown": len(shown), "skills": shown}, ensure_ascii=False))
    else:
        for skill in shown:
            print(f"{skill['name']}\t{skill['path']}\t{skill['description']}")
        print(f"Showing {len(shown)} of {len(matches)} skills")
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
