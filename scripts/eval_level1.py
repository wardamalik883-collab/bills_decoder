"""Level 1 accuracy evaluation script.

Compares extractor output against ground truth (KESC_0008.expected.json)
and draft reference fixtures. Uses disk caching so repeated runs are fast and free.

Usage:
    python scripts/eval_level1.py
"""

import json
import math
import sys
from pathlib import Path
from typing import Any

# Ensure src/ is in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from bill_decoder.extractor import extract_level1

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BILLS_DIR = PROJECT_ROOT / "data" / "train" / "bills"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"

SCALAR_FIELDS = [
    "provider",
    "tariff",
    "sanctioned_load_kw",
    "bill_month",
    "reading_date",
    "issue_date",
    "due_date",
    "previous_reading",
    "current_reading",
    "units_consumed",
    "total_charges",
    "total_taxes",
    "current_bill",
    "arrears",
    "payable_within_due_date",
    "payable_after_due_date",
]


def compare_value(expected: Any, actual: Any) -> bool:
    """Compare expected and actual values (numbers within +-1, text exact)."""
    if expected is None and actual is None:
        return True
    if expected is None or actual is None:
        return False

    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(expected) - float(actual)) <= 1.0

    return str(expected).strip() == str(actual).strip()


def evaluate_bill(bill_stem: str, fixture_path: Path, is_truth: bool) -> dict[str, Any]:
    """Evaluate extraction accuracy for a single bill fixture."""
    # Find image file
    candidates = list(BILLS_DIR.glob(f"{bill_stem}.*"))
    valid_images = [p for p in candidates if p.suffix.lower() in (".png", ".jpg", ".jpeg")]

    if not valid_images:
        return {
            "bill": bill_stem,
            "status": "MISSING_IMAGE",
            "score": 0.0,
            "fields": {},
        }

    image_path = valid_images[0]
    expected_data = json.loads(fixture_path.read_text(encoding="utf-8"))

    # Extract using cached LLM client
    extracted_data = extract_level1(image_path)

    field_results: dict[str, dict[str, Any]] = {}
    matches = 0
    total = len(SCALAR_FIELDS)

    for field in SCALAR_FIELDS:
        exp_val = expected_data.get(field)
        act_val = extracted_data.get(field)
        is_match = compare_value(exp_val, act_val)
        if is_match:
            matches += 1
        field_results[field] = {
            "expected": exp_val,
            "actual": act_val,
            "match": is_match,
        }

    score = (matches / total) * 100.0 if total > 0 else 0.0
    return {
        "bill": bill_stem,
        "is_truth": is_truth,
        "status": "EVALUATED",
        "matches": matches,
        "total": total,
        "score": score,
        "fields": field_results,
    }


def main() -> None:
    print("=" * 70)
    print(" LEVEL 1 EXTRACTION ACCURACY EVALUATION")
    print("=" * 70)

    # Locate fixtures
    fixture_files: list[tuple[str, Path, bool]] = []

    # 1. Ground truth
    truth_file = FIXTURES_DIR / "KESC_0008.expected.json"
    if truth_file.exists():
        fixture_files.append(("KESC_0008", truth_file, True))

    # 2. Draft fixtures
    for p in sorted(FIXTURES_DIR.glob("*.draft.json")):
        stem = p.name.replace(".draft.json", "")
        fixture_files.append((stem, p, False))

    if not fixture_files:
        sys.exit(f"No fixtures found in {FIXTURES_DIR}")

    total_matches = 0
    total_fields = 0

    for bill_stem, fix_path, is_truth in fixture_files:
        ref_label = "[GROUND TRUTH]" if is_truth else "[DRAFT REF]"
        print(f"\n--- Evaluating {bill_stem} {ref_label} ---")
        result = evaluate_bill(bill_stem, fix_path, is_truth)

        if result["status"] == "MISSING_IMAGE":
            print(f"  Warning: No image found for {bill_stem} in {BILLS_DIR}. Skipping.")
            continue

        print(f"{'Field':<25} | {'Expected':<18} | {'Extracted':<18} | {'Status'}")
        print("-" * 70)
        for field, info in result["fields"].items():
            exp_str = str(info["expected"])[:17]
            act_str = str(info["actual"])[:17]
            status_str = "PASS" if info["match"] else "FAIL"
            print(f"{field:<25} | {exp_str:<18} | {act_str:<18} | {status_str}")

        print(f"Bill Score: {result['matches']}/{result['total']} ({result['score']:.1f}%)")

        total_matches += result["matches"]
        total_fields += result["total"]

    print("\n" + "=" * 70)
    if total_fields > 0:
        overall_score = (total_matches / total_fields) * 100.0
        print(f"OVERALL EVALUATION SCORE: {total_matches}/{total_fields} ({overall_score:.1f}%)")
    else:
        print("No bills evaluated.")
    print("=" * 70)


if __name__ == "__main__":
    main()
