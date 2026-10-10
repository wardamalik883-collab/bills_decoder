"""Packaging script: build submission.zip safely (no secrets, <= 15 MB).

Usage:
    python scripts/package.py
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = PROJECT_ROOT / "submission.zip"
MAX_SIZE_BYTES = 15 * 1024 * 1024

EXCLUDE_DIRS = {".git", ".venv", "cache", "__pycache__", "data", ".pytest_cache", "output", ".mypy_cache"}
EXCLUDE_NAMES = {".env", "submission.zip"}

SOURCE_ITEMS = [
    "main.py",
    "pyproject.toml",
    "README.md",
    "requirements.txt",
    ".env.example",
    "scripts",
    "src",
    "tests",
]

SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"API_KEY=(?!your-api-key-here)[A-Za-z0-9\-_]{16,}"),
]


def _should_exclude(path: Path) -> bool:
    if path.name in EXCLUDE_NAMES:
        return True
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return True
    return False


def _iter_source_files() -> list[Path]:
    files: list[Path] = []
    for item in SOURCE_ITEMS:
        target = PROJECT_ROOT / item
        if not target.exists():
            continue
        if target.is_file():
            files.append(target)
        else:
            for p in target.rglob("*"):
                if p.is_file() and not _should_exclude(p.relative_to(PROJECT_ROOT)):
                    files.append(p)
    return files


def _scan_secrets(text: str) -> str | None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return pattern.pattern
    return None


def build_zip() -> Path:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # output/
        out_dir = PROJECT_ROOT / "output"
        for csv_name in ("level1.csv", "level2.csv"):
            csv_path = out_dir / csv_name
            if csv_path.exists():
                zf.write(csv_path, f"output/{csv_name}")
            else:
                print(f"  Warning: missing output/{csv_name}")

        # source/
        for path in _iter_source_files():
            rel = path.relative_to(PROJECT_ROOT)
            arcname = f"source/{rel.as_posix()}"
            data = path.read_bytes()
            if path.suffix.lower() in (".py", ".md", ".txt", ".toml", ".cfg", ".example"):
                secret = _scan_secrets(data.decode("utf-8", errors="ignore"))
                if secret and path.name != ".env.example":
                    print(f"  ABORT: secret-like content found in {rel} (pattern {secret})")
                    raise SystemExit(1)
            zf.writestr(arcname, data)

        # demo/ (optional)
        demo_dir = PROJECT_ROOT / "demo"
        if demo_dir.exists():
            for p in demo_dir.rglob("*"):
                if p.is_file() and p.suffix.lower() in (".mp4", ".mov", ".webm"):
                    zf.write(p, f"demo/{p.name}")

    size = ZIP_PATH.stat().st_size
    print(f"Created {ZIP_PATH.name}: {size / 1024:.1f} KB")
    if size > MAX_SIZE_BYTES:
        print("  ABORT: ZIP exceeds 15 MB limit")
        raise SystemExit(1)
    return ZIP_PATH


def main() -> None:
    print("Building submission.zip ...")
    build_zip()
    print("Done. Open the ZIP and verify structure: output/, source/, demo/ (optional).")


if __name__ == "__main__":
    main()
