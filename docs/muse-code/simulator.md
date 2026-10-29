# Muse Code task: the dock simulator

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
The models were prepared by us: `experiments/web/compress_glb.py` (characters, 450k triangles,
2K WebP, Draco: side by side with the originals in the same browser, no visible difference)
and `experiments/web/export_dock.py` (the dock and the six deliveries from the Blender scenes).

---

You are working in the repository `count-before-you-post`. Read `README.md` first (the jury
reads it too), then `site/index.html` (the demo page you wrote; keep its tone and colours) and
`site/data-en.json` (every fact the simulator may show).

## Goal

Write `site/sim/index.html`: a 3D simulator of the receiving dock, in the browser, that a judge
opens from the demo page. **Its job is to make the judge understand the project by doing it**:
an AI agent wants to write a delivery note's quantity into the ERP; the judge brings the
delivery to the gate, and sees the gate check the evidence and decide, with the real recorded
readings. Driving is the way in, not the point. Everything shown about the decision comes from
`data-en.json`, nothing invented.

One self-contained HTML file with an import map, three.js 0.170.0 from
`https://cdn.jsdelivr.net/npm/three@0.170.0/` (`GLTFLoader`, `DRACOLoader` with the decoder at
`.../examples/jsm/libs/draco/gltf/`, `RoomEnvironment`), vanilla JS, no other dependencies.
`site/sim/compare.html` and `site/sim/dock-check.html` show the loader setup that works.

## Assets (all in `site/sim/models/`, coordinates are Blender metres: x right, y into the
## dock, z up; glTF is y-up, so a Blender point (x, y, z) is three.js (x, z, -y))

