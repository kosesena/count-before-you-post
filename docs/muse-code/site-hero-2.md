# Muse Code task: the hero, closer to the chosen design

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena's notes on round 1: the background must be the picture Muse Image drew for the chosen
design, not the Blender render; the characters on the cards must be drawn for that design,
from their reference portraits. Both now exist: `experiments/site_mockups.py background`
redrew the chosen scene without text, and `experiments/hero_characters.py` drew the seven
tool characters in its light from their own portraits.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote
it). Compare it with `experiments/mockups/hero-dock.png` (the design Sena chose) and change
only the hero.

- `data.hero.src` is now the background Muse Image drew for that design (a dock at dusk,
  darker on the left). Use it as it is: no extra filter that changes its colours; only a soft
  gradient where the text sits, as in the mockup.
- `data.hero.tools` maps each tool's character id (spark, sam, voice, iris, ada, wonder,
  spark-open) to that character drawn for these cards (transparent WebP, full body, lit like
  the scene). On each of the seven glass cards use this picture instead of the current cutout,
  the way the mockup shows them: the character stands inside the upper part of the card, a
  little larger than the card's top edge (head may rise above it), the name and line on the
  frosted panel at the bottom of the card. Keep the hover growth (≈1.15× from the feet) and the
  links to `character.html?id=…`.
- Match the mockup's proportions: the cards taller than now, the seven in one row along the
  bottom of the hero, the title block on the left over the dark part of the picture, the
  "Drive the dock →" button as now.
- Mobile (375 px): the card row scrolls sideways inside itself, the page never does.

Change nothing outside `site/index.html`. No console errors in light and dark theme.
