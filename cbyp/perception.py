"""What the cameras see: SAM 3.1 detections and Spark's look at the same frame."""
import base64
import json
from pathlib import Path

from .meta import SPARK, client
from .image_input import image_data_url
from .product_identity import SCHEMA as IDENTITY_SCHEMA, PROMPT as IDENTITY_PROMPT
from .sam import parse, segment_image

MIN_CONF = 0.7

LOOK = {
    "type": "object", "additionalProperties": False,
    "required": ["product_on_labels", "cartons_visible", "damaged_cartons", "stacked",
                 "all_cartons_visible", "product_identity", "all_labels_identified", "packaging_condition"],
    "properties": {
        "packaging_condition": {"type": "string", "enum": ["intact", "open_or_damaged", "uncertain"], "description": "Inspect ALL cartons: open ends/flaps, exposed foam or contents, torn/wet/crushed packaging require open_or_damaged even when count matches. Use uncertain if condition cannot be assessed. Intact requires affirmative visible evidence, not merely zero detected damage."},
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
CONDITION_PROMPT = " Inspect packaging separately from count and labels. Open ends, exposed foam/contents or loose flaps are open_or_damaged, even without crushing. If obscured or uncertain, use uncertain; never infer intact from a matching count. "
LOOK_PROMPT = (
    "Warehouse receiving photo from an unknown camera position. Do not assume an overhead view. Read the product name "
    "printed on the carton labels exactly as written, count the cartons, count cartons that "
    "look crushed, wet or torn, and say whether cartons are stacked so some may be hidden."
)


def look(path):
    """Spark looks at a ceiling-camera frame: product, count, damage, stacking."""
    path = Path(path)
    url = image_data_url(path)
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="medium", max_tokens=8000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "pallet", "strict": True, "schema": LOOK}},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": LOOK_PROMPT + CONDITION_PROMPT},
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
            {"type": "text", "text": VIDEO_PROMPT + CONDITION_PROMPT},
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
    "Inspect this warehouse or shelf photograph from its actual camera angle. "
    "Do not assume an overhead view or invent a regular grid. Locate each distinct visible "
    "cardboard carton individually, including cartons in vertical stacks. Scan from top to "
    "bottom and left to right; put exactly ONE point well inside each carton's visible face. "
    "Avoid straps, labels, seams, gaps and shared edges when choosing the point. "
    "Two visible faces of the same carton are ONE object. Never put two points on one carton. "
    "Do not point at pallets, shelves, gaps, floor or loose packaging. "
    "Use the actual image geometry, not a guessed row/column layout. "
    "Coordinates on a 0-1000 grid: x increases from the LEFT image edge to the RIGHT; "
    "y increases from the TOP image edge to the BOTTOM."
)


def point_cartons(path):
    """Spark marks each carton with a point; returns pixel coordinates [(x, y), ...]."""
    from PIL import Image, ImageOps

    path = Path(path)
    with Image.open(path) as image:
        w, h = ImageOps.exif_transpose(image).size
    url = image_data_url(path)
    r = client().chat.completions.create(
        model=SPARK, reasoning_effort="medium", max_tokens=8000,
        response_format={"type": "json_schema",
                         "json_schema": {"name": "points", "strict": True, "schema": POINTS}},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": POINTS_PROMPT},
            {"type": "image_url", "image_url": {"url": url}}]}],
    )
    pts = json.loads(r.choices[0].message.content)["points"]
    if any(type(p.get(axis)) is not int or not 0 <= p[axis] <= 1000
           for p in pts for axis in ("x", "y")):
        raise ValueError("Carton points must use integer coordinates on the 0-1000 image grid")
    return [(min(w - 1, p["x"] * w // 1000), min(h - 1, p["y"] * h // 1000)) for p in pts]

LOOK_PROMPT += IDENTITY_PROMPT
VIDEO_PROMPT += IDENTITY_PROMPT
