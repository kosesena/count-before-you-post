"""A second, independent reading of the delivery note on open weights.

Muse Glimmer (30B, Apache 2.0, distilled from Muse Spark) reads the same note with the same
schema and prompt, through OpenRouter: a different model on different servers, so one model's
misreading is not silently trusted. The gate compares only what decides a receipt
(gate.differences): the line items (product, quantity, legibility) and whether the note tries
to instruct software.
"""
import base64
import json
import mimetypes
import os
import time
from pathlib import Path

from openai import OpenAI

from .delivery_note import PROMPT, SCHEMA
from .meta import TIMEOUT, _load_env

OPENROUTER = "https://openrouter.ai/api/v1"
GLIMMER = "meta/muse-glimmer-30b"
SPARK_OPEN = "meta/muse-spark-open"

# OpenRouter routes to whichever host is free. On 28 Oct Spark Open landed on an fp4 host
# without response_format, and Glimmer ran out of room mid-JSON after its long reasoning. So:
# only hosts that honour the schema (require_parameters, no fallback), Glimmer with the
# sampling Meta recommends for it (dev.meta.ai/docs/muse-glimmer/prompting) and room to think.
SETTINGS = {
    GLIMMER: {"max_tokens": 16000, "temperature": 1.0, "top_p": 0.95,
              "extra_body": {"top_k": 64, "provider": {
                  "order": ["DeepInfra", "Together"], "allow_fallbacks": False,
                  "require_parameters": True}}},
    SPARK_OPEN: {"max_tokens": 16000,
                 "extra_body": {"provider": {
                     "order": ["Fireworks", "Together", "Modal"], "allow_fallbacks": False,
                     "require_parameters": True}}},
}


def client() -> OpenAI:
    _load_env()
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set (see .env.example)")
    return OpenAI(base_url=OPENROUTER, api_key=key, timeout=TIMEOUT, max_retries=2)


def _part(path: Path) -> dict:
    data = base64.b64encode(path.read_bytes()).decode()
    if path.suffix.lower() == ".pdf":
        return {"type": "file", "file": {"filename": path.name,
                                         "file_data": "data:application/pdf;base64," + data}}
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}}


def read_note(path, model=GLIMMER, api=None, tries=2) -> dict:
    """Same contract as delivery_note.read_note: {"claim", "seconds", "model"}, plus the host
    that answered and how many tries it took. A reply that is not valid JSON, or has no line
    item, is asked once more; after that the error goes up."""
    path = Path(path)
    api = api or client()
    start = time.perf_counter()
    for attempt in range(1, tries + 1):
        r = api.chat.completions.create(
            model=model, **SETTINGS.get(model, {"max_tokens": 16000}),
            response_format={"type": "json_schema",
                             "json_schema": {"name": "delivery_note", "strict": True,
                                             "schema": SCHEMA}},
            messages=[{"role": "user",
                       "content": [{"type": "text", "text": PROMPT}, _part(path)]}])
        try:
            claim = json.loads(r.choices[0].message.content or "")
            if claim.get("items"):
                break
            why = "no line item"
        except ValueError as e:
            why = f"not JSON ({r.choices[0].finish_reason}): {e}"
        if attempt == tries:
            raise ValueError(f"{model} gave no usable reading after {tries} tries: {why}")
    return {"claim": claim, "seconds": round(time.perf_counter() - start, 1), "model": model,
            "provider": getattr(r, "provider", None), "tries": attempt}
