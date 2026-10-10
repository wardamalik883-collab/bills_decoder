"""
T01 – Smoke-test: send one training bill image to the configured LLM and
print the model's answer.

Usage:
    python scripts/test_api_call.py
"""

import os
import sys
import glob
import base64
import mimetypes
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env ────────────────────────────────────────────────────────────────
load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "").lower()
MODEL_NAME = os.getenv("MODEL_NAME", "")
API_KEY = os.getenv("API_KEY", "")

if not API_KEY:
    sys.exit("ERROR: API_KEY is not set in .env")
if not MODEL_NAME:
    sys.exit("ERROR: MODEL_NAME is not set in .env")

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

# ── Google (google-genai SDK) ─────────────────────────────────────────────────
if MODEL_PROVIDER == "google":
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=API_KEY)

    # Read the image file
    img_bytes = Path(image_path).read_bytes()
    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=img_bytes, mime_type=mime_type),
                    types.Part.from_text(text=PROMPT),
                ],
            )
        ],
    )
    print(response.text)

else:
    sys.exit(f"ERROR: Unsupported MODEL_PROVIDER='{MODEL_PROVIDER}'. Supported: google")
