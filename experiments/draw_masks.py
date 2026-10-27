"""Paint SAM 3.1's masks on the ceiling camera: sure cartons green, doubtful ones amber.

Usage: .venv/bin/python experiments/draw_masks.py [variant ...]
Caches SAM's raw output in experiments/results/sam_raw/<variant>.txt (delete to re-query),
writes experiments/blender/out/annotated/depo-<variant>-masks.jpg and depo-masks.jpg (grid).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.gate import MIN_CONF, SURE  # noqa: E402
from cbyp.sam import segment_image, segments  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from paths import OUT, RAW, RES  # noqa: E402
ANN = OUT / "annotated"
SURE_RGB, DOUBT_RGB = (46, 204, 113), (243, 156, 18)


def raw_output(variant):
    RAW.mkdir(parents=True, exist_ok=True)
    cache = RAW / f"{variant}.txt"
    if not cache.exists():
        cache.write_text(segment_image(OUT / f"depo-{variant}-kamera.png", "cardboard box"))
    return cache.read_text()


def paint(variant):
    img = Image.open(OUT / f"depo-{variant}-kamera.png").convert("RGB")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=22)
    sure = doubtful = 0
    for s in segments(raw_output(variant)):
        c = s.conf or 0
        if c < MIN_CONF:
            continue
        rgb = SURE_RGB if c >= SURE else DOUBT_RGB
        sure, doubtful = sure + (c >= SURE), doubtful + (c < SURE)
        w, h = s.right - s.left, s.bottom - s.top
        mask = Image.frombytes("L", (w, h), bytes(255 * v for v in s.raster))
        overlay.paste(Image.new("RGBA", (w, h), rgb + (110,)), (s.left, s.top), mask)
        draw.text((s.left + 6, s.top + 4), f"{c:.2f}", fill=rgb, font=font,
                  stroke_width=3, stroke_fill="black")
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    ImageDraw.Draw(img).text((20, 16), f"{variant}: {sure} sure, {doubtful} doubtful",
                             fill="white", font=ImageFont.load_default(size=34),
                             stroke_width=4, stroke_fill="black")
    img.save(ANN / f"depo-{variant}-masks.jpg", quality=85)
    return img, sure, doubtful


def main(variants):
    truth = json.loads((OUT / "depo-truth.json").read_text())
    (OUT / "annotated").mkdir(exist_ok=True)
    tiles = []
    for v in variants or list(truth):
        img, sure, doubtful = paint(v)
        tiles.append(img.resize((800, int(800 * img.height / img.width))))
        print(v, sure, doubtful)
    w, h = tiles[0].size
    grid = Image.new("RGB", (w * 3, h * ((len(tiles) + 2) // 3)), "white")
    for i, t in enumerate(tiles):
        grid.paste(t, ((i % 3) * w, (i // 3) * h))
    grid.save(OUT / "depo-masks.jpg", quality=82)


if __name__ == "__main__":
    main(sys.argv[1:])
