# Muse Code task: the LEGO loading dock outside (`lego_front.py`)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 30 Oct, on Muse Image's `lego-outside.png` (branch `claude/laughing-brattain-dd01bb`,
`experiments/mockups/`): "the truck and the entrance, I love them, let's make exactly
that". The truck and the forklift come from Meshy; this task builds the dock front around
them. It runs in parallel with the LEGO round on `warehouse.py`, so it lives in its own file.

---

You are working in the repository `count-before-you-post`. Do not run commands or write
probe scripts: this run cannot approve them. Read what you need, write the new file, and
stop; we build and render ourselves. **Do not edit `experiments/blender/warehouse.py`**
(another task is editing it); only create `experiments/blender/lego_front.py`.

Read `experiments/blender/warehouse.py` for context: the helpers `box`, `cyl`, `text`,
`mat`, `_hex`, `aim`, `_pcone`, `_psphere`; the polished scene's back wall at y = 10
(inner face ~9.85, outer face ~10.15) with the dock door opening x in [−1.6, 1.6], 3.4 m
high (`building`, `p_shell`, `p_door`); the apron outside (`p_sky`: `p_apron`, y from 10 to
34) and the trailer docked behind the door (`p_truck`). LEGO scale constants (factor 60 on
a 4 cm minifigure): `STUD_PITCH = 0.48`, `STUD_R = 0.144`, `STUD_H = 0.10`,
`PLATE_H = 0.192`, `BRICK_H = 0.576`.

Write `build_lego_front(P, box, cyl, text, mat)` in `experiments/blender/lego_front.py`
that builds, as in `lego-outside.png`:

1. **Outer facade of the back wall** (the face the outside camera sees, y > 10.15, x from
   −15 to 15, 7 m high): light bluish grey `#a0a5a9` **corrugated cladding** as vertical
   ribs (0.05 × 0.08 boxes every 0.24 m, slightly lighter than the panel behind), a
   2-course band of grey bricks along the bottom (box courses of 1.92 × 0.576 bricks in
   running bond, alternate bricks ±4 % lighter, a few dark bluish grey `#6c6e68`), and a
   dark bluish grey roof edge/fascia on top (0.4 m tall, 0.3 m proud).
2. **Roof-edge lights**: 9 warm lamps evenly along the fascia (small black housings with
   an emissive warm `#ffd9a0` disc, emission 6), and one warm point light (40 W) per lamp
   pointing down at the apron.
3. **The dock door frame** around the opening: a thick **black** surround (0.5 m wide
   posts and a 0.6 m header, 0.4 m deep) like the concept; a **green traffic light** on a
   short black post at the left of the door, outside (a 1x1 black housing with three lamps,
   only green lit, emission 8).
4. **Studded apron**: the apron becomes a dark bluish grey baseplate `#6c6e68`
   (glossy, roughness 0.25) with studs on the `STUD_PITCH` grid over x in [−12, 12],
   y in [10.4, 30] — build them as **instances** via a Geometry Nodes modifier (Mesh Grid →
   Instance on Points, one 16-sided cylinder r `STUD_R`, h `STUD_H`), object
   `p_lego_apronstuds`. Leave a clear lane under the truck's wheels? No: studs everywhere;
   the truck sits on them.
5. **Yellow dashed lane markings**: two dashed lines of flat yellow tiles `#f2cd37`
   (1x4 tiles: 1.92 × 0.48 × 0.19, gaps of 0.96 m) running from the door outwards at
   x = −2.6 and x = 2.6, from y = 10.6 to y = 30, plus a grey 2x6 tile "dock plate" step in
   front of the door at y ≈ 10.4.
6. **A dock guard minifig spot**: leave a 1 m clear square on the apron at (−4.0, 12.0) (we
   stand a character there later); put nothing on it.

Name every object `p_lf_*` (the apron studs `p_lego_apronstuds`). Return nothing. Use only
`bpy`, `math` and the passed helpers. Write a short module docstring saying what the file
builds and that `warehouse.py` calls it from `polish()`.
