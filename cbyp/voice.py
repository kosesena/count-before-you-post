"""The receiver's spoken count: Muse Voice Transcribe, then Spark pulls out the numbers.

A third, independent reading next to the delivery note and the camera: the person at the
dock says "12 koli geldi, Doğan Gıda'dan" and the gate can compare it with the other two.
"""
import json
import os
import uuid
import urllib.request
from pathlib import Path

from .meta import BASE_URL, SPARK, TIMEOUT, _load_env, client

VOICE = "muse-voice-transcribe-1.0"

SPOKEN = {
    "type": "object", "additionalProperties": False,
    "required": ["quantity", "unit", "supplier", "product", "certain"],
    "properties": {
        "quantity": {"type": ["integer", "null"], "description": "Null if no number is said."},
        "unit": {"type": "string"},
        "supplier": {"type": "string"},
        "product": {"type": "string"},
        "certain": {"type": "boolean",
                    "description": "False if the speaker hedges ('galiba', 'I think', 'roughly')."},
    },
}


def transcribe(path: str | Path, keywords: list[str] | None = None,
               languages: list[str] | None = ("Turkish",)) -> str:
    """Transcribe a WAV recording (mono 16-bit PCM) and return the transcript."""
    _load_env()
    request = {"model": VOICE, "audioEncoding": "WAV", "mode": "PUSH_TO_TALK"}
    if keywords:
        request["keywords"] = list(keywords)
    if languages:
        request["languageBias"] = list(languages)
    boundary = uuid.uuid4().hex
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"request\"\r\n"
        f"Content-Type: application/json\r\n\r\n".encode(),
        json.dumps(request).encode(), b"\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; "
        f"filename=\"{Path(path).name}\"\r\nContent-Type: audio/wav\r\n\r\n".encode(),
        Path(path).read_bytes(), f"\r\n--{boundary}--\r\n".encode(),
    ])
    req = urllib.request.Request(
        BASE_URL + "/asr/transcribe", data=body, method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Accept": "application/json",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read())["transcript"]


def understand(transcript: str) -> dict:
    """Spark turns the spoken sentence into quantity, unit, supplier and product."""
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="low", max_tokens=4000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "spoken", "strict": True, "schema": SPOKEN}},
        messages=[{"role": "user", "content": (
            "A warehouse receiver said this about a delivery (it may be Turkish, numbers may "
            "be written as words). Extract the number of cartons/units received, the unit, "
            "the supplier and the product. Use empty strings for anything not said. If the "
            "speaker corrects themself, use the corrected number.\n\n"
            f"Transcript: {transcript}")}],
    )
    return json.loads(r.choices[0].message.content)
