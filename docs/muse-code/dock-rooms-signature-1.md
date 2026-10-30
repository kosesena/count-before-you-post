# Muse Code task: every room its own place (ground floor)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 30 Oct: the video is shot in the warehouse, so it has to look premium. Rendered in
Cycles from the yard, the ten rooms are one template (full-height shelving on both side walls,
a desk in the middle, the same rug, the same pendant), flat and washed out. Each should look
like the Muse Image concept Sena chose for it. This round does the five ground-floor rooms; a
second round does the upper five.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py`, function `p_rooms` (you wrote it). Do not run commands or
write probe scripts: this run cannot approve them. Read the file, edit it directly, and stop;
we build and render in Cycles ourselves.

## The problem

Seen from the yard, the ten rooms look like one room in ten colours: tall shelving units along
**both** side walls, a desk in the middle, the same rug with a coloured edge, the same pendant,
a pale coloured back wall. The concepts Sena chose
(`experiments/mockups/room-choices.json` → `experiments/mockups/room-<id>-<variant>.png`) are
each a different place. This round: rebuild the dressing of the **five ground-floor rooms**
(`voice`, `sef`, `spark`, `sam`, `kapi`, the `if cid == "spark": … elif cid == "kapi":`
branches of the dense chain and anything shared that they get) so each reads as its concept.
Do not touch `ada`, `iris`, `glimmer`, `wonder`, `rover` this round (their branches must keep
working exactly as now).

## What each room must be (read from the chosen concepts)

- **Voice** (concept B, deep navy): a warm, dim radio/listening room. Walls in dark navy with
  soft acoustic panels (a grid of slightly proud padded squares, a little lighter than the
  wall) on the back wall; sticky notes and paper slips pinned scattered across the back and
  west walls (many, slightly rotated, yellow/white/light blue); a **big reel-to-reel tape
  recorder** on the east end of the desk (two large reels clearly visible from the yard), a
  warm table lamp with a cream shade glowing on the desk, an old desk phone with a coiled
  cord, headphones; a dark wooden desk with a solid front panel. No bookshelves. The room's
  light is warm amber, low, intimate.
- **Şef** (concept B, royal blue): a supervisor's booth, tidy and bright. Blue back wall with a
  **shift planner** (cork board with a 3×4 grid of coloured cards and pins) to the east, a
  handheld radio in a wall cradle to the west; a grey steel counter-style desk with a steel
  thermos jug, a large red-and-black rubber stamp, stacked forms, a pen cup; a bright cool-white
  strip light across the ceiling front. A hard-hat hook, a safety vest on a hook. No
  bookshelves.
- **Spark** (concept A, orange): a cosy reading office. Orange walls; a large **cork board**
  on the back wall crowded with checklists and orange/yellow sticky notes, more checklists
  pinned down the west wall; a wooden desk with a pedestal of drawers, a black **anglepoise
  desk lamp** with a warm pool of light, a desk organiser with stacked papers, a magnifying
  glass, a clipboard, a pen cup, an orange office chair. The glass east wall stays clear.
- **Sam** (concept B, bright blue): a clean counting studio. Blue back wall with a neat grid
  of **carton drawings** (white sheets with simple box outlines, 2 rows × 5), a tally sheet;
  a white desk; a camera on a **tall tripod** at the west end pointed at the desk; a small
  stack of mini cartons on a mini pallet on the desk; a flip counter showing digits; pencils.
  Minimal, bright, a lot of white.
- **Kapı** (concept B, cardboard): everything is **made of cardboard**. Walls clad in
  corrugated cardboard panels (visible panel seams, strips of brown packing tape, a few
  "fragile" style markings without text), a cardboard desk with taped edges, a roll of
  packing tape on the desk, a clipboard; on the east/back wall a **three-lamp signal panel**
  (big red, amber, green lamps in a cardboard housing, green lit) next to a control box with
  knobs and a small display; a **big open rule book** on a cardboard lectern at the east side
  (pages with dark lines of "text" as thin bars, no legible words); a red-and-white striped
  barrier post at the west front. Warm light from a cove strip along the ceiling edge.

## How

1. **Remove the template** for these five rooms: no full-height shelving on both side walls,
   no shared rug-with-coloured-edge, no identical pendant. Each room gets its own wall
   treatment, its own floor (rug only where the concept has one), its own ceiling light
   (Şef strip, Kapı cove, Voice table lamp + dim ceiling, Spark warm pendant/desk lamp, Sam
   bright panel).
2. **Composition reads from the yard.** The camera looks in through the glass from about 6 m
   away at eye height 2 m. The signature pieces (Voice's reels, Şef's planner, Spark's cork
   board, Sam's tripod and carton grid, Kapı's three lamps and rule book) must be large enough
   to read at that distance (no prop smaller than ~0.15 m carries a room's identity).
   Asymmetry is good: put the signature piece on one side, the desk slightly off it, leave
   breathing room.
3. **Materials for a Cycles render.** Use the existing helpers (`mat`, `box`, `cyl`,
   `_pcone`, `_psphere`); you may add a node-based variant where it makes a real difference
   (cardboard: a noise-driven colour variation plus a fine wave bump for corrugation; acoustic
   panels: a fabric-like roughness 0.95). Keep the base colour in the Principled BSDF so the
   glTF export still carries it. Emissive things (lamps, the green signal, the reels' VU
   window) glow with emission strength 3–8, not more.
4. **Light per room**: one or two small lights inside each room (area or point,
   `use_shadow` on for the main one), warm (2700–3500 K look) except Şef's cooler strip and
   Sam's neutral panel. Energies modest (point 15–60 W, area 30–120 W) so the room glows
   through the glass without blowing out.
5. Keep: seat position, `seat_z` and facing in `rooms.json`; desk top about 0.97 m in front of
   the seat; nothing taller than about 1.15 m between the seat and the glass within
   |x − xc| < 0.35; the 1 m doorway at the west end clear; the shell (glass front, plate,
   dividers, ceilings); every object named `p_room_<id>_*`; only lights may be added outside
   the mesh naming. About 30–60 objects per room; reuse geometry by building in loops.

Change nothing outside `experiments/blender/warehouse.py`, and nothing in it outside
`p_rooms`.
