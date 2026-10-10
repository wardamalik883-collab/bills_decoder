"""Pydantic schemas and models for Level 1 bill extraction.

Enforces strict field types, dropped extra keys, and safe defaults.
"""

from __future__ import annotations

import re
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

ProviderType = Literal["KE", "LESCO", "IESCO"]

ChargeType = Literal[
    "energy",
    "fixed",
    "fpa",
    "quarterly_adjustment",
    "surcharge",
    "meter_rent",
    "subsidy",
    "other",
]

TaxType = Literal[
    "gst",
    "electricity_duty",
    "income_tax",
    "municipal_tax",
    "other_tax",
]


class ChargeItem(BaseModel):
    """Itemized electricity charge entry."""

    model_config = ConfigDict(extra="ignore", strict=True)

    type: ChargeType
    amount: float | int


class TaxItem(BaseModel):
    """Itemized tax or duty entry."""

    model_config = ConfigDict(extra="ignore", strict=True)

    type: TaxType
    amount: float | int


class Level1Bill(BaseModel):
    """Schema for Level 1 extracted bill data.

    Every field must be present in output even when null.
    Numbers are strictly numeric (never strings).
    Unknown keys are automatically dropped.
    """

    model_config = ConfigDict(extra="ignore", strict=True)

    provider: ProviderType | None = None
    tariff: str | None = None
    sanctioned_load_kw: float | int | None = None
    bill_month: str | None = None
    reading_date: str | None = None
    issue_date: str | None = None
    due_date: str | None = None
    previous_reading: float | int | None = None
    current_reading: float | int | None = None
    units_consumed: float | int | None = None
    charges: list[ChargeItem] = Field(default_factory=list)
    total_charges: float | int | None = None
    taxes: list[TaxItem] = Field(default_factory=list)
    total_taxes: float | int | None = None
    current_bill: float | int | None = None
    arrears: float | int | None = None
    payable_within_due_date: float | int | None = None
    payable_after_due_date: float | int | None = None

    @field_validator("bill_month")
    @classmethod
    def validate_bill_month(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError(f"bill_month must be YYYY-MM format, got '{v}'")
        return v

    @field_validator("reading_date", "issue_date", "due_date")
    @classmethod
    def validate_dates(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", v):
            raise ValueError(f"Date must be YYYY-MM-DD format, got '{v}'")
        return v


def safe_all_null_bill() -> Level1Bill:
    """Return a safe all-null Level 1 bill object with charges and taxes as []."""
    return Level1Bill(
        provider=None,
        tariff=None,
        sanctioned_load_kw=None,
        bill_month=None,
        reading_date=None,
        issue_date=None,
        due_date=None,
        previous_reading=None,
        current_reading=None,
        units_consumed=None,
        charges=[],
        total_charges=None,
        taxes=[],
        total_taxes=None,
        current_bill=None,
        arrears=None,
        payable_within_due_date=None,
        payable_after_due_date=None,
    )


def safe_all_null_dict() -> dict[str, Any]:
    """Return a safe all-null Level 1 dictionary with all fields present."""
    return safe_all_null_bill().model_dump()
