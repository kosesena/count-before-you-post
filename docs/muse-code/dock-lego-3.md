# Muse Code task: the bright LEGO look (round 3)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
After LEGO rounds 1–2 Sena compared our warehouse with screenshots of another LEGO
warehouse she had made (`site/sim-lego/*.jpg`, uncommitted, built with a different tool)
and preferred its look. Her decision: the site says Muse Code wrote the simulator and that
must stay true, so **the other code is not copied or read**; only the four screenshots are
the visual reference, and Muse Code brings `dock.glb` to that style.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py` (polished scene, LEGO rounds 1–2 are yours),
`experiments/blender/lego_front.py` and `experiments/web/export_dock.py`. Do not run
commands or write probe scripts: this run cannot approve them. Read the files, edit them
directly, and stop; we build, render and export ourselves. **Do not open any file in
`site/sim-lego/` except the four images below**; do not read or reuse its code.

Visual reference (look at them): `site/sim-lego/interior-lego.jpg` (the hall),
`site/sim-lego/preview.jpg` (same, wider), `site/sim-lego/exterior-lego.jpg` (the dock
outside with the truck), `site/sim-lego/offices-wall.jpg` (the rooms from the hall).

## What the reference does that ours doesn't

1. **Bright and airy.** Near-white to light-grey palette (`#f2f3f2` white, `#e4e6e3`,
   light bluish grey `#a0a5a9` only for accents), flat even light, no dark corners, no green
   cast. Ours is dark with big black-grey shapes.
2. **Fine, dense studs.** The floor reads as a light-grey baseplate with small studs in a
   tight grid; ours has large widely spaced studs. Make the floor studs a **texture, not
   geometry**: generate (in Python, `bpy.data.images.new` + pixels, then `image.pack()`)
   a tileable 512×512 colour image of one 4×4 stud cell (light grey base `#d9dbd8`, round
   studs with a soft top highlight and a soft contact shadow) and a matching normal map
   (raised round studs), and map them on the floor plate so the stud pitch is **0.24 m**
   (one tile = 0.96 m). Remove the geometry-node floor studs (`p_lego_floorstuds`) and the
   apron's (`p_lego_apronstuds`); use the same texture on the apron in dark bluish grey
   `#6c6e68` with the dashed yellow lane tiles **flat (0.03 m thick)**, not bars. Keep the
   floor plate's top surface at z = 0. Keep geometric studs only on small things (table
   top, stools, cartons, cab roof).
3. **Ceiling of studded grey plates** with black **pendant lamps** (black cone shades with a
   warm white emissive underside), many of them in rows; steel trusses light grey.
4. **White brick walls** with small bricks (1x4 at our scale: 1.92 × 0.576 is too big — use
   **0.96 × 0.288** bricks in running bond, white/off-white with a faint light-grey mortar),
   on the back, left and right walls; the generated brick image updated accordingly.
5. **Racks**: blue uprights `#0055bf`, **yellow** shelves `#f2cd37` (not orange), tan
   brick cartons on every level, running the full length of the walls they stand against.
6. **Meeting table** (keep the Meshy table and stools, centre (1.0, −7.0), radius 1.8, top
   1.35, stools on the 2.4 m circle): tint the top **orange** `#e4a149` with a thin tile grid
   (a separate overlay disc with dark grid lines 0.48 m apart, 2 mm above the top); replace
   the flat rug with a **raised navy platform** (a 0.19 m thick disc r 3.4, `#1f3a73`, with a
   0.25 m wide **yellow** rim ring, studs on the rim as texture), and colour the stools
   teal `#00a3a3`, orange `#fe8a18`, yellow `#f2cd37`, blue `#0055bf` (cycle).
7. **Rooms from the hall**: black **balcony railings** of thin black bars, a **yellow
   staircase** (`#f2cd37` treads and stringers), each room's plate a coloured band in the
   room's colour (keep the names).
8. **Outside**: the facade **white/light-grey bricks** (not corrugated steel), the dock door
   a thick **black** frame with a yellow sign `MAL KABUL 01` on its header, the apron dark
   grey with fine studs (texture), flat yellow dashes; the docked truck's trailer
   **white** `#f2f3f2` brick-built, cab red as now.
9. **Light**: raise the hall's overall level (bays to 1.6× their current energy and colour
   `(1.0, 0.96, 0.9)`, world ambient strength 0.8, exposure 0.0 with the Standard view
   transform), keep each room's key light.

## Keep

The layout and every position (rooms, stations, table, zone, quarantine, door, racks,
cartons of the delivery), every object-name prefix the simulator relies on (`p_`, `zone_`,
`screen_`, `gate_`, `pallet`, `p_rk*`, `p_fl_*`, `p_meet_*`, `p_room_<id>_*`), `rooms.json`,
the floor top at z = 0. Images must be packed so the glTF export carries them;
`export_dock.py` must stay Draco-compressed and drop the removed stud instancers cleanly.
