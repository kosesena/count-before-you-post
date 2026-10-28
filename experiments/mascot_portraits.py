"""Full-HD portraits of the cast without a background: Muse Image draws, SAM 3.1 cuts out.

Usage: .venv/bin/python experiments/mascot_portraits.py draw [name ...]   # Muse Image
       .venv/bin/python experiments/mascot_portraits.py cut [name ...]    # SAM 3.1 mask
Muse Image can't draw a transparent background (it is always opaque), so each character is
redrawn from its hello portrait (and character sheet, if any) on a flat plain colour, full
body, portrait 1080x1920. SAM 3.1 then segments the figure and its mask becomes the alpha.
Writes assets/mascots/portraits/<name>-raw.png (drawn, 1152x2048) and <name>.png
(transparent, 1080x1920).
Skips anything already there: delete a file to draw or cut it again.
"""
import base64
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402
from cbyp.sam import segment_image  # noqa: E402

MASCOTS = Path(__file__).resolve().parent.parent / "assets" / "mascots"
OUT = MASCOTS / "portraits"
SIZE = "1080x1920"

# hello/<file>.jpg -> a flat backdrop that none of the character's own colours is close to.
CAST = {"spark": "spark", "sam": "sam", "voice": "voice", "kapi": "kapi", "sef": "sef",
        "wonder": "wonder", "rover": "spark-open", "glimmer": "glimmer", "iris": "iris",
        "ada": "ada"}
BG = {"spark": "light grey", "sam": "light grey", "voice": "light grey", "kapi": "white",
      "sef": "light grey", "wonder": "light grey", "rover": "light grey",
      "glimmer": "light grey", "iris": "light grey", "ada": "light grey"}

# What each one holds: told to Muse Image (it dropped Sam's tablet once), and
# asked of SAM separately ("toy figure" alone leaves the props out of the mask).
PROPS = {
    "spark": ("", []),
    "sam": ("holding his tablet that shows a grid of cartons, as in the reference", ["tablet"]),
    "voice": ("", ["headphones"]),
    "kapi": ("holding the plain red-and-white striped barrier baton in one hand (red and white "
             "only, no stars, no blue) and waving with the other, as in the reference",
             ["striped baton"]),
    "sef": ("holding the checklist tablet and giving a thumbs up, as in the reference",
            ["tablet"]),
    "wonder": ("holding the fountain pen and the clipboard with a red seal, as in the reference",
               ["pen", "clipboard"]),
    "rover": ("with the gadget backpack on and holding the checklist paper, as in the reference",
              ["backpack", "paper"]),
    "glimmer": ("holding the small glowing crystal orb in her hand, as in the reference",
                ["glowing orb", "crystal ball", "hand"]),
    "iris": ("holding the paint palette and paintbrush, the shoulder bag on, as in the reference",
             ["paint palette", "paintbrush", "bag"]),
    # Ada as Sena chose her: no laptop, hands free (the laptop version was wrong).
    "ada": ("waving with one hand, both hands empty and holding nothing: no laptop, no "
            "computer, no robot, no props", []),
}

# SAM found no mask for Sam's tablet or Voice's microphone under any word we tried. For these
# two, whatever stands out from the flat backdrop and touches SAM's figure is kept too.
KEY = {"sam", "voice"}

PROMPT = (
    "The same character as in the reference images, exactly the same design: same face, hair, "
    "outfit, colours, accessories, proportions and the same glossy plastic toy minifigure "
    "material and finish. Full body, head to feet, centred, facing the camera, {hold}. "
    "Filling most of the frame with a small margin all around. Plain flat {bg} "
    "background, one even colour, no gradient, no floor, no shadow on the background, no "
    "props behind, no text, no labels, no other characters. Sharp, high detail, soft "
    "even studio light.")


def _jpeg(path, width=1024):
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return buf.getvalue()


