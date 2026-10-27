"""Draft the mascot cast with Muse Image (fan-made characters, not official Meta mascots).

Usage: .venv/bin/python experiments/mascots.py [character ...]   (default: all)
Writes experiments/mascots/v2-<character>-<n>.png (v1, the vinyl-toy cast, is in git history)
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import client  # noqa: E402

OUT = Path(__file__).parent / "mascots"
DRAFTS = 3

STYLE = (
    "Collectible plastic toy minifigure, glossy injection-moulded plastic, cylindrical head "
    "with a simple printed friendly face, blocky body and C-shaped hands, full body, dynamic "
    "three-quarter pose, standing on a small square toy-brick base, cinematic warm studio "
    "light with soft glow and bokeh, high detail product photo. No text, no letters, no "
    "logos, no brand marks on clothing."
)

# Each character wears its own symbol instead of any company logo.
CAST = {
    "spark": "Spark, the reader: energetic minifigure with spiky glossy orange hair, orange "
             "hoodie over a white shirt printed with a small yellow lightning bolt, black "
             "trousers, orange and white sneakers. Holds a paper delivery note in one hand and "
             "points at a line on it with the other, one eyebrow raised as if spotting a "
             "suspicious line. Orange and amber palette, small glowing sparks around.",
    "sam": "SAM, the counter: focused minifigure with dark curly hair, royal blue hoodie "
           "printed with a small white camera-lens circle, beige trousers. Points at three "
           "small cardboard boxes, each outlined by a glowing blue rectangle, a tiny floating "
           "number tag over each box. Blue palette.",
    "kapi": "Kapi, the gatekeeper: friendly minifigure with a classic yellow cylindrical head, "
            "rosy cheeks and a smile, a royal blue guard cap with a black visor and a gold "
            "button. Torso, arms and legs look like a brown cardboard shipping box covered in "
            "packing tape, with a small 'this side up' arrows symbol. A small traffic light "
            "is mounted on the chest, its green lamp glowing. Holds a red and white striped "
            "barrier pole in one blue hand. Blue shoes.",
    "glimmer": "Glimmer, the second reader: gentle minifigure with long glossy lavender hair, "
               "lilac sweater printed with a small magnifying-glass symbol, holding a big "
               "magnifying glass over a delivery note, soft violet glow. Purple palette.",
    "voice": "Voice, the listener: calm minifigure with a black beanie and blue-tipped dark "
             "hair, black hoodie printed with a small sound-wave symbol, big silver over-ear "
             "headphones, a glowing speech bubble with sound waves floating nearby. Black and "
             "electric blue palette.",
    "sef": "The warehouse supervisor: friendly minifigure with a classic yellow cylindrical "
           "head and a smile, royal blue hard hat, royal blue work jacket and trousers with a "
           "yellow and silver reflective safety vest, a small walkie-talkie on the belt. "
           "Gives a thumbs up with one hand and holds a tablet showing a checklist with "
           "ticks in the other. Black shoes.",
}


def main(names):
    OUT.mkdir(exist_ok=True)
    for name in names:
        resp = client().images.generate(
            model="muse-image-1.0", prompt=f"{CAST[name]} {STYLE}", n=DRAFTS,
            size="1024x1024", response_format="b64_json", output_format="png",
        )
        for k, item in enumerate(resp.data, 1):
            (OUT / f"v2-{name}-{k}.png").write_bytes(base64.b64decode(item.b64_json))
        print(name, len(resp.data))


if __name__ == "__main__":
    main(sys.argv[1:] or list(CAST))
