"""Storyboard for the demo video's opening, drawn by Muse Image (Sena's idea, 31 Oct): a child
builds the toy-brick dock on a table, seen from straight above, so only the top of the head,
the hands and the table show; then the camera dives into the model and the 3D simulator takes
over.

Usage: .venv/bin/python experiments/video_storyboard.py [shot ...]
One images/edits call per shot (muse-image-1.0, 1792x1024), with the tabletop diorama the page
uses as the look reference. Writes experiments/mockups/story-<shot>.png. Frames to plan the
edit with, not footage.
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
OUT = HERE / "mockups"
REFS = [OUT / "hero-lego-tabletop-diorama.png", OUT / "hero-diorama-topdown.png"]

BASE = (
    "A frame from a short film, shot from directly above a light wooden table (top-down, 90 "
    "degrees), soft warm daylight, cinematic, photorealistic. A child of about eight is seen "
    "only from above: the top of the head with messy hair, the shoulders and the hands; the "
    "face is never visible. The toys are the toy-brick warehouse dock, truck, cartons, traffic "
    "light and the seven toy figures from the reference images, the same style and colours. "
    "No text overlays, no brand names or logos. Shot: ")
SHOTS = {
    "1-arrive": (
        "the very start, NOTHING IS BUILT YET: no warehouse, no truck, no figures standing; "
        "only a bare grey baseplate in the middle of the table and loose bricks scattered "
        "around it in small piles, the seven figures lying in an open box at the side. The "
        "child has just run in and is sitting down at the bottom edge of the frame: only the "
        "top of the head and two small hands reaching for the bricks, motion blur on the "
        "hands."),
    "2-walls": (
        "the child's hands pressing grey bricks onto the baseplate, the first walls of the "
        "warehouse half built, a yellow 'GOODS IN' sign lying ready next to them; the top of "
        "the head at the bottom edge."),
    "3-truck": (
        "the warehouse walls finished with the open dock door; one hand pushes a small toy "
        "truck full of tan carton bricks on pallets up to the door; a yellow taped zone and a "
        "small traffic light in front of the dock."),
    "4-cast": (
        "the finished dock with the truck at the door; the child's fingers placing the last of "
        "seven small toy figures on round grey stands in a row in front of it; the six others "
        "already standing; a figure in a cardboard-box costume holding a striped barrier is "
        "being set next to the traffic light."),
    "5-dive": (
        "NOT top-down any more: the camera is now low, at the height of the toy figures, "
        "inside the model, looking through the open dock door into the warehouse; the yellow "
        "taped floor zone and a pallet of carton bricks in front, the traffic light glowing "
        "amber at the side, the figures small in the background; no child, no hands, no "
        "hair; the table edges and the room are a soft blur at the frame edges, as if we "
        "have shrunk into the toy world."),
}


def draw(name):
    dst = OUT / f"story-{name}.png"
    if dst.exists():
        return
    body = {"model": "muse-image-1.0", "n": 1, "size": "1792x1024", "output_format": "png",
            "response_format": "b64_json", "prompt": BASE + SHOTS[name],
            "images": [{"image_url": _jpeg(p, 1536)} for p in REFS]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print(name, Image.open(dst).size, flush=True)


if __name__ == "__main__":
    _load_env()
    for n in sys.argv[1:] or list(SHOTS):
        draw(n)
