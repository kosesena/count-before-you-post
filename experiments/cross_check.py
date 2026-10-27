"""SAM and Spark agree carton by carton on the six dock cases.

Usage: .venv/bin/python experiments/cross_check.py [variant ...]
Needs SAM's concept output from draw_masks.py (experiments/results/sam_raw/<variant>.txt).
Caches Spark's points and SAM's point-prompt output next to it, writes
experiments/results/cross_check.json, annotated/depo-<variant>-cross.jpg and depo-cross.jpg.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.crosscheck import cross_check  # noqa: E402
from cbyp.gate import MIN_CONF  # noqa: E402
from cbyp.perception import point_cartons  # noqa: E402
from cbyp.sam import segment_points, segments  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "blender" / "out"
RAW = HERE / "results" / "sam_raw"
GREEN, RED, AMBER = (46, 204, 113), (231, 76, 60), (243, 156, 18)


def cached(path, make):
    if not path.exists():
        path.write_text(make())
    return path.read_text()


def check(v):
    cam = OUT / f"depo-{v}-kamera.png"
    concept = segments((RAW / f"{v}.txt").read_text())
    points = [tuple(p) for p in json.loads(cached(
        RAW / f"{v}-spark-points.json", lambda: json.dumps(point_cartons(cam))))]
    probes = segments(cached(RAW / f"{v}-points.txt", lambda: segment_points(cam, points)))
    r = cross_check(concept, points, probes)

    img = Image.open(cam).convert("RGB")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cartons = [s for s in concept if (s.conf or 0) >= MIN_CONF]
    agreed = {k for k, _ in r.agreed}
    for k, s in enumerate(cartons):
        rgb = GREEN if k in agreed else AMBER
        w, h = s.right - s.left, s.bottom - s.top
        mask = Image.frombytes("L", (w, h), bytes(255 * b for b in s.raster))
        overlay.paste(Image.new("RGBA", (w, h), rgb + (100,)), (s.left, s.top), mask)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)
    for x, y in points:
        bad = (x, y) in r.spark_only
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=RED if bad else "white",
                  outline="black", width=3)
    label = (f"{v}: {len(r.agreed)} agreed, {len(r.sam_only)} SAM only, "
             f"{len(r.spark_only)} Spark only" + (f", {len(r.doubled)} doubled" if r.doubled else ""))
    d.text((20, 16), label, fill="white", font=ImageFont.load_default(size=34),
           stroke_width=4, stroke_fill="black")
    img.save(OUT / "annotated" / f"depo-{v}-cross.jpg", quality=85)
    return r, len(points), img


def main(variants):
    truth = json.loads((OUT / "depo-truth.json").read_text())
    rows, tiles = [], []
    for v in variants or list(truth):
        r, n_points, img = check(v)
        rows.append({"variant": v, "cartons": truth[v]["cartons"], "spark_points": n_points,
                     "agreed": len(r.agreed), "sam_only": len(r.sam_only),
                     "spark_only": len(r.spark_only), "doubled": len(r.doubled),
                     "count": r.count})
        tiles.append(img.resize((800, int(800 * img.height / img.width))))
        print(rows[-1])
    (HERE / "results" / "cross_check.json").write_text(json.dumps(rows, indent=2))
    w, h = tiles[0].size
    grid = Image.new("RGB", (w * 3, h * ((len(tiles) + 2) // 3)), "white")
    for i, t in enumerate(tiles):
        grid.paste(t, ((i % 3) * w, (i // 3) * h))
    grid.save(OUT / "depo-cross.jpg", quality=82)


if __name__ == "__main__":
    main(sys.argv[1:])
