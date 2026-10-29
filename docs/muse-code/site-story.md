# Muse Code task: the page as a story in chapters

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena chose direction 3, "story", of four designs Muse Image drew for the rest of the page
(`experiments/mockups/hero-rest-*.png`), and, for the cast, horizontal cards that alternate
sides, the way the crew is introduced in her earlier project's README.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote it).
Look at `experiments/mockups/hero-rest-story.png`: the direction Sena chose. Keep the hero as it
is. Rebuild everything below it as a story told in numbered chapters, in the hero's dark,
cinematic look (deep navy, frosted-glass panels, the drawn characters), reusing the content
and render functions the page already has: no fact, section or interaction may be lost, and
nothing new may be invented. Do not touch `site/sim/`, `site/character.html` or data files.

## Structure

A thin progress line down the left edge (desktop) that fills as you scroll and marks the
chapter you are in. Each chapter: a big chapter number ("01"), a title, one short intro line,
the character who does that step standing beside it (`data.hero.tools[id]` where there is one,
otherwise the character's `cutout`), then the existing content for that step in glass panels.

- **01 · The note** (Spark; Wonder and Rover appear in it): how the note is read, the injected
  instruction and the PDF's invisible text (as the deliveries show them), and the existing
  "second reader on two hosts" table.
- **02 · The count** (Sam): SAM's masks and the carton-by-carton check (the existing camera /
  masks / cross views of the cases).
- **03 · The receiver** (Voice): the existing voice clips and the driver-and-receiver dialogue
  cards.
- **04 · The gate** (Kapı, with Şef): the four headline numbers (`renderStats`), and the whole
  existing "Deliveries at the dock" section: language selector, dock views, case tabs, each
  case's readings, gate rules, Wonder's draft, the agent with and without the gate. This is the
  heart of the page: give it room.
- **05 · An agent we did not write** (Ada): the existing outside-agent section with its big 0.

Put a "Drive the dock →" call to action at the end of chapter 04 as well.

## The cast, after the chapters

Replace the old group picture (`#castImg`) with `data.cast_video` (autoplay, muted, loop,
playsinline, the poster, no controls; a still poster only with `prefers-reduced-motion`).
Then "Meet the cast" as **horizontal cards, one per row, alternating sides**: the character's
`cutout` large on the left for the first, on the right for the next, and so on; on the other
side the name, model and status, their `line` directly on the card's colour (`bg`, text colour
by luminance as now), and one bold closing line. Use the character's first `profile.jobs`
entry for that bold line. Each card links to `character.html?id=<id>` ("Open profile →").
Keep the per-character hover effects you made (Glimmer's sparkles and the rest). On phones the
picture goes above the text.

## Checks

- Light and dark theme (the chapters stay dark in both; text readable), desktop and 375 px
  (no sideways page scroll), four languages via the selector, no console errors.
- Every element id that scripts or links use still exists (`#h-dock`, `#h-cast`, `#langSel`,
  `#tabs`, `#case`, `#voice`, `#dialogue`, `#outside`, `#secondTable`, `#stats`), so links like
  `index.html#h-cast` and the language switch keep working.
- Change nothing outside `site/index.html`.
