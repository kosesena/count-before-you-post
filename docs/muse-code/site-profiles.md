# Muse Code task: characters you can open, and a button that drives

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena's requests: the characters on the hero cards without a background, growing on hover; a
click opens that character's page, like an ID card, with what they did during the project;
round profile photos as in `experiments/mockups/hero-editorial.png`; and an animated "Drive the
dock" button: when pressed, a truck drives across the middle of the screen until the
simulator opens.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote it)
and a new page `site/character.html`. Do not touch `site/sim/` (another task is changing it)
or any data file.

Every entry of `data.characters` (in `site/data.json` and `data-<lang>.json`) now has:
`cutout` (the character without background, transparent WebP), `avatar_large` (a square photo
for a round frame) and `profile` = { `tool`, `model_id`, `where`, `first_day` (YYYY-MM-DD),
`jobs` [..], `record` [..] }. Every line of `profile` is a measured fact: show them as given,
add nothing.

## 1. Hero tool cards (the seven glass cards in the hero)

- Replace each round avatar with the character's `cutout`, standing on the card's top edge so
  it rises out of the glass a little. Name and line stay on the frosted glass panel below it.
- On hover (focus too): the character grows smoothly (about 1.15×, from its feet), the glass
  brightens a touch. No motion with `prefers-reduced-motion`.
- The whole card is a link to `character.html?id=<id>` (ids: spark, sam, voice, iris, ada,
  wonder, spark-open).

## 2. Cast cards ("Meet the cast")

Keep how they look and their hover effects; make each card a link to its
`character.html?id=<id>` too (all ten), with a visible focus state.

## 3. `site/character.html`: one page per character, like an ID card

Loads `data.json` (and the language file if `?lang=` is given), finds the character by `id`.
In the page's style (same fonts, colours, light and dark theme), built around the character's
`bg` colour:
- **The ID card**: a large round photo (`avatar_large`, as round as the avatars in
  `hero-editorial.png`, with a ring in `colour`), the name, the status pill, and a compact
  table of fields: Tool (`tool`), Model (`model_id`, monospace), Runs on (`where`), First day
  on the job (`first_day`, written out as "26 October 2026"). A small "COUNT BEFORE YOU POST ·
  CAST ID" line on the card, like a badge.
- **In their own words**: `line`, directly on the colour (no bubble), as on the cast cards.
- **What they did**: `jobs` as a list.
- **On the record**: `record` as a list of facts, each with a small check mark.
- The full-figure `cutout` large on one side of the page (desktop), below the card on phones.
- Round avatars (`avatar`) of the other nine characters at the bottom, each linking to their
  page, the current one highlighted; and "← Back to the cast" to `index.html#h-cast`.
- Unknown `id`: a short message and the link back.

## 4. "Drive the dock →" moves

- The button itself is alive but calm: a soft shine sweeping across it every few seconds, and
  a tiny truck icon in it that rolls forward on hover.
- On click: instead of jumping, a full-screen overlay fades in (dark, the page's dock colours)
  and a stylised side-view truck, in CSS/SVG, drives from left to the middle with turning
  wheels and a little motion blur, while the line "Opening the dock…" shows; then the page
  goes to `sim/`. About 1.2 seconds in all; with `prefers-reduced-motion`, go straight to
  `sim/`. Pressing Back from the simulator must return to a normal page (no stuck overlay:
  handle `pageshow`).

## Checks

- Light and dark, desktop and 375 px (no horizontal page scroll), no console errors on
  `index.html` and on `character.html?id=` for all ten ids.
- Change nothing outside `site/index.html` and `site/character.html`.
