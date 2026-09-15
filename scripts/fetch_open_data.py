#!/usr/bin/env python3
"""Regenera el pack de datos abiertos de este repositorio.

Fuente: https://openrouter.ai/api/v1/models
Licencia: ver open-data/README.md
Solo libreria estandar (sin dependencias).
"""

from __future__ import annotations

import csv
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE_URL = "https://openrouter.ai/api/v1/models"
PACK = "ai-models"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "open-data"


def fetch(url: str = SOURCE_URL, timeout: float = 30.0):
    req = urllib.request.Request(url, headers={"User-Agent": "manus-ai-skill-pack-open-data/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ['data', 'results', 'docs', 'vulnerabilities', 'objects', 'records', 'items']:
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return [payload]


def _scalar(value):
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        return value[:300]
    if isinstance(value, list) and all(
        isinstance(x, (str, int, float)) for x in value
    ):
        return "; ".join(str(x) for x in value)[:300]
    return None


def normalize(items):
    rows = []
    for item in items:
        if not isinstance(item, dict):
            rows.append({"value": _scalar(item)})
            continue
        row = {}
        for key, value in item.items():
            scalar = _scalar(value)
            if scalar is not None:
                row[key] = scalar
        rows.append(row)
    return rows


def write(rows, out: Path = OUT):
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / f"{PACK}.json"
    csv_path = out / f"{PACK}.csv"
    meta = {
        "source": SOURCE_URL,
        "license": "ver open-data/README.md",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(rows),
    }
    json_path.write_text(
        json.dumps({"meta": meta, "records": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return json_path, csv_path


def main() -> int:
    rows = normalize(records(fetch()))
    json_path, csv_path = write(rows)
    print(f"{len(rows)} registros -> {json_path.name}, {csv_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
