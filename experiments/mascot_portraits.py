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
SAVE_SIZE = (1080, 1920)
# Redrawn on 5 Nov from their earlier portrait (kept as <name>-v1.png)
REDRAW = {"sef": [OUT / "sef-v1.png"],
          "iris": [OUT / "iris-v2.png", OUT / "iris-v1.png"]}   # v2: the bag, v1: the flower charm   # cut() output; None keeps the figure's own box

# hello/<file>.jpg -> a flat backdrop that none of the character's own colours is close to.
CAST = {"spark": "spark", "sam": "sam", "voice": "voice", "kapi": "kapi", "sef": "sef",
        "wonder": "wonder", "rover": "spark-open", "glimmer": "glimmer", "iris": "iris",
        "ada": "ada"}
BG = {"spark": "light grey", "sam": "light grey", "voice": "light grey", "kapi": "white",
      "sef": "bright chroma green",   # 5 Nov: grey ate his reflective vest stripes "wonder": "light grey", "rover": "light grey",
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
    # Şef, Sena 5 Nov: the small blue infinity sign the rest of the cast wears, on his vest.
    "sef": ("giving a thumbs up with one hand and holding the checklist tablet firmly in the other "
            "yellow hand, the hand clearly visible gripping the tablet's edge; keep his "
            "yellow minifigure head, blue hard hat, blue work vest and blue trousers exactly; "
            "the only change: a small light-blue infinity sign printed on the left chest of the "
            "vest",
            ["tablet"]),
    "wonder": ("holding the fountain pen and the clipboard with a red seal, as in the reference",
               ["pen", "clipboard"]),
    "rover": ("with the gadget backpack on and holding the checklist paper, as in the reference",
              ["backpack", "paper"]),
    "glimmer": ("holding the small glowing crystal orb in her hand, as in the reference",
                ["glowing orb", "crystal ball", "hand"]),
    # Iris, Sena 5 Nov: a proper bag (the first one was an open, hollow frame).
    "iris": ("holding the paint palette and paintbrush, exactly as in the first reference: the "
             "same face, hair with the pencil, cream jumper with the pink infinity sign, beige "
             "trousers, white trainers and the same closed brown leather satchel with its flap "
             "and buckle; the only addition, from the second reference: a small pink "
             "five-petal flower charm clearly hanging from the satchel's buckle, easy to see",
             ["paint palette", "paintbrush", "bag"]),
    # Ada, Sena 31 Oct: the blue infinity sign on her hoodie like the rest of the cast, and
    # an open dark grey laptop like Sam's tablet (the earlier pink one with stickers was wrong),
    # its screen turned to her, the same infinity sign on the back of the lid.
    "ada": ("waving with one hand and holding an open dark grey laptop in the other, the "
            "laptop the same dark grey and style as the tablet of the second reference "
            "character; the screen faces HER, not the camera: we see the plain back of the "
            "lid, no screen, no code visible to us, no stickers, no pink; in the middle of "
            "the lid's back the same blue infinity sign as on her hoodie, as a small glossy "
            "emblem; on the chest "
            "of her plain mint-green hoodie the small blue infinity sign, exactly like the "
            "one on the second reference character's hoodie; no robot, no other props",
            ["laptop", "hand"]),
}

# SAM found no mask for Sam's tablet or Voice's microphone under any word we tried. For these
# two, whatever stands out from the flat backdrop and touches SAM's figure is kept too.
KEY = {"sam", "voice", "sef", "iris"}

PROMPT = (
    "The same character as in the reference images, exactly the same design: same face, hair, "
    "outfit, colours, accessories, proportions and the same glossy plastic toy minifigure "
    "material and finish. Full body, head to feet, centred, facing the camera, {hold}. "
    "Filling most of the frame with a small margin all around. Plain flat {bg} "
    "background, one even colour, no gradient, no floor, no shadow on the background, no "
    "props behind, no text, no labels, no other characters. Sharp, high detail, soft "
    "even studio light.")


def _jpeg(path, width=1024):
    im = Image.open(path)
    if im.mode == "RGBA":   # a cut-out portrait: flatten on light grey, not black
        flat = Image.new("RGB", im.size, (214, 214, 214))
        flat.paste(im, mask=im.getchannel("A"))
        im = flat
    im = im.convert("RGB")
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
    if name == "ada":   # her current look first, Sam for the logo and the device
        refs = [OUT / "ada-v2.png", OUT / "ada-v1.png", OUT / "sam.png"]
    if name in REDRAW:   # its own portrait only (with Sam as a second reference Şef became Sam)
        refs = REDRAW[name]
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
    if SAVE_SIZE:
        im.resize(SAVE_SIZE, Image.LANCZOS).save(dst)
    else:
        im.crop(im.getbbox()).save(dst)
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
