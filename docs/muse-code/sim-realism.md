# Muse Code task: the simulator, realism round

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena's notes: it should feel real; driving like a real forklift, sound, and a driver's-seat
view (on a real forklift there is no windscreen: you look through the mast, under the overhead
guard, with the wheel and the levers in front of you).

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you wrote
it). Make the simulator feel real. Keep the intro, the decision sequence, the result card, the
`?test` hook (`window.__sim`) and the case buttons / `#startBtn` as they are:
`node experiments/web/sim_test.mjs` must still print ALL OK.

## 1. Driving like a forklift

- Rear-wheel steering: the forklift turns around its front (drive) axle, the tail swings out.
  Steering angle eases towards the input (it takes a moment to turn the wheel), up to ~70°.
- Inertia: it accelerates and brakes with a short ramp, coasts a little when you let go, and
  is slower and heavier with a pallet on the forks (top speed about 2/3, softer acceleration).
- The mast lifts and lowers at a hydraulic pace (≈0.35 m/s), not instantly; `Space` still
  picks up / sets down (the forks move to the right height first).
- Wheels turn with the speed; front wheels turn with steering if they are separate meshes in
  `forklift` (if not, skip).
- While carrying, the pallet sways very slightly when you brake or turn (a few millimetres,
  it settles quickly).

## 2. Sound (Web Audio, synthesised, no audio files)

A small speaker button, **off by default**; the choice is remembered (localStorage, in a
try/catch). When on: a low engine hum whose pitch and volume follow speed; a reverse beeper
while backing up; a short hydraulic whine while the forks move; a soft "clunk" on pick-up and
set-down; on the gate's decision a two-tone chime (rising for post, falling for block, a
neutral one for human). Everything quiet and pleasant, never harsh.

## 3. Driver's seat view

`C` now cycles three cameras: chase (default) → driver's seat → overview. The seat view sits
at the operator's eye height (≈2.0 m from the floor, a little behind the steering wheel) and
moves with the forklift. Build the cab from simple meshes in code, matching the forklift's
colours: a steering wheel with a knob that turns with the steering, the seat back edge at the
bottom of the view, the two front posts of the overhead guard at the sides, the guard's bars
across the top, the mast rails and the fork tips ahead, two lift/tilt levers to the right, and
a small dashboard: speed (km/h), fork height (cm), load (empty / 1 pallet). The view must make
lining the forks up with a pallet easy: the fork tips are visible.

On touch screens add a camera button next to Pick/Drop.

## 4. Light, closer to the Blender render

Compare with `experiments/blender/out/polish/depo-ok-genel.png` and
`experiments/blender/out/polish/depo-ok-teslimat.png`: warm light from the high-bay lamps
above, softer grey ambient, soft shadows under the forklift, the pallet and the characters
(one shadow-casting light is enough; soften with PCFSoft), the gate light's colour glowing on
the floor around the pole (a small coloured point light that follows the gate state), and a
cool daylight from the open dock door. Keep 60 fps on a laptop.

## 5. Phones

On touch devices (or `?lite`), load the characters from `models/lite/<name>.glb` (150k
triangles, 1K textures, ~1 MB each) instead of `models/<name>.glb`; same names and actions.

## Checks

- `node experiments/web/sim_test.mjs` → ALL OK; no console errors.
- `window.stats.fps` stays near 60 on a laptop with all ten characters loaded.
- 375 px: joystick, Pick/Drop and camera buttons reachable, no sideways scroll.
- Change nothing outside `site/sim/index.html`.
