# Muse Code task: LEGO fine-tuning (round 4)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
After LEGO round 3 (`dock-lego-3.md`), rendered next to Sena's reference shots
(`experiments/blender/out/cycles/lego3-vs-referans.jpg`: reference left, ours right), the
hall, the platform and the rooms match well; four things still don't. Sena: "yes, fine-tune".

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py` and `experiments/blender/lego_front.py` (the LEGO rounds
are yours). Do not run commands or write probe scripts: this run cannot approve them. Read
the files, edit them directly, and stop; we build and render ourselves. As before, do not
open any file in `site/sim-lego/` except its `.jpg` images.

Look at `experiments/blender/out/cycles/lego3-vs-referans.jpg` first (left: reference,
right: ours; rows: hall, outside, rooms).

1. **Meeting table top.** Ours carries ~20 large orange studs (r ≈ 0.14, h 0.10) that read
   as bumps. The reference top is a smooth orange **tiled** disc: remove the table-top
   studs; keep the thin tile grid lines, make them 0.24 m apart and fainter (darker orange
   `#c98a3a`, 0.01 wide), and add a slim darker orange edge band. Stool seats keep one small
   stud each (r 0.08).
2. **Outside facade.** Ours is a flat white wall with a few scattered grey bricks. The
   reference shows **small bricks everywhere**: apply the hall's small white brick texture
   (0.96 × 0.288 running bond, faint light-grey mortar, a normal map for relief) to the
   whole outer facade in `lego_front.py`, at the same scale as inside, and remove the
   scattered grey brick boxes. Keep the roof fascia, the lights, the black door frame and its
   `MAL KABUL 01` sign.
3. **Apron.** Ours is glossy near-black with no visible studs. Make it **dark bluish grey**
   `#6c6e68`, roughness 0.45 (not mirror-like), with the floor's stud texture (colour and
   normal) at the same 0.24 m pitch, tinted dark; yellow dashes stay flat tiles.
4. **Floor studs visibility.** Inside, the stud texture barely shows from the hall camera.
   Increase the normal map strength (1.0) and give the stud colour image a slightly stronger
   top highlight and contact ring so the grid reads at 10–15 m like the reference.

Keep everything else as it is (positions, names, `rooms.json`, floor top at z = 0, the
platform). Change nothing outside these two files.
