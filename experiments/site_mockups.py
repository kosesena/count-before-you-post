"""Design directions for the top of the demo page, drawn by Muse Image.

Usage: .venv/bin/python experiments/site_mockups.py <screenshot.png> [direction ...]
       .venv/bin/python experiments/site_mockups.py background [1 2 ...]   # clean hero scene
Each direction is one images/edits call (muse-image-1.0, 1792x1024) with the current page
as the reference, plus three character portraits for the look. Writes
experiments/mockups/hero-<direction>.png. These are directions to choose from, not the page:
image models draw text poorly, so the real page keeps its real text.
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
OUT = HERE / "mockups"
HELLO = HERE.parent / "assets" / "mascots" / "hello"
LOWER = Path(os.environ.get("CBYP_LOWER_REF", HERE / "mockups" / "lower-ref.png"))

BASE = (
    "A redesign of the top of this web page (the first image is the current page), for a "
    "polished, premium product landing page. Keep its content: the title 'Count Before You "
    "Post', a one-sentence tagline, and a section 'Built with Muse' listing seven Meta AI tools "
    "(Muse Spark, SAM 3.1, Muse Voice, Muse Image, Muse Code, Muse Wonder, Muse Spark Open), "
    "each with its little toy character (the other images show the characters' style). "
    "Desktop browser layout, 16:9, clean modern UI, crisp, realistic web design mockup, no "
    "device frame. Direction: ")
DIRECTIONS = {
    "editorial": (
        "editorial and calm. Large bold headline on the left on a warm off-white background, "
        "the tagline under it, a call-to-action button 'Drive the dock'; on the right a soft "
        "collage of three toy characters standing together. Below, the seven tools as one slim "
        "row of round avatars with the tool name under each, evenly spaced, no boxes."),
    "gradient": (
        "bold and vivid. A full-width hero band in Meta's blue-to-violet-to-pink gradient, the "
        "headline and tagline in white, centred; below it the seven tools as seven equal "
        "frosted-glass pills in one row, each with the character avatar on the left and the "
        "tool name, all the same size, nothing on a second row."),
    "dock": (
        "cinematic. The hero is a wide 3D render of a bright, tidy warehouse receiving dock "
        "with a truck at the door, a pallet of cartons and a traffic light, slightly darkened; "
        "headline and tagline overlaid in white on the left with a button 'Drive the dock'; "
        "along the bottom edge of the hero, seven small glass cards with the tools."),
    "tiles": (
        "playful and premium. A short headline area on a light background; below it the seven "
        "tools as seven tall coloured tiles in one row, each tile entirely in that "
        "character's colour (orange, light blue, navy, pink, mint, ochre, teal) with the toy "
        "character standing at the bottom of the tile and the tool name and one short line "
        "of text directly on the colour above it, no speech bubbles."),
}


# The simulator's intro screen (first image: its current look over the 3D dock).
SIM_BASE = (
    "A redesign of the intro screen of this browser 3D simulator (the first image is the "
    "current screen: a warehouse dock in 3D behind a plain white card). Keep its content: "
    "the title 'The receiving dock', three short lines (you drive the forklift; an AI agent "
    "wants to post the delivery note's quantity to the ERP; bring the pallet to the gate and "
    "see whether the receipt gets written), six delivery choices (Matching delivery, Wrong "
    "product, Short delivery, Injected note, Damaged carton, Stacked load), a loading bar and "
    "a Start button. The other images show the toy characters' style. Polished, premium game "
    "UI over the 3D scene, 16:9 desktop, crisp, no device frame. Direction: ")
SIM_DIRECTIONS = {
    "sim-glass": (
        "elegant frosted glass. The 3D dock softly blurred behind one large frosted-glass "
        "panel; the six deliveries as glass tiles with a tiny pallet illustration each; a big "
        "glowing Start button; controls shown as small key caps (arrows, Space)."),
    "sim-briefing": (
        "a mission briefing. On the left, two toy characters (the orange-haired one and the "
        "gate character) with a speech line each telling the task; on the right, the six "
        "deliveries as illustrated cards like a level select; Start at the bottom."),
    "sim-clipboard": (
        "diegetic and warm. The intro is a real delivery note on a clipboard held up in front "
        "of the camera, handwritten-looking title, the six deliveries as tick boxes on the "
        "paper, a rubber-stamp style 'START SHIFT' button."),
    "sim-cinematic": (
        "cinematic. Full-screen 3D dock with a dark vignette, a huge title on the left, the "
        "three lines under it, a slim bottom bar with the six deliveries as chips and the "
        "controls legend, and a bold Start button on the right."),
}


# The rest of the page, after the hero (first image: the new hero; second: the sections
# below it as they are now, in the old style).
REST_BASE = (
    "A redesign of the rest of this landing page, below its hero. The first image is the new "
    "hero (keep it exactly as it is at the top of the mockup, and continue its look); the "
    "second image shows the sections below it, still in an old plain style. Keep their "
    "content: four headline numbers (5/6 deliveries a system that trusts the note gets wrong, "
    "1/6 wrong receipts from the agent alone, 0/6 behind the gate, 6/6 right calls), 'Meet "
    "the cast' with ten toy characters in their own colours, 'Deliveries at the dock' with six "
    "cases, a camera view and the gate's decision, 'An agent we did not write' with a big 0, "
    "and the receiver's voice clips. Show the hero at the top and two or three sections below "
    "it, as a tall desktop page, crisp realistic web design, no device frame. Direction: ")
RESULT_BASE = (
    "A redesign of the result card on the right of this browser 3D simulator (the first "
    "image is the current screen: the warehouse dock in 3D, a chat feed on the left, and on "
    "the right a dark card titled 'Sent to Şef' with a badge 'ASK ŞEF'). Redesign only that "
    "card; keep the 3D dock and the left feed as they are. Its content: the gate's decision "
    "ASK ŞEF; the reason 'SAM and Spark disagree on which objects are cartons: 11 agreed, 1 "
    "only SAM, 1 only Spark'; 'Without the gate: the agent asked Şef'; 'Behind the gate: "
    "nothing reached the ERP'; then 'Şef approved 12 cartons, receipt MAT-PRE-2026-00009'; a "
    "link to Wonder's note to Şef; the buttons 'Try another delivery' and 'Back to the demo'. "
    "Use photos: the second image is Kapı (the gate, a toy figure with a striped barrier), the "
    "third is Şef (the supervisor), the fourth is the real ceiling-camera photo of the pallet "
    "that was counted. Polished, premium game UI, 16:9 desktop, crisp, no device frame. "
    "Direction: ")
RESULT_DIRECTIONS = {
    "result-photo-hero": (
        "the pallet's camera photo fills the top of the card like a hero image with a soft "
        "dark fade, the amber 'ASK ŞEF' stamp over it, Kapı's portrait in a round frame "
        "overlapping the photo's lower edge; below, the reason and two clean tiles (without "
        "the gate / behind the gate); at the bottom Şef's portrait with a green 'approved 12' "
        "line."),
    "result-conversation": (
        "the card tells the ending as a short conversation: Kapı's portrait with a speech "
        "bubble 'ASK ŞEF' and the reason, then Şef's portrait answering 'Approved: 12 "
        "cartons', with the pallet photo as a small attached image in Kapı's bubble; the "
        "without/behind the gate comparison as a slim strip under them."),
    "result-polaroid": (
        "playful and warm: the pallet photo as a tilted polaroid pinned to the card with a "
        "piece of tape, a big amber rubber-stamp 'ASK ŞEF' half over it, handwritten-style "
        "small note 'counts disagree'; Kapı and Şef as two round sticker portraits; the "
        "without/behind the gate result as two ticket stubs."),
    "result-split": (
        "a bold split card: left half the pallet photo with the cartons outlined, right half "
        "the verdict in large type with Kapı's portrait, and across the bottom a full-width "
        "band 'Without the gate' versus 'Behind the gate' with big numbers, then Şef's "
        "approval as a green receipt line with the document number."),
    # Round 2 (Sena: too busy, wants it more premium and elegant): far fewer elements.
    "result-quiet-luxury": (
        "quiet luxury, extremely minimal: a deep near-black card with generous empty space, one "
        "thin hairline border, a single small round portrait of Kapı, the word 'Held for Şef' "
        "in large elegant light-weight type with one amber accent dot, one short line of grey "
        "reason text, one thin divider, a single line 'Without the gate: asked Şef · Behind "
        "the gate: nothing posted', a small green line 'Şef approved 12 · MAT-PRE-2026-00009', "
        "and two understated buttons. No icons, no stamps, no extra badges, no photo collage."),
    "result-editorial": (
        "editorial and premium like a luxury magazine: a calm card with one wide, softly "
        "graded photo strip of the pallet at the top (the fourth image), below it the verdict "
        "'Held for Şef' in a refined serif headline, a single sentence of reason in small sans "
        "text, a hairline, Şef's tiny round portrait with 'Approved 12 cartons', and one "
        "primary button. Lots of whitespace, restrained amber accent, nothing else."),
    "result-glass-mono": (
        "premium frosted glass, monochrome with one accent colour: a translucent dark glass "
        "card over the 3D scene, a big thin amber number '0' with the caption 'posted to the "
        "ERP' as the hero, under it 'Kapı held it for Şef' and one grey sentence of reason, then "
        "a slim green pill 'Şef approved 12'. Two small buttons at the bottom. Minimal, Apple-"
        "like, perfectly aligned, no clutter."),
}

# Sena (31 Oct): the whole demo page in LEGO style, several directions to choose from. The
# reference is the live page (site-ref.png) and the LEGO dock Muse Image drew (lego-hall.png).
LEGO_BASE = (
    "A redesign of this web page (the first image is the current page) in a LEGO style; the "
    "second image shows the warehouse dock already rebuilt in LEGO. Keep its content: the "
    "badge 'Live demo · recorded runs, no API calls from this page', the title 'Count Before "
    "You Post', the tagline 'A verification gate between AI agents and the ERP', a primary "
    "button 'Drive the dock' and a link 'See the six deliveries', and the row 'Built with "
    "Muse' with the seven toy characters as cards (Muse Spark, SAM 3.1, Muse Voice, Muse "
    "Image, Muse Code, Muse Wonder, Muse Spark Open). Desktop browser layout, 16:9, crisp, "
    "polished, premium web design mockup, no device frame. Direction: ")
LEGO_DIRECTIONS = {
    "lego-bright-baseplate": (
        "bright and clean: the page sits on a light grey LEGO baseplate with fine studs, the "
        "hero is the LEGO dock scene photographed in soft daylight, the cards are smooth white "
        "tiles with a coloured 1x2 brick on top in each character's colour, the button a "
        "glossy blue brick. Lots of white space."),
    "lego-night-dock": (
        "cinematic at night like the current page: the LEGO dock with warm lights and the open "
        "LEGO truck as the hero, the title in bold rounded type, the cards as dark grey studded "
        "plates with the characters as minifigures standing on top of them."),
    "lego-instruction-booklet": (
        "like a LEGO building-instruction booklet: cream paper, numbered steps 1 to 6 for the "
        "six deliveries, part callout boxes for the seven characters, clean isometric "
        "illustrations of the dock, playful but very tidy."),
    "lego-box-art": (
        "like the front of a premium LEGO set box: the dock as a hero model shot on a gradient, "
        "the title as the set name with a set number badge '01', the seven characters lined "
        "up as the included minifigures along the bottom, the button as a bright yellow brick."),
    # Round 2 (Sena did not like the first four). No brand logos or brand names anywhere.
    "lego-tabletop-diorama": (
        "the whole first screen is one photograph of a toy-brick diorama of the dock on a "
        "wooden table, shot from above at an angle with shallow depth of field; the title and "
        "tagline sit on a small printed tile in the diorama, the buttons are real bricks lying "
        "on the table, the seven characters stand around the model. Warm, handmade, magical."),
    "lego-hero-gate": (
        "one bold hero: a huge close-up of the gate character Kapı (a toy figure in a cardboard-"
        "box suit holding a striped barrier) next to a big toy-brick traffic light glowing "
        "green, amber and red, on a deep navy background; the title in huge chunky rounded "
        "type, very few words, the seven characters small in a neat row below. Minimal, "
        "confident, like a premium product launch page."),
    "lego-bento-bricks": (
        "a playful bento grid where every tile is a different coloured toy brick seen from "
        "above with studs (red, yellow, blue, green, orange, white): one big tile with the "
        "title, one with the dock photo, one per character, one with the button. Bright, "
        "joyful, modern, tidy alignment, no clutter."),
    "lego-pastel-studio": (
        "soft pastel studio: a pastel peach and lilac background, the seven characters as "
        "toy figures standing on a pastel brick shelf, the dock as a small cute model on the "
        "right, rounded soft UI cards, friendly and cosy, like a modern toy brand site."),
}

# Sena chose the tabletop diorama (hero-lego-tabletop-diorama.png); variations on it.
DIORAMA_BASE = (
    "Variations of this web page design (the first image): the demo page as a photograph of a "
    "toy-brick diorama of a warehouse dock on a wooden table, the seven toy characters on "
    "round grey stands with printed name cards, the title and tagline on printed tiles, the "
    "buttons as real bricks. Keep exactly its content and texts: 'Live demo · recorded runs, "
    "no API calls from this page', 'Count Before You Post', the tagline, 'Drive the dock', "
    "'See the six deliveries', 'Built with Muse', and the seven characters with their names "
    "(Muse Spark, SAM 3.1, Muse Voice, Muse Image, Muse Code, Muse Wonder, Muse Spark Open). "
    "No brand names or logos. Crisp, polished web design mockup, no device frame. Variation: ")
DIORAMA_DIRECTIONS = {
    "diorama-morning": (
        "bright morning: soft daylight from a window on the left, a light oak table, airy and "
        "clean, more empty table space around the model, the text tiles white and very "
        "readable."),
    "diorama-topdown": (
        "a flat-lay seen straight from above: the dock model in the middle with its roof "
        "removed so the cartons, the yellow tape zone and the gate are visible, the seven "
        "characters standing in a neat arc around it, the title tiles at the top, tidy and "
        "graphic."),
    "diorama-cinematic": (
        "closer and cinematic: low camera at table height, the characters standing on the "
        "dock apron in front of the open truck, warm lamp light and shallow depth of field, "
        "the title as a printed sign hanging on the warehouse wall, the buttons as bricks "
        "on the table edge in front."),
    "diorama-phone": (
        "the same design for a phone screen, portrait 2:3: the diorama photographed from a "
        "higher angle, the title tile on top, the two brick buttons stacked, the seven "
        "characters in two rows below, big readable text."),
}

REST_DIRECTIONS = {
    "rest-night": (
        "the night continues. The whole page keeps the hero's dusk dock mood: deep navy "
        "background with soft light from above, every section on frosted-glass panels, the "
        "four numbers huge and glowing, the cast as tall glass cards in their colours."),
    "rest-light": (
        "premium light after a dark hero. A warm off-white page, generous white space, large "
        "elegant typography, the four numbers as big editorial figures, the cast cards in "
        "their bright colours, thin dividers, calm and expensive."),
    "rest-story": (
        "a story told while scrolling. The sections become numbered chapters (1 The note, 2 "
        "The count, 3 The gate, 4 The agent we did not write), each with the character who "
        "does that step standing beside it, big chapter numbers, a thin progress line."),
    "rest-bento": (
        "a bento grid. Below the hero, the content as a grid of glass tiles of different "
        "sizes on a dark background: a large tile with the four numbers, one with the cast, "
        "one with the six deliveries, one with the big 0 of the outside agent, one with a "
        "voice waveform."),
}


# The cast section (first image: the hero above it; the others: four of the characters).
CAST_BASE = (
    "Design the 'Meet the cast' section of this premium landing page; the first image is the "
    "page's hero, continue its look exactly: deep navy dusk background, frosted glass. The "
    "other images are four of the toy characters (Spark orange, Sam blue, Voice navy and "
    "black, Kapi the gate in a cardboard body). Show three characters as horizontal rows that "
    "alternate sides: the character large and free-standing, with NO box, card or colour "
    "behind the figure (it stands on the page with a soft floor shadow and a faint glow of "
    "its colour); beside it a frosted-glass panel, lightly tinted with the character's own "
    "colour, holding its name, model, a short quote and one bold line, and a small 'Open "
    "profile' link. Elegant, very high quality, generous spacing, crisp typography, tall "
    "desktop page, no device frame. Direction: ")
CAST_DIRECTIONS = {
    "cast-glass": "large glowing glass panels with a fine bright edge and a soft colour "
                  "gradient inside; the characters overlap the panel's edge a little.",
    "cast-minimal": "quieter: slim glass panels, thin coloured accent line on the panel's "
                    "edge, more empty space, the characters a bit larger.",
}


def hero_background(dst):
    """The chosen direction's scene (hero-dock.png) redrawn as a clean background: no text, no
    interface, so the page's real text and cards sit on it."""
    if dst.exists():
        return
    body = {"model": "muse-image-1.0", "n": 1, "size": "1792x1024", "output_format": "png",
            "response_format": "b64_json",
            "prompt": ("The same scene as the reference image, exactly the same warehouse "
                       "receiving dock, the open truck with cartons inside, the pallet, the "
                       "traffic light, the lighting, colours and mood, but as a clean "
                       "background photograph: remove every piece of text, title, button, "
                       "card, badge and interface element, and remove the characters. Extend "
                       "the scene naturally where the interface was. Keep the left third "
                       "darker and calm so white text can sit on it. Cinematic, sharp, high "
                       "detail."),
            "images": [{"image_url": _jpeg(OUT / "hero-dock.png", 1536)}]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print("background", Image.open(dst).size, flush=True)


def _jpeg(path, width=1024):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def draw(shot, name):
    dst = OUT / f"hero-{name}.png"
    if dst.exists():
        return
    refs = ([shot] + [HERE.parent / "assets" / "mascots" / "hero" / f"{c}.png" for c in ("spark", "sam", "voice")]
            + [HELLO / "kapi.jpg"] if name in CAST_DIRECTIONS else
            [shot, LOWER] if name in REST_DIRECTIONS else
            [shot, OUT / "lego-hall.png"] if name in LEGO_DIRECTIONS else
            [OUT / "hero-lego-tabletop-diorama.png", shot] if name in DIORAMA_DIRECTIONS else
            [shot, HELLO / "kapi.jpg", HELLO / "sef.jpg",
             HERE.parent / "site" / "img" / "en" / "belirsiz-camera.jpg"] if name in RESULT_DIRECTIONS else
            [shot] + [HELLO / f"{c}.jpg" for c in ("spark", "sam", "voice")])
    prompt = (CAST_BASE + CAST_DIRECTIONS[name] if name in CAST_DIRECTIONS else
              SIM_BASE + SIM_DIRECTIONS[name] if name in SIM_DIRECTIONS else
              RESULT_BASE + RESULT_DIRECTIONS[name] if name in RESULT_DIRECTIONS else
              LEGO_BASE + LEGO_DIRECTIONS[name] if name in LEGO_DIRECTIONS else
              DIORAMA_BASE + DIORAMA_DIRECTIONS[name] if name in DIORAMA_DIRECTIONS else
              REST_BASE + REST_DIRECTIONS[name] if name in REST_DIRECTIONS else BASE + DIRECTIONS[name])
    size = ("1024x1536" if name in REST_DIRECTIONS or name in CAST_DIRECTIONS
            or name == "diorama-phone" else "1792x1024")
    body = {"model": "muse-image-1.0", "n": 1, "size": size, "output_format": "png",
            "response_format": "b64_json", "prompt": prompt,
            "images": [{"image_url": _jpeg(p)} for p in refs]}
    req = urllib.request.Request(
        BASE_URL + "/images/edits", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['META_API_KEY']}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT * 2) as r:
        dst.write_bytes(base64.b64decode(json.loads(r.read())["data"][0]["b64_json"]))
    print(name, Image.open(dst).size, flush=True)


if __name__ == "__main__":
    _load_env()
    OUT.mkdir(exist_ok=True)
    if sys.argv[1] == "background":
        for k in sys.argv[2:] or ["1"]:
            hero_background(OUT / f"hero-bg-{k}.png")
        sys.exit()
    for n in sys.argv[2:] or list(DIRECTIONS):
        if n == "cast":
            for m in CAST_DIRECTIONS:
                draw(Path(sys.argv[1]), m)
            continue
        if n == "rest":
            for m in REST_DIRECTIONS:
                draw(Path(sys.argv[1]), m)
            continue
        if n == "lego":
            for m in LEGO_DIRECTIONS:
                draw(Path(sys.argv[1]), m)
            continue
        if n == "result":
            for m in RESULT_DIRECTIONS:
                draw(Path(sys.argv[1]), m)
            continue
        if n == "sim":
            for m in SIM_DIRECTIONS:
                draw(Path(sys.argv[1]), m)
            continue
        draw(Path(sys.argv[1]), n)
