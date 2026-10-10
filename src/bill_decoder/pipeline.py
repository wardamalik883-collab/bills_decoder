"""End-to-end extraction and Q&A pipeline orchestrator."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from bill_decoder.config import Config
from bill_decoder.context import empty_context_dict, extract_context
from bill_decoder.csv_io import (
    dump_json_line,
    find_image,
    level1_fieldnames,
    level2_fieldnames,
    read_level1_template,
    read_level2_template,
    write_level1_csv,
    write_level2_csv,
)
from bill_decoder.extractor import extract_level1
from bill_decoder.llm_client import LLMClient
from bill_decoder.qa import FALLBACK_ANSWER, answer_questions
from bill_decoder.schema import safe_all_null_dict

logger = logging.getLogger(__name__)


def _group_questions(level2_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    grouped: dict[str, dict[str, str]] = {}
    for row in level2_rows:
        bill_id = row.get("bill_id") or ""
        qid = row.get("question_id") or ""
        grouped.setdefault(bill_id, {})[qid] = row.get("question") or ""
    return grouped


def _process_bill(
    bill_id: str,
    image_path: Path | None,
    questions: dict[str, str],
    config: Config,
    no_cache: bool,
) -> dict[str, Any]:
    """Extract and answer one bill. Never raises; returns fallbacks on failure."""
    result: dict[str, Any] = {
        "bill_id": bill_id,
        "fell_back": False,
        "reasons": [],
    }

    if image_path is None:
        result["bill_json"] = safe_all_null_dict()
        result["context"] = empty_context_dict()
        result["answers"] = {qid: FALLBACK_ANSWER for qid in questions}
        result["fell_back"] = True
        result["reasons"].append("image_not_found")
        return result

    try:
        client = LLMClient(config=config)
    except Exception as e:
        result["bill_json"] = safe_all_null_dict()
        result["context"] = empty_context_dict()
        result["answers"] = {qid: FALLBACK_ANSWER for qid in questions}
        result["fell_back"] = True
        result["reasons"].append(f"client_init_failed: {e}")
        return result

    try:
        bill_json = extract_level1(image_path, config=config, client=client)
        scalar_keys = ("provider", "tariff", "bill_month", "current_bill", "units_consumed")
        if all(bill_json.get(k) is None for k in scalar_keys):
            result["fell_back"] = True
            result["reasons"].append("extraction_empty")
    except Exception as e:
        bill_json = safe_all_null_dict()
        result["fell_back"] = True
        result["reasons"].append(f"extract_failed: {e}")

    try:
        context = extract_context(image_path, bill_json=bill_json, config=config, client=client)
    except Exception as e:
        context = empty_context_dict()
        result["reasons"].append(f"context_failed: {e}")

    try:
        answers = answer_questions(
            bill_json, context, image_path, questions, config=config, client=client
        )
        if any(ans == FALLBACK_ANSWER for ans in answers.values()):
            result["reasons"].append("some_answers_fell_back")
    except Exception as e:
        answers = {qid: FALLBACK_ANSWER for qid in questions}
        result["fell_back"] = True
        result["reasons"].append(f"qa_failed: {e}")

    result["bill_json"] = bill_json
    result["context"] = context
    result["answers"] = answers
    return result


def run_pipeline(
    bills_dir: Path | str,
    level1_template: Path | str,
    level2_template: Path | str,
    out_dir: Path | str,
    config: Config,
    workers: int = 2,
    only: str | None = None,
    no_cache: bool = False,
) -> dict[str, Any]:
    """Run the full pipeline and write level1.csv, level2.csv and run_report.json."""
    start = time.time()
    l1_rows = read_level1_template(level1_template)
    l2_rows = read_level2_template(level2_template)
    grouped_questions = _group_questions(l2_rows)

    bill_ids: list[str] = []
    for row in l1_rows:
        bid = row.get("bill_id") or ""
        if bid and bid not in bill_ids:
            bill_ids.append(bid)
    if only:
        bill_ids = [b for b in bill_ids if b == only]

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if no_cache and config.cache_dir.exists():
        for cache_file in config.cache_dir.glob("*.txt"):
            try:
                cache_file.unlink()
            except OSError:
                pass

    logger.info("Processing %d bill(s) with %d worker(s)...", len(bill_ids), workers)

    processed: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {}
        for i, bill_id in enumerate(bill_ids, start=1):
            image = find_image(bills_dir, bill_id)
            futures[executor.submit(
                _process_bill, bill_id, image, grouped_questions.get(bill_id, {}), config, no_cache
            )] = (i, bill_id)
        for future in as_completed(futures):
            i, bill_id = futures[future]
            try:
                result = future.result()
            except Exception as e:  # pragma: no cover - defensive
                result = {
                    "bill_id": bill_id,
                    "bill_json": safe_all_null_dict(),
                    "context": empty_context_dict(),
                    "answers": {qid: FALLBACK_ANSWER for qid in grouped_questions.get(bill_id, {})},
                    "fell_back": True,
                    "reasons": [f"unexpected: {e}"],
                }
            processed[bill_id] = result
            status = "fallback" if result["fell_back"] else "ok"
            logger.info("[%d/%d] %s ... %s", i, len(bill_ids), bill_id, status)

    # Build Level 1 output rows (preserve template order)
    l1_out: list[dict[str, str]] = []
    for row in l1_rows:
        bid = row.get("bill_id") or ""
        if only and bid != only:
            continue
        result = processed.get(bid)
        bill_json = result["bill_json"] if result else safe_all_null_dict()
        new_row = dict(row)
        new_row["json"] = dump_json_line(bill_json)
        l1_out.append(new_row)

    # Build Level 2 output rows (preserve template order)
    l2_out: list[dict[str, str]] = []
    for row in l2_rows:
        bid = row.get("bill_id") or ""
        if only and bid != only:
            continue
        result = processed.get(bid)
        answers = result["answers"] if result else {}
        qid = row.get("question_id") or ""
        answer = answers.get(qid) or FALLBACK_ANSWER
        new_row = dict(row)
        new_row["answer"] = answer
        l2_out.append(new_row)

    write_level1_csv(out_path / "level1.csv", l1_out, level1_fieldnames(l1_rows))
    write_level2_csv(out_path / "level2.csv", l2_out, level2_fieldnames(l2_rows))

    report = {
        "bills_processed": len(bill_ids),
        "successes": sum(1 for b in bill_ids if not processed.get(b, {}).get("fell_back")),
        "fallbacks": sum(1 for b in bill_ids if processed.get(b, {}).get("fell_back")),
        "level1_rows": len(l1_out),
        "level2_rows": len(l2_out),
        "elapsed_seconds": round(time.time() - start, 2),
        "fallback_bills": {
            b: processed[b]["reasons"] for b in bill_ids if processed.get(b, {}).get("fell_back")
        },
    }
    (out_path / "run_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Pipeline complete in %.1fs: %s", report["elapsed_seconds"], report)
    return report
