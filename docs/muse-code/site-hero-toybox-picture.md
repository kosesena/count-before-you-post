# Muse Code task: the page opens with the toy box picture

The prompt below was given verbatim to Muse Code (`muse exec`).
Sena (31 Oct): "the home page should start directly with this" — the demo video's toy box,
drawn by ChatGPT from our Muse Image cast (`experiments/mockups/story-0-box-chatgpt.png`,
saved for the site as `site/img/toybox.webp`, 1659×948). Because ChatGPT drew it, the page
must say so, and the Muse Image card can no longer claim every character on the page.

---

You are working in the repository `count-before-you-post`, on `site/index.html` (you wrote
it). The page must open with a new picture, `img/toybox.webp` (1659×948): a child's hands
holding a blue toy box on a wooden table; the box reads "COUNT BEFORE YOU POST · Built with
Muse · WAREHOUSE 01" and shows the ten figures in front of a warehouse. It was drawn by
ChatGPT from our Muse Image characters.

## 1. The opening picture

- Add it as the very first thing on the page, above the current `<header class="hero">`:
  full window width, as tall as the window allows on desktop (about 100vh, never cropping
  the box's title or the figures: crop only the wooden table at the edges, centred on the
  box), on a warm wood-brown background that matches the table for any letterboxing.
- `alt`: "A child's hands hold the Count Before You Post toy box: a blue box with the ten
  figures in front of a warehouse dock."
- The picture already shows the title, so the visible `<h1>` stays where it is in the hero
  below; do not add a second title over the picture.
- A small, quiet credit in the bottom-right corner of the picture, white on a soft dark pill,
  readable but not loud: "Toy box picture: ChatGPT (OpenAI), drawn from our Muse Image cast".
- A small "scroll" cue at the bottom centre (a chevron that gently bobs; still when
  `prefers-reduced-motion: reduce`), linking to the hero below.
- Load it eagerly with `fetchpriority="high"`, width and height attributes set, so the page
  doesn't jump.

## 2. One caption

In the "Built with Muse" row, the Muse Image card (`data-tool="iris"`) says "drew every
character on this page". That is no longer true. Change its line to exactly:
"drew the cast; ChatGPT drew the toy box from it"

## Keep

- Everything else as it is: the hero below (with its dock picture, kicker, h1, lede, both
  "Drive the dock →" links to `sim-lego/`, the seven tool cards), the progress nav, the
  chapters, the footer, every id the script uses. The progress nav must not cover the
  opening picture's box.
- Change nothing outside `site/index.html`; no libraries.

## Checks

- Light and dark theme at 1440×900 and 1280×800, and 375 px wide: no console errors, no
  horizontal page scroll, the box's title and all ten figures fully visible in the picture.