def draw(name):
    dst = OUT / f"{name}-raw.png"
    if dst.exists():
        return
    hello = CAST[name]
    refs = [MASCOTS / "hello" / f"{hello}.jpg"]
    sheet = MASCOTS / "sheets" / f"{hello}.jpg"
    if sheet.exists():
        refs.append(sheet)
    body = {"model": "muse-image-1.0", "n": 1, "size": SIZE, "output_format": "png",
            "response_format": "b64_json", "prompt": PROMPT.format(bg=BG[name], hold=PROPS[name][0] or "a friendly pose"),
            "images": [{"image_url": "data:image/jpeg;base64," + base64.b64encode(_jpeg(p)).decode()}
                       for p in refs]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print(name, "drawn", Image.open(dst).size, flush=True)


def cut(name, concept="toy figure"):
    src, dst = OUT / f"{name}-raw.png", OUT / f"{name}.png"
    if dst.exists() or not src.exists():
        return
    found = sorted(_masks(segment_image(src, concept)), key=lambda m: -(m[0] or 0))
    if not found:
        print(name, "SAM found nothing", flush=True)
        return
    im = Image.open(src).convert("RGBA")
    conf = found[0][0]
    parts = [found[0]]
    for prop in PROPS[name][1]:
        parts += [m for m in _masks(segment_image(src, prop)) if (m[0] or 0) >= 0.5]
    # SAM sends a large object's mask scaled down (longest side 1024): scale it back up to
    # the object's box. The dock's cartons are small enough to come back at full size.
    mask = Image.new("L", im.size, 0)
    for _, box, small in parts:
        part = Image.new("L", im.size, 0)
        part.paste(small.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS), box[:2])
        mask = ImageChops.lighter(mask, part)
    if name in KEY:
        mask = _filled(ImageChops.lighter(mask, _touching(_keyed(im), mask)))
    # Soften the mask edge by one pixel so the cut-out does not look jagged.
    im.putalpha(mask.filter(ImageFilter.GaussianBlur(1)))
    # Full HD portrait (1080x1920): Muse Image draws 1152x2048, so this only scales down.
    im.resize((1080, 1920), Image.LANCZOS).save(dst)
    print(name, "cut", f"figure conf={conf:.2f}, {len(parts) - 1} prop mask(s)", flush=True)


def _keyed(im, threshold=60):
    """Pixels clearly unlike the backdrop (its colour taken from the four corners)."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    corners = [rgb.getpixel(p) for p in ((5, 5), (w - 6, 5), (5, h - 6), (w - 6, h - 6))]
    bg = tuple(sorted(c[i] for c in corners)[1] for i in range(3))
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, bg)).convert("L")
    return diff.point(lambda v: 255 if v > threshold else 0)


def _touching(keyed, seed, scale=4, steps=5000):
    """The parts of `keyed` connected to `seed`: grow seed inside keyed until it stops."""
    small = (keyed.width // scale, keyed.height // scale)
    k, x = keyed.resize(small), seed.resize(small).point(lambda v: 255 if v > 127 else 0)
    for _ in range(steps):
        grown = ImageChops.darker(x.filter(ImageFilter.MaxFilter(5)), k)
        if ImageChops.difference(grown, x).getbbox() is None:
            break
        x = grown
    return ImageChops.darker(x.resize(keyed.size), keyed)


def _filled(mask):
    """Close holes: whatever the outside can't reach is part of the figure (a tablet's light
    screen reads as backdrop, but it is enclosed by the tablet's frame)."""
    outside = ImageChops.invert(mask.point(lambda v: 255 if v > 127 else 0))
    border = Image.new("L", mask.size, 0)
    border.paste(255, (0, 0, mask.width, 16))  # thick enough to survive _touching's downscale
    reached = _touching(outside, ImageChops.darker(border, outside))
    return ImageChops.invert(reached)


def _masks(text):
    """(confidence, box, mask image at SAM's own resolution) for every object."""
    import meta_sam_parser as msp
    parser = msp.image_segmentation_format().create_parser()
    parser.push(text)
    out = []
    for rec in parser.finish(msp.CompletedOutcome()).result.records:
        if isinstance(rec, msp.SegmentationMaskRecord):
            b, m = rec.bounds, rec.mask
            raster = msp.decode_mask_to_raster(m)
            out.append((rec.confidence, (b.left, b.top, b.right, b.bottom),
                        Image.frombytes("L", (m.width, m.height), bytes(255 * v for v in raster))))
    return out


if __name__ == "__main__":
    _load_env()
    OUT.mkdir(parents=True, exist_ok=True)
    step, names = sys.argv[1], sys.argv[2:] or list(CAST)
    for n in names:
        {"draw": draw, "cut": cut}[step](n)
