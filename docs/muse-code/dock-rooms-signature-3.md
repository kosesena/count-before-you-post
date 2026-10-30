# Muse Code task: mirror fix, the upper five rooms, warm cinematic light

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
After round 2 (`dock-rooms-signature-2.md`), rendered in Cycles with the cast seated: the
ground rooms are closer (clear glass, Şef's counter, Voice's notes and reels), but the
layout is mirrored. Seen from the yard the camera looks toward −y, so +x is on the left of
the picture, and the round-2 brief placed things by the concept's right as +x. The light was
also tuned by hand in test renders (hall dimmer and warm, each room lit warm from inside);
this round makes those values part of the scene and does the five upper rooms.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py` (you wrote `p_rooms` and rebuilt the ground-floor rooms
in two rounds). Do not run commands or write probe scripts: this run cannot approve them.
Read the file, edit it directly, and stop; we build and render in Cycles ourselves.

## Orientation (read first)

Every room is seen from the yard: the camera stands at larger y looking toward −y. So in
the picture **+x is on the left and −x on the right**. The concepts
(`experiments/mockups/room-choices.json` → `experiments/mockups/room-<id>-<variant>.png`)
are pictures from the same side. Below, "left" and "right" mean the picture; **left = +dx,
right = −dx** (dx = x − xc). The 1 m doorway is at dx in [−2.5, −1.5] (picture right) and
must stay clear from the glass to y = −15.2.

## 1. Mirror the ground-floor rooms

In the five ground rooms (`voice`, `sef`, `spark`, `sam`, `kapi`) last round placed every
piece at the dx the brief gave, which put it on the wrong side. **Negate the dx of every
furnishing and wall piece** in those five rooms (side-wall pieces move to the other side
wall), with these exceptions: Şef's counter keeps its span x in [x0 + 1.7, x0 + 5.8] (the
doorway); the items on it are mirrored. Kapı's rule book and lectern would land in the
doorway strip: put the lectern centre at dx −0.95, y −14.3 (its 0.9 m width spans dx −1.4
to −0.5). Check after mirroring that nothing lands in the
doorway strip. Expected result, picture-wise: Voice's reel-to-reel and lamp on the right
side of the desk; Şef's thermos and stamp on the left, the forms on the right, the radio on
the left of the back wall, the planner on the right; Spark's in-tray and drawers on the left,
the cork board right of centre; Sam's tripod on the left; Kapı's signal panel, control box
and rule book on the right, the barrier post on the left.

Also make sure every item named in round 2 for these rooms exists and is the size given
(Spark's desk organiser with files, magnifier, clipboard stand; Sam's mini pallet of cartons
and flip counter; Voice's phone and calendar stand; Şef's forms stack and pen cup).

## 2. The five upper rooms, as their concepts (all concept B)

Upper rooms: floor z0 = 3.2; seat (xc, −15.5), desk centred at y = −14.7, top 0.97 m above
z0. Delete the template dressing these rooms have now (side-wall shelving units, the shared
rug and pendant, legacy branches) and build:

### Ada (teal, code)
- Walls teal `#0f8b8d`.
- **Whiteboard** on the back wall at dx +1.4, centre 1.75 m: 1.7 × 1.15 white board in an
  aluminium frame with a tray; a flowchart drawn on it: 10 small rectangles (0.16 × 0.10
  outlines of thin dark strips) joined by thin lines, plus three sticky notes (yellow, pink,
  green 0.10 square).
- **"</>" neon sign** on the back wall at dx −0.7, centre 2.0: a frosted panel 0.95 × 0.62
  (white, alpha 0.6) on stand-offs, the glyphs `</>` as a text object (size 0.42, extruded
  0.02) in emissive cyan `#2ff3e0`, emission 6, plus a cyan point light 25 W in front.
- **Server rack** against the back wall at dx −1.9, y −17.25: 0.62 × 0.62 × 1.7 dark grey
  cabinet with 8 rack units (thin horizontal slabs), each with a row of 4 tiny LEDs (green
  and blue, emissive 6), a cable bundle running to the floor.
- Desk light grey `#d1d5db` 2.4 × 0.95 with slab legs; a **pink laptop** (lid `#f9a8d4`,
  open, screen emissive pale) at dx 0.3; an open notebook at dx +0.7; a small succulent in a
  pot at dx +1.0; two pens; a pink chair.

### Iris (pink, drawing)
- Walls hot pink `#e83e8c`.
- **Sketch string** across the back wall at z0 + 2.15 from dx +2.3 to −2.3 (a thin brown
  cord sagging 0.08 in the middle) with **9 sketches** (white sheets 0.30 × 0.40, rotated a
  few degrees, each with 4–6 thin dark strokes suggesting a figure) held by small wooden
  pegs; 3 more sketches pinned on the left side wall.
- **Drawing tablet** on the desk at dx +0.8: dark frame 0.62 × 0.46, tilted 30° on a stand,
  white screen (emission 1.5) with a few dark strokes.
- Wooden desk `#9a6a3a` 2.6 × 0.95, a beige drawer cabinet under the left end; on the desk a
  **paint palette** (flat oval 0.30 × 0.22 with 6 colour dots) at dx −0.6, 6 colourful
  markers scattered, a pen cup with 5 pencils at dx +1.25, loose drawings.
