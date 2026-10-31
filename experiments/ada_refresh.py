"""Ada's new look everywhere on the site (Sena, 31 Oct): the infinity sign on her hoodie and on
the lid of a dark grey laptop like Sam's tablet, its screen turned to her.

Usage: .venv/bin/python experiments/ada_refresh.py hello   # Muse Image: the hello portrait
       .venv/bin/python experiments/hero_characters.py draw ada && ... cut ada
       .venv/bin/python experiments/ada_refresh.py site    # the site's six Ada images
The full-HD portrait (assets/mascots/portraits/ada.png) is drawn by mascot_portraits.py. The
hello portrait is redrawn from it on the old hello's backdrop; the site images are made from
these the same way experiments/build_site.py makes them (that script also needs the rendered
dock scenes, so this only redoes Ada's files). The old files are kept as *-v1.
"""
import base64
import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402
import experiments.mascot_portraits as mp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HELLO = mp.MASCOTS / "hello"
IMG = ROOT / "site" / "img"

PROMPT = (
    "The same picture as the second reference image (the same soft mint background, the same "
    "floating code symbols, the same framing, pose, light and toy minifigure style), but the "
    "character must look exactly like the first reference image: the small blue infinity sign "
    "on her mint hoodie, and in her hand the open dark grey laptop held exactly as in the "
    "first reference image: the screen faces HER, so the camera sees only the plain dark grey "
    "BACK of the lid with the blue infinity sign in its middle; NO screen, NO code visible to "
    "the camera. No pink laptop, no stickers, no robot. One hand waving. Square, sharp, high "
    "detail.")


def hello():
    old = HELLO / "ada-v1.jpg"
    if not old.exists():
        shutil.copy(HELLO / "ada.jpg", old)
    body = {"model": "muse-image-1.0", "n": 1, "size": "1024x1024", "output_format": "png",
            "response_format": "b64_json", "prompt": PROMPT,
            "images": [{"image_url": "data:image/jpeg;base64,"
                        + base64.b64encode(mp._jpeg(p)).decode()}
                       for p in (mp.OUT / "ada.png", old)]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        raw = base64.b64decode(json.loads(r.read())["data"][0]["b64_json"])
    tmp = HELLO / "ada-raw.png"
    tmp.write_bytes(raw)
    Image.open(tmp).convert("RGB").save(HELLO / "ada.jpg", quality=92)
    tmp.unlink()
    print("hello drawn", flush=True)


def site():
    """build_site.py's crops and sizes, for Ada only."""
    im = Image.open(HELLO / "ada.jpg").convert("RGB")
    w, h = im.size
    im.crop((round(w * .26), round(h * .04), round(w * .74), round(h * .52))).resize(
        (160, 160)).save(IMG / "av-ada.jpg", quality=85)
    im.crop((round(w * .22), round(h * .02), round(w * .78), round(h * .58))).resize(
        (480, 480)).save(IMG / "avl-ada.jpg", quality=86)
    hi = im.resize((640, round(640 * h / w))) if w > 640 else im
    hi.save(IMG / "hello-ada.jpg", quality=82)
    por = Image.open(mp.OUT / "ada.png")
    fig = por.crop(por.getbbox())
    fig.resize((520, round(520 * fig.height / fig.width)), Image.LANCZOS).save(
        IMG / "cut-ada.webp", "WEBP", quality=88, method=6)
    hero = Image.open(mp.MASCOTS / "hero" / "ada.png")
    hero.resize((440, round(440 * hero.height / hero.width)), Image.LANCZOS).save(
        IMG / "hero-ada.webp", "WEBP", quality=88, method=6)
    w2 = min(760, hero.width)
    hero.resize((w2, round(w2 * hero.height / hero.width)), Image.LANCZOS).save(
        IMG / "fig-ada.webp", "WEBP", quality=88, method=6)
    print("site images written", flush=True)


if __name__ == "__main__":
    _load_env()
    {"hello": hello, "site": site}[sys.argv[1]]()
