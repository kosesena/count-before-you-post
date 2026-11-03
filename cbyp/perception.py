"""What the cameras see: SAM 3.1 detections and Spark's look at the same frame."""
import base64
import json
import mimetypes
from pathlib import Path

from .meta import SPARK, client
from .product_identity import SCHEMA as IDENTITY_SCHEMA, PROMPT as IDENTITY_PROMPT
from .sam import parse, segment_image

MIN_CONF = 0.7

LOOK = {
    "type": "object", "additionalProperties": False,
    "required": ["product_on_labels", "cartons_visible", "damaged_cartons", "stacked",
                 "all_cartons_visible", "product_identity", "all_labels_identified"],
    "properties": {
        "product_on_labels": {"type": "string"},
        "product_identity": IDENTITY_SCHEMA,
        "all_labels_identified": {"type": "boolean", "description": "True only if brand, at least one product code or technical model, and any variant can be read on EVERY carton and all agree. False for unreadable, mixed or hidden labels."},
        "cartons_visible": {"type": "integer"},
        "damaged_cartons": {"type": "integer"},
        "stacked": {"type": "boolean", "description": "Cartons stacked in more than one layer."},
        "all_cartons_visible": {"type": "boolean",
                                "description": "False if any carton is clipped by the image boundary, obscured by shelving/objects, or may be hidden. Counting a visible carton does not establish its complete extent."},
    },
}
LOOK_PROMPT = (
    "Warehouse receiving photo from an unknown camera position. Do not assume an overhead view. Read the product name "
    "printed on the carton labels exactly as written, count the cartons, count cartons that "
    "look crushed, wet or torn, and say whether cartons are stacked so some may be hidden."
)


def look(path):
    """Spark looks at a ceiling-camera frame: product, count, damage, stacking."""
    path = Path(path)
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    url = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="medium", max_tokens=8000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "pallet", "strict": True, "schema": LOOK}},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": LOOK_PROMPT},
            {"type": "image_url", "image_url": {"url": url}}]}],
    )
    return json.loads(r.choices[0].message.content)


VIDEO_PROMPT = (
    "Video of a pallet at a warehouse receiving dock, filmed by someone walking around it. "
    "Use every frame: read the product name printed on the carton labels exactly as written, "
    "count the distinct cartons (each carton once, however many frames show it), count cartons "
    "that look crushed, wet or torn, and say whether cartons are stacked and whether some "
    "stay hidden in every frame."
)


def look_video(path):
    """Spark watches a walk-around mp4 of the pallet: product, count, damage, stacking."""
    url = "data:video/mp4;base64," + base64.b64encode(Path(path).read_bytes()).decode()
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="medium", max_tokens=8000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "pallet", "strict": True, "schema": LOOK}},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": VIDEO_PROMPT},
            {"type": "video_url", "video_url": {"url": url}}]}],
    )
    return json.loads(r.choices[0].message.content)


def sam_confs(path, concept):
    """Confidences of every detection at or above MIN_CONF, highest first."""
    confs = [d.conf or 0 for d in parse(segment_image(path, concept))]
    return sorted((round(c, 3) for c in confs if c >= MIN_CONF), reverse=True)


POINTS = {
    "type": "object", "additionalProperties": False, "required": ["points"],
    "properties": {"points": {"type": "array", "items": {
        "type": "object", "additionalProperties": False, "required": ["x", "y"],
        "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}}}},
}
POINTS_PROMPT = (
    "Ceiling camera view of a pallet. Put exactly one point on the centre of every cardboard "
    "carton you can see, and on nothing else (not on the pallet, gaps or the floor). "
    "Coordinates on a 0-1000 grid: x from the left edge, y from the top edge."
)


def point_cartons(path):
    """Spark marks each carton with a point; returns pixel coordinates [(x, y), ...]."""
    from PIL import Image, ImageOps

    path = Path(path)
    with Image.open(path) as image:
        w, h = ImageOps.exif_transpose(image).size
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    url = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="medium", max_tokens=8000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "points", "strict": True, "schema": POINTS}},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": POINTS_PROMPT},
            {"type": "image_url", "image_url": {"url": url}}]}],
    )
    pts = json.loads(r.choices[0].message.content)["points"]
    return [(min(w - 1, p["x"] * w // 1000), min(h - 1, p["y"] * h // 1000)) for p in pts]

LOOK_PROMPT += IDENTITY_PROMPT
VIDEO_PROMPT += IDENTITY_PROMPT
