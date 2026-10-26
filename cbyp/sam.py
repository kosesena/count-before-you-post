"""SAM 3.1 calls and output parsing (image and video, concept prompts)."""
import re
from dataclasses import dataclass
from pathlib import Path

from .meta import SAM, client

# One record: "<id><|box;x1=..;y1=..;x2=..;y2=..;w=..;h=..;c=..|><|mask;...|>"
# '|' never appears in the base85 mask payload, so "<|box;" can't occur inside a mask.
_FRAME = re.compile(r"<(\d+)f>")
_BOX = re.compile(r"(\d+)<\|box;([^|]*)\|>")


@dataclass
class Detection:
    frame: int
    obj: int
    x1: float
    y1: float
    x2: float
    y2: float
    conf: float | None

    @property
    def center(self) -> tuple[float, float]:
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2


def parse(text: str) -> list[Detection]:
    """Parse SAM output text into detections. Frames with no objects emit no line."""
    out = []
    for line in text.splitlines():
        m = _FRAME.match(line)
        if not m:
            continue
        frame = int(m.group(1))
        for obj, fields in _BOX.findall(line[m.end():]):
            kv = dict(f.split("=", 1) for f in fields.split(";") if "=" in f)
            out.append(Detection(
                frame, int(obj), float(kv["x1"]), float(kv["y1"]), float(kv["x2"]),
                float(kv["y2"]), float(kv["c"]) if "c" in kv else None,
            ))
    return out


def upload(path: str | Path) -> str:
    with open(path, "rb") as f:
        return client().files.create(file=f, purpose="user_data").id


def segment_video(file_id: str, concept: str) -> str:
    """Track every instance of `concept` through an uploaded video; return raw output text."""
    stream = client().responses.create(
        model=SAM,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": concept},
            {"type": "input_video", "file_id": file_id},
        ]}],
        metadata={"include_confidence": "true", "mask_encoding": "one_bit"},
        stream=True,
    )
    parts = []
    for event in stream:
        if event.type == "response.output_text.delta":
            parts.append(event.delta)
        elif event.type in ("response.failed", "error"):
            raise RuntimeError(f"SAM video failed: {event}")
    # Each delta is one frame line.
    return "\n".join(parts)
