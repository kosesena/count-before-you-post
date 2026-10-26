"""Count objects in a stock video with SAM 3.1 tracking.

Usage: .venv/bin/python experiments/count_video.py <video> <axis x|y> <line 0-1> <concept> [...]
  e.g. count_video.py experiments/videos/conveyor-5903898.mp4 x 0.5 "cardboard box" "package"

Three counts per concept:
  ids       every distinct track id
  solid     ids seen in >= MIN_FRAMES frames with max confidence >= MIN_CONF
  crossed   solid ids whose box centre crosses the counting line (what a dock camera
            would count: things that pass, not things parked in the background)
Raw SAM output and an annotated video go to experiments/frames/ (not committed);
the summary is appended to experiments/results/count_video.json.
"""
import json
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.sam import parse, segment_video, upload  # noqa: E402

HERE = Path(__file__).parent
MIN_FRAMES, MIN_CONF = 5, 0.7


def counts(dets, axis, line, size):
    tracks = defaultdict(list)
    for d in dets:
        tracks[d.obj].append(d)
    limit = line * (size[0] if axis == "x" else size[1])
    solid, crossed = [], []
    for obj, ds in tracks.items():
        if len(ds) < MIN_FRAMES or max(d.conf or 0 for d in ds) < MIN_CONF:
            continue
        solid.append(obj)
        pos = [d.center[0 if axis == "x" else 1] for d in sorted(ds, key=lambda d: d.frame)]
        if min(pos) < limit < max(pos):
            crossed.append(obj)
    return tracks, sorted(solid), sorted(crossed)


def annotate(video, dets, crossed, axis, line, out):
    frames_dir = out.with_suffix("")
    frames_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video),
                    str(frames_dir / "%05d.png")], check=True)
    by_frame = defaultdict(list)
    for d in dets:
        by_frame[d.frame].append(d)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    k = 0 if axis == "x" else 1
    pngs = sorted(frames_dir.glob("*.png"))
    limit = line * Image.open(pngs[0]).size[k]
    # Frame at which each counted track first lands on the other side of the line.
    crossing = {}
    for obj in crossed:
        ds = sorted((d for d in dets if d.obj == obj), key=lambda d: d.frame)
        side = ds[0].center[k] < limit
        crossing[obj] = next(d.frame for d in ds if (d.center[k] < limit) != side)
    for i, png in enumerate(pngs):
        img = Image.open(png).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size
        draw.line((limit, 0, limit, h) if axis == "x" else (0, limit, w, limit),
                  fill=(255, 220, 0), width=3)
        for d in by_frame.get(i, []):
            color = (0, 200, 80) if d.obj in crossed else (230, 60, 60)
            draw.rectangle((d.x1, d.y1, d.x2, d.y2), outline=color, width=3)
            draw.text((d.x1 + 4, d.y1 + 2), f"#{d.obj}", font=font, fill=color)
        n = sum(f <= i for f in crossing.values())
        draw.rectangle((0, 0, 260, 40), fill=(0, 0, 0))
        draw.text((10, 8), f"counted: {n}", font=font, fill=(255, 255, 255))
        img.save(png)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", "25", "-i",
                    str(frames_dir / "%05d.png"), "-pix_fmt", "yuv420p", str(out)], check=True)


def main(video, axis, line, concepts):
    video, line = Path(video), float(line)
    file_id = upload(video)
    results = []
    for concept in concepts:
        start = time.perf_counter()
        raw = segment_video(file_id, concept)
        seconds = time.perf_counter() - start
        dets = parse(raw)
        stem = f"{video.stem}-{concept.replace(' ', '_')}"
        (HERE / "frames" / f"{stem}.txt").write_text(raw)
        tracks, solid, crossed = counts(dets, axis, line, _frame_size(video))
        frames = len({d.frame for d in dets})
        row = {"video": video.name, "concept": concept, "seconds": round(seconds, 1),
               "frames_with_hits": frames, "ids": len(tracks), "solid": len(solid),
               "crossed": len(crossed), "crossed_ids": crossed}
        results.append(row)
        print(json.dumps(row))
        annotate(video, dets, set(crossed), axis, line, HERE / "frames" / f"{stem}.mp4")
    out = HERE / "results" / "count_video.json"
    prev = json.loads(out.read_text()) if out.exists() else []
    out.write_text(json.dumps(prev + results, indent=2))


def _frame_size(video):
    png = HERE / "frames" / f"{video.stem}-first.png"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-frames:v", "1",
                    str(png)], check=True)
    with Image.open(png) as im:
        return im.size


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
