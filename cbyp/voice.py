"""The receiver's spoken count: Muse Voice Transcribe, then Spark pulls out the numbers.

A third, independent reading next to the delivery note and the camera: the person at the
dock says "12 koli geldi, Doğan Gıda'dan" and the gate can compare it with the other two.

At a real dock two people talk: the driver says what they brought, the receiver says what
they counted. DIARIZATION splits the recording into speakers, and Spark tells the two roles
apart, so the driver's number is never taken for the receiver's count.
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
    return _asr(path, "PUSH_TO_TALK", keywords, languages)["transcript"]


def turns(path: str | Path, keywords: list[str] | None = None,
          languages: list[str] | None = ("Turkish",)) -> list[dict]:
    """Who said what: [{"speaker": "A", "transcript": ...}]. Speaker labels only tell
    speakers apart within this one recording.

    Asked as text/plain ("A:..." per turn): with DIARIZATION the JSON answer reset the
    connection every time (28 Oct 2026, 4 tries, curl too), the plain one came back."""
    text = _asr(path, "DIARIZATION", keywords, languages, accept="text/plain")
    return parse_turns(text)


def parse_turns(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        speaker, sep, said = line.partition(":")
        if sep and speaker.strip() and len(speaker.strip()) <= 3:
            out.append({"speaker": speaker.strip(), "transcript": said.strip()})
        elif line.strip() and out:  # a turn that wrapped onto the next line
            out[-1]["transcript"] += " " + line.strip()
    return out


def _asr(path, mode, keywords, languages, accept="application/json"):
    _load_env()
    request = {"model": VOICE, "audioEncoding": "WAV", "mode": mode}
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
                 "Accept": accept,
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        body = r.read()
    return json.loads(body) if accept == "application/json" else body.decode()


def understand(transcript: str) -> dict:
    """Spark turns the spoken sentence into quantity, unit, supplier and product."""
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="low", max_tokens=4000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "spoken", "strict": True, "schema": SPOKEN}},
        messages=[{"role": "user", "content": (
            "A warehouse receiver said this about a delivery (in any language, numbers may "
            "be written as words). Extract the number of cartons/units received, the unit, "
            "the supplier and the product. Use empty strings for anything not said. If the "
            "speaker corrects themself, use the corrected number.\n\n"
            f"Transcript: {transcript}")}],
    )
    return json.loads(r.choices[0].message.content)


DIALOGUE = {
    "type": "object", "additionalProperties": False,
    "required": ["receiver_speaker", "driver_quantity", "receiver"],
    "properties": {
        "receiver_speaker": {"type": "string",
                             "description": "The label of the speaker who counted the goods."},
        "driver_quantity": {"type": ["integer", "null"],
                            "description": "What the driver says they brought; null if unsaid."},
        "receiver": SPOKEN,
    },
}


def understand_dialogue(said: list[dict]) -> dict:
    """Spark reads the speaker turns and keeps the two roles apart: the driver's claim, and
    the receiver's own count (the one the gate compares with the camera)."""
    lines = "\n".join(f"{t['speaker']}: {t['transcript']}" for t in said)
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="low", max_tokens=4000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "dialogue", "strict": True, "schema": DIALOGUE}},
        messages=[{"role": "user", "content": (
            "A delivery driver and a warehouse receiver talk at the dock (any language, numbers "
            "may be written as words). Speaker labels come from diarization. Decide which "
            "speaker is the receiver (the one who counts what is on the pallet), what quantity "
            "the driver claims, and what the receiver counted. The receiver's count is their "
            "own last word on it; if they hedge, certain is false. Use empty strings for "
            "anything not said.\n\n" + lines)}],
    )
    return json.loads(r.choices[0].message.content)
