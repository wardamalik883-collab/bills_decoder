"""Tests for calculation tools."""

from bill_decoder.calc_tools import (
    average,
    bill_helpers,
    cost_per_unit,
    count_above,
    difference,
    estimate_late_penalty,
    max_min_month,
    percentage,
    total,
)


def test_percentage_guide_example() -> None:
    """Taxes 569.62 of 3430.24 is about 16.6%."""
    assert percentage(569.62, 3430.24) == 16.61


def test_percentage_zero_whole() -> None:
    assert percentage(10, 0) is None
    assert percentage(None, 100) is None


def test_average_and_total() -> None:
    assert average([100, 200, 300]) == 200.0
    assert average([]) is None
    assert total([1, 2, 3.5]) == 6.5
    assert total([]) is None


def test_count_above_history() -> None:
    history = [{"month": "2026-01", "units": 210}, {"month": "2026-02", "units": 150}, {"month": "2026-03", "units": 260}]
    assert count_above(history, 200) == 2
    assert count_above([100, 250, 300], 200) == 2


def test_max_min_month() -> None:
    history = [{"month": "2026-01", "units": 210}, {"month": "2026-02", "units": 150}]
    result = max_min_month(history)
    assert result["max"] == {"month": "2026-01", "units": 210.0}
    assert result["min"] == {"month": "2026-02", "units": 150.0}
    assert max_min_month([]) == {"max": None, "min": None}


def test_difference_and_late_penalty() -> None:
    assert difference(3716, 3430) == 286.0
    assert difference(None, 5) is None
    assert estimate_late_penalty(3430, 3716) == 286.0


def test_cost_per_unit() -> None:
    assert cost_per_unit(3430.24, 151) == 22.72
    assert cost_per_unit(100, 0) is None


def test_bill_helpers() -> None:
    bill = {
        "units_consumed": 151,
        "current_bill": 3430.24,
        "total_taxes": 569.62,
        "total_charges": 2860.62,
        "payable_within_due_date": 3430,
        "payable_after_due_date": 3716,
    }
    context = {
        "usage_history": [
            {"month": "2025-04", "units": 210},
            {"month": "2025-05", "units": 150},
            {"month": "2025-06", "units": 230},
        ]
    }
    helpers = bill_helpers(bill, context)
    assert helpers["tax_percentage_of_current_bill"] == 16.61
    assert helpers["months_over_200_units"] == 2
    assert helpers["late_penalty_amount"] == 286.0
    assert helpers["history_months_count"] == 3
