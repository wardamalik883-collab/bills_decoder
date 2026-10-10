"""Tests for LLM client abstraction layer using mocked SDK."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from bill_decoder.config import Config
from bill_decoder.llm_client import LLMClient, generate


def test_model_whitelist_enforcement(tmp_path: Path) -> None:
    """Disallowed models must raise ValueError immediately."""
    invalid_config = Config(
        model_provider="google",
        model_name="claude-3-opus",  # Not on whitelist
        api_key="test-key",
        cache_dir=tmp_path,
    )
    with pytest.raises(ValueError, match="is not allowed"):
        LLMClient(config=invalid_config)


def test_retry_on_429_then_success(tmp_path: Path) -> None:
    """Client retries on 429 rate limit with backoff and succeeds."""
    config = Config(
        model_provider="google",
        model_name="gemini-3.1-flash-lite",
        api_key="test-key",
        cache_dir=tmp_path,
    )
    client = LLMClient(config=config)

    # First call raises 429, second succeeds
    mock_call = MagicMock()
    error_429 = RuntimeError("429 RESOURCE_EXHAUSTED: Rate limit exceeded")
    mock_call.side_effect = [error_429, '{"answer": "success"}']

    with patch.object(client, "_call_google", mock_call):
        with patch("time.sleep") as mock_sleep:
            result = client.generate("test prompt", no_cache=True)

            assert result == '{"answer": "success"}'
            assert mock_call.call_count == 2
            assert mock_sleep.call_count == 1


def test_cache_hit_makes_only_one_network_call(tmp_path: Path) -> None:
    """Second call with identical arguments returns from disk cache without network call."""
    config = Config(
        model_provider="google",
        model_name="gemini-3.5-flash-lite",
        api_key="test-key",
        cache_dir=tmp_path,
    )
    client = LLMClient(config=config)

    mock_call = MagicMock(return_value='{"bill_month": "2026-04"}')

    with patch.object(client, "_call_google", mock_call):
        res1 = client.generate("Extract bill month", json_mode=True)
        res2 = client.generate("Extract bill month", json_mode=True)

        assert res1 == '{"bill_month": "2026-04"}'
        assert res2 == '{"bill_month": "2026-04"}'
        # Network must be called only once
        assert mock_call.call_count == 1


def test_no_cache_bypasses_disk_cache(tmp_path: Path) -> None:
    """When no_cache=True, cache is bypassed and network is called each time."""
    config = Config(
        model_provider="google",
        model_name="gemini-3.1-flash-lite",
        api_key="test-key",
        cache_dir=tmp_path,
    )
    client = LLMClient(config=config)

    mock_call = MagicMock(return_value='{"val": 123}')

    with patch.object(client, "_call_google", mock_call):
        res1 = client.generate("test prompt", no_cache=True)
        res2 = client.generate("test prompt", no_cache=True)

        assert res1 == '{"val": 123}'
        assert res2 == '{"val": 123}'
        assert mock_call.call_count == 2
