# Muse Code task: the cast as free-standing figures beside glass panels

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Muse Image drew two designs for the cast section (`experiments/mockups/hero-cast-glass.png`,
`hero-cast-minimal.png`). Sena chose the layout of the first (the figure stands free, no colour
or box behind it; colour only in the text's glass panel, glass dominant, premium) with the
panels styled like the second. Muse Image wrote "Four AI agents" in its drawing; the cast has
ten, and the page keeps all ten.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote it).
Do not run commands or write probe scripts: this run cannot approve them. Read the file, edit
it directly, and stop; we run checks ourselves.

Redesign only the "Meet the cast" cards (`renderCrew` and the `.member` styles). Everything
else on the page stays as it is, including the cast video above the cards, the `#h-cast`
heading and the `#roles` line.

Look at the two images first:
- `experiments/mockups/hero-cast-glass.png`: the **layout** Sena chose. The character stands
  free on the page, large, with **no box, card, frame or colour behind the figure**; only a soft
  floor shadow under its feet and at most a very faint glow of its colour. The rows alternate
  sides (zigzag), and the figure overlaps the panel's edge a little.
- `experiments/mockups/hero-cast-minimal.png`: the **panel style** Sena chose. A frosted-glass
  panel (backdrop blur, a fine bright 1px edge, rounded corners about 24px) lightly tinted with
  the character's colour as a soft gradient from one side, a small uppercase eyebrow in the
  character's colour, the name large and bold in white, "Model · …" in muted text, the quote,
  one bold line in a light tint of the character's colour, and "Open profile →" in that colour.
  Ignore that drawing's outer box around the figure: Sena does not want it.

## Content (all ten characters, in data order, nothing invented)

- The figure: `data.hero.figures[m.id]` (all ten drawn in the hero's light, transparent PNG
  converted to WebP); fall back to `m.profile.cutout`, then `m.portrait`.
- Eyebrow: the status (`STATUS_TEXT[m.status]`), small uppercase, in the character's colour.
- Name: `m.name`. Under it: `m.model`.
- Quote: `m.line`, in quotation marks.
- Bold line: the first `m.profile.jobs` entry (as now).
- "Open profile →"; the whole row links to `character.html?id=<id>` as now.
- Colour: `m.colour` for the accents. Many colours are dark (Voice's navy, Ada's, Kapı's
  cardboard); for text use a lightened version of the colour (mix it with white until it reads
  on the dark glass, e.g. `color-mix(in srgb, var(--c) 55%, white)`), and keep the panel's tint
  subtle (around 18–30% of the colour at its strongest corner, fading to clear glass).

Remove the old full-colour card background (`--cardbg`, the `.dark` variant, the speech-bubble
look) from the cast cards. Keep the per-character hover effects you made (the canvas `fx`
sparkles and the rest), but they must sit on the panel, not draw a box around the figure.
Hover: the figure lifts a few pixels and the panel's edge brightens; no movement with
`prefers-reduced-motion`.

## Layout

- Desktop: each row is the figure (about 38% of the width, figure height up to about 420px,
  bottom-aligned on its shadow) and the panel (the rest), alternating sides; generous vertical
  space between rows (about 56px), the column no wider than the page's other chapters.
- Phones (below about 720px): the figure above the panel, centred, height up to about 300px,
  overlapping the panel's top edge a little; no sideways page scroll at 375px.
- The section keeps the page's dark look in both themes.
- Images: `loading="lazy"`, `decoding="async"`, `alt` = the name.

## Checks we will run

- Desktop 1440 and 375 px, light and dark theme, four languages via the selector, no console
  errors, no sideways scroll.
- Every element id the scripts and links use still exists (`#h-dock`, `#h-cast`, `#langSel`,
  `#tabs`, `#case`, `#voice`, `#dialogue`, `#outside`, `#secondTable`, `#stats`, `#crew`,
  `#roles`).
- Change nothing outside `site/index.html`.
