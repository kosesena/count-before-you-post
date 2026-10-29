# Muse Code task: the simulator, realism round 2

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
(Second attempt: the first stopped while waiting to run a probe script, before any edit.)
What we saw after round 1 (`docs/muse-code/sim-realism.md`), from screenshots and
`window.stats` in headless Chrome.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you wrote
it). Round 1 works (`node experiments/web/sim_test.mjs` → ALL OK) and driving feels right. Fix
three things we measured; keep everything else, and keep the test passing.

1. **Performance.** `window.stats.triangles` went from about 2.1 million to 4.4 million and fps
   dropped (46 where it was 57-61): the ten characters (450k triangles each) are drawn a
   second time into the shadow map. Characters must not cast real-time shadows: give each a
   soft round contact shadow on the floor (a small transparent radial-gradient plane under
   its feet). Real shadows only for the forklift, the delivery and the static dock (and the
   static ones only once if you can: `shadowMap.autoUpdate = false` with a manual update when
   something static changes is fine; the forklift and pallet may use their own small shadow).
   Target: triangles back near 2.2 million, fps near 60.
2. **Driver's seat view.** It is too close and cluttered: the overhead-guard posts fill the
   screen, two white rectangles float at the left and right edges (find what they are and
   remove them), the dashboard is cut off and the steering wheel is not visible. Make it read
   like sitting on a forklift: eye about 2.05 m high, a little behind the wheel, field of view
   ~75°; the guard posts thin and at the far edges; the guard bars only at the very top; the
   wheel visible at the lower centre-left and turning with the steering; the dashboard fully
   visible below the mast (speed, fork height, load); the mast rails and fork tips clearly
   ahead so a pallet can be lined up.
3. **Light.** Still flat and too bright compared with
   `experiments/blender/out/polish/depo-ok-genel.png`: lower the exposure, warmer key light from
   the high-bay lamps, deeper ambient in the corners, and make the gate light's colour visibly
   pool on the floor around the pole (a coloured point light plus a soft emissive disc on the
   floor), green / red / amber with the decision.

Change nothing outside `site/sim/index.html`.

Do not run commands or write probe scripts: this run cannot approve them. Read the file, edit
it directly, and stop; we run `sim_test.mjs` and measure `window.stats` ourselves.
