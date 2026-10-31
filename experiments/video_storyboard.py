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
# Shots with no child in them: the base above says a child is at the table, so these get
# their own base (the model drew the child anyway when told only in the shot line).
BASE_NO_CHILD = (
    "A frame from a short film, cinematic, photorealistic, shallow depth of field. NO PEOPLE "
    "AT ALL in this shot: no child, no hands, no hair, no shadow of a person. The toys are the "
    "toy-brick warehouse dock, truck, cartons, traffic light and the seven toy figures from "
    "the reference images, the same style and colours, standing on a wooden table. No text "
    "overlays, no brand names or logos. Shot: ")
NO_CHILD = {"1b-leave", "1c-alive", "6-night", "7-go", "5-dive"}
# The box the figures come in (Sena: not a plain box). The project's own name on it, no
# company logo: a logo on a toy box would read as an official product.
BOX = (
    "The toy-set box is a glossy printed retail box, not plain cardboard: on its lid in big "
    "bold navy letters 'COUNT BEFORE YOU POST', under it smaller 'Built with Muse', a small "
    "round badge 'WAREHOUSE 01', and a printed picture of the toy-brick dock with the "
    "seven figures in a row. The seven figures, on the box and in the tray, must be exactly "
    "the seven characters of the first reference image (left to right, same faces, skin, "
    "hair, clothes and props), as toy figures like in the second reference image. No other "
    "logos or brand names. ")
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
    # Sena's story (31 Oct): the child leaves for a moment, the figures come alive and talk,
    # freeze when the child comes back, and at night, when the child has gone to bed, the
    # game begins. Shots after 1-arrive, numbered in story order.
    "0-box": (
        "the very first moment, a moment before the first reference image: top-down, the "
        "bare table with the same printed box as in the first reference image, still closed, "
        "in the middle, its lid art exactly as there (title, 'Built with Muse', the badge, "
        "the dock picture, the seven figures on grey stands); the child's two hands on the "
        "lid about to lift it, the top of the head at the bottom edge."),
    "0b-open": (
        "top-down: the box lid lies beside the open box; inside, EXACTLY SEVEN toy figures, "
        "the seven characters of the first reference image in the same order, in a neat moulded tray "
        "with seven slots, smiling up; the child's hand lifting the first figure out; next "
        "to the box a bare grey baseplate and bags of loose bricks. NOTHING IS BUILT yet: no "
        "warehouse, no truck on the table."),
    "1b-leave": (
        "top-down, exactly the table of the first reference image a moment later: NOTHING IS "
        "BUILT, only the bare grey baseplate with three or four bricks clicked on it, the "
        "colour-sorted piles of loose bricks around it, the open cardboard box with the seven "
        "figures lying in it; at the bottom edge an empty wooden chair pushed back; quiet."),
    "1c-alive": (
        "NOT top-down: a close-up at the height of the toy figures, inside the open cardboard "
        "box on the table; the seven toy figures have sat up and are leaning together, talking, "
        "one peeking over the edge of the box toward where the child went; the empty chair a "
        "soft blur behind; warm daylight; playful and secretive."),
    "1d-shh": (
        "same close-up at figure height: the figures startled, one with a finger on its lips "
        "going 'shh', two diving back down into the box, a child's shadow falling across the "
        "table from the side; motion blur on the figures; funny and tense."),
    "6-night": (
        "top-down again, late evening: the room is dark, moonlight from a window and a soft "
        "night light; on the table the finished toy-brick dock, the truck at the door and the "
        "seven figures on their stands, frozen; the chair empty, the child gone to bed."),
    "7-go": (
        "NOT top-down: a low dramatic close-up at figure height in the dark, the seven figures "
        "on the dock apron turning their heads together toward the camera, the small traffic "
        "light flickering on in amber, the figure in the cardboard-box costume lifting its "
        "striped barrier; the moment the game begins."),
}


BOXED = {"0-box", "0b-open", "1-arrive", "1b-leave", "1c-alive"}


HELLO = HERE.parent / "assets" / "mascots" / "hello"
CAST = ("spark", "sam", "voice", "iris", "ada", "wonder", "spark-open")


def cast_sheet():
    """The seven Muse characters' portraits side by side, in the page's order, so the box and
    the tray show exactly them (the model drifted when it only had the diorama)."""
    dst = OUT / "story-cast-sheet.jpg"
    if not dst.exists():
        ims = [Image.open(HELLO / f"{c}.jpg").convert("RGB").resize((400, 400)) for c in CAST]
        sheet = Image.new("RGB", (400 * len(ims), 400), "white")
        for i, im in enumerate(ims):
            sheet.paste(im, (400 * i, 0))
        sheet.save(dst, quality=90)
    return dst


def draw(name):
    dst = OUT / f"story-{name}.png"
    if dst.exists():
        return
    refs = ([OUT / "story-1-arrive.png"] + REFS if name == "1b-leave"
            else [OUT / "story-0b-open.png", cast_sheet(), OUT / "story-4-cast.png"]
            if name == "0-box"
            else [cast_sheet(), OUT / "story-4-cast.png", OUT / "story-1-arrive.png"]
            if name == "0b-open" else REFS)
    body = {"model": "muse-image-1.0", "n": 1, "size": "1792x1024", "output_format": "png",
            "response_format": "b64_json",
            "prompt": ((BASE_NO_CHILD if name in NO_CHILD else BASE) + BOX + SHOTS[name]
                       if name in BOXED else
                       (BASE_NO_CHILD if name in NO_CHILD else BASE) + SHOTS[name]),
            "images": [{"image_url": _jpeg(p, 1536)} for p in refs]}
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
