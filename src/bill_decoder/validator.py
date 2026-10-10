"""Validation checks and sanity rules for Level 1 extracted bill data.

Produces human-readable warnings to detect inconsistencies (e.g. sums mismatch,
readings mismatch, date order, positive subsidies, or leaked identifiers).
Never raises exceptions and never modifies data.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from bill_decoder.schema import Level1Bill

# Pattern to detect sensitive identifier sequences (e.g. 10+ digits or CNIC pattern)
IDENTIFIER_DIGIT_PATTERN = re.compile(r"\b\d{10,}\b|\b\d{5}-\d{7}-\d\b")
IDENTIFIER_KEYWORDS = [
    "cnic",
    "meter no",
    "meter number",
    "account no",
    "account number",
    "consumer no",
    "consumer id",
    "reference no",
    "ref no",
]


def validate_bill(bill: dict[str, Any] | Level1Bill) -> list[str]:
    """Perform sanity checks on extracted bill data.

    Args:
        bill: A Level1Bill model instance or a dictionary.

    Returns:
        A list of warning strings. Empty list indicates all sanity checks passed.
        Guaranteed to never raise an exception and never mutate input values.
    """
    warnings: list[str] = []

    try:
        data = bill.model_dump() if isinstance(bill, Level1Bill) else dict(bill)
    except Exception as e:
        return [f"Failed to access bill data: {e}"]

    # 1. Readings vs Units Consumed
    prev_r = data.get("previous_reading")
    curr_r = data.get("current_reading")
    units = data.get("units_consumed")
    if prev_r is not None and curr_r is not None and units is not None:
        try:
            diff = float(curr_r) - float(prev_r)
            # Only validate if not rolled over / negative
            if diff >= 0 and abs(diff - float(units)) > 1.5:
                warnings.append(
                    f"Readings difference ({curr_r} - {prev_r} = {diff:.1f}) "
                    f"does not match units_consumed ({units})."
                )
        except (ValueError, TypeError):
            pass

    # 2. Sum of charges vs Total Charges
    charges = data.get("charges") or []
    total_charges = data.get("total_charges")
    if total_charges is not None and charges:
        try:
            sum_charges = sum(float(c.get("amount", 0)) for c in charges if isinstance(c, dict))
            if abs(sum_charges - float(total_charges)) > 1.5:
                warnings.append(
                    f"charges sum to {sum_charges:.2f} but printed total_charges is {float(total_charges):.2f}; "
                    "re-read the charges section. Extract as printed, do not adjust values to make them add up."
                )
        except (ValueError, TypeError):
            pass

    # 3. Sum of taxes vs Total Taxes
    taxes = data.get("taxes") or []
    total_taxes = data.get("total_taxes")
    if total_taxes is not None and taxes:
        try:
            sum_taxes = sum(float(t.get("amount", 0)) for t in taxes if isinstance(t, dict))
            if abs(sum_taxes - float(total_taxes)) > 1.5:
                warnings.append(
                    f"taxes sum to {sum_taxes:.2f} but printed total_taxes is {float(total_taxes):.2f}; "
                    "re-read the taxes section. Extract as printed, do not adjust values to make them add up."
                )
        except (ValueError, TypeError):
            pass

    # 4. Payable amounts: payable_after_due_date >= payable_within_due_date
    within_due = data.get("payable_within_due_date")
    after_due = data.get("payable_after_due_date")
    if within_due is not None and after_due is not None:
        try:
            if float(within_due) > 0 and float(after_due) < float(within_due):
                warnings.append(
                    f"payable_after_due_date ({after_due}) is less than "
                    f"payable_within_due_date ({within_due})."
                )
        except (ValueError, TypeError):
            pass

    # 5. Date formats and Due date after Issue date
    issue_date_str = data.get("issue_date")
    due_date_str = data.get("due_date")
    reading_date_str = data.get("reading_date")
    bill_month_str = data.get("bill_month")

    if bill_month_str:
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", str(bill_month_str)):
            warnings.append(f"Invalid bill_month format: '{bill_month_str}' (expected YYYY-MM).")

    for field_name, d_val in [
        ("reading_date", reading_date_str),
        ("issue_date", issue_date_str),
        ("due_date", due_date_str),
    ]:
        if d_val:
            if not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", str(d_val)):
                warnings.append(f"Invalid {field_name} format: '{d_val}' (expected YYYY-MM-DD).")

    if issue_date_str and due_date_str:
        try:
            dt_issue = datetime.strptime(str(issue_date_str), "%Y-%m-%d")
            dt_due = datetime.strptime(str(due_date_str), "%Y-%m-%d")
            if dt_due < dt_issue:
                warnings.append(
                    f"due_date ({due_date_str}) is before issue_date ({issue_date_str})."
                )
        except ValueError:
            pass

    # 6. Subsidy amounts must be negative
    for c in charges:
        if isinstance(c, dict) and c.get("type") == "subsidy":
            amt = c.get("amount")
            if amt is not None:
                try:
                    if float(amt) > 0:
                        warnings.append(
                            f"Subsidy charge amount must be negative, got {amt}."
                        )
                except (ValueError, TypeError):
                    pass

    # 7. No identifier-like content
    for key, val in data.items():
        if isinstance(val, str):
            val_lower = val.lower()
            if IDENTIFIER_DIGIT_PATTERN.search(val):
                warnings.append(
                    f"Field '{key}' appears to contain sensitive digits/identifier: '{val}'."
                )
            for kw in IDENTIFIER_KEYWORDS:
                if kw in val_lower:
                    warnings.append(
                        f"Field '{key}' contains forbidden identifier keyword '{kw}': '{val}'."
                    )

    return warnings
