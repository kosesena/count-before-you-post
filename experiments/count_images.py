"""Count boxes in rendered scenes with SAM 3.1 and compare with the known truth.

Usage: .venv/bin/python experiments/count_images.py <dir with truth.json> [concept ...]
Writes annotated images to <dir>/annotated/ and appends to experiments/results/count_images.json.
"""
import json
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.sam import parse, segment_image  # noqa: E402

HERE = Path(__file__).parent
MIN_CONF = 0.7


def main(folder, concepts):
    folder = Path(folder)
    truth = json.loads((folder / "truth.json").read_text())
    (folder / "annotated").mkdir(exist_ok=True)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 18)
    rows = []
    for name, t in truth.items():
        for concept in concepts:
            start = time.perf_counter()
            dets = parse(segment_image(folder / f"{name}.png", concept))
            seconds = time.perf_counter() - start
            sure = [d for d in dets if (d.conf or 0) >= MIN_CONF]
            row = {"scene": name, "concept": concept, "truth": t["boxes_on_belt"],
                   "all": len(dets), "conf>=0.7": len(sure), "seconds": round(seconds, 1)}
            rows.append(row)
            print(json.dumps(row))
            img = Image.open(folder / f"{name}.png").convert("RGB")
            draw = ImageDraw.Draw(img)
            for d in dets:
                color = (0, 200, 80) if (d.conf or 0) >= MIN_CONF else (255, 140, 0)
                draw.rectangle((d.x1, d.y1, d.x2, d.y2), outline=color, width=3)
                draw.text((d.x1 + 3, d.y1 + 2), f"{d.conf:.2f}", font=font, fill=color)
            draw.rectangle((0, 0, 560, 34), fill=(0, 0, 0))
            draw.text((10, 7), f"{concept}: SAM {len(sure)} (>=0.7) / truth {t['boxes_on_belt']}",
                      font=font, fill=(255, 255, 255))
            img.save(folder / "annotated" / f"{name}-{concept.replace(' ', '_')}.jpg", quality=88)
    out = HERE / "results" / "count_images.json"
    prev = json.loads(out.read_text()) if out.exists() else []
    out.write_text(json.dumps(prev + rows, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or ["cardboard box", "box"])
