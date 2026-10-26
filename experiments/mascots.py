"""Draft the mascot cast with Muse Image (fan-made characters, not official Meta mascots).

Usage: .venv/bin/python experiments/mascots.py [character ...]   (default: all)
Writes experiments/mascots/<character>-<n>.png
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import client  # noqa: E402

OUT = Path(__file__).parent / "mascots"
DRAFTS = 3

STYLE = (
    "Friendly mascot character, glossy 3D vinyl-toy style, soft rounded shapes, cheerful, "
    "cool blue and violet palette with small warm accents, full body, three-quarter view, "
    "standing on a plain light grey background, soft studio light. No text, no letters, "
    "no logos."
)

CAST = {
    "spark": "Spark, the reader: a small bright character with round glasses and hair made "
             "of little electric sparks, holding a clipboard with a delivery note, looking "
             "closely at it, one eyebrow raised as if spotting a suspicious line.",
    "sam": "SAM, the counter: a compact robot-like character whose single big eye is a "
           "camera lens, drawing glowing coloured outlines around three small cardboard boxes "
           "with a pointer finger, focused and precise.",
    "kapi": "Kapi, the gatekeeper: a sturdy character made from a brown cardboard shipping "
            "box with packing tape, wearing a little guard cap, one arm is a striped red and "
            "white barrier boom, a small traffic light on its chest glowing green.",
    "glimmer": "Glimmer, the second reader: a tiny glowing firefly-like character, apprentice "
               "of a reader, carrying a small magnifying glass, shimmering softly.",
    "voice": "Voice, the listener: a round character wearing big over-ear headphones, a "
             "speech bubble with sound waves floating next to it, attentive and kind.",
    "sef": "The warehouse supervisor: a calm human character in a high-visibility vest and "
           "hard hat, simple stylised face, holding a tablet, giving a thumbs up.",
}


def main(names):
    OUT.mkdir(exist_ok=True)
    for name in names:
        resp = client().images.generate(
            model="muse-image-1.0", prompt=f"{CAST[name]} {STYLE}", n=DRAFTS,
            size="1024x1024", response_format="b64_json", output_format="png",
        )
        for k, item in enumerate(resp.data, 1):
            (OUT / f"{name}-{k}.png").write_bytes(base64.b64decode(item.b64_json))
        print(name, len(resp.data))


if __name__ == "__main__":
    main(sys.argv[1:] or list(CAST))
