# Muse Code task: the simulator's cinematic intro

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena chose direction 4, "cinematic", of four intro screens Muse Image drew
(`experiments/mockups/hero-sim-*.png`).

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you wrote
it). Look at `experiments/mockups/hero-sim-cinematic.png`, the direction Sena chose for the
intro screen. Change only the intro screen and the loading state; the game, the decision
sequence and the result card stay as they are, and the `?test` hook (`window.__sim`) must keep
working.

## The intro, after hero-sim-cinematic.png

- The 3D dock stays live behind it, with a dark vignette (darker at the left and bottom).
- Left: a large title "The receiving dock" in white, the three lines under it as now.
- "Pick a delivery": the six cases as chips in a glass panel (frosted, fine light border); the
  picked one is filled in the accent orange with a check mark.
- Bottom bar (glass): the loading line ("The dock is ready. Characters arriving… n/10") with a
  thin progress bar, the controls legend as small key caps (↑ ↓ ← → or WASD: drive · Space:
  pick up / set down · C: camera · R: restart), and "Back to the demo".
- Right: a bold orange "▶ Start" button, large.
- Bottom-left: three of the cast standing in front of the panel, the way the mockup shows,
  using the real cutouts `../img/cut-spark.webp`, `../img/cut-sam.webp`,
  `../img/cut-voice.webp` (transparent).

## Loading: a truck on the way

While `dock.glb` and the picked delivery load (before the dock is ready), show a slim loading
strip in the bottom bar with a small side-view truck (CSS/SVG) driving along it as the
progress fills, wheels turning; when ready it parks at the end and the Start button lights up.
The demo page sends people here with its own truck animation, so this continues the same idea.

## Checks

- `node experiments/web/sim_test.mjs` must still print ALL OK (it clicks the case buttons by
  their text and `#startBtn`: keep both).
- 375 px: the panel stacks, the chips wrap, the Start button stays reachable, no sideways page
  scroll; the three cutouts hide on narrow screens.
- Change nothing outside `site/sim/index.html`.
