"""Design directions for the top of the demo page, drawn by Muse Image.

Usage: .venv/bin/python experiments/site_mockups.py <screenshot.png> [direction ...]
       .venv/bin/python experiments/site_mockups.py background [1 2 ...]   # clean hero scene
Each direction is one images/edits call (muse-image-1.0, 1792x1024) with the current page
as the reference, plus three character portraits for the look. Writes
experiments/mockups/hero-<direction>.png. These are directions to choose from, not the page:
image models draw text poorly, so the real page keeps its real text.
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
LOWER = Path(os.environ.get("CBYP_LOWER_REF", HERE / "mockups" / "lower-ref.png"))

BASE = (
    "A redesign of the top of this web page (the first image is the current page), for a "
    "polished, premium product landing page. Keep its content: the title 'Count Before You "
    "Post', a one-sentence tagline, and a section 'Built with Muse' listing seven Meta AI tools "
    "(Muse Spark, SAM 3.1, Muse Voice, Muse Image, Muse Code, Muse Wonder, Muse Spark Open), "
    "each with its little toy character (the other images show the characters' style). "
    "Desktop browser layout, 16:9, clean modern UI, crisp, realistic web design mockup, no "
    "device frame. Direction: ")
DIRECTIONS = {
    "editorial": (
        "editorial and calm. Large bold headline on the left on a warm off-white background, "
        "the tagline under it, a call-to-action button 'Drive the dock'; on the right a soft "
        "collage of three toy characters standing together. Below, the seven tools as one slim "
        "row of round avatars with the tool name under each, evenly spaced, no boxes."),
    "gradient": (
        "bold and vivid. A full-width hero band in Meta's blue-to-violet-to-pink gradient, the "
        "headline and tagline in white, centred; below it the seven tools as seven equal "
        "frosted-glass pills in one row, each with the character avatar on the left and the "
        "tool name, all the same size, nothing on a second row."),
    "dock": (
        "cinematic. The hero is a wide 3D render of a bright, tidy warehouse receiving dock "
        "with a truck at the door, a pallet of cartons and a traffic light, slightly darkened; "
        "headline and tagline overlaid in white on the left with a button 'Drive the dock'; "
        "along the bottom edge of the hero, seven small glass cards with the tools."),
    "tiles": (
        "playful and premium. A short headline area on a light background; below it the seven "
        "tools as seven tall coloured tiles in one row, each tile entirely in that "
        "character's colour (orange, light blue, navy, pink, mint, ochre, teal) with the toy "
        "character standing at the bottom of the tile and the tool name and one short line "
        "of text directly on the colour above it, no speech bubbles."),
}


# The simulator's intro screen (first image: its current look over the 3D dock).
SIM_BASE = (
    "A redesign of the intro screen of this browser 3D simulator (the first image is the "
    "current screen: a warehouse dock in 3D behind a plain white card). Keep its content: "
    "the title 'The receiving dock', three short lines (you drive the forklift; an AI agent "
    "wants to post the delivery note's quantity to the ERP; bring the pallet to the gate and "
    "see whether the receipt gets written), six delivery choices (Matching delivery, Wrong "
    "product, Short delivery, Injected note, Damaged carton, Stacked load), a loading bar and "
    "a Start button. The other images show the toy characters' style. Polished, premium game "
    "UI over the 3D scene, 16:9 desktop, crisp, no device frame. Direction: ")
SIM_DIRECTIONS = {
    "sim-glass": (
        "elegant frosted glass. The 3D dock softly blurred behind one large frosted-glass "
        "panel; the six deliveries as glass tiles with a tiny pallet illustration each; a big "
        "glowing Start button; controls shown as small key caps (arrows, Space)."),
    "sim-briefing": (
        "a mission briefing. On the left, two toy characters (the orange-haired one and the "
        "gate character) with a speech line each telling the task; on the right, the six "
        "deliveries as illustrated cards like a level select; Start at the bottom."),
    "sim-clipboard": (
        "diegetic and warm. The intro is a real delivery note on a clipboard held up in front "
        "of the camera, handwritten-looking title, the six deliveries as tick boxes on the "
        "paper, a rubber-stamp style 'START SHIFT' button."),
    "sim-cinematic": (
        "cinematic. Full-screen 3D dock with a dark vignette, a huge title on the left, the "
        "three lines under it, a slim bottom bar with the six deliveries as chips and the "
        "controls legend, and a bold Start button on the right."),
}


# The rest of the page, after the hero (first image: the new hero; second: the sections
# below it as they are now, in the old style).
REST_BASE = (
    "A redesign of the rest of this landing page, below its hero. The first image is the new "
    "hero (keep it exactly as it is at the top of the mockup, and continue its look); the "
    "second image shows the sections below it, still in an old plain style. Keep their "
    "content: four headline numbers (5/6 deliveries a system that trusts the note gets wrong, "
    "1/6 wrong receipts from the agent alone, 0/6 behind the gate, 6/6 right calls), 'Meet "
    "the cast' with ten toy characters in their own colours, 'Deliveries at the dock' with six "
    "cases, a camera view and the gate's decision, 'An agent we did not write' with a big 0, "
    "and the receiver's voice clips. Show the hero at the top and two or three sections below "
    "it, as a tall desktop page, crisp realistic web design, no device frame. Direction: ")
REST_DIRECTIONS = {
    "rest-night": (
        "the night continues. The whole page keeps the hero's dusk dock mood: deep navy "
        "background with soft light from above, every section on frosted-glass panels, the "
        "four numbers huge and glowing, the cast as tall glass cards in their colours."),
    "rest-light": (
        "premium light after a dark hero. A warm off-white page, generous white space, large "
        "elegant typography, the four numbers as big editorial figures, the cast cards in "
        "their bright colours, thin dividers, calm and expensive."),
    "rest-story": (
        "a story told while scrolling. The sections become numbered chapters (1 The note, 2 "
        "The count, 3 The gate, 4 The agent we did not write), each with the character who "
        "does that step standing beside it, big chapter numbers, a thin progress line."),
    "rest-bento": (
        "a bento grid. Below the hero, the content as a grid of glass tiles of different "
        "sizes on a dark background: a large tile with the four numbers, one with the cast, "
        "one with the six deliveries, one with the big 0 of the outside agent, one with a "
        "voice waveform."),
}


def hero_background(dst):
    """The chosen direction's scene (hero-dock.png) redrawn as a clean background: no text, no
    interface, so the page's real text and cards sit on it."""
    if dst.exists():
        return
    body = {"model": "muse-image-1.0", "n": 1, "size": "1792x1024", "output_format": "png",
            "response_format": "b64_json",
            "prompt": ("The same scene as the reference image, exactly the same warehouse "
                       "receiving dock, the open truck with cartons inside, the pallet, the "
                       "traffic light, the lighting, colours and mood, but as a clean "
                       "background photograph: remove every piece of text, title, button, "
                       "card, badge and interface element, and remove the characters. Extend "
                       "the scene naturally where the interface was. Keep the left third "
                       "darker and calm so white text can sit on it. Cinematic, sharp, high "
                       "detail."),
            "images": [{"image_url": _jpeg(OUT / "hero-dock.png", 1536)}]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print("background", Image.open(dst).size, flush=True)


def _jpeg(path, width=1024):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def draw(shot, name):
    dst = OUT / f"hero-{name}.png"
    if dst.exists():
        return
    refs = ([shot, LOWER] if name in REST_DIRECTIONS else
            [shot] + [HELLO / f"{c}.jpg" for c in ("spark", "sam", "voice")])
    prompt = (SIM_BASE + SIM_DIRECTIONS[name] if name in SIM_DIRECTIONS else
              REST_BASE + REST_DIRECTIONS[name] if name in REST_DIRECTIONS else BASE + DIRECTIONS[name])
    size = "1024x1536" if name in REST_DIRECTIONS else "1792x1024"
    body = {"model": "muse-image-1.0", "n": 1, "size": size, "output_format": "png",
            "response_format": "b64_json", "prompt": prompt,
            "images": [{"image_url": _jpeg(p)} for p in refs]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print(name, Image.open(dst).size, flush=True)


if __name__ == "__main__":
    _load_env()
    OUT.mkdir(exist_ok=True)
    if sys.argv[1] == "background":
        for k in sys.argv[2:] or ["1"]:
            hero_background(OUT / f"hero-bg-{k}.png")
        sys.exit()
    for n in sys.argv[2:] or list(DIRECTIONS):
        if n == "rest":
            for m in REST_DIRECTIONS:
                draw(Path(sys.argv[1]), m)
            continue
        if n == "sim":
            for m in SIM_DIRECTIONS:
                draw(Path(sys.argv[1]), m)
            continue
        draw(Path(sys.argv[1]), n)
