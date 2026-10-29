# Muse Code task: reading cards at work, a bigger forklift, a clear pickup

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, looking at the reading cards during a decision: the moves should look better; Spark's
picture with a "reading the note" animation and then its output, Sam with a counting icon and
animation, glass behind, and bigger pictures so it is clear who is speaking. Then, after playing: the forklift should be
bigger, it isn't clear whether you picked the pallet up.
(Her other note, that the characters with nothing to do look like they are just standing
around, is the rooms task: `docs/muse-code/dock-rooms.md`.)

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it). Do not run commands or write probe scripts: this run cannot approve them. Read the
file, edit it directly, and stop; we run checks ourselves (`experiments/web/sim_test.mjs` must
still print ALL OK).

Rework the reading cards (`#reads`, `readCard` and the five steps in `startDeciding`). Keep the
step timings (600, 1700, 2800, 3900, 5000 ms, result at 6800 ms), the facts and the texts each
card ends with; what changes is how each card arrives and looks.

## Look

- Dark frosted glass, like the demo site: `rgba(11,18,38,.68)`, `backdrop-filter: blur(16px)
  saturate(1.3)`, a fine `rgba(255,255,255,.14)` edge, radius 18px, white text. No white cards.
- The character's picture **large**: a 56 px round avatar (`../img/av-<id>.jpg`, 48 px on
  phones) with a 3 px ring in the character's colour (Spark `#f97316`, Sam `#3b82f6`, Kapı
  `#a16207`), and its name in that colour above the title, so it is clear at a glance who
  speaks. "Carton by carton" shows Sam and Spark overlapping.
- While a card's character works, its avatar ring pulses softly.

## Each card: first the work, then the result

Every card arrives (slide and fade in, as now) showing the character **at work** with a small
animated icon in the character's colour and a short "…ing" line, for about 0.7 s; then the
result replaces that line with a soft cross-fade. Inline SVG icons drawn in the page, no emoji,
no image files.

| step | at work (≈0.7 s) | then |
|------|------------------|------|
| Spark reads the note | a small paper note whose text lines are highlighted one after another by a scan line; "Reading the note…" | the note's line as now; injected instructions appear after it, each with a small red "set aside" tag |
| Sam counts | a tally/counter icon, and the number counting up from 0 to Sam's total (sure + doubtful) in large digits; "Counting the cartons…" | "N sure, M doubtful", the numbers large |
| Spark looks at the pallet | a magnifier gliding over a tiny carton stack; "Looking at the pallet…" | labels, cartons seen, damage, stacking as small chips (damage / stacked / not all visible chips in amber) |
| Carton by carton | the dots appear one by one, quickly | "A agreed, S only SAM, P only Spark" |
| Kapı decides | a small traffic light whose three lamps blink in turn; "Checking the rules…" | the decision word large in its colour (POST / BLOCK / ASK ŞEF), the reason under it; the card gets a coloured left edge and a faint glow of that colour |

`prefers-reduced-motion`: no animations; each card shows its result directly.

## Keep

- The 3D actions (`wave`, the outline over the cartons, the gate light, the screen, the
  barrier) at the same moments.
- On phones the cards stay at the bottom, compact (only the latest two fully visible, the
  older ones collapsed to a single line with the avatar and the title).
- Don't touch the result card or the deciding camera.

## A bigger forklift

The characters are now 1.5× larger and the forklift looks like a toy beside them. Make the
forklift (its model, the cab view geometry, the collision footprint) about 1.35× larger, and
keep every piece of geometry consistent: the fork length and the distance at which a pallet
engages, the set-down distance ahead of the forklift, the collision footprint against the
walls and the trailer, the driver's-seat eye height, the chase camera distance. The pallet and
the cartons keep their real size (the pallet must still fit the yellow zone as now). Make sure
the forklift still fits through the dock door up the leveller into the trailer and can turn
in the yard.

Expose the two distances our test needs on the `?test` hook: `window.__sim.FORK = { pick, set }`
(how far behind the pallet's centre the forklift's origin must stand to pick it up, heading at
it, and how far ahead of the origin the pallet lands when set down; today 1.8 and 1.19).

## A clear pickup

Picking the pallet up must be unmistakable, from the chase view and from the driver's seat:
- the forks visibly lift with the pallet (as now) and the pallet gets a brief bright outline
  pulse in the zone's yellow;
- a HUD chip appears and stays while carrying: "Pallet on the forks · 12 cartons" (the case's
  note quantity) with a small pallet icon, and turns into "Set down in the yellow zone" when the
  forks are over the zone;
- a failed attempt (forks not lined up) says why in the hint: "Line up straight with the
  pallet" or "Get closer";
- setting it down: the chip goes away and the zone's tape glows once.
No new sounds.

## Checks we will run

- `node experiments/web/sim_test.mjs` (it will read `window.__sim.FORK`): all six cases, ALL OK.
- Screenshots while driving (chase and seat views), at pickup, and while deciding.
- Don't move or re-time the characters (another change handles them).
- Desktop frame rate does not drop. Change nothing outside `site/sim/index.html`.
