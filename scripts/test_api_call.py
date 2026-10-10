"""
T01/T04 – Smoke-test: send one training bill image to the configured LLM using
the unified LLM client, and print ONLY the model's answer.

Usage:
    python scripts/test_api_call.py
"""

import glob
import sys
from pathlib import Path

from bill_decoder.llm_client import generate

# ── Pick the first image in data/train/bills/ ─────────────────────────────────
BILLS_DIR = Path(__file__).resolve().parent.parent / "data" / "train" / "bills"
images = sorted(
    glob.glob(str(BILLS_DIR / "*.png"))
    + glob.glob(str(BILLS_DIR / "*.jpg"))
    + glob.glob(str(BILLS_DIR / "*.jpeg"))
)

if not images:
    sys.exit(
        f"ERROR: No images found in {BILLS_DIR}. "
        "Download training bills first (see README)."
    )

image_path = images[0]
PROMPT = "What is the bill month and provider?"

# Generate using the unified client (respects whitelist, caching, retries, and config)
answer = generate(prompt=PROMPT, image_path=image_path, json_mode=False)
print(answer)
