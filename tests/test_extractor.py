"""Unit tests for extractor module and image preprocessing with mocked LLM."""

from pathlib import Path
from unittest.mock import MagicMock
from PIL import Image

from bill_decoder.extractor import extract_level1, parse_json_from_llm
from bill_decoder.llm_client import LLMClient
from bill_decoder.preprocess import load_and_preprocess_image, preprocess_image_path
from bill_decoder.schema import safe_all_null_dict


def _create_test_image(path: Path, size: tuple[int, int] = (200, 200), mode: str = "RGB") -> Path:
    """Helper to create a temporary test image."""
    img = Image.new(mode, size, color=(255, 255, 255))
    img.save(path)
    return path


def test_fenced_json_parses(tmp_path: Path) -> None:
    """Markdown fenced JSON response is cleanly stripped and validated."""
    test_img = _create_test_image(tmp_path / "test_bill.png")
    mock_client = MagicMock(spec=LLMClient)

    fenced_response = (
        "```json\n"
        "{\n"
        '  "provider": "KE",\n'
        '  "tariff": "A1-R",\n'
        '  "sanctioned_load_kw": 3,\n'
        '  "bill_month": "2026-04",\n'
        '  "units_consumed": 151,\n'
        '  "charges": [{"type": "energy", "amount": 1054}],\n'
        '  "taxes": [{"type": "gst", "amount": 520.21}],\n'
        '  "extra_dropped_key": "some_value"\n'
        "}\n"
        "```"
    )
    mock_client.generate.return_value = fenced_response

    result = extract_level1(test_img, client=mock_client)

    assert result["provider"] == "KE"
    assert result["tariff"] == "A1-R"
    assert result["units_consumed"] == 151
    assert len(result["charges"]) == 1
    assert result["charges"][0] == {"type": "energy", "amount": 1054}
    assert "extra_dropped_key" not in result
    assert mock_client.generate.call_count == 1


def test_invalid_json_retries_once(tmp_path: Path) -> None:
    """First attempt invalid JSON triggers single retry with error prompt."""
    test_img = _create_test_image(tmp_path / "test_bill.png")
    mock_client = MagicMock(spec=LLMClient)

    # 1st call: unparseable text; 2nd call: valid JSON
    mock_client.generate.side_effect = [
        "Sorry, I cannot parse this: {invalid json",
        '{"provider": "LESCO", "bill_month": "2026-07", "units_consumed": 65}',
    ]

    result = extract_level1(test_img, client=mock_client)

    assert result["provider"] == "LESCO"
    assert result["bill_month"] == "2026-07"
    assert result["units_consumed"] == 65
    assert mock_client.generate.call_count == 2

    # Check that retry prompt includes previous error message
    retry_prompt = mock_client.generate.call_args_list[1].kwargs["prompt"]
    assert "previous output failed with error" in retry_prompt


def test_double_failure_returns_safe_object(tmp_path: Path) -> None:
    """When both attempts fail, returns safe all-null object without raising."""
    test_img = _create_test_image(tmp_path / "test_bill.png")
    mock_client = MagicMock(spec=LLMClient)

    mock_client.generate.side_effect = [
        "First completely broken output",
        "Second completely broken output",
    ]

    result = extract_level1(test_img, client=mock_client)

    assert result == safe_all_null_dict()
    assert result["provider"] is None
    assert result["charges"] == []
    assert result["taxes"] == []
    assert mock_client.generate.call_count == 2


def test_validation_failure_triggers_retry(tmp_path: Path) -> None:
    """Pydantic validation failure (e.g. invalid provider) triggers retry."""
    test_img = _create_test_image(tmp_path / "test_bill.png")
    mock_client = MagicMock(spec=LLMClient)

    mock_client.generate.side_effect = [
        '{"provider": "INVALID_DISCO"}',
        '{"provider": "IESCO", "bill_month": "2026-09", "units_consumed": 158}',
    ]

    result = extract_level1(test_img, client=mock_client)

    assert result["provider"] == "IESCO"
    assert result["bill_month"] == "2026-09"
    assert result["units_consumed"] == 158
    assert mock_client.generate.call_count == 2


def test_preprocess_oversized_rgba_image(tmp_path: Path) -> None:
    """Preprocess converts RGBA to RGB and resizes oversized images."""
    img_path = tmp_path / "oversized.png"
    _create_test_image(img_path, size=(3200, 2400), mode="RGBA")

    processed = load_and_preprocess_image(img_path, max_dimension=2000)

    assert processed.mode == "RGB"
    assert max(processed.size) <= 2000


def test_parse_json_from_llm_fallbacks() -> None:
    """parse_json_from_llm extracts JSON even when wrapped in commentary."""
    raw = "Here is the extracted bill:\n{\"provider\": \"KE\", \"tariff\": \"A1-R\"}\nHope this helps!"
    parsed = parse_json_from_llm(raw)
    assert parsed == {"provider": "KE", "tariff": "A1-R"}
