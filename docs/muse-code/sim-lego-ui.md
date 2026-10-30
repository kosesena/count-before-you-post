# Muse Code task: the simulator's interface as LEGO plates

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Muse Image redrew the whole dock as LEGO (`experiments/lego_dock.py`,
`experiments/mockups/lego-*.png`). Sena on `lego-rooms.png`: "I love it, let's try to make
exactly this". The 3D world (studded baseplate floor, brick walls, LEGO racks and forklift) is
the dock session's work in `dock.glb`; this task is the interface on top of it, as in that
picture: grey LEGO plates with studs along the edges, the tiles as framed bricks, glossy
plastic buttons. The result card stays (in the picture it is a LEGO plate); the earlier idea
of turning it into a strip (`docs/muse-code/sim-result-strip.md`) is dropped.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it). Do not run commands or write probe scripts: this run cannot approve them. Read the
file, edit it directly, and stop; we run the checks ourselves
(`experiments/web/sim_test.mjs` must still print ALL OK). Do not touch `site/sim/models/`.
Everything stays English; no texts change, no data changes, no sound. Only the look.

## The look: LEGO plates

Restyle every panel of the interface as a dark-grey LEGO plate (the reference picture shows
this exactly):

- **Plate**: the panels (the agent run feed `#feed`, the reading cards `.read`, the result
  card `#result`, the intro dialog, the note card, the HUD chips, the speech bubbles) become
  solid plastic instead of frosted glass: background `#3a3f47` (dark bluish grey), a 2px
  darker edge `#2a2e35`, radius 14px, a subtle top highlight
  (`inset 0 1px 0 rgba(255,255,255,.12)`) and a soft drop shadow, white text.
- **Studs**: a row of round studs along the panel's edges (top and bottom on wide panels, all
  four sides on the feed and the result card, like the reference), drawn with CSS only: a
  repeating `radial-gradient` of a 10px stud every 16px, each stud a slightly lighter grey
  with a tiny highlight and shadow so it reads as raised plastic. Keep text clear of them
  (padding). On phones (max-width 640px) studs only along the top edge, 8px every 13px.
- **Tiles inside panels** (the feed rows, the result card's two "Without / Behind the gate"
  tiles, the draft `<details>`, the tabs): flat lighter plates `#4a505a` with a 1px darker
  edge, radius 10px, no studs (smooth tiles). The highlighted tile ("Behind the gate", the
  gate row) gets a thick 4px frame in the decision colour like a yellow LEGO frame in the
  picture (`--dpost`, `--dblock`, `--dhuman`), the other tile a light grey 4px frame.
- **Buttons**: glossy plastic: the primary (Try another delivery, Start) the site orange
  `#f97316` with a lighter top half (a hard-stop linear gradient), 2px darker bottom edge,
  radius 10px; secondary buttons the light-grey tile style. Pressed: moves 1px down, the
  bottom edge shrinks.
- **Badges** (ASK ŞEF, POST, BLOCK): a yellow/green/red 1x2 brick: solid colour, darker
  edge, two tiny studs on top drawn with radial gradients.
- **Ticks** in the feed (✓ / ✓✓): a small green 1x1 round tile behind the ✓✓ like the green
  check bricks in the picture.
- **Fonts**: a rounded, chunky sans for headings (`"Nunito", "Arial Rounded MT Bold",
  system-ui`, loaded from Google Fonts with `display=swap`, weights 700/800), body text
  stays as now.
- The speech bubbles over the heads become small plates (no studs) with the colour edge as
  now; the tail stays.

## Keep

All layout, sizes, positions, behaviours, animations, timings, tabs, playback controls,
`prefers-reduced-motion`, the phone layouts and every test hook stay as they are. Contrast:
all text at least 4.5:1 on its plate. Performance: CSS only, no images, no extra DOM per
stud. Change nothing outside `site/sim/index.html`.
