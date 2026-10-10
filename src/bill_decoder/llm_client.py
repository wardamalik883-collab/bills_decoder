"""LLM client abstraction layer supporting google, anthropic, and openai providers.

Features:
- Enforces strict allowed-model whitelist to prevent disqualification.
- Retries with exponential backoff and jitter on 429, 5xx, and timeouts (max 4 attempts).
- Never logs or prints API keys or prompt contents.
- Disk caching in CACHE_DIR keyed by SHA-256 of model, system, prompt, and image bytes.
"""

import base64
import hashlib
import logging
import mimetypes
import random
import time
from pathlib import Path
from typing import Any

from bill_decoder.config import Config, load_config

logger = logging.getLogger(__name__)

# Strict allowed models whitelist (per competition rules)
ALLOWED_MODELS: set[str] = {
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "claude-haiku-4-5",
    "gpt-4.1-mini",
    "gpt-5-mini",
}


def compute_cache_key(
    model_name: str,
    system: str | None,
    prompt: str,
    image_path: Path | str | None,
) -> str:
    """Compute deterministic SHA-256 cache key."""
    hasher = hashlib.sha256()
    hasher.update(model_name.encode("utf-8"))
    hasher.update((system or "").encode("utf-8"))
    hasher.update(prompt.encode("utf-8"))
    if image_path:
        img_bytes = Path(image_path).read_bytes()
        hasher.update(img_bytes)
    return hasher.hexdigest()


def is_retryable_exception(exc: Exception) -> bool:
    """Determine whether an error is transient (429, 5xx, timeout)."""
    status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status_code in (429, 500, 502, 503, 504):
        return True

    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True

    msg = str(exc).lower()
    retryable_patterns = [
        "429",
        "rate limit",
        "resource_exhausted",
        "quota",
        "500",
        "502",
        "503",
        "504",
        "server error",
        "internal error",
        "timeout",
        "timed out",
        "connection reset",
        "connection refused",
        "service unavailable",
        "overloaded",
    ]
    return any(pattern in msg for pattern in retryable_patterns)


