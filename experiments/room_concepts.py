"""Room concepts for the simulator's warehouse, drawn by Muse Image: two per character.

Usage: .venv/bin/python experiments/room_concepts.py [id ...]
Each concept is one images/edits call (muse-image-1.0, 1792x1024) with the character's
portrait and the dock render as references. Writes experiments/mockups/room-<id>-<a|b>.png.
Sena picks one per room (or edits it); Muse Code then builds the chosen rooms in Blender
(docs/muse-code/dock-rooms.md). These are directions, not the scene.
"""
import base64
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "mockups"
HELLO = HERE.parent / "assets" / "mascots" / "hello"
DOCK = HERE / "blender" / "out" / "polish" / "depo-ok-genel.png"

BASE = (
    "A small glass-fronted room inside a warehouse receiving dock, for a toy character. The "
    "first image is the character (keep exactly its look: a LEGO-style minifigure toy); the "
    "second image is the warehouse it works in (keep its style, light and materials: a clean "
    "3D render, warm high-bay light, plastic toy look). The room is about 3 m wide and 4 m "
    "deep, seen from the warehouse floor through its glass front with an open doorway, the "
    "back wall painted in the character's colour ({colour}), a lit name plate '{name}' above "
    "the glass. The character sits at a desk facing us, working, face clearly visible (no "
    "screen blocks the face). Its job: {job}. Wide 16:9, eye level from the aisle in front of "
    "the room, crisp, premium toy-world render, no text other than the name plate. Room: ")

ROOMS = {
    "spark": ("Spark", "#f97316 orange", "reads delivery notes and runs the receiving agent", {
        "a": "a tidy reading desk with trays of delivery notes, a desk lamp, a magnifier, a "
             "wall of pinned notes with highlighted lines, sticky notes in orange.",
        "b": "an energetic command post: a big wall board of delivery notes connected with "
             "orange string, a document scanner on the desk, a coffee mug, a small rocket toy."}),
    "sam": ("Sam", "#3b82f6 blue", "counts the cartons from the ceiling camera", {
        "a": "a camera control room: a wall of small screens showing cartons from above with "
             "blue outlines, the screens on the side walls, a joystick on the desk.",
        "b": "a calm lab: a camera on a tripod, a scale model of a pallet with cartons on the "
             "desk, blue outline drawings of cartons pinned up, a tally counter."}),
    "voice": ("Voice", "#1e3a8a navy", "listens to the receiver and writes down what is said", {
        "a": "a small sound studio: acoustic foam panels on the navy wall, a studio microphone "
             "on an arm, headphones, a waveform glowing on a side screen.",
        "b": "a radio-room look: a vintage receiver, a reel-to-reel recorder, speech bubbles "
             "pinned on the wall, a cosy lamp."}),
    "kapi": ("Kapı", "#a16207 amber-brown", "the gate: twelve rules in plain code, posts, blocks or asks the supervisor", {
        "a": "a gatekeeper's booth: a mini barrier arm and a traffic light on the desk, the "
             "twelve rules as numbered plaques on the wall, a stamp with POST / BLOCK.",
        "b": "a control room: a big panel with three lamps (green, red, amber), switches, a "
             "rule book on a lectern, cardboard textures matching its body."}),
    "sef": ("Şef", "#1d4ed8 blue", "the shift supervisor who signs off when the evidence can't decide", {
        "a": "a supervisor's office, slightly larger feeling: a clipboard and a tablet with "
             "checkmarks, a shift board on the wall, a hard-hat on a hook, a window view.",
        "b": "a busy foreman's office: a wall planner with shifts, a radio, a stack of signed "
             "papers, a big 'approved' stamp, a coffee thermos."}),
    "wonder": ("Wonder", "#ca8a04 golden", "the clerk who writes disputes and damage reports", {
        "a": "a writer's desk: a fountain pen, letter trays, an ink pot, envelopes with wax "
             "seals, shelves of binders in golden tones.",
        "b": "an old post-office counter feel: pigeonhole shelves full of letters, a "
             "typewriter, a rubber-stamp rack, a pinned map."}),
    "ada": ("Ada", "#0f766e teal", "wrote the code (named after Ada Lovelace)", {
        "a": "a developer's den: two monitors turned sideways with green code, a mechanical "
             "keyboard, a rubber duck, a framed portrait of Ada Lovelace, plants.",
        "b": "a maker lab: a whiteboard full of diagrams, a laptop, a small server rack with "
             "blinking lights, a teal neon sign '</>'."}),
    "iris": ("Iris", "#db2777 pink", "the painter who drew the whole cast", {
        "a": "an artist's studio: an easel with a canvas of the cast, paint tubes and brushes "
             "in jars, colour swatches pinned on the pink wall.",
        "b": "a design studio: a large drawing tablet on the desk, printed character sketches "
             "on a string with clips, a palette, a mannequin figure."}),
    "rover": ("Rover", "#0d9488 teal-green", "Spark's open-weight cousin who travels to other servers and reads the note a second time", {
        "a": "a traveller's base camp: a backpack, a thermos, a map with pins of server "
             "locations, a small tent-like canopy over the desk, a lantern.",
        "b": "a field station: a rugged laptop, stacked travel cases with stickers, a globe, "
             "postcards from data centres on the wall."}),
    "glimmer": ("Glimmer", "#8b5cf6 violet", "a small open-weight model who reads notes in trials", {
        "a": "a calm observatory: a glowing glass orb on the desk, star charts on the violet "
             "wall, a small telescope, soft fairy lights.",
        "b": "a crystal reading room: shelves of small glowing crystals, a notebook, a "
             "lavender plant, soft violet light."}),
}


def _jpeg(path, width=1024):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def draw(cid, variant):
    dst = OUT / f"room-{cid}-{variant}.png"
    if dst.exists():
        return
    name, colour, job, options = ROOMS[cid]
    portrait = HELLO / f"{'spark-open' if cid == 'rover' else cid}.jpg"
    body = {"model": "muse-image-1.0", "n": 1, "size": "1792x1024", "output_format": "png",
            "response_format": "b64_json",
            "prompt": BASE.format(colour=colour, name=name, job=job) + options[variant],
            "images": [{"image_url": _jpeg(portrait)}, {"image_url": _jpeg(DOCK)}]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print(cid, variant, Image.open(dst).size, flush=True)


if __name__ == "__main__":
    _load_env()
    OUT.mkdir(exist_ok=True)
    for cid in sys.argv[1:] or list(ROOMS):
        for v in ("a", "b"):
            try:
                draw(cid, v)
            except Exception as e:  # one failed drawing shouldn't stop the rest
                print(cid, v, "failed:", e, flush=True)
