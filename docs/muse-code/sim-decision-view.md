# Muse Code task: the decision, seen clearly and told beautifully

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
After the walking round (`docs/muse-code/sim-actors.md`) the walkers arrive where they should,
but the now larger characters stand between the deciding camera and the pallet, the gate's
screen still shows a baked "KAPI: GEÇTİ" whatever the decision, and Sena found the reading
cards and the result card plain: "the info screen should be much nicer".

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it). Do not run commands or write probe scripts: this run cannot approve them. Read the
file, edit it directly, and stop; we run checks ourselves (`experiments/web/sim_test.mjs` must
still print ALL OK: it finds the result text "written to the ERP", "Nothing written" and
"Sent to Şef", so keep those three headings' words).

## 1. The deciding view

What we see now, during `deciding`, from the camera at `px -4.6, py -2.4, pz 3.3`: Voice
(home `[-4.6, 2.1]`) fills the left foreground, Glimmer (home `[1.0, 0.5]`) covers the pallet on
the right, Şef stands in front of Sam, and the name labels of Kapı/Glimmer and Şef/Sam overlap.

- Frame the pallet in the zone, the walker(s) beside it (or Kapı at the barrier), the gate's
  light and the gate's screen, with **no character between the camera and those**. Do it by
  moving the deciding camera (higher and further back is fine, a gentle three-quarter view
  from the dock floor's front) and, where still needed, a home position by up to a metre and a
  half; keep the yard tidy and symmetric.
- During `deciding` and `done`, show only the labels of the characters acting in this case
  (and Kapı's); hide the others, and make sure the shown labels don't overlap each other.
- The deciding camera must also work on a 390 px wide phone in portrait (the reading cards are
  at the bottom there): the pallet and the walker stay in the upper part of the screen.

## 2. The gate's screen

`drawScreen` paints a canvas plane "just in front of the baked display", but the camera sees the
display's baked texture instead ("KAPI: GEÇTİ, İrsaliye 12 · Sayılan 12 …", green) in every
case, even when Kapı blocks or asks Şef. Make the canvas the visible face of that display from
the side the cameras see it (position it on that face, matching its size and angle, or replace
the baked display's material map with the canvas texture), so it shows "waiting for the
pallet" and then POST / BLOCK / ASK ŞEF with the reason. Keep its look: a dark screen, the
word large in the decision's colour.

## 3. The info screens: the reading cards and the result

Restyle them to match the demo site (`site/index.html`): **dark frosted glass** (deep navy
`rgba(11,18,38,.72)` with `backdrop-filter: blur(16px) saturate(1.3)`, a fine 1px
`rgba(255,255,255,.14)` edge, radius 18–22px, soft shadow), white text, the decision colours
(post `#4ade80`, block `#f87171`, human `#fbbf24`) as accents, a clean sans with clear sizes.
No plain white cards anywhere in the HUD (the intro screen already has its own look; leave
it).

Reading cards (`#reads`, `readCard`):
- Compact glass cards that slide in one by one (as now), each with the character's round
  avatar (`../img/av-<id>.jpg`) ringed in that character's colour, the title, and the content
  in short form; numbers in bold; the "carton by carton" dots stay.
- "Kapı decides" is the last and strongest card: a coloured edge and the decision word large.

The result (`#result`, `showResult`): today it is a long white card with a wall of text. Make
it a verdict screen, read in two seconds:
1. Top: the verdict as the headline ("Receipt written to the ERP" / "Nothing written" /
   "Sent to Şef"), large, in the decision's colour, with Kapı's figure (`../img/hero-kapi.webp`
   does not exist; use `../img/fig-kapi.webp`) or a coloured badge beside it; for a post, the
   quantity and the receipt number as a big figure ("12 cartons · MAT-PRE-2026-00007").
2. One line: the gate's reason, in plain text, shortened to its first sentence if it is long
   (the full reason stays available in the expandable part below).
3. The point of the demo as **two side-by-side tiles**: "Without the gate" (what the agent did:
   posted N, or asked Şef, or posted nothing) and "Behind the gate" (what reached the ERP),
   the first in the block colour when it posted something wrong, the second in the decision's
   colour. On phones they stack.
4. Wonder's draft collapsed in a `<details>` ("Read Wonder's draft · Dispute to the supplier"),
   opening to the full text in a calm, readable letter style; the full gate reason goes there
   too.
5. The buttons "Try another delivery" (primary) and "Back to the demo", and the tally.

The result card no longer covers the pallet and the walker: on desktop place it at the side
(right, about 440px wide, full height scroll if needed) so the scene stays visible; on phones it
is a bottom sheet that starts at about 60% of the height and scrolls.

Keep every fact the cards show today; invent nothing. Keep keyboard focus on "Try another
delivery" when the result appears, and `prefers-reduced-motion` without the slide-ins.

## Checks we will run

- `node experiments/web/sim_test.mjs`: all six cases, ALL OK, no console errors.
- Screenshots of each case during `deciding` and at `done`, desktop 1600×900 and phone 390 px:
  pallet and walker visible, no character in front, the screen showing the real decision,
  labels not overlapping, the cards in dark glass.
- Change nothing outside `site/sim/index.html`.
