"""CLI entry point for utility bill decoder pipeline."""

from __future__ import annotations

import argparse
import logging
import sys

from bill_decoder.config import load_config
from bill_decoder.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bill-decoder",
        description="Extract Level 1 JSON and answer Level 2 questions for Pakistani utility bills.",
    )
    parser.add_argument("--bills", required=True, help="Folder containing bill images (png/jpg/jpeg).")
    parser.add_argument("--level1-template", required=True, help="Path to the level1.csv template.")
    parser.add_argument("--level2-template", required=True, help="Path to the level2.csv template.")
    parser.add_argument("--out", required=True, help="Output directory for the completed CSVs.")
    parser.add_argument("--workers", type=int, default=2, help="Concurrent workers (default 2).")
    parser.add_argument("--only", default=None, help="Process only this bill_id.")
    parser.add_argument("--no-cache", action="store_true", help="Ignore and clear the LLM cache.")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = build_parser().parse_args(argv)

    try:
        config = load_config()
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 2

    report = run_pipeline(
        bills_dir=args.bills,
        level1_template=args.level1_template,
        level2_template=args.level2_template,
        out_dir=args.out,
        config=config,
        workers=args.workers,
        only=args.only,
        no_cache=args.no_cache,
    )

    print(
        f"\nDone: {report['successes']} ok, {report['fallbacks']} fallback(s), "
        f"{report['level1_rows']} L1 rows, {report['level2_rows']} L2 rows, "
        f"{report['elapsed_seconds']}s."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
