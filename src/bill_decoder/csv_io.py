"""CSV input/output module for reading templates and writing Level 1 / Level 2 CSVs."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def read_level1_template(path: Path | str) -> list[dict[str, str]]:
    """Read the Level 1 template (columns: bill_id, json)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_level2_template(path: Path | str) -> list[dict[str, str]]:
    """Read the Level 2 template (columns: bill_id, question_id, question, answer)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def level1_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    return list(rows[0].keys()) if rows else ["bill_id", "json"]


def level2_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    return list(rows[0].keys()) if rows else ["bill_id", "question_id", "question", "answer"]


def find_image(bills_dir: Path | str, bill_id: str) -> Path | None:
    """Locate an image for a bill_id by trying known extensions."""
    base = Path(bills_dir)
    for ext in IMAGE_EXTENSIONS:
        candidate = base / f"{bill_id}{ext}"
        if candidate.exists():
            return candidate
    return None


def dump_json_line(obj: Any) -> str:
    """Serialize an object as compact single-line JSON (UTF-8 preserved)."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def write_level1_csv(
    path: Path | str,
    rows: list[dict[str, str]],
    fieldnames: list[str] | None = None,
) -> None:
    """Write the Level 1 CSV, preserving row order and column names."""
    fieldnames = fieldnames or level1_fieldnames(rows)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def write_level2_csv(
    path: Path | str,
    rows: list[dict[str, str]],
    fieldnames: list[str] | None = None,
) -> None:
    """Write the Level 2 CSV, preserving row order and column names."""
    fieldnames = fieldnames or level2_fieldnames(rows)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})
