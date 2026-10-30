# Muse Code task: LEGO City truck and forklift (round 2)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
After LEGO round 1 (`dock-lego-1.md`): the docked semi-truck and the working forklift still
have the old low-poly look. Sena loves the truck and entrance in Muse Image's
`lego-outside.png` ("exactly that"). The docked trailer and the forklift must keep working
in the simulator (the forklift drives up the leveller into the trailer, lifts the delivery
pallet off the trailer floor at y ≈ 11, z = 0.54, and carries it to the receiving zone), so
they are restyled in place, not replaced.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py`, functions `p_truck` and `p_forklift` (polished scene).
Do not run commands or write probe scripts: this run cannot approve them. Read the file,
edit it directly, and stop; we build, render and export ourselves.

Use the LEGO helpers and constants from round 1 (`lego_mat`, `STUD_PITCH`, `STUD_R`,
`STUD_H`, `PLATE_H`, `BRICK_H`).

## `p_truck`: LEGO City semi-truck, as in `lego-outside.png`

Keep the trailer's position, its open rear at the dock door, its interior floor height
(0.54) and the cargo pallets inside it; keep the tractor's position and heading. Restyle:
- **Tractor**: a **bright red** brick-built cab (`#c91a09`, glossy) with a flat front, black
  trans-dark windows (2 side, 1 wide front), a **white** horizontal grille band with a
  dark grille, two round headlights (emissive warm, emission 4) and two orange side
  markers, two chrome exhaust stacks (cylinders, metallic 0.9) behind the cab, a dark
  bluish grey chassis, black wheels with light grey hubs; studs on the cab roof (2 rows).
- **Trailer**: **light bluish grey** `#a0a5a9` box built from brick courses (subtle
  horizontal grooves every `BRICK_H`), a dark grey chassis rail, red/white reflector
  strip along the bottom edge, black wheels in two axles near the back, studs along the top
  edges; the open rear shows the inside (keep the interior and the cargo).

## `p_forklift`: LEGO City forklift, keep every `p_fl_*` name

The simulator moves the forklift as one group and lifts the forks: **keep the names and
the pivots of `p_fl_fork*`, `p_fl_mast_in*`, `p_fl_carriage*`** and every other `p_fl_*`
object's role; change shapes and materials only within the same footprint (±5 %). Bright
yellow `#f2cd37` brick body with a stud row on the counterweight, black overhead guard
cage of 1x1 round bars, black mast and forks, black seat, black tyres with yellow hubs, an
orange beacon (emissive) on the guard.

Change nothing outside `p_truck` and `p_forklift` in `experiments/blender/warehouse.py`.
