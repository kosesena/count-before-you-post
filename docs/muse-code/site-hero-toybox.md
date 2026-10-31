# Muse Code task: the hero as the toy box

The prompt below was given verbatim to Muse Code (`muse exec`).
Sena wants the top of the site to look like the demo video's toy box (the video's box frames
are in `experiments/mockups/story-0-box-chatgpt.png` and `story-0b-open-chatgpt.png`; the
box designs drawn in HTML/CSS with the cast's real cut-outs are in
`experiments/mockups/box/box.html`). Her choices (31 Oct): the box is drawn in HTML/CSS with
the site's own Muse Image figures (no ChatGPT picture on the site, so "Muse Image drew every
character on this page" stays true), and only the hero changes.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote
it). Turn the hero (`<header class="hero">`, including the "Built with Muse" band) into a toy
box sitting on a wooden table. Everything below the hero stays exactly as it is.

Look first at `experiments/mockups/story-0-box-chatgpt.png` (the closed box: blue box, white
rounded title panel, "Built with Muse" under it, a round "WAREHOUSE 01" badge, a warehouse
picture printed on the box, the figures standing along the bottom) and
`experiments/mockups/story-0b-open-chatgpt.png` (the open box: each figure in its own clear
plastic bag in a cardboard compartment). Also read `experiments/mockups/box/box.html`: it draws
such a box in CSS with the real cut-outs; reuse its ideas, not its 3D tilt (the hero must be
flat and readable).

## The hero

1. **The table.** The hero's background is a warm wooden table top drawn in CSS (wood-grain
   gradients, warm afternoon light falling from the upper left, a soft shadow under the box).
   No new image files.
2. **The box lid** sits on the table, centred, the page's max width, slightly rounded corners,
   a thin lighter edge on top and a darker one on the right so it reads as a cardboard box.
   Its face is a deep blue printed box:
   - Printed on it, as the box's artwork, the existing dock picture (`data.hero.src`, alt
     `data.hero.alt`), cropped to the right two thirds, fading into the blue on the left.
   - A white rounded panel with the title "Count Before You Post" in a heavy rounded type
     (Nunito 900 from Google Fonts is fine, with system fallbacks), dark navy text.
   - Under it a smaller pill: "Built with Muse".
   - A round badge at the top right: "WAREHOUSE" small over "01" large.
   - The existing kicker pill, the lede (word for word as it is now, with its strong first
     sentence), and the two links ("Drive the dock →" to `sim-lego/` with its truck icon and
     the same click overlay as now, and "See the six deliveries" to `#h-dock`) stay, placed on
     the box face where they read clearly (white text on the blue part).
3. **The tray.** Directly under the lid, as if the box were open beneath it, a cardboard tray
   with **seven compartments in one row**, one per tool, in the current order (spark, sam,
   voice, iris, ada, wonder, spark-open), with the same links (`character.html?id=…`), the
   same figures (`data.hero.tools`, the `img/hero-<id>.webp` images) and the same name and
   one-line text as now, word for word. The line "Meta's models, on the Meta Model API and on
   open weights, do every step that needs AI." stays, as a small printed line on the tray's
   front edge.
   - Each figure stands in its compartment inside a **clear plastic bag** drawn in CSS:
     translucent, a few soft crinkle highlights and a crimped top edge, the figure clearly
     visible through it.
   - On hover / keyboard focus (and on tap on touch screens) the figure **lifts out of its
     bag**: it rises a little and comes in front of the bag, the bag stays; back on leave.
     Respect `prefers-reduced-motion: reduce` (no movement then, only a light highlight).
   - Name and line under each compartment, on the cardboard, readable.
4. **Themes.** In the dark theme it is the same table and box at evening light (darker wood,
   a warm lamp glow), not a different design. Text contrast must pass in both.
5. **Narrow screens.** Desktop is what matters; below 900 px the lid stacks its content and
   the tray scrolls sideways inside its own row (scroll-snap); the page never scrolls
   sideways.

## Keep

- Every id the script uses (`heroImg`, `driveBtn`, …) and the JS that fills the hero from
  `data.hero`; the progress nav, the chapters, the footer: unchanged.
- No new image files, no libraries; change nothing outside `site/index.html`.

## Checks

- Light and dark theme at 1440×900 and 1280×800, and 375 px wide: no console errors, no
  horizontal page scroll, all seven figures visible, all links working.
