# Muse Code task: premium cast cards

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena's request: the whole card takes the colour of the portrait's background, the character
sits at the bottom, and its speech sits above it, in a stylish way.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote
it). Change only the "Meet the cast" cards (`renderCrew` and the `.member` styles) and the
`roles` line under them. Everything else on the page stays exactly as it is.

Every entry of `data.characters` now has `bg`: the background colour of that character's
portrait (`portrait`, a square image with a soft studio backdrop in that colour).

## The new card

- **One colour, edge to edge.** The card's background is `bg`. The portrait sits at the
  **bottom** of the card, full width, and melts into the card: its top edge fades into `bg`
  (for example a CSS `mask-image` gradient on the image, or a gradient overlay in `bg`), so
  there is no visible seam between picture and card.
- **The speech on top.** Above the portrait: the name (large, bold), `model` and the status
  pill on one line, then `line` as an elegant speech bubble whose tail points down at the
  character. The bubble is a frosted, semi-transparent white (or dark on dark cards) with a
  soft shadow; the text stays readable on every card colour, including the dark one (Voice,
  `#18315d`): pick light or dark text per card from the colour's luminance.
- **Premium feel.** Generous padding, a larger radius, a subtle inner highlight or border, a
  gentle lift on hover (no motion when `prefers-reduced-motion`). No new external fonts or
  scripts.
- Keep `colour` as the small accent (the dot by the name). Keep the grid, the order, the alt
  texts and lazy loading.
- The `roles` line: remove "Coming soon … Glimmer only starts its second reading of the note
  later" (no character is "coming" any more); keep the other two definitions.

## Checks

- Works in light and dark theme, at desktop width and at 375 px (no horizontal scroll).
- Change nothing outside `site/index.html`.
