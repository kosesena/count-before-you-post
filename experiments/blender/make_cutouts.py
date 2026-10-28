"""Cut mascots out of their plain backgrounds for the warehouse standees.

Usage: .venv/bin/python experiments/blender/make_cutouts.py
Writes experiments/blender/cutouts/kapi-gec.png (green), kapi-dur.png (red), sef.png,
spark.png, sam.png, voice.png and wonder.png.

The Kapı/Şef photos have a flat light-grey studio background, so a plain flood fill
from the corners is enough. The hello/<name>.jpg portraits have a coloured studio
backdrop with a gradient/vignette: a plain flood either leaves background behind
(the gradient drifts further than the threshold) or eats into the figure (Spark's
orange hair and skin are close to the orange backdrop). For those, the corner flood
only marks sure-background pixels; a smooth background surface is then interpolated
from them on a coarse grid, and pixels close to that local surface become
transparent. Interior holes are filled back. PIL only, no extra packages.
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / "cutouts"
SOURCES = {"kapi-gec": "assets/mascots/kapi.jpg", "kapi-dur": "assets/mascots/kapi-dur.jpg",
           "sef": "assets/mascots/sef.jpg"}
HELLO = {"spark": 16, "sam": 16, "voice": 20, "wonder": 12}
MARKER = (255, 0, 255)


def edge_seeds(w, h):
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for i in range(1, 8):
        t = i / 8
        seeds += [(int(w * t), 0), (int(w * t), h - 1), (0, int(h * t)),
                  (w - 1, int(h * t))]
    return seeds


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


def cut_gradient(src: Path, tol: int) -> Image.Image:
    """Cut-out for the coloured-gradient hello/ portraits (see module docstring)."""
    im = Image.open(src).convert("RGB")
    w, h = im.size
    work = im.copy()
    seeds = edge_seeds(w, h)
    for seed in seeds:
        ImageDraw.floodfill(work, seed, MARKER, thresh=28)
    px, ipx = work.load(), im.load()
    # Coarse grid of mean sure-background colours; empty cells are filled by
    # diffusion from their neighbours, then upscaled to a smooth bg estimate.
    n = 48
    cw, ch = w / n, h / n
    acc = [[[0, 0, 0, 0] for _ in range(n)] for _ in range(n)]
    for y in range(0, h, 4):
        gy = min(n - 1, int(y / ch))
        for x in range(0, w, 4):
            if px[x, y] == MARKER:
                a = acc[gy][min(n - 1, int(x / cw))]
                c = ipx[x, y]
                a[0] += c[0]
                a[1] += c[1]
                a[2] += c[2]
                a[3] += 1
    small = Image.new("RGB", (n, n), (0, 0, 0))
    spx = small.load()
    empty = [[True] * n for _ in range(n)]
    for gy in range(n):
        for gx in range(n):
            a = acc[gy][gx]
            if a[3]:
                spx[gx, gy] = (a[0] // a[3], a[1] // a[3], a[2] // a[3])
                empty[gy][gx] = False
    for _ in range(n * 3):
        changed = False
        for gy in range(n):
            for gx in range(n):
                if not empty[gy][gx]:
                    continue
                tot, cnt = [0, 0, 0], 0
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = gy + dy, gx + dx
                    if 0 <= ny < n and 0 <= nx < n and not empty[ny][nx]:
                        c = spx[nx, ny]
                        tot[0] += c[0]
                        tot[1] += c[1]
                        tot[2] += c[2]
                        cnt += 1
                if cnt:
                    spx[gx, gy] = (tot[0] // cnt, tot[1] // cnt, tot[2] // cnt)
                    changed = True
        for gy in range(n):
            for gx in range(n):
                if empty[gy][gx] and spx[gx, gy] != (0, 0, 0):
                    empty[gy][gx] = False
        if not changed:
            break
    bg_est = small.resize((w, h), Image.BICUBIC)
    d = ImageChops.difference(im, bg_est)
    m = ImageChops.lighter(ImageChops.lighter(d.getchannel("R"), d.getchannel("G")),
                           d.getchannel("B"))
    bgmask = m.point([255 if v <= tol else 0 for v in range(256)])
    fg = bgmask.point([255 if v == 0 else 0 for v in range(256)])
    # Background not connected to the border is a hole inside the figure: fill it.
    f2 = fg.copy()
    for seed in seeds:
        if f2.getpixel(seed) == 0:
            ImageDraw.floodfill(f2, seed, 128, thresh=10)
    holes = f2.point([255 if v == 0 else 0 for v in range(256)])
    fg = ImageChops.lighter(fg, holes)
    im.putalpha(fg)
    return im.crop(fg.getbbox())


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, src in SOURCES.items():
        cut(REPO / src).save(OUT / f"{name}.png")
        print(name)
    for name, tol in HELLO.items():
        cut_gradient(REPO / f"assets/mascots/hello/{name}.jpg", tol).save(
            OUT / f"{name}.png")
        print(name)
