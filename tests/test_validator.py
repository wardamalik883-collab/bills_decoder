"""Unit tests for bill validator sanity checks."""

import json
from pathlib import Path
from bill_decoder.schema import Level1Bill
from bill_decoder.validator import validate_bill


def _get_base_valid_data() -> dict:
    """Load valid KESC_0008 fixture as clean baseline."""
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "KESC_0008.expected.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def test_valid_bill_has_no_warnings() -> None:
    """Clean ground truth bill produces zero validation warnings."""
    data = _get_base_valid_data()
    warnings = validate_bill(data)
    assert warnings == []

    # Also test with Level1Bill model
    bill = Level1Bill.model_validate(data)
    assert validate_bill(bill) == []


def test_units_consumed_matches_readings() -> None:
    """Warning is emitted when reading difference does not match units_consumed."""
    data = _get_base_valid_data()
    # 8970 - 8819 = 151, change units_consumed to 200
    data["units_consumed"] = 200

    warnings = validate_bill(data)
    assert any("does not match units_consumed" in w for w in warnings)


def test_total_charges_matches_sum_charges() -> None:
    """Warning is emitted when sum of charges differs from total_charges."""
    data = _get_base_valid_data()
    data["total_charges"] = 5000.0  # Real sum is 2860.62

    warnings = validate_bill(data)
    assert any("charges sum to" in w and "total_charges is 5000.00" in w for w in warnings)


def test_total_taxes_matches_sum_taxes() -> None:
    """Warning is emitted when sum of taxes differs from total_taxes."""
    data = _get_base_valid_data()
    data["total_taxes"] = 1200.0  # Real sum is 569.62

    warnings = validate_bill(data)
    assert any("taxes sum to" in w and "total_taxes is 1200.00" in w for w in warnings)


def test_payable_after_due_date_greater_or_equal() -> None:
    """Warning is emitted when payable_after_due_date is less than payable_within_due_date."""
    data = _get_base_valid_data()
    data["payable_within_due_date"] = 4000
    data["payable_after_due_date"] = 3500

    warnings = validate_bill(data)
    assert any("payable_after_due_date (3500) is less than" in w for w in warnings)


def test_due_date_after_issue_date() -> None:
    """Warning is emitted when due_date is chronologically earlier than issue_date."""
    data = _get_base_valid_data()
    data["issue_date"] = "2026-04-25"
    data["due_date"] = "2026-04-10"

    warnings = validate_bill(data)
    assert any("due_date (2026-04-10) is before issue_date (2026-04-25)" in w for w in warnings)


def test_invalid_date_formats() -> None:
    """Warning is emitted when dates do not conform to ISO standards."""
    data = _get_base_valid_data()
    data["bill_month"] = "04-2026"  # Expected YYYY-MM
    data["reading_date"] = "2026/04/03"  # Expected YYYY-MM-DD

    warnings = validate_bill(data)
    assert any("Invalid bill_month format" in w for w in warnings)
    assert any("Invalid reading_date format" in w for w in warnings)


def test_subsidy_amount_must_be_negative() -> None:
    """Warning is emitted when a subsidy charge amount is positive."""
    data = _get_base_valid_data()
    data["charges"].append({"type": "subsidy", "amount": 500.0})

    warnings = validate_bill(data)
    assert any("Subsidy charge amount must be negative, got 500.0" in w for w in warnings)


def test_no_identifier_like_content() -> None:
    """Warning is emitted when long digit sequences or sensitive keywords appear."""
    data = _get_base_valid_data()
    data["tariff"] = "A1-R CNIC: 42101-1234567-1"

    warnings = validate_bill(data)
    assert any("contains forbidden identifier keyword 'cnic'" in w for w in warnings)
    assert any("sensitive digits/identifier" in w for w in warnings)
