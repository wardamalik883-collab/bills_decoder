"""Extract Level 1 JSON from a single bill image.

Usage:
    python scripts/extract_one.py data/train/bills/KESC_0008.png
"""

import json
import sys
from pathlib import Path

# Ensure src/ is in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from bill_decoder.extractor import extract_level1


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/extract_one.py <path_to_bill_image>")

    image_path = Path(sys.argv[1])
    if not image_path.exists():
        sys.exit(f"Error: File not found at {image_path}")

    # Extract Level 1 data
    result = extract_level1(image_path)

    # Print pure JSON output only (never prints env values or secrets)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
