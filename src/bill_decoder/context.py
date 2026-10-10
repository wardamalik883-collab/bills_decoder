"""Context extraction module: usage history, billing history, and metadata for Q&A."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from bill_decoder.config import Config
from bill_decoder.extractor import parse_json_from_llm
from bill_decoder.llm_client import LLMClient
from bill_decoder.preprocess import preprocess_image_path
from bill_decoder.prompts import CONTEXT_SYSTEM_PROMPT, CONTEXT_USER_PROMPT

logger = logging.getLogger(__name__)


class UsageMonth(BaseModel):
    model_config = ConfigDict(extra="ignore")

    month: str | None = None
    units: float | int | None = None


class BillingMonth(BaseModel):
    model_config = ConfigDict(extra="ignore")

    month: str | None = None
    billed_amount: float | int | None = None
    pay_date: str | None = None
    paid_amount: float | int | None = None


class LineItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    label: str | None = None
    amount: float | int | None = None


class BillContext(BaseModel):
    """Extra contextual facts extracted from a bill for Level 2 Q&A."""

    model_config = ConfigDict(extra="ignore")

    usage_history: list[UsageMonth] = Field(default_factory=list)
    billing_history: list[BillingMonth] = Field(default_factory=list)
    tax_percent: float | int | None = None
    energy_percent: float | int | None = None
    message_board: str | None = None
    late_surcharge_notes: str | None = None
    line_items: list[LineItem] = Field(default_factory=list)


def empty_context_dict() -> dict[str, Any]:
    """Return a safe empty context dictionary with all fields present."""
    return BillContext().model_dump()


def extract_context(
    image_path: Path | str,
    bill_json: dict[str, Any] | None = None,
    config: Config | None = None,
    client: LLMClient | None = None,
) -> dict[str, Any]:
    """Extract contextual facts (histories, splits, line items) from a bill image.

    Never raises: returns empty_context_dict() on any failure.
    """
    try:
        proc_image_path = preprocess_image_path(image_path)
    except Exception as e:
        logger.warning("Context preprocessing failed for %s: %s. Using original.", image_path, e)
        proc_image_path = Path(image_path)

    try:
        llm = client or LLMClient(config=config)
    except Exception as e:
        logger.warning("Context LLM init failed: %s. Returning empty context.", e)
        return empty_context_dict()

    try:
        raw = llm.generate(
            prompt=CONTEXT_USER_PROMPT,
            image_path=proc_image_path,
            system=CONTEXT_SYSTEM_PROMPT,
            json_mode=True,
        )
        parsed = parse_json_from_llm(raw)
        context = BillContext.model_validate(parsed)
        return context.model_dump()
    except Exception as e:
        logger.warning("Context extraction failed for %s: %s. Returning empty context.", image_path, e)
        return empty_context_dict()
