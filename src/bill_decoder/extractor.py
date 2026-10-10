"""Level 1 bill data extractor using vision LLM.

Orchestrates preprocessing, LLM prompting, JSON parsing, Pydantic validation,
and single-retry error recovery with guaranteed safe all-null fallback.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from bill_decoder.config import Config
from bill_decoder.llm_client import LLMClient
from bill_decoder.preprocess import preprocess_image_path
from bill_decoder.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT
from bill_decoder.schema import Level1Bill, safe_all_null_dict

logger = logging.getLogger(__name__)


def parse_json_from_llm(raw_text: str) -> dict[str, Any]:
    """Parse JSON string from model response, stripping code fences or extra text."""
    text = raw_text.strip()

    # Strip markdown code fences if present
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(fence_pattern, text)
    if match:
        text = match.group(1).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
        raise ValueError(f"Expected JSON object, got {type(parsed).__name__}")
    except json.JSONDecodeError:
        # Fallback: search for first '{' and matching last '}'
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            sub = text[first_brace : last_brace + 1]
            parsed = json.loads(sub)
            if isinstance(parsed, dict):
                return parsed
        raise


def extract_level1(
    image_path: Path | str,
    config: Config | None = None,
    client: LLMClient | None = None,
) -> dict[str, Any]:
    """Extract Level 1 bill data from an image into a schema-validated dictionary.

    Args:
        image_path: Path to the bill image file.
        config: Optional Config instance.
        client: Optional LLMClient instance (useful for mocking/testing).

    Returns:
        A dictionary conforming to Level1Bill schema.
        Guaranteed to never raise an exception; returns safe_all_null_dict() on failure.
    """
    try:
        proc_image_path = preprocess_image_path(image_path)
    except Exception as e:
        logger.warning(
            "Preprocessing failed for %s: %s. Using original path.",
            image_path,
            e,
        )
        proc_image_path = Path(image_path)

    try:
        llm = client or LLMClient(config=config)
    except Exception as e:
        logger.warning("Could not initialize LLM client: %s. Returning safe all-null bill.", e)
        return safe_all_null_dict()

    # First attempt
    first_error: Exception | None = None
    try:
        raw_output = llm.generate(
            prompt=EXTRACTION_USER_PROMPT,
            image_path=proc_image_path,
            system=EXTRACTION_SYSTEM_PROMPT,
            json_mode=True,
        )
        parsed = parse_json_from_llm(raw_output)
        bill = Level1Bill.model_validate(parsed)
        return bill.model_dump()
    except Exception as err:
        first_error = err
        logger.warning(
            "Initial Level 1 extraction failed for %s with error: %s. Retrying once...",
            image_path,
            err,
        )

    # Retry ONCE with the error message appended
    try:
        retry_prompt = (
            f"{EXTRACTION_USER_PROMPT}\n\n"
            f"Your previous output failed with error: {str(first_error)}\n"
            "Please fix the issue and return strictly valid JSON matching the required schema."
        )
        raw_output_retry = llm.generate(
            prompt=retry_prompt,
            image_path=proc_image_path,
            system=EXTRACTION_SYSTEM_PROMPT,
            json_mode=True,
        )
        parsed_retry = parse_json_from_llm(raw_output_retry)
        bill_retry = Level1Bill.model_validate(parsed_retry)
        return bill_retry.model_dump()
    except Exception as err2:
        logger.warning(
            "Retry Level 1 extraction also failed for %s with error: %s. Returning safe all-null object.",
            image_path,
            err2,
        )
        return safe_all_null_dict()
