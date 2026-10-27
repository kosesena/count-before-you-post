"""Design a new cast member with Muse Image, using only Muse-drawn images as style references.

Usage: .venv/bin/python experiments/mascot_design.py <name> [n]
Writes experiments/mascots/design-<name>-<k>.png
Names: muse-code, cast-8, and hello-<character> (each character introducing themself, for the site).
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
# Every reference here was itself drawn by Muse Image.
STYLE_REFS = [OUT / "ref-cast-1.png", OUT / "ref-muse-1.png"]
REFS = {
    "cast-8": [OUT / "ref-cast-1.png", OUT / "ref-kapi-sef-1.png", OUT / "ref-muse-1.png",
               OUT / "design-muse-code-2.png"],
}

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
    "cast-8": (
        "Group shot of the whole cast, all eight characters exactly as they look in the "
        "reference images, same glossy plastic toy minifigure style and soft studio lighting "
        "as the first image. Left to right on a long table, each on its own coloured toy-brick "
        "pedestal with its name and a short tagline printed on the front: "
        "Spark (orange, 'READS THE NOTE'), Sam (blue, 'COUNTS THE CARTONS'), "
        "Glimmer (lavender, 'SECOND READING'), Voice (navy, 'HEARS THE RECEIVER'), "
        "Kapı (brown cardboard body, guard cap, traffic light, barrier pole, 'GUARDS THE ERP'), "
        "Şef (yellow head, blue hard hat, safety vest, tablet, 'APPROVES'), "
        "Muse (brown curly hair, cream sweater, pen and tablet, with the cat, 'DRAWS THE CAST'), "
        "Muse Code (teal hair, glasses, green hoodie, laptop, small robot, 'WRITES THE CODE'). "
        "Keep the Turkish letters in 'Kapı' and 'Şef' exactly. Wide cinematic composition, "
        "warm-to-cool gradient background, every name clearly legible."
    ),
}


CAST = OUT / "design-cast-8-2.png"
# Each character alone, saying hello, doing their job in this project. No text in the image:
# the site prints what they say next to the picture.
HELLO = {
    "spark": (OUT / "ref-spark-1.png", "orange",
              "Spark: spiky orange hair, orange hoodie. Waves with one hand and holds up a paper "
              "delivery note with a small table of items in the other, a little lightning spark "
              "glowing above the hand."),
    "sam": (OUT / "ref-sam-1.png", "soft blue",
            "Sam: dark curly hair, blue jacket. Waves with one hand and holds a tablet in the "
            "other whose screen shows a grid of brown cartons, each outlined in a different "
            "bright colour, like segmentation masks."),
    "glimmer": (OUT / "ref-glimmer-1.png", "lavender",
                "Glimmer: long lavender hair, lavender outfit. Waves with one hand and holds a "
                "glowing crystal orb in the other, a paper note floating behind the orb as if "
                "read a second time."),
    "voice": (OUT / "ref-voice-1.png", "navy blue",
              "Voice: black hair with blue streaks, headphones, black hoodie. Waves with one "
              "hand and holds a small microphone in the other, soft blue sound waves around it."),
    "kapi": (OUT / "ref-kapi-sef-1.png", "warm beige",
             "Kapı: the cardboard-box guard with the blue guard cap and the traffic light on the "
             "chest showing green. Waves with one purple hand and holds the red-and-white "
             "barrier pole upright in the other."),
    "sef": (OUT / "ref-kapi-sef-1.png", "bright blue",
            "Şef: the supervisor with the yellow head, blue hard hat and safety vest. Gives a "
            "thumbs up with one hand and holds a tablet with a ticked checklist in the other."),
    "muse": (OUT / "ref-muse-1.png", "pastel pink",
             "Muse: long curly brown hair with a pencil in it, cream sweater, brown satchel. "
             "Waves with one hand and holds a glowing drawing pen in the other, the little cat "
             "sitting at her feet."),
    "muse-code": (OUT / "design-muse-code-2.png", "slate blue",
                  "Muse Code: short teal hair, round glasses, dark green hoodie. Stands, waves "
                  "with one hand and holds an open laptop with green terminal lines in the "
                  "other, the small toy robot buddy standing next to the feet."),
}
for _name, (_ref, _colour, _who) in HELLO.items():
    REFS[f"hello-{_name}"] = [_ref, CAST]
    DESIGNS[f"hello-{_name}"] = (
        f"Solo portrait of one character from the reference images, exactly the same design, "
        f"colours and glossy plastic toy minifigure style. {_who} Standing alone, full body, "
        f"centred, facing the viewer with a warm smile as if introducing themself. Plain soft "
        f"{_colour} studio background with a gentle gradient. Only this one character. "
        f"No text, no letters, no labels, no name plate.")


def main(name, n=1):
    # The JSON form of /images/edits takes several reference images; the SDK's multipart
    # form sends them under a key the API rejects.
    _load_env()
    images = [{"image_url": "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()}
              for p in REFS.get(name, STYLE_REFS)]
    body = {"model": "muse-image-1.0", "prompt": DESIGNS[name], "images": images, "n": n,
            "size": "1024x1024" if name.startswith("hello-") else "1792x1024",
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
