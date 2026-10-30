# Muse Code task: a meeting table in the middle of the hall

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 30 Oct: the agents work in their rooms and at their stations; when a delivery really
needs several of them together (the gate answers "ask a human" in the recorded runs), they
should gather at one table in the middle. The table goes into the Blender warehouse (for the
video) and through `dock.glb` into the simulator, which walks the agents there.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py`. Do not run commands or write probe scripts: this run
cannot approve them. Read the file, edit it directly, and stop; we build and render
ourselves.

Add a function `p_meeting(P)` and call it from `polish()` right after `p_rooms(P)`. It builds
a meeting area in the open hall between the rooms and the receiving stations, centred at
**(x, y) = (−4.0, −6.5)** on the floor (z = 0). The simulator uses these exact numbers, so
keep them as module constants `MEET_X = -4.0`, `MEET_Y = -6.5`, `MEET_R = 1.1`.

- **Round table** for the 2.4 m toy characters: top radius 1.1 m, 0.07 thick, top surface at
  0.97 m, warm oak `#b07a45` (roughness 0.5) with a thin dark edge band; a central pedestal
  (cylinder r 0.16) on a round base plate (r 0.55, 0.05 thick), dark steel.
- **Six stools** around it on a circle of radius 1.7 m at angles 0°, 60°, …, 300° (0° = +x):
  seat r 0.24 at 0.62 m, a single post and a small foot ring, seats in the cast's colours in
  this order: `#f97316`, `#3b82f6`, `#a16207`, `#1d4ed8`, `#ca8a04`, `#0d9488`.
- **A rug** under it: a flat disc r 2.4, 0.012 thick, colour `#2b3a55` with a 0.10 wide ring
  near the edge in `#ffd21f` (two discs or a ring mesh).
- On the table: a stack of three delivery notes (white sheets 0.21 × 0.30, slightly
  rotated), a clipboard, one rubber stamp, a small tablet face up with an emissive pale
  screen; nothing taller than 0.25 m.
- **A pendant lamp** above it: a wide warm shade (cone r 0.55) on a cable from the roof, a
  warm emissive disc under it and an area light (disc, 1.2 m, 200 W, colour
  `(1.0, 0.82, 0.6)`, shadows on) at 4.2 m pointing down.
- A floor sign stand at the table's −y side, 1.6 m to the south: a post and a 0.9 × 0.3 board
  reading `MEETING` in white on dark navy (text object).

Name every mesh `p_meet_*` (the export keeps `p_` objects as static meshes). Change nothing
else.
