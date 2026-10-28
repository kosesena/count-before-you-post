"""Close-up angle references of one character with Muse Image, for animation consistency.

Usage: .venv/bin/python experiments/mascot_angles.py <character> [angle ...]
Writes assets/mascots/angles/<character>/<angle>.png, one call per angle, skipping done ones.
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402
from experiments.mascot_design import jpeg  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MASCOTS = ROOT / "assets" / "mascots"

ANGLES = {
    "front": "seen straight from the front, facing the camera",
    "three-quarter-left": "turned three-quarters to the left (we see the front and its right side)",
    "profile-left": "in full side profile facing left",
    "back": "seen straight from behind, the back of the head and the back of the outfit",
    "three-quarter-right": "turned three-quarters to the right (we see the front and its left side)",
    "profile-right": "in full side profile facing right",
    "face-close": "a close-up of the head and shoulders, facing the camera, a friendly smile",
    "high-angle": "seen from slightly above at three-quarters, looking up at the camera",
}

PROMPT = (
    "Character reference for animation: the same minifigure-style toy character as in the "
    "reference images, exactly the same design: same hair shape and colour, same face, same "
    "outfit, same colours, same proportions and the same glossy plastic toy material. "
    "{angle}. Standing in a neutral relaxed pose, arms down, hands empty, full body in frame "
    "unless it is a close-up. Plain light {bg} studio background, soft even light, no text, "
    "no labels, no other characters, sharp detail.")

BG = {"spark": "orange", "sam": "soft blue", "voice": "teal", "wonder": "cream",
      "ada": "pink", "iris": "peach", "glimmer": "lavender", "kapi": "green", "sef": "grey"}


def main(name, angles):
    _load_env()
    refs = [MASCOTS / "hello" / f"{name}.jpg"]
    sheet = MASCOTS / "sheets" / f"{name}.jpg"
    if sheet.exists():
        refs.append(sheet)
    images = [{"image_url": "data:image/jpeg;base64," + base64.b64encode(jpeg(p)).decode()}
              for p in refs]
    out = MASCOTS / "angles" / name
    out.mkdir(parents=True, exist_ok=True)
    for angle in angles:
        dst = out / f"{angle}.png"
        if dst.exists():
            continue
        body = {"model": "muse-image-1.0", "images": images, "n": 1, "size": "1024x1024",
                "prompt": PROMPT.format(angle=ANGLES[angle].capitalize(), bg=BG.get(name, "grey")),
                "output_format": "png", "response_format": "b64_json"}
        req = urllib.request.Request(
            BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
            headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
            dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
        print(name, angle, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or list(ANGLES))