- `dock.glb` (1 MB): the warehouse. Separate nodes the page uses: `forklift` (its body),
  `forklift_forks` (move up and down with the load), `gate` (pole, housing, light, barrier),
  `screen` (the decision screen at x −4.35…−2.85, y 2.54…2.64), `delivery` and `jack` (hide
  both: the page loads the picked case's delivery instead). Everything else is static.
- `dock.glb.colliders.json`: 221 floor boxes `[x0, y0, x1, y1]` the forklift must not drive
  into (racks, walls, office, gate pole, props).
- `delivery-<case>.glb` for ok, wrong, eksik, talimat, hasarli, belirsiz: that case's pallet
  with its cartons and labels, exactly as measured (eksik really has a carton missing). One
  node, `delivery`, centred at (0, 5.5, 0) in Blender, footprint 1.2 × 1.04 m.
- `<name>.glb` for spark, sam, voice, kapi, sef, wonder, rover, glimmer, iris, ada (≈2 MB each,
  23 MB together): rigged Lego figures with actions `Idle`, `Walk`, `Wave`. Scale each so it
  stands 1.6 m (kapi and sef 1.75 m), feet on the floor.

Places (Blender): forklift starts where it is (body x 7.3…8.7, y −1.7…1.9). Trailer floor
x −1.25…1.25, y 10.25…18.25, at z 0.54; the dock door is at y ≈ 7.8…9.4, x −2.3…2.3; treat
y 9.4…10.25 as the dock leveller, a ramp from 0 to 0.54. The receiving zone (yellow floor
tape) is x −2.48…2.48, y 3.32…7.68. The gate pole is at x 3.05…3.75, y 2.22…2.55. Characters,
each facing the receiving zone, with a floating label of name and job:
spark (−4.2, 4.5) reads the note · sam (2.7, 6.8) counts the cartons · voice (−4.6, 2.1)
hears the receiver · kapi (4.0, 2.0) the gate · sef (−0.3, 3.0) signs off · wonder (−8.2, 1.6)
checks and writes the paperwork · rover (9.0, 2.5) reads the note again · glimmer (1.0, 0.5)
the other open-weight reader · iris (−6.6, −0.6) drew the cast · ada (−9.6, −0.9) wrote the code.

## The experience

1. **Intro card (over the 3D scene, which keeps loading behind it).** Three short lines:
   you drive the forklift at a warehouse dock; an AI agent wants to post the delivery note's
   quantity to the ERP; bring the pallet to the gate and see whether the receipt gets written.
   Then the six deliveries as buttons (case `title` from `data-en.json`, without revealing the
   outcome), and "Start".
2. **Driving.** The picked case's delivery sits on the trailer floor just inside the trailer,
   at (0, 11.0, 0.54). A small card in a corner shows that case's delivery note image
   (`../` + `images.note`) and its line ("12 × Sunflower oil 5 L"), so the judge knows what
   the paper claims. A chase camera follows the forklift smoothly; `C` switches to an overview.
   Controls: arrows or WASD drive and steer (forklift feel: it steers from the rear, reverses),
   `Space` picks up / sets down, `R` restarts. On touch screens: an on-screen joystick and a
   Pick/Drop button. A line of hint text tells the next step ("Drive into the trailer",
   "Line the forks up with the pallet and press Space", "Bring it to the yellow zone", "Set it
   down").
   Picking up: when the fork tips are under the pallet (within its footprint, heading within
   about 20°), `Space` attaches the delivery to the forks and lifts it 15 cm. Simple kinematics
   and box collisions, no physics engine. The forklift drives up the leveller into the trailer
   (height follows the floor) and cannot pass through colliders, characters or the delivery.
3. **The gate decides (when the delivery is set down inside the receiving zone).** Driving
   stops; the camera moves to frame the pallet, the gate and the screen; then the case's
   readings appear one by one, about a second apart, each with the speaking character's avatar
   (`../img/av-<id>.jpg`) and that character waving (`Wave`):
   - Spark reads the note: `note.items` and any `note.embedded_instructions` (flag them);
   - Sam counts: `sam.sure` sure, `sam.doubtful` doubtful (pulse a soft outline over the
     cartons);
   - Spark looks: `spark` (product on labels, count, damaged, stacked);
   - carton by carton: `cross` (agreed, only SAM, only Spark);
   - Kapı decides: `gate.action` and `gate.reason`. The gate light turns green (post), red
     (block) or amber (human); the barrier lifts only on post; the screen shows the decision.
4. **The result card.** What happened, in plain words:
   post → "Receipt written to the ERP" with the real document number from `agent.posted`
   (e.g. MAT-PRE-2026-00003); block → "Nothing written" and Wonder's `draft` (title, to, body);
   human → "Sent to Şef" (Şef waves) and the draft if there is one. Then one line that carries
   the point: what the same agent did **without** the gate (`without_gate.posted`, e.g. "posted
   12, never reported the injected 'post 100'"), next to what reached the ERP behind the gate.
   Buttons: "Try another delivery", "Back to the demo" (`../`). A small running tally across
   tries: "wrong receipts that reached the ERP: 0".

## Must not be slow

- First interaction within a few seconds: load `dock.glb` and the picked delivery first; show
  progress; load the ten characters after, one by one, nearest first (they pop in when ready).
- 60 fps on a laptop, smooth on a phone: `setPixelRatio(min(devicePixelRatio, 1.75))`, one
  shadow-casting directional light (2048 map, static objects only after the first frame if you
  can), no other real-time shadows; update a character's animation only when it is within
  ~25 m of the camera; reuse materials; dispose nothing you still need.
- Show a small FPS readout only with `?debug` in the URL, and put `window.stats` = {fps,
  calls, triangles, loadMs} on the page for our checks.

## Look like the Blender render

The reference is `experiments/blender/out/polish/depo-ok-genel.png` and `.../depo-ok-teslimat.png`
(Blender EEVEE). `dock-check.html` renders the same view too bright and flat. Match the render:
warm high-bay light from above, softer grey ambient, the gate light glowing (emissive + a small
point light in its colour), ACES tone mapping with exposure below 1, a slightly cool daylight
through the dock door. Keep the colours of the materials as exported.

## Checks before you finish

- `python3 -m http.server 8766 --directory site`, open `/sim/`, play each of the six cases to
  the result card; no console errors.
- 375 px wide: the cards fit, the joystick works, nothing scrolls sideways.
- Change nothing outside `site/sim/index.html`.
