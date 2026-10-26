"""Cut the Kapı mascot out of its plain background for the warehouse standee.

Usage: .venv/bin/python experiments/blender/make_cutouts.py
Writes experiments/blender/cutouts/kapi-gec.png (green) and kapi-dur.png (red).
"""
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "cutouts"
SOURCES = {"kapi-gec": "assets/mascots/kapi.jpg", "kapi-dur": "assets/mascots/kapi-dur.jpg"}
MARKER = (255, 0, 255)


def cut(src: Path) -> Image.Image:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    work = im.copy()
    # Flood the light-grey studio background from the corners and the top edge.
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0)):
        ImageDraw.floodfill(work, seed, MARKER, thresh=28)
    alpha = Image.new("L", (w, h), 255)
    px, ap = work.load(), alpha.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == MARKER:
                ap[x, y] = 0
    im.putalpha(alpha)
    return im.crop(alpha.getbbox())


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, src in SOURCES.items():
        cut(REPO / src).save(OUT / f"{name}.png")
        print(name)
