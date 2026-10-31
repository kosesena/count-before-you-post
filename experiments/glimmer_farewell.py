"""Glimmer's farewell for the end of the home page: a 3D Glimmer that winks and waves.

Usage: .venv/bin/python experiments/glimmer_farewell.py draw     # Muse Image: Glimmer winking, A-pose
       .venv/bin/python experiments/glimmer_farewell.py green    # Muse Image: Glimmer on chroma green (video start frame)
       .venv/bin/python experiments/glimmer_farewell.py wink     # Muse Image: the Genjutsu clip's last frame, one eye winking
       .venv/bin/python experiments/glimmer_farewell.py model    # Meshy: image to 3D (textured GLB)
       .venv/bin/python experiments/glimmer_farewell.py rig      # Meshy: rig the model
       .venv/bin/python experiments/glimmer_farewell.py wave     # Meshy: wave animation on the rig
Writes experiments/glimmer-farewell/: glimmer-wink.png, model.glb, rigged.glb, wave.glb and
tasks.json (the Meshy task ids, so a step can be re-polled without paying twice).
"""
import base64
import io
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "glimmer-farewell"
TASKS = OUT / "tasks.json"
MESHY = "https://api.meshy.ai/openapi/v1"
WAVE = 290   # Meshy animation library: Wave_One_Hand

PROMPT = (
    "The same toy figure as in the image, exactly the same design: the same face, long wavy "
    "lavender hair, lavender hoodie with the blue infinity sign, light grey trousers, lavender "
    "shoes, the glowing purple orb. Full body, standing straight and facing the camera, arms "
    "slightly away from the body (A-pose), the orb resting in her left hand. She is winking: "
    "her right eye closed in a playful wink, her left eye open, a happy smile. Plain flat light "
    "grey background, soft even studio light, no shadow on the background, no text.")


def _jpeg(path, width=1024):
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return buf.getvalue()


def _tasks():
    return json.loads(TASKS.read_text()) if TASKS.exists() else {}


def _save_task(step, task_id):
    t = _tasks()
    t[step] = task_id
    TASKS.write_text(json.dumps(t, indent=1))


def _meshy(method, path, body=None):
    req = urllib.request.Request(
        MESHY + path, method=method, data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {os.environ['MESHY_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def _wait(path):
    while True:
        t = _meshy("GET", path)
        print(path, t["status"], t.get("progress"), flush=True)
        if t["status"] == "SUCCEEDED":
            return t
        if t["status"] in ("FAILED", "CANCELED"):
            sys.exit(f"{path}: {t['status']} {t.get('task_error')}")
        time.sleep(15)


def _fetch(url, dst):
    with urllib.request.urlopen(url, timeout=300) as r:
        dst.write_bytes(r.read())
    print("saved", dst, dst.stat().st_size, flush=True)


def draw():
    dst = OUT / "glimmer-wink.png"
    ref = HERE / "mockups" / "cast-for-chatgpt" / "Glimmer.jpg"
    body = {"model": "muse-image-1.0", "n": 1, "size": "1024x1536", "output_format": "png",
            "response_format": "b64_json", "prompt": PROMPT,
            "images": [{"image_url": "data:image/jpeg;base64," + base64.b64encode(_jpeg(ref)).decode()}]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print("drawn", dst, Image.open(dst).size)


GREEN = (
    "The same toy figure as in the image, exactly the same design: the same face, long wavy "
    "lavender hair, lavender hoodie with the blue infinity sign, light grey trousers, lavender "
    "shoes, the glowing purple orb resting in her left hand. Full body, standing and facing the "
    "camera, both eyes open, a gentle smile, the figure centred with space around it. The "
    "background is one flat pure chroma-key green (#00B140), evenly lit, no shadow, no floor, "
    "no gradient, no text; no green anywhere on the figure.")


def green():
    dst = OUT / "glimmer-green.png"
    ref = HERE / "mockups" / "cast-for-chatgpt" / "Glimmer.jpg"
    body = {"model": "muse-image-1.0", "n": 1, "size": "1024x1536", "output_format": "png",
            "response_format": "b64_json", "prompt": GREEN,
            "images": [{"image_url": "data:image/jpeg;base64," + base64.b64encode(_jpeg(ref)).decode()}]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print("drawn", dst, Image.open(dst).size)


WINK = (
    "Exactly the same image: the same toy figure, the same pose, the same raised hand, the same "
    "orb, the same framing, the same flat green background and light. Change only her face: "
    "she winks, her right eye closed in a playful wink, her left eye open, a happy smile.")


def wink():
    src, dst = OUT / "genjutsu-last.png", OUT / "genjutsu-wink.png"
    w, h = Image.open(src).size
    body = {"model": "muse-image-1.0", "n": 1, "size": f"{w}x{h}", "output_format": "png",
            "response_format": "b64_json", "prompt": WINK,
            "images": [{"image_url": "data:image/jpeg;base64," + base64.b64encode(_jpeg(src, width=w)).decode()}]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print("drawn", dst, Image.open(dst).size)


def model():
    t = _tasks()
    if "model" not in t:
        img = OUT / "glimmer-wink.png"
        uri = "data:image/png;base64," + base64.b64encode(img.read_bytes()).decode()
        r = _meshy("POST", "/image-to-3d", {"image_url": uri, "should_texture": True, "enable_pbr": False,
                                             "should_remesh": True, "target_polycount": 60000,
                                             "pose_mode": "a-pose", "target_formats": ["glb"]})
        _save_task("model", r["result"])
    done = _wait("/image-to-3d/" + _tasks()["model"])
    _fetch(done["model_urls"]["glb"], OUT / "model.glb")


def rig():
    if "rig" not in _tasks():
        r = _meshy("POST", "/rigging", {"input_task_id": _tasks()["model"], "height_meters": 1.0})
        _save_task("rig", r["result"])
    done = _wait("/rigging/" + _tasks()["rig"])
    _fetch(done["result"]["rigged_character_glb_url"], OUT / "rigged.glb")


def wave():
    if "wave" not in _tasks():
        r = _meshy("POST", "/animations", {"rig_task_id": _tasks()["rig"], "action_id": WAVE})
        _save_task("wave", r["result"])
    done = _wait("/animations/" + _tasks()["wave"])
    _fetch(done["result"]["animation_glb_url"], OUT / "wave.glb")


if __name__ == "__main__":
    _load_env()
    OUT.mkdir(parents=True, exist_ok=True)
    {"draw": draw, "green": green, "wink": wink, "model": model, "rig": rig, "wave": wave}[sys.argv[1]]()
