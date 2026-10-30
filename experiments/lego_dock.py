"""The whole warehouse redrawn as LEGO, by Muse Image (Sena's request).

Usage: .venv/bin/python experiments/lego_dock.py [view ...]
One images/edits call per view (muse-image-1.0, 1792x1024) with that view of the dock as the
reference. Writes experiments/mockups/lego-<view>.png. A look to choose from, not the scene.
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402
from experiments.site_mockups import _jpeg  # noqa: E402

HERE = Path(__file__).parent
ROOT = HERE.parent
OUT = HERE / "mockups"

VIEWS = {
    "hall": ROOT / "site" / "img" / "en" / "dock-genel.jpg",
    "receiving": ROOT / "site" / "img" / "en" / "dock-teslimat.jpg",
    "outside": ROOT / "site" / "img" / "en" / "dock-disari.jpg",
    "rooms": OUT / "result-ref.png",
}

PROMPT = (
    "Redraw this exact scene, from exactly the same camera angle and with the same layout, as "
    "if every single thing were built from LEGO bricks: the floor a huge grey baseplate with "
    "visible studs, the walls and the roof of stacked bricks and plates, the blue and orange "
    "pallet racks from LEGO beams, the cartons as tan 2x2 and 2x4 bricks with printed labels, "
    "the pallet, the forklift as an official-looking LEGO City forklift set, the traffic light "
    "and barrier, the dock door, the truck, the glass rooms with transparent LEGO panels, the "
    "lamps and the yellow floor tape as flat tiles. The toy characters stay as LEGO minifigures "
    "in the same places and poses. Bright, clean studio lighting, slight tilt-shift depth of "
    "field, glossy ABS plastic with soft reflections, photorealistic LEGO photography, high "
    "detail, no text other than the signs already in the scene.")


def draw(view):
    dst = OUT / f"lego-{view}.png"
    if dst.exists():
        return
    body = {"model": "muse-image-1.0", "n": 1, "size": "1792x1024", "output_format": "png",
            "response_format": "b64_json", "prompt": PROMPT,
            "images": [{"image_url": _jpeg(VIEWS[view], 1536)}]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print(view, Image.open(dst).size, flush=True)


if __name__ == "__main__":
    _load_env()
    for v in sys.argv[1:] or list(VIEWS):
        draw(v)
