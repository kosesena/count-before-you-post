# Muse Code task: the ground-floor rooms as the concepts, piece by piece

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
After round 1 (`dock-rooms-signature-1.md`), rendered in Cycles next to the concepts, Sena:
"the rooms are not made the same as the reference images". Side by side: our rooms are twice
as wide as the concept booths and nearly empty, the props are small, a forest of glass
mullions hides the inside, the light is flat white, and the signature pieces either don't
read (Voice's notes are dots) or are missing (Şef's stamp and thermos, Kapı's cardboard).
This round gives every piece with a size and a place.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py`, function `p_rooms` (you wrote it and rebuilt the
ground-floor rooms last round). Do not run commands or write probe scripts: this run cannot
approve them. Read the file, edit it directly, and stop; we build and render in Cycles
ourselves.

## Why the last round missed

We rendered each room in Cycles from the yard (camera at x = xc + 0.6, y = −9.6, 2 m above
the room's floor, 22 mm lens) next to the concept Sena chose
(`experiments/mockups/room-choices.json` → `experiments/mockups/room-<id>-<variant>.png`):

1. **Empty.** The concept is a booth the character and the desk fill; ours is 6 m wide with a
   2.2 m desk and small props in the middle of bare walls. The room size stays (the
   simulator walks to these seats), so the furniture and the wall pieces must get **much
   bigger and fill the width**: the desk wide and solid, the signature pieces large, the walls
   covered where the concept covers them.
2. **Bars.** The glass front has a mullion every ~1.1 m, so the room looks caged. The concepts
   have big clear panes.
3. **Flat light.** Everything is evenly white-lit by the hall; the concepts glow warm from
   inside and their name plates are light boxes.
4. **Small or missing signatures.** Anything under ~0.15 m disappears at 6 m.

## Shell changes (all ten rooms; shared code in `p_rooms`)

- Glass front: keep the frame (two jambs, head, sill), the door's two jambs and the door
  head; **remove the intermediate mullions** (`mull` loop entries between the jambs) so each
  side of the door is one clear pane.
- Name plate per room as a **light box**, styled per concept (keep size about 1.8 × 0.4 m
  and position): a dark steel frame 3 cm proud around an emissive face, the name as text in
  front of the face. Colours: Voice navy face `#1e2a5a` (emit 1.5) with white text; Şef cream
  face `#fff1c4` (emit 3) with dark grey text `#3a3a3a`; Spark cream face with a row of 14
  small warm bulbs (emissive spheres r 0.025, emit 8) along the top and bottom edges, dark
  text; Sam white face (emit 3) dark text; Kapı cream face, dark text. (Upper rooms: keep
  their plates this round.) Text must not be emissive-white on a white face: make the text a
  dark non-emissive material on light faces.

## The five rooms

Coordinates: room x in [x0, x0 + 6], centre `xc = x0 + 3`; back wall face at y = −17.66,
glass at y = −13.5; floor z0 = 0. Seat at (xc, −15.5), desk centred at y = −14.7, top at
0.97 m. The 1 m doorway is at x in [x0 + 0.5, x0 + 1.5] and must stay clear from the glass
to y = −15.2. "dx" below is x − xc. Delete everything round 1 put in these rooms that this
list does not name (keep the shell).

### Voice (concept B: dark-blue listening room, warm lamp)
- Walls (back and both sides): saturated royal blue `#1f3fae`, roughness 0.9.
- **Sticky notes**: 22 squares 0.30 × 0.30 m (yellow `#fde68a`, white, pale blue `#bfdbfe`),
  each rotated a few degrees about the wall normal, each with a red or blue pin (sphere
  r 0.03), spread over the back wall (dx from −2.4 to 2.4, z 1.3–2.5) and 6 more on the east
  side wall. Four lines of dark "writing" (thin bars) on each.
- **Desk**: dark walnut `#5a3518`, 3.0 m wide × 1.0 m deep, top 0.08 thick at 0.97 m, a
  **solid front panel** (no visible legs) from the floor to the top on the yard side, a
  drawer pedestal on the east end with three drawer fronts and brass knobs.
- **Reel-to-reel recorder** on the desk at dx +0.95: body 0.80 × 0.40 × 0.45 (cream
  `#e8dcc0` front, dark grey sides), two reels upright facing the yard, r 0.17, 0.04 thick,
  silver with five dark holes each, at dx +0.75 and +1.15, z top; a row of four black knobs
  and a green VU window (emit 4) under them.
- **Table lamp** at dx +0.35, back of the desk: brass base cylinder r 0.10, stem 0.35, cream
  drum shade r 0.18 h 0.22 with emission 2.5 warm `#ffd9a0`, a point light inside it (35 W,
  warm, shadows on).
- **Desk phone** black at dx −0.9 (0.30 × 0.22 × 0.10 with a handset on top) and a coiled
  cord (a thin torus spiral or 8 small rings) running to it.
- A **spiral desk calendar/note stand** at dx −0.3 (0.25 wide, A-frame), an open notepad, a
  stack of three paper slips, a pen cup with three pens.
- High-back black office chair behind the desk.
- Light: only the lamp plus a dim warm ceiling area light (20 W); no bright panel.

### Şef (concept B: supervisor's booth behind a counter)
- Walls royal blue `#1d4ed8`; the side walls a darker grey `#4b5563` from z 0 to 1.0
  (wainscot).
- **Counter** instead of a desk: grey steel `#9ca3af`, from x = x0 + 1.7 to x0 + 5.8,
  1.0 m deep at y = −14.7, top 0.97 m, 0.10 thick, with a solid front panel and a recessed
  dark kick strip.
- On the counter, all big: a **steel thermos jug** at dx −1.1 (cylinder r 0.12 h 0.38,
  metallic 0.9 roughness 0.25, black lid and handle); a **rubber stamp** at dx −0.65 (red
  base 0.28 × 0.16 × 0.09, black handle cylinder r 0.04 h 0.20 and a black ball r 0.07 on
  top); two sheets of paper; a **stack of forms** at dx +1.2 (0.36 × 0.28 × 0.16, white with
  grey edges); a steel pen cup with two pens at dx +0.8.
- **Walkie-talkie** on the back wall at dx −1.4, z 1.6: black body 0.18 × 0.08 × 0.36 with a
  keypad face (3 × 4 small grey squares), an antenna cylinder 0.25 tall.
- **Shift planner** on the back wall at dx +1.3, z 1.75: cork board 1.0 × 1.1 m in a wood
  frame, 3 columns × 4 rows of cards 0.22 × 0.17 (alternating pale yellow and pale blue) with
  coloured pins.
- A bright cool-white strip light across the front of the ceiling (emissive bar 2.4 × 0.12,
  area light 80 W, 5000 K look).

### Spark (concept A: orange reading office, anglepoise lamp)
- Walls orange `#f26a1b`, roughness 0.85.
- **Cork board** on the back wall at dx +0.3, z 1.75: 1.6 × 1.1 m, wood frame, 12 items
  (checklists 0.20 × 0.28 white with 4 grey lines and small coloured ticks, sticky notes
  orange/yellow 0.14 square), pins.
- West side wall: two columns of 5 **checklists** (0.24 × 0.34) from z 1.1 to 2.4, rotated
  slightly, pinned; three more on the back wall left of the board.
- **Desk**: warm wood `#9a6a3a`, 2.8 m × 1.0 m, top 0.97, with a **solid wood drawer
  pedestal** at the west end (0.6 wide, 3 drawers) and a plain leg panel at the east end.
- On the desk: a grey **desk organiser/in-tray** at dx −0.9 (0.45 × 0.32 × 0.20) with a stack
  of 6 paper files sticking out; a black **anglepoise lamp** at dx −0.2 (base r 0.10, two arm
  segments 0.35 each at an angle, conical shade r 0.11 pointing down at the desk, warm bulb
  emissive and a spot light 30 W aimed at the desk); a magnifying glass (ring r 0.07 with a
  handle) at dx +0.5; a clipboard on a small stand at dx +0.1; a pen cup; two small books.
- Orange office chair `#ea580c`.
- Light: the lamp's warm pool plus a warm ceiling light (area 40 W).

### Sam (concept B: bright blue counting studio)
- Walls bright blue `#2563eb`; the frame and ceiling light grey.
- **Carton drawings** on the back wall: 2 rows × 5 white sheets 0.42 × 0.52 m from dx −2.2 to
  +2.2, z 1.35 and 2.0; on each a simple carton outline (a front square and a top
  parallelogram drawn with thin dark-blue strips 0.012 wide) and a pin.
- West wall: a tally sheet (white 0.4 × 0.5 with five groups of tally strokes).
- **Tripod** at dx −2.0, y −14.6: three black legs 1.5 m splayed, a head, and a black camera
  body 0.26 × 0.16 × 0.18 with a lens cylinder r 0.06 pointing at the desk.
- **Desk**: white `#f1f5f9` top 2.6 × 0.95, top at 0.97, with two **solid white side panels**
  (slab legs) instead of thin legs.
- On the desk: a **mini pallet** at dx −0.8 (0.45 × 0.35 wooden slats) with 3 × 2 × 2 mini
  cartons (cubes 0.12, cardboard brown with tape strip); an open notebook at dx 0 with blue
  lines; a **flip counter** at dx +0.9 (dark box 0.30 × 0.15 × 0.20 with two white digit
  cards on the front showing "2" and "7" as text); two yellow pencils.
- Light: neutral bright ceiling panel (area 70 W) — this room is the brightest and coolest.

### Kapı (concept B: everything cardboard)
- **Cardboard material** for the walls, ceiling, desk, lectern and panel housings: base
  `#b98a52`, roughness 0.9, with a noise texture (scale 40) mixing the colour ±8 % and a
  fine **wave texture bump** (bands along z, scale 60, strength 0.15) for corrugation; keep
  the Principled base colour set so the glTF still gets the brown.
- Walls in panels: vertical seams every 0.9 m (dark brown strips 0.02 wide) and **packing
  tape** strips (translucent tan `#d8b98a`, 0.06 wide) across a few seams.
- **Signal panel** on the back wall at dx +1.2, z 1.4–2.4: cardboard housing 0.45 × 0.15 ×
  1.05 with three lamps r 0.13 (red, amber, green), each in a dark ring; **green lit**
  (emit 7), red and amber dark glass (emit 0.2). Next to it at dx +2.0: a **control box**
  0.80 × 0.12 × 0.75 with a dark display 0.40 × 0.12 at the top and 2 rows of 4 black knobs.
  A small warm point light (10 W, green tint) in front of the green lamp.
- **Rule book** at dx +1.9, y −14.3: a cardboard lectern (sloped top 0.9 × 0.6 at 30°, top
  edge 1.25 m) carrying a big open book (two cream pages 0.42 × 0.58, a dark spine, 12 rows of
  dark text bars on each page, varying lengths). Keep it east of dx +1.2 (clear of the
  seat-to-glass strip).
- **Desk**: a cardboard box desk 2.2 × 1.0, top 0.97, solid on all sides, taped edges; on it
  a clipboard standing up at dx −0.8, a roll of packing tape (torus r 0.08) at dx −0.4, two
  sheets, a pencil.
- **Barrier post** at the west front, x = x0 + 1.75 (east of the doorway), y −13.9: cylinder
  r 0.07 h 1.3 with 7 alternating red/white bands and a dark base.
- Blue office chair `#1e40af`.
- **Cove light**: a warm emissive strip along the ceiling's front and side edges (0.05 tall,
  emit 3, `#ffd8a0`) plus an area light 60 W.

## Keep

Seat position, `seat_z`, facing and everything in `rooms.json`; desk top at about 0.97 m in
front of the seat; nothing taller than about 1.15 m between the seat and the glass within
|x − xc| < 0.35; the doorway clear; every object named `p_room_<id>_*`; the upper five rooms
unchanged except the mullions. Delete the dead branches you parked last round
(`__old_*`, `__legacy_*`) for these five rooms so the file shrinks.

Change nothing outside `p_rooms` in `experiments/blender/warehouse.py`.
