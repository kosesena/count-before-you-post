"""SAM 3.1 calls and output parsing (image and video, concept prompts)."""
import base64
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


def segment_image(path: str | Path, concept: str) -> str:
    """Find every instance of `concept` in an image; return raw output text."""
    path = Path(path)
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode()
    stream = client().responses.create(
        model=SAM,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": concept},
            {"type": "input_image", "image_url": f"data:{mime};base64,{data}"},
        ]}],
        metadata={"include_confidence": "true", "mask_encoding": "one_bit"},
        stream=True,
    )
    parts = []
    for event in stream:
        if event.type == "response.output_text.delta":
            parts.append(event.delta)
        elif event.type in ("response.failed", "error"):
            # A failed stream must not read as "no boxes found".
            raise RuntimeError(f"SAM image failed: {event}")
    return "".join(parts)


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


@dataclass
class Segment:
    """One object with its pixel mask, from Meta's own parser (meta-sam-parser)."""
    obj: str
    conf: float | None
    left: int
    top: int
    right: int
    bottom: int
    raster: bytes        # row-major 0/1, (bottom - top) rows x (right - left) columns

    def contains(self, x: float, y: float) -> bool:
        """True if pixel (x, y) of the source image is inside this object's mask."""
        if not (self.left <= x < self.right and self.top <= y < self.bottom):
            return False
        w = self.right - self.left
        return bool(self.raster[int(y - self.top) * w + int(x - self.left)])


def segments(text: str) -> list[Segment]:
    """Decode every mask in an image response. Masks come back cropped to their bounds."""
    import meta_sam_parser as msp

    parser = msp.image_segmentation_format().create_parser()
    parser.push(text)
    result = parser.finish(msp.CompletedOutcome()).result
    out = []
    for rec in result.records:
        if isinstance(rec, msp.SegmentationMaskRecord):
            b = rec.bounds
            out.append(Segment(rec.object_id, rec.confidence, b.left, b.top, b.right, b.bottom,
                               msp.decode_mask_to_raster(rec.mask)))
    return out


def segment_points(path: str | Path, points: list[tuple[int, int]]) -> str:
    """Ask SAM what object sits under each point (one object per point, at most 16)."""
    import meta_sam_parser as msp
    from PIL import Image

    path = Path(path)
    w, h = Image.open(path).size
    prompt = msp.build_object_prompt(size=(w, h), objects=[
        msp.PromptObject(id=i + 1, prompts=[msp.FramePrompt(points=[msp.PromptPoint(x, y)])])
        for i, (x, y) in enumerate(points[:16])])
    return segment_image(path, prompt)