class LLMClient:
    """Multi-provider LLM client with retries and caching."""

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or load_config()
        self._validate_model()

    def _validate_model(self) -> None:
        """Enforce model whitelist."""
        if self.config.model_name not in ALLOWED_MODELS:
            raise ValueError(
                f"Model '{self.config.model_name}' is not allowed. "
                f"Allowed models: {sorted(ALLOWED_MODELS)}"
            )

    def generate(
        self,
        prompt: str,
        image_path: Path | str | None = None,
        system: str | None = None,
        json_mode: bool = True,
        no_cache: bool = False,
    ) -> str:
        """Generate text/JSON from model with caching and retries.

        Args:
            prompt: Text prompt to send to the model.
            image_path: Optional path to an image file.
            system: Optional system instruction/prompt.
            json_mode: Whether to request JSON output.
            no_cache: If True, bypass reading and writing disk cache.

        Returns:
            The raw text/JSON response string.
        """
        self._validate_model()

        # Check disk cache
        cache_key = compute_cache_key(
            model_name=self.config.model_name,
            system=system,
            prompt=prompt,
            image_path=image_path,
        )
        cache_dir = self.config.cache_dir
        cache_file = cache_dir / f"{cache_key}.txt"

        if not no_cache and cache_file.exists():
            return cache_file.read_text(encoding="utf-8")

        # Execute call with exponential backoff
        response_text = self._call_with_retries(
            prompt=prompt,
            image_path=image_path,
            system=system,
            json_mode=json_mode,
        )

        # Write to cache
        if not no_cache:
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(response_text, encoding="utf-8")

        return response_text

    def _call_with_retries(
        self,
        prompt: str,
        image_path: Path | str | None,
        system: str | None,
        json_mode: bool,
        max_attempts: int = 4,
        base_delay: float = 1.0,
    ) -> str:
        """Call provider with retries on transient errors."""
        last_exception: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                provider = self.config.model_provider.lower()
                if provider == "google":
                    return self._call_google(
                        prompt=prompt,
                        image_path=image_path,
                        system=system,
                        json_mode=json_mode,
                    )
                elif provider == "anthropic":
                    return self._call_anthropic(
                        prompt=prompt,
                        image_path=image_path,
                        system=system,
                        json_mode=json_mode,
                    )
                elif provider == "openai":
                    return self._call_openai(
                        prompt=prompt,
                        image_path=image_path,
                        system=system,
                        json_mode=json_mode,
                    )
                else:
                    raise ValueError(
                        f"Unsupported MODEL_PROVIDER '{self.config.model_provider}'. "
                        "Supported providers: google, anthropic, openai"
                    )
            except Exception as e:
                last_exception = e
                if attempt < max_attempts and is_retryable_exception(e):
                    # Exponential backoff + jitter; never log prompt or key
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
                    logger.warning(
                        "LLM call attempt %d/%d failed with %s. Retrying in %.2fs...",
                        attempt,
                        max_attempts,
                        type(e).__name__,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    raise last_exception from None

        raise last_exception or RuntimeError("Exhausted retry attempts")

    def _call_google(
        self,
        prompt: str,
        image_path: Path | str | None,
        system: str | None,
        json_mode: bool,
    ) -> str:
        """Call Google GenAI SDK."""
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.config.api_key)

        parts: list[Any] = []
        if image_path:
            img_path = Path(image_path)
            img_bytes = img_path.read_bytes()
            mime_type = mimetypes.guess_type(str(img_path))[0] or "image/png"
            parts.append(types.Part.from_bytes(data=img_bytes, mime_type=mime_type))

        parts.append(types.Part.from_text(text=prompt))

        config_args: dict[str, Any] = {
            "temperature": 0.0,
        }
        if system:
            config_args["system_instruction"] = system
        if json_mode:
            config_args["response_mime_type"] = "application/json"

        response = client.models.generate_content(
            model=self.config.model_name,
            contents=[types.Content(role="user", parts=parts)],
            config=types.GenerateContentConfig(**config_args),
        )
        return response.text or ""

    def _call_anthropic(
        self,
        prompt: str,
        image_path: Path | str | None,
        system: str | None,
        json_mode: bool,
    ) -> str:
        """Call Anthropic SDK lazily."""
        try:
            import anthropic  # type: ignore
        except ImportError as e:
            raise ImportError(
                "Anthropic SDK is not installed. Install with: pip install anthropic"
            ) from e

        client = anthropic.Anthropic(api_key=self.config.api_key)
        content_parts: list[dict[str, Any]] = []

        if image_path:
            img_path = Path(image_path)
            img_bytes = img_path.read_bytes()
            b64_data = base64.b64encode(img_bytes).decode("utf-8")
            mime_type = mimetypes.guess_type(str(img_path))[0] or "image/png"
            content_parts.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": b64_data,
                    },
                }
            )

        prompt_text = prompt
        if json_mode and "json" not in prompt.lower():
            prompt_text = f"{prompt}\n\nPlease respond strictly in valid JSON format."

        content_parts.append({"type": "text", "text": prompt_text})

        kwargs: dict[str, Any] = {
            "model": self.config.model_name,
            "max_tokens": 4096,
            "temperature": 0.0,
            "messages": [{"role": "user", "content": content_parts}],
        }
        if system:
            kwargs["system"] = system

        message = client.messages.create(**kwargs)
        return message.content[0].text

    def _call_openai(
        self,
        prompt: str,
        image_path: Path | str | None,
        system: str | None,
        json_mode: bool,
    ) -> str:
        """Call OpenAI SDK lazily."""
        try:
            import openai  # type: ignore
        except ImportError as e:
            raise ImportError(
                "OpenAI SDK is not installed. Install with: pip install openai"
            ) from e

        client = openai.OpenAI(api_key=self.config.api_key)
        content_parts: list[dict[str, Any]] = []

        if image_path:
            img_path = Path(image_path)
            img_bytes = img_path.read_bytes()
            b64_data = base64.b64encode(img_bytes).decode("utf-8")
            mime_type = mimetypes.guess_type(str(img_path))[0] or "image/png"
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{b64_data}"},
                }
            )

        content_parts.append({"type": "text", "text": prompt})

        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": content_parts})

        kwargs: dict[str, Any] = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": 0.0,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""


def generate(
    prompt: str,
    image_path: Path | str | None = None,
    system: str | None = None,
    json_mode: bool = True,
    no_cache: bool = False,
    config: Config | None = None,
) -> str:
    """Generate text/JSON using the configured LLM provider.

    Convenience wrapper around LLMClient.generate.
    """
    client = LLMClient(config=config)
    return client.generate(
        prompt=prompt,
        image_path=image_path,
        system=system,
        json_mode=json_mode,
        no_cache=no_cache,
    )
