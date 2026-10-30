# Muse Code task: bigger pieces, glowing signatures, toy colours

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
After round 3 (`dock-rooms-signature-3.md`), rendered in Cycles with the cast seated and
compared with the concepts: every room now has its own identity and the right side, but the
pieces are still small against a 6 m room, several signatures don't glow (Glimmer's
crystals render white, Ada's neon is hard to see), Kapı's cardboard reads pale pink, the
floors blow out white, and AgX washes the toy colours. A test with the "Standard" view
transform matched the concepts' saturated colours much better.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py` (you wrote `p_rooms` and three rounds of room dressing).
Do not run commands or write probe scripts: this run cannot approve them. Read the file,
edit it directly, and stop; we build and render in Cycles ourselves.

Seen from the yard (+x is the picture's left; keep last round's sides), compared with the
concepts (`experiments/mockups/room-choices.json` → `experiments/mockups/room-<id>-<variant>.png`):

## 1. Everything bigger (all ten rooms)

The pieces are right but too small for the 6 m rooms and the 2.4 m seated figures. Scale
**every desk-top prop by 1.5** about its own base (lamps, reels, phone, thermos, stamp,
forms, in-tray, organiser, magnifier, laptops, tablet, typewriter, mug, stamps, globe,
palette, plant pots, pen cups, book, mini pallet, flip counter) and **every wall piece by
1.4** about its centre (sticky notes, checklists, cork boards, planner, carton drawings,
sketches, postcards, whiteboard, neon panel, map board, pigeonhole grid, signal panel,
control box), keeping them on their walls and inside the room; where a scaled wall piece
would overlap another, spread them along the wall. Keep the desk-top items on the desk top
(z on the top surface after scaling) and keep the seat-to-glass rule (nothing taller than
~1.15 m above the room floor within |dx| < 0.35).

## 2. Signatures that must glow or read

- **Glimmer's crystals**: base colour `#7c3aed`, emission colour `#a78bfa` strength 4, no
  transmission, roughness 0.15; clusters 1.5× bigger; add L-shaped corner shelving: the
  right-wall shelves continue 0.8 m along the back wall at the same heights, each with two
  more clusters. Shelf point lights 25 W violet `(0.62, 0.45, 1.0)`.
- **Ada's neon**: the `</>` glyphs 1.4× bigger, emission 10, the frosted panel slightly
  darker (`#1f3b3d`, alpha 0.85) so the cyan reads; a cyan rim strip (emission 4) around the
  panel edge.
- **Kapı's cardboard**: base colour `#a8743c` (not paler), noise colour variation ±12 %,
  the corrugation bump strength 0.35 and band scale 35 so the ribs show; the tape strips
  `#c9a46a`; the three signal lamps r 0.17 with the green at emission 9 and a green point
  light 20 W in front.
- **Iris's tablet** must read as a drawing tablet on a stand, not a laptop: a flat dark
  slab 0.75 × 0.55 tilted back 30° on a small easel stand, a white screen face (emission 2)
  with a dozen dark strokes forming two little figures; no hinged lid.
- **Voice's lamp** shade emission 4, the lamp's point light 60 W; the notes 0.36 square.
- **Wonder's pigeonholes**: envelopes in 14 of the cubbies, cream `#f3e7c9`, each a flat box
  proud of the cubby by 3 cm so they show from the yard; the typewriter's sheet standing
  0.25 above the roller.
- **Rover's postcards** 0.48 × 0.34 with brighter image blocks (sky blue, green, sand).

## 3. Floors and colour

- Each room gets its own floor finish (a 0.01 thick slab over the room floor inside the
  walls, not under the glass): Voice dark walnut boards `#4a2e1a`, Şef grey vinyl
  `#6b7280`, Spark warm oak `#b07a45`, Sam light grey `#a1a7b0`, Kapı cardboard (same
  material), Ada pale grey `#9ca3af`, Iris warm oak, Glimmer lilac grey `#8f86b8`, Wonder
  honey wood `#a86b2d`, Rover dark grey `#5b6168`. Roughness 0.6–0.8.
- `p_quality`: view transform **"Standard"** (try/except TypeError), look none, exposure
  −0.35 (replace last round's AgX/Punchy). Keep the light energies from last round.

## Keep

`rooms.json` unchanged; desk tops ~0.97 m above the room floor; the doorway strip
(dx −2.5 to −1.5, y > −15.2) clear; every object named `p_room_<id>_*`; the shell.

Change nothing outside `experiments/blender/warehouse.py`.
