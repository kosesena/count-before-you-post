"""Design a new cast member with Muse Image, using only Muse-drawn images as style references.

Usage: .venv/bin/python experiments/mascot_design.py <name> [n]
Writes experiments/mascots/design-<name>-<k>.png
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "mascots"
# Both references were drawn by Muse Image (mascots_from_ref.py).
STYLE_REFS = [OUT / "ref-cast-1.png", OUT / "ref-muse-1.png"]

DESIGNS = {
    "muse-code": (
        "Design a new character for this same cast, in exactly the same glossy plastic toy "
        "minifigure style, lighting and soft pastel background as the reference images. "
        "Muse Code, the coding agent: a focused, friendly minifigure with short teal hair and "
        "round glasses, a dark green hoodie printed with a small '</>' symbol, grey trousers, "
        "sitting cross-legged on a toy-brick seat with an open laptop whose screen shows a "
        "terminal with green code lines and a passing test checkmark. Floating glowing panels "
        "around: a code bracket icon, a terminal prompt icon, a checklist with green ticks. A "
        "small toy robot buddy sits next to the laptop. Full body, centred, the label "
        "'Muse Code' in a clean dark sans-serif font under the figure. No company logos."
    ),
}


def main(name, n=1):
    # The JSON form of /images/edits takes several reference images; the SDK's multipart
    # form sends them under a key the API rejects.
    _load_env()
    images = [{"image_url": "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()}
              for p in STYLE_REFS]
    body = {"model": "muse-image-1.0", "prompt": DESIGNS[name], "images": images, "n": n,
            "output_format": "png", "response_format": "b64_json"}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        data = json.loads(r.read())["data"]
    for k, item in enumerate(data, 1):
        (OUT / f"design-{name}-{k}.png").write_bytes(base64.b64decode(item["b64_json"]))
    print(name, len(data))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
