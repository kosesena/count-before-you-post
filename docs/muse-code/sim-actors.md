# Muse Code task: the responsible character walks to the pallet

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena's feedback on the simulator: every character just stands still whatever delivery you
pick; the one responsible for the case should go to the pallet or do something, and the
characters look tiny.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it). Do not run commands or write probe scripts: this run cannot approve them. Read the
file, edit it directly, and stop; we run checks ourselves (`experiments/web/sim_test.mjs` plays
all six cases to their result card and must still print ALL OK).

## 1. Bigger characters

The characters read as tiny next to the forklift and the pallet. Make every character 1.5×
its current height (`PEOPLE[].h`: 1.60 → 2.40, 1.75 → 2.62) and scale the contact-shadow blob
and the name label height (`updateLabels` uses 2.05 m) to match. Check that no character now
stands inside a wall, the trailer, the receiving zone's tape or the forklift's driving lane
from START to the trailer and to the zone; nudge a home position (`PEOPLE[].b`) by up to a
metre only where it is needed, and keep the layout symmetric and tidy.

## 2. The responsible character acts on the delivery

Every GLB has three clips: `Idle`, `Walk` and `Wave`. Today only `Wave` plays in place. Make
the character whose job the chosen delivery tests walk to the pallet when the forklift sets it
down in the zone (at the start of `startDeciding`), and act there:

| case       | who walks              | what they do at the pallet |
|------------|------------------------|----------------------------|
| `ok`       | Sam                    | counts (Wave) while Sam's card shows; Kapı waves when the barrier opens, in place |
| `wrong`    | Spark                  | looks at the labels (Wave) when "Spark looks at the pallet" shows |
| `eksik`    | Sam                    | counts (Wave) when "Sam counts" shows |
| `talimat`  | Kapı                   | steps in front of the barrier (not the pallet), faces the forklift, Wave when "Kapı decides" shows |
| `hasarli`  | Şef                    | comes to the pallet, Wave when the result says "Sent to Şef" |
| `belirsiz` | Sam and Spark          | both come, one on each side of the pallet, Wave together at "Carton by carton" |

How:
- Keep the decision sequence, its timings, its cards and its texts exactly as they are; the
  walking is added on top. Characters who don't act keep idling where they stand.
- Walking: crossfade `Idle` → `Walk` (about 0.25 s), move in a straight line on the floor at
  about 1.3 m/s, turned to face the direction of travel, then crossfade back to `Idle`, turn
  to face the pallet (or, for Kapı, the forklift) and play the action. Use a small
  per-character state (home, target, walking flag) updated in the main loop with `dt`; don't
  use timers for the motion itself.
- Target spot: beside the pallet, about 1.4 m from its centre, on the side that faces the
  deciding camera (it frames the pallet, the gate and the screen from `px = -4.6, py = -2.4`),
  never on the forklift's side (the forklift stays behind the pallet after it sets it down).
  Two walkers (`belirsiz`) stand on opposite sides, both visible from the camera. Kapı's spot
  is in front of the barrier (find it from `barrierMesh`'s position), on the dock side.
- If a walker could not arrive before its action time (a long way to go), it plays the action
  on arrival instead; never teleport during play.
- The walker must stay visible in the deciding camera's frame when it stands there: adjust the
  spot, not the camera, if it falls out of frame.
- Name labels follow the character's current position, not its home (`updateLabels` uses
  `p.b`).
- `mixer.update` must keep running for walkers even if the camera is more than 25 m away.
- "Try another delivery" and `resetScene` send everyone back home (walking back is nice, but
  if a new case starts they must be home and idle before the forklift starts driving; snapping
  home at reset is fine).
- `prefers-reduced-motion`: no walking; the responsible character appears at its spot
  directly, and still plays the action.
- Phones (lite models) get the same behaviour.

## 3. Test hook

Add the character records to the existing `?test` hook: `window.__sim.CHAR` (the `CHAR`
object), and give each record `x`, `y` (current floor position in the same coordinates as
`PEOPLE[].b`) and `walking` (boolean), so our test can check that the responsible character
reached the pallet.

## Checks we will run

- `node experiments/web/sim_test.mjs`: all six cases, ALL OK, no console errors.
- Screenshots of each case's result: the responsible character large, at the pallet (or the
  barrier), facing it, in frame; the others still at home.
- Frame rate on desktop does not drop (the walking adds no new models or shadows).
- Change nothing outside `site/sim/index.html`.
