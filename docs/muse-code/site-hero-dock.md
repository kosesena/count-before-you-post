# Muse Code task: the dock hero, and a touch of life on the cast cards

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena chose direction 3 ("dock") of four hero designs Muse Image drew
(`experiments/mockups/hero-*.png`, `experiments/site_mockups.py`), and this tagline.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote
it). Look at `experiments/mockups/hero-dock.png`: the direction Sena chose for the top of the
page. Change only the header (`.hero`, the "Built with Muse" band) and the cast cards'
effects. Everything else on the page stays as it is.

## 1. The hero, after hero-dock.png

- A full-width hero over `data.hero.src` (the real dock render, alt `data.hero.alt`), darkened
  with a gradient so white text reads (darker on the left where the text is, lighter on the
  right where the truck and the cast are). It bleeds to the edges of the window; the content
  inside keeps the page's max width.
- On it, in white: the kicker pill as now, the title "Count Before You Post", and this tagline,
  word for word:
  "A verification gate between AI agents and the ERP. Before a goods receipt is written, the
  delivery note, the camera, the receiver's voice and a second model must agree. If they
  don't, nothing is written and a person decides."
  Make "A verification gate between AI agents and the ERP." the strong part.
- A primary button **"Drive the dock →"** linking to `sim/` (the simulator, being built), and a
  quieter link "See the six deliveries" to `#h-dock`.
- Along the bottom of the hero: "Built with Muse" and the seven tools as **seven equal glass
  cards in one row** (frosted: translucent white, `backdrop-filter: blur`, a fine light
  border, a soft inner highlight), each with the character's avatar (`img/av-<id>.jpg`: spark,
  sam, voice, iris, ada, wonder, spark-open), the tool name and its one line. Seven columns on
  wide screens; on narrow screens they scroll sideways inside their own row (scroll-snap), the
  page itself never scrolls sideways. No card alone on a second row.
- The old cast group picture (`#castImg`) and the stats row stay, just below the hero.

## 2. The cast cards: each character's own touch, on hover (and on tap on phones)

Keep the cards exactly as they look now. Add, per character, a short light effect over the
card while the pointer is on it, drawn with one small `<canvas>` overlay or CSS only (no
libraries), in the character's own colours:
- **Glimmer**: soft purple and white sparkles that twinkle up around her (Sena asked for this
  one first; make it lovely).
- Spark: a few orange sparks · Voice: soft sound-wave rings · Sam: a thin scan line passing
  down the portrait · Kapı: the traffic light's green glow · Wonder: a few floating paper
  flecks · Rover: small travel dots along a dashed path · Iris: paint-coloured dots · Ada: tiny
  `</>` and `>_` glyphs · Şef: a check mark that draws itself.
- And "glass here and there": the status pill and the name row get a frosted-glass look, and on
  hover a soft diagonal glass sheen sweeps across the card once.
- Effects start on `pointerenter` / tap and fade out on leave; at most one card animates at a
  time; none at all when `prefers-reduced-motion: reduce`; nothing runs while no card is
  hovered (no idle animation loop).

## Checks

- Light and dark theme, desktop and 375 px (no horizontal page scroll), no console errors.
- Change nothing outside `site/index.html`.
