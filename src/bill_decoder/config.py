"""Configuration management for utility bill decoder.

Loads and validates environment variables from .env using python-dotenv.
Never exposes or logs secret API keys.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""

    model_provider: str
    model_name: str
    api_key: str
    max_workers: int = 2
    cache_dir: Path = Path("cache")

    def __repr__(self) -> str:
        masked_key = "***" if self.api_key else "<not set>"
        return (
            f"Config(model_provider={self.model_provider!r}, "
            f"model_name={self.model_name!r}, "
            f"api_key={masked_key!r}, "
            f"max_workers={self.max_workers}, "
            f"cache_dir={self.cache_dir!r})"
        )


def load_config() -> Config:
    """Load configuration from environment variables and .env file.

    Raises:
        ValueError: If any required environment variable is missing or empty.
    """
    load_dotenv()

    model_provider = os.getenv("MODEL_PROVIDER", "").strip().lower()
    model_name = os.getenv("MODEL_NAME", "").strip()
    api_key = os.getenv("API_KEY", "").strip()

    missing = []
    if not model_provider:
        missing.append("MODEL_PROVIDER")
    if not model_name:
        missing.append("MODEL_NAME")
    if not api_key:
        missing.append("API_KEY")

    if missing:
        raise ValueError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Please ensure they are set in your .env file."
        )

    try:
        max_workers = int(os.getenv("MAX_WORKERS", "2"))
    except ValueError:
        max_workers = 2

    cache_dir = Path(os.getenv("CACHE_DIR", "cache"))

    return Config(
        model_provider=model_provider,
        model_name=model_name,
        api_key=api_key,
        max_workers=max_workers,
        cache_dir=cache_dir,
    )
