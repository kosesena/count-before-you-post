"""Design a new cast member with Muse Image, using only Muse-drawn images as style references.

Usage: .venv/bin/python experiments/mascot_design.py <name> [n]
Writes experiments/mascots/design-<name>-<k>.png
Names: muse-code, cast-8, and hello-<character> (each character introducing themself, for the site).
"""
import base64
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from cbyp.meta import BASE_URL, TIMEOUT, _load_env  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "mascots"
# Every reference here was itself drawn by Muse Image.
STYLE_REFS = [OUT / "ref-cast-1.png", OUT / "ref-muse-1.png"]
REFS = {
    "cast-8": [OUT / "ref-cast-1.png", OUT / "ref-kapi-sef-1.png", OUT / "ref-muse-1.png",
               OUT / "design-muse-code-2.png"],
    # The same group picture with Muse replaced by Iris (27 Oct).
    "cast-iris": [OUT / "design-cast-8-2.png", OUT / "design-hello-iris-1.png"],
    # Then Sam with camera glasses, and Muse Code's character as Ada (27 Oct).
    "hello-ada-meta": [OUT / "design-hello-ada-cute.png"],
    "hello-ada-big": [OUT / "design-hello-ada-small-laptop.png"],
    "cast-ada-big": [OUT / "design-cast-v3-chosen.png"],
    "cast-v3": [OUT / "design-cast-iris-1.png", OUT / "design-hello-sam-1.png",
                OUT / "design-hello-ada-1.png"],
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
    "hello-ada-meta": (
        "Keep this image exactly the same: the character, pose, sweater with '</>', robot, "
        "floating panels, colours and background. Only change the laptop: put one clear blue "
        "infinity-loop symbol, like the one on the other characters' shirts, in the centre "
        "of the laptop lid, among the cute stickers."
    ),
    "hello-ada-big": (
        "Keep this image exactly the same: the character, face, hair, flower, sweater, pose, "
        "robot, floating panels, colours and background. Only change the laptop: make it much "
        "bigger, a full-size laptop held open in front of her with both the screen and the "
        "lid clearly visible, about as big as her torso, like Sam's laptop in the cast. Make "
        "it pastel pink, keep the cute stickers and the blue infinity symbol on the lid, and "
        "green code with a check mark on the screen."
    ),
    "cast-ada-big": (
        "Keep this image exactly the same: every character, pose, pedestal, name, colour, "
        "light and the background. Only change Ada, the last character on the right: her "
        "laptop becomes much bigger, a full-size open laptop about as big as her torso like "
        "Sam's laptop, pastel pink, with cute stickers and a blue infinity symbol on the lid "
        "and green code on the screen. Keep the names exactly, including 'Kapı' and 'Şef'."
    ),
    "cast-v3": (
        "Recreate the first image exactly: the same eight characters, poses, pedestals, "
        "colours, lighting, background and printed names, with two changes. Sam (second from "
        "the left, blue pedestal) now wears the sleek black smart glasses with a tiny camera "
        "lens from the second image, no logos. The last character on the right is now Ada, "
        "drawn exactly as in the third image: long wavy dark brown hair with a yellow flower "
        "clip, a mint-green knit sweater with '</>', a lilac laptop with stickers and a blue "
        "infinity symbol, the tiny robot at her feet; she replaces the teal-haired figure "
        "completely; her pedestal reads "
        "'Ada' with the tagline 'WRITES THE CODE'. Keep every other name exactly: Spark, Sam, "
        "Glimmer, Voice, Kapı, Şef, Iris, with the Turkish letters in 'Kapı' and 'Şef'."
    ),
    "cast-iris": (
        "Recreate the first image exactly: the same eight characters, poses, pedestals, "
        "colours, lighting, background and printed names, with one change. The seventh "
        "character, on the pink pedestal, is now Iris, drawn exactly as in the second image: "
        "curly brown hair with a pencil, cream sweater, a paintbrush and a wooden palette with "
        "bright paint blobs, a small easel with a colourful canvas and a few paint pots beside "
        "her. Remove the cat completely. Her pedestal reads 'Iris' with the tagline "
        "'DRAWS THE CAST'. Keep every other name exactly: Spark, Sam, Glimmer, Voice, Kapı, "
        "Şef, Muse Code, with the Turkish letters in 'Kapı' and 'Şef'."
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
        "Iris (brown curly hair with a pencil, cream sweater, paintbrush and a palette of bright "
        "paints, a small easel with a canvas and paint pots at her feet, no cat, 'DRAWS THE CAST'), "
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
            "Sam: dark curly hair, blue jacket, now wearing sleek black smart glasses with a "
            "tiny camera lens at the front corner of the frame (no logos, no brand). Waves with "
            "one hand and holds a tablet in the other whose screen shows a grid of brown "
            "cartons, each outlined in a different bright colour, like segmentation masks, as "
            "if seen through the glasses."),
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
    # Iris (Muse Image's character, called Muse until 27 Oct; the cat became an easel).
    "iris": (OUT / "ref-muse-1.png", "pastel pink",
             "Iris: long curly brown hair with a pencil in it, cream sweater, brown satchel. "
             "Waves with one hand and holds a paintbrush in the other, a wooden palette with "
             "bright paint blobs hooked on her arm. Next to her a small easel with a canvas "
             "showing a colourful half-finished painting, and around her feet lots of paint "
             "tubes, jars of brushes and colourful paint pots. No cat, no animals."),
    # Ada (Muse Code's character, named on 27 Oct).
    "ada": (OUT / "design-hello-iris-1.png", "soft mint",
            "Ada: a new character, as cute as Iris and Glimmer in the reference images and in "
            "exactly their style: long, soft, wavy dark chocolate-brown hair falling past her "
            "shoulders with a small yellow flower clip (a nod to Ada Lovelace), big sparkly eyes, "
            "rosy cheeks, a sweet smile. An oversized cosy mint-green knit sweater with a small "
            "'</>' embroidered on it, cream trousers, white sneakers. She waves with one hand and "
            "hugs a pastel lilac laptop covered in cute stickers with the other; its screen shows "
            "green code and a check mark. A few glowing pastel panels float around her: a code "
            "bracket, a terminal prompt, a checklist with ticks. A tiny cute robot buddy sits at "
            "her feet."),
}
for _name, (_ref, _colour, _who) in HELLO.items():
    REFS[f"hello-{_name}"] = [_ref, CAST]
    DESIGNS[f"hello-{_name}"] = (
        f"Solo portrait of one character from the reference images, exactly the same design, "
        f"colours and glossy plastic toy minifigure style. {_who} Standing alone, full body, "
        f"centred, facing the viewer with a warm smile as if introducing themself. Plain soft "
        f"{_colour} studio background with a gentle gradient. Only this one character. "
        f"No text, no letters, no labels, no name plate.")
# Ada was redesigned from scratch to match the cutest of the cast, not the old Muse Code figure.
REFS["hello-ada"] = [OUT / "design-hello-iris-1.png", OUT / "design-hello-glimmer-1.png", CAST]


def jpeg(path, width=1600):
    """References as JPEG: a few hundred KB instead of 3-4 MB PNG, so uploads don't time out."""
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=90)
    return buf.getvalue()


def main(name, n=1):
    # The JSON form of /images/edits takes several reference images; the SDK's multipart
    # form sends them under a key the API rejects.
    _load_env()
    images = [{"image_url": "data:image/jpeg;base64," + base64.b64encode(jpeg(p)).decode()}
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
