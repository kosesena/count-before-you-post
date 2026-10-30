# Muse Code task: the result card becomes a slim strip

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena did not like the result card on the right ("Sent to Şef"): too busy. Two rounds of Muse
Image directions (`experiments/mockups/hero-result-*.png`) did not land either. The feed on the
left already tells the whole story, so the card repeats it; the 3D scene (and the meeting at
the table) should stay in view. Agreed with Sena: the big card goes, the result becomes a slim
glass strip under the scene, details open on a tap.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it, including the result card `#result` / `showResult`, the agent run feed and the
meeting at the table). Do not run commands or write probe scripts: this run cannot approve
them. Read the file, edit it directly, and stop; we run the checks ourselves
(`experiments/web/sim_test.mjs` must still print ALL OK: it reads the text of `#result` and
expects "written to the ERP", "Nothing written" or "Şef" in it, so keep `id="result"` on the
new strip and keep those titles). Do not touch `site/sim/models/`. Everything stays English.

## The strip

Replace the right-hand card (`#resultWrap` / `#result`) with one slim strip, centred at the
bottom of the free area (between the feed panel on the left and the right edge on desktop):

- Same dark frosted glass as the feed (`rgba(11,18,38,.68)`, blur 16px saturate 1.3, a fine
  `rgba(255,255,255,.14)` edge, radius 18px), max width 720px, height about 64px on desktop,
  a 3px left edge in the decision's colour (`--dpost`, `--dblock`, `--dhuman`). Calm,
  aligned, plenty of air; no icons beyond the ones listed, no badges, no images.
- Left: Kapı's small round avatar (32px), then the decision as one word in its colour,
  medium weight, letter-spaced: POST / BLOCK / ASK ŞEF.
- Middle, one line (ellipsis when it does not fit): the title as today ("Receipt written to
  the ERP" / "Nothing written" / "Sent to Şef") in white, then a thin "·" and
  `firstSentence(G.cs.gate.reason)` in grey.
- Right: "Try another delivery" (the one filled button, the site's orange) and a quiet
  chevron button "Details" (`aria-expanded`).
- The strip rises in (slide up 12px and fade, 300ms) when the result shows;
  `prefers-reduced-motion` just shows it.

## Details (on tap, above the strip)

"Details" opens a small panel of the same glass directly above the strip (same width, max
height 50dvh, scrolls inside), with, in this order and nothing more:
1. The two lines that were the tiles: "Without the gate · <as today>" and "Behind the gate ·
   <as today>", each one line, the first in red when it was a wrong receipt (as today's
   `.v-tile.without.bad`); "Without the gate" stays a button that opens the feed's "Without
   Kapı" tab.
2. When `G.cs.signoff` exists: one green line "Şef approved <quantity> · <document>" (from
   `G.cs.signoff.decision` and `G.cs.signoff.posted[0]`), with a grey "(follow-up run)".
3. Wonder's draft as today's `<details>` (unchanged content), when there is one.
4. The full gate reason, when it is longer than the first sentence.
5. "Back to the demo" as a quiet link, and the tally "wrong receipts that reached the ERP: N".
Tapping "Details" again, or outside the panel, closes it. Esc closes it.

## Phones (max-width 640px)

The strip spans the width (left/right 10px, bottom 10px + safe area), two lines tall at most:
first line the decision word and the title, second line the reason clamped to one line;
"Try another delivery" becomes a compact button on the right of the first line, "Details"
the chevron next to it. The details panel opens as a sheet above it (max 60dvh). The feed
strip at the top and this strip at the bottom must never overlap; tap targets at least 36px.

## Keep the scene in view

With the big card gone, the deciding camera and the table camera frame their subject in the
middle of the free area above the strip (desktop: between the feed panel and the right edge;
phones: between the feed strip and the result strip). Adjust only the framing values for the
result phase; the driving cameras stay as they are.

Keep everything else: the result logic and texts, `G.wrongCount`, the again button's
behaviour (now on the strip), the tally chip, focus moving to "Try another delivery" when
the result shows, no sound. Change nothing outside `site/sim/index.html`.
