"""The seven tool characters for the hero cards, drawn in the light of the chosen hero scene.

Usage: .venv/bin/python experiments/hero_characters.py draw [name ...]   # Muse Image
       .venv/bin/python experiments/hero_characters.py cut [name ...]    # SAM 3.1
Each character is redrawn by Muse Image from three references: its own hello portrait (so
face, hair, outfit and prop stay exactly its own), the chosen design
(experiments/mockups/hero-dock.png, the cards along its bottom) and the hero background
(experiments/mockups/hero-bg-1.png, for the light). Plain flat grey backdrop, then cut out
with the same SAM pipeline as the full-HD portraits (experiments/mascot_portraits.py).
Writes assets/mascots/hero/<name>-raw.png and <name>.png (transparent).
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402
import mascot_portraits as mp  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE.parent / "assets" / "mascots" / "hero"
TOOLS = ["spark", "sam", "voice", "iris", "ada", "wonder", "rover"]

PROMPT = (
    "The same toy character as in the first image, exactly the same design: same face, hair, "
    "outfit, colours, accessories, proportions and glossy plastic toy minifigure material. "
    "{hold}. Drawn the way the characters stand on the cards along the bottom of the second "
    "image: full body, a three-quarter turn towards the viewer, a confident friendly pose, "
    "lit like the scene in the third image: a cool blue-grey rim light from behind and a warm "
    "soft key light from the front left, subtle reflections on the plastic. Plain flat mid "
    "grey background, one even colour, no floor, no shadow on the background, nothing else in "
    "the picture, no text. Sharp, high detail.")


def smooth_keyed(im, threshold=38, gw=80, gh=120):
    """Pixels clearly unlike the backdrop, for a soft gradient backdrop. The backdrop under the
    figure is spanned from the picture's four border strips (a Coons patch on a coarse grid:
    only backdrop is at the edges) and compared with every pixel."""
    from PIL import ImageChops
    g = im.convert("RGB").resize((gw, gh))
    px = g.load()
    top = [px[x, 1] for x in range(gw)]
    bot = [px[x, gh - 2] for x in range(gw)]
    lef = [px[1, y] for y in range(gh)]
    rig = [px[gw - 2, y] for y in range(gh)]
    c00, c10, c01, c11 = px[1, 1], px[gw - 2, 1], px[1, gh - 2], px[gw - 2, gh - 2]
    bg = Image.new("RGB", (gw, gh))
    out = bg.load()
    for y in range(gh):
        v = y / (gh - 1)
        for x in range(gw):
            u = x / (gw - 1)
            out[x, y] = tuple(round(
                (1 - v) * top[x][c] + v * bot[x][c] + (1 - u) * lef[y][c] + u * rig[y][c]
                - ((1 - u) * (1 - v) * c00[c] + u * (1 - v) * c10[c]
                   + (1 - u) * v * c01[c] + u * v * c11[c])) for c in range(3))
    bg = bg.resize(im.size, Image.BILINEAR)
    diff = ImageChops.difference(im.convert("RGB"), bg).convert("L")
    return diff.point(lambda val: 255 if val > threshold else 0)


def draw(name):
    dst = OUT / f"{name}-raw.png"
    if dst.exists():
        return
    hello = mp.MASCOTS / "hello" / f"{mp.CAST[name]}.jpg"
    refs = [hello, HERE / "mockups" / "hero-dock.png", HERE / "mockups" / "hero-bg-1.png"]
    hold = mp.PROPS[name][0] or "a friendly pose, hands empty"
    body = {"model": "muse-image-1.0", "n": 1, "size": "1024x1536", "output_format": "png",
            "response_format": "b64_json", "prompt": PROMPT.format(hold=hold[0].upper() + hold[1:]),
            "images": [{"image_url": "data:image/jpeg;base64," + base64.b64encode(mp._jpeg(p)).decode()}
                       for p in refs]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print(name, "drawn", Image.open(dst).size, flush=True)


if __name__ == "__main__":
    _load_env()
    OUT.mkdir(parents=True, exist_ok=True)
    step, names = sys.argv[1], sys.argv[2:] or TOOLS
    if step == "cut":
        mp.OUT, mp.SAVE_SIZE = OUT, None   # same SAM cut, these folders, the figure's own box
        # SAM found no mask for Sam's tablet or Rover's backpack gadget under any word; these
        # drawings have a soft gradient backdrop, so the backdrop key is spanned from its edges.
        mp.KEY = {"sam", "rover"}
        mp._keyed = smooth_keyed
        mp.PROPS["sam"] = (mp.PROPS["sam"][0], ["tablet", "tablet computer", "digital screen",
                                                 "electronic device"])
        mp.PROPS["rover"] = (mp.PROPS["rover"][0], ["backpack", "paper", "device", "machine",
                                                     "tag"])
        for n in names:
            mp.cut(n)
    else:
        for n in names:
            draw(n)