- **Wooden artist's mannequin** on the floor at dx −1.0, y −14.2 (height 1.1: jointed
  cylinders and spheres in light wood).
- Two pencils on the floor near the glass.

### Glimmer (violet, crystals)
- Walls violet `#7c5cf0`.
- **Crystal shelves**: on the right side wall (−dx side, y from −17.3 to −15.0) four wooden
  shelves at z0 + 0.9, 1.35, 1.8, 2.25, each carrying 3 **crystal clusters**; on the left
  side two shelves with 2 clusters each. A cluster = 3–5 hexagonal prisms (6-sided
  cylinders r 0.03–0.06, h 0.12–0.28, tilted 5–25° out of a common base) with pointed
  tips (6-sided cones), material pale lavender `#c4b5fd`, transmission/glass-like
  (roughness 0.1) with emission 2.5 in `#a78bfa`. One violet point light (15 W, no shadow)
  per shelf.
- Wooden desk; an **open book** at dx 0, a lavender plant (pot + 6 thin stems with purple
  bead tips) at dx +1.0, one crystal on a small stand at dx +0.6, notes on the desk and 5
  paper notes on the floor.
- The room glows violet: ceiling light area 60 W colour `#c8b8ff`.

### Wonder (mustard, post office)
- Walls mustard `#d9a42b`.
- **Pigeonholes** on the back wall left (dx +0.9 to +2.6, z0 + 1.0 to 2.5): a wooden grid
  5 columns × 4 rows of cubbies (0.30 × 0.32 × 0.30 deep), envelopes (cream/white flat
  boxes, some angled) in 12 of them.
- **Cork board with a map** on the back wall at dx −0.9: 1.2 × 0.85, a pale blue-green map
  sheet with 6 coloured pins and thin red string between them; two notes beside it.
- Warm wood desk 2.8 × 1.0; on it a **typewriter** at dx +1.0 (cream body 0.42 × 0.36 × 0.16,
  3 rows of small dark round keys, a black roller with a white sheet standing up), a
  **yellow mug** at dx +0.5, **three rubber stamps** (wooden handles with round knobs) at
  dx −0.3, a stapler at dx −1.0, a clipboard with paper, loose sheets, paper clips; a
  succulent in a terracotta pot at dx +1.3.

### Rover (teal, travel)
- Walls teal `#128c86`.
- **Postcard string** across the back wall at z0 + 2.1 from dx +1.8 to −1.4 with 6
  photo postcards (0.34 × 0.24, white border, image area in blue/green/grey blocks, no
  text), wooden pegs; two more pinned below.
- Left side wall: two small shelves with a thermos, a toolbox, a mug.
- Grey desk 2.4 × 0.95; a **rugged laptop** at dx +0.3 (dark grey thick body, 3 coloured
  sticker squares on the lid); a **globe** on a stand at dx +1.0 (sphere r 0.13, blue with
  green blobs); a pen cup; headphones; two notebooks.
- On the right (dx −1.6 to −2.4, against the back wall at y −17.0, out of the doorway strip):
  **4 stacked rugged hard cases** (dark grey 0.70 × 0.45 × 0.30 each, slight offsets,
  black latches and a coloured sticker each), a small radio on top, a coiled black cable on
  the floor (3 torus loops).

Plates for the upper rooms as light boxes like the ground rooms: Ada cream face with white
bold text outlined dark (or dark text); Iris cream face with a row of 8 warm bulbs along the
bottom edge, dark text; Glimmer white face with violet text `#6d28d9`; Wonder cream face
with gold-brown text `#8a5a14`; Rover grey face `#9ca3af` with cream text.

## 3. Warm cinematic light (values tuned in test renders; put them in the scene)

- `p_lights`: the high-bay spots at **0.35 ×** their current energy and colour
  `(1.0, 0.78, 0.55)`.
- `p_quality`: the grey ambient world `Background` strength at **0.2 ×** its current value;
  set the view transform to AgX and the look `"AgX - Punchy"` (inside try/except TypeError;
  fall back silently), exposure 0.2.
- In every room: the room's own lights (lamp, ceiling, strips, cove) at **2.5 ×** their
  current energy and with shadows on; the plate's front sign light at **0.3 ×**; plus one
  **key area light** per room, rectangle 2.4 × 1.2, at (xc, −14.3, z0 + 2.75) pointing down,
  energy 300 W, colour `(1.0, 0.80, 0.58)` (Sam's neutral `(1.0, 0.95, 0.88)`, Glimmer's
  `(0.85, 0.78, 1.0)`), named `p_room_<id>_key`.

## Keep

`rooms.json` unchanged (seats, `seat_z`, facing, doors, stairs); desk top ~0.97 m above the
room floor in front of the seat; nothing taller than about 1.15 m above the room floor
between the seat and the glass within |dx| < 0.35; the doorway strip clear; every object
named `p_room_<id>_*`; the shell. Delete dead branches for the upper rooms too
(`__legacy_*`, anything that can no longer run).

Change nothing outside `experiments/blender/warehouse.py`.
