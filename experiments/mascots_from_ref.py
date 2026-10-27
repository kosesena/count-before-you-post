"""Recreate a reference image of the cast with Muse Image (images.edit).

Usage: .venv/bin/python experiments/mascots_from_ref.py <reference.png> <name> [n]
Writes experiments/mascots/ref-<name>-<k>.png

The references are character sheets Sena drew with another image model; they stay
outside this repository. Muse Image redraws them so the cast in the project is its own.
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import client  # noqa: E402

OUT = Path(__file__).parent / "mascots"

PROMPT = (
    "Recreate this image faithfully as a new high-quality render: the same characters, "
    "poses, outfits, colours, lighting, composition and text labels. Glossy plastic toy "
    "minifigure style, cinematic studio light."
)


def main(ref, name, n=1):
    OUT.mkdir(exist_ok=True)
    with open(ref, "rb") as image:
        resp = client().images.edit(model="muse-image-1.0", prompt=PROMPT, image=image,
                                    n=n, output_format="png")
    for k, item in enumerate(resp.data, 1):
        (OUT / f"ref-{name}-{k}.png").write_bytes(base64.b64decode(item.b64_json))
    print(name, len(resp.data))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
