"""Unit tests for Level 1 bill schema and validation."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from bill_decoder.schema import (
    ChargeItem,
    Level1Bill,
    TaxItem,
    safe_all_null_bill,
    safe_all_null_dict,
)


def test_kesc_0008_expected_validates() -> None:
    """KESC_0008.expected.json validates cleanly against Level1Bill schema."""
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "KESC_0008.expected.json"
    raw_data = json.loads(fixture_path.read_text(encoding="utf-8"))

    bill = Level1Bill.model_validate(raw_data)
    assert bill.provider == "KE"
    assert bill.tariff == "A1-R"
    assert bill.sanctioned_load_kw == 3
    assert bill.bill_month == "2026-04"
    assert bill.units_consumed == 151
    assert len(bill.charges) == 6
    assert bill.total_charges == 2860.62
    assert len(bill.taxes) == 3
    assert bill.total_taxes == 569.62
    assert bill.current_bill == 3430.24
    assert bill.arrears == -0.53
    assert bill.payable_within_due_date == 3430
    assert bill.payable_after_due_date == 3716


def test_strings_in_numeric_fields_fail() -> None:
    """Strings passed into numeric fields must fail validation."""
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "KESC_0008.expected.json"
    valid_data = json.loads(fixture_path.read_text(encoding="utf-8"))

    # Test top-level numeric field
    bad_data_1 = dict(valid_data)
    bad_data_1["units_consumed"] = "151"
    with pytest.raises(ValidationError):
        Level1Bill.model_validate(bad_data_1)

    bad_data_2 = dict(valid_data)
    bad_data_2["total_charges"] = "2860.62"
    with pytest.raises(ValidationError):
        Level1Bill.model_validate(bad_data_2)

    # Test nested charge amount
    bad_data_3 = dict(valid_data)
    bad_data_3["charges"] = [{"type": "fixed", "amount": "900"}]
    with pytest.raises(ValidationError):
        Level1Bill.model_validate(bad_data_3)

    # Test nested tax amount
    bad_data_4 = dict(valid_data)
    bad_data_4["taxes"] = [{"type": "gst", "amount": "500"}]
    with pytest.raises(ValidationError):
        Level1Bill.model_validate(bad_data_4)


def test_unknown_keys_are_dropped() -> None:
    """Unknown / unexpected keys must be silently dropped from the model."""
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "KESC_0008.expected.json"
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    data["extra_account_id"] = "12345678"
    data["unknown_random_key"] = True

    bill = Level1Bill.model_validate(data)
    dumped = bill.model_dump()

    assert "extra_account_id" not in dumped
    assert "unknown_random_key" not in dumped
    assert hasattr(bill, "units_consumed")


def test_safe_all_null_object() -> None:
    """Helper returns object with all fields present, null values, and empty lists."""
    bill = safe_all_null_bill()
    data = safe_all_null_dict()

    expected_keys = {
        "provider",
        "tariff",
        "sanctioned_load_kw",
        "bill_month",
        "reading_date",
        "issue_date",
        "due_date",
        "previous_reading",
        "current_reading",
        "units_consumed",
        "charges",
        "total_charges",
        "taxes",
        "total_taxes",
        "current_bill",
        "arrears",
        "payable_within_due_date",
        "payable_after_due_date",
    }

    assert set(data.keys()) == expected_keys
    assert data["charges"] == []
    assert data["taxes"] == []
    assert data["provider"] is None
    assert data["units_consumed"] is None


def test_invalid_date_and_provider_validation() -> None:
    """Invalid date format or invalid provider must raise ValidationError."""
    with pytest.raises(ValidationError):
        Level1Bill(provider="XYZ")  # Not KE/LESCO/IESCO

    with pytest.raises(ValidationError):
        Level1Bill(bill_month="2026/04")  # Not YYYY-MM

    with pytest.raises(ValidationError):
        Level1Bill(due_date="21-04-2026")  # Not YYYY-MM-DD
