"""Deterministic calculation tools for percentages, differences, averages, and sums.

All math for Level 2 answers is done here in Python so the LLM only quotes facts.
"""

from __future__ import annotations

from typing import Any, Iterable


def _to_float(value: Any) -> float | None:
    """Coerce a numeric-ish value to float, returning None on failure."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def percentage(part: float | int | None, whole: float | int | None) -> float | None:
    """Return part/whole * 100, or None when not computable."""
    p = _to_float(part)
    w = _to_float(whole)
    if p is None or w is None or w == 0:
        return None
    return round(p / w * 100.0, 2)


def average(values: Iterable[Any]) -> float | None:
    """Return the mean of numeric values, or None if empty/invalid."""
    nums = [n for n in (_to_float(v) for v in values) if n is not None]
    if not nums:
        return None
    return round(sum(nums) / len(nums), 2)


def total(values: Iterable[Any]) -> float | None:
    """Return the sum of numeric values, or None if empty."""
    nums = [n for n in (_to_float(v) for v in values) if n is not None]
    if not nums:
        return None
    return round(sum(nums), 2)


def count_above(history: Iterable[Any], threshold: float | int) -> int:
    """Count entries above a threshold.

    Accepts an iterable of numbers or of dicts with a 'units' key.
    """
    thr = _to_float(threshold)
    count = 0
    for item in history:
        if isinstance(item, dict):
            val = _to_float(item.get("units"))
        else:
            val = _to_float(item)
        if val is not None and thr is not None and val > thr:
            count += 1
    return count


def max_min_month(history: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Return the max and min usage months from a month->units history."""
    entries = [
        (h.get("month"), _to_float(h.get("units")))
        for h in history
        if isinstance(h, dict)
    ]
    entries = [(m, u) for m, u in entries if u is not None]
    if not entries:
        return {"max": None, "min": None}
    max_month, max_units = max(entries, key=lambda e: e[1])
    min_month, min_units = min(entries, key=lambda e: e[1])
    return {
        "max": {"month": max_month, "units": max_units},
        "min": {"month": min_month, "units": min_units},
    }


def difference(a: float | int | None, b: float | int | None) -> float | None:
    """Return a - b, or None if either value is missing."""
    fa = _to_float(a)
    fb = _to_float(b)
    if fa is None or fb is None:
        return None
    return round(fa - fb, 2)


def cost_per_unit(amount: float | int | None, units: float | int | None) -> float | None:
    """Return amount/units (average cost per unit), or None."""
    a = _to_float(amount)
    u = _to_float(units)
    if a is None or u is None or u == 0:
        return None
    return round(a / u, 2)


def estimate_late_penalty(
    payable_within: float | int | None,
    payable_after: float | int | None,
) -> float | None:
    """Return the printed late-payment penalty (after - within), or None."""
    return difference(payable_after, payable_within)


def estimate_extra_usage_cost(
    avg_cost_per_unit: float | int | None,
    extra_units: float | int | None,
) -> float | None:
    """Estimate cost of extra units using an average cost per unit."""
    c = _to_float(avg_cost_per_unit)
    u = _to_float(extra_units)
    if c is None or u is None:
        return None
    return round(c * u, 2)


def bill_helpers(bill: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Compute a bundle of helper numbers from Level 1 bill + context.

    Returns a JSON-serializable dict of pre-computed facts for the Q&A prompt.
    """
    context = context or {}
    history = context.get("usage_history") or []
    units = bill.get("units_consumed")
    current_bill = bill.get("current_bill")
    total_taxes = bill.get("total_taxes")

    helpers: dict[str, Any] = {
        "tax_percentage_of_current_bill": percentage(total_taxes, current_bill),
        "charges_percentage_of_current_bill": percentage(bill.get("total_charges"), current_bill),
        "average_cost_per_unit": cost_per_unit(current_bill, units),
        "average_monthly_units": average([h.get("units") for h in history if isinstance(h, dict)]),
        "months_over_200_units": count_above(history, 200),
        "months_over_300_units": count_above(history, 300),
        "usage_max_min": max_min_month(history),
        "late_penalty_amount": estimate_late_penalty(
            bill.get("payable_within_due_date"), bill.get("payable_after_due_date")
        ),
        "history_months_count": len(history),
    }
    return helpers
