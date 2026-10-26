"""Meta Model API client (OpenAI-compatible, https://api.meta.ai/v1)."""
import os
from pathlib import Path

from openai import OpenAI

BASE_URL = "https://api.meta.ai/v1"
SPARK = "muse-spark-1.3"
SAM = "sam-3.1"


def _load_env() -> None:
    env = Path(__file__).resolve().parent.parent / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() and key.strip() not in os.environ:
            os.environ[key.strip()] = value.strip()


def client() -> OpenAI:
    _load_env()
    key = os.environ.get("META_API_KEY")
    if not key:
        raise RuntimeError("META_API_KEY is not set (see .env.example)")
    # The OpenAI SDK does not read META_API_KEY on its own, so pass it explicitly.
    return OpenAI(base_url=BASE_URL, api_key=key)
