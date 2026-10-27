# Muse Code task: the demo page

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
What it produced and what had to be fixed afterwards is recorded in `docs/JOURNAL.md`.

---

You are working in the repository `count-before-you-post`. Read `README.md` first, then
`site/data.json` (every fact the page may show), then the current `site/index.html` (a plain
first version written by hand: it shows the right content but looks too sparse).

## Goal

Rewrite `site/index.html` from scratch as the public demo page of this project: a single,
self-contained static page (HTML, CSS and vanilla JavaScript in one file, no build step, no
frameworks, no external scripts). It loads `data.json` with `fetch` and renders everything
from it. It must feel alive and friendly, built around the cast of characters, while staying
clear and honest about what the system does.

## What the page must contain

1. **Hero.** The project name, one sentence on the idea ("an AI agent that can't write a
   number into the ERP until a camera has counted it"), the group picture `data.cast`, and the
   three numbers in `data.summary`: wrong receipts reaching the ERP without the gate
   (`wrong_without_gate` of `cases`), with the gate (`wrong_with_gate` of `cases`), and
   deliveries where the gate made the right call (`gate_right` of `cases`).
2. **Meet the cast.** One card per entry in `data.characters`, in that order: the portrait
   (`portrait`), the name, `model` (which Meta tool or role it is), a status label from
   `status` ("on duty", "done" = built part of this project, "coming" = not working yet), and
   `line` shown as a speech bubble: the character introducing itself in the first person. Use
   each character's `colour` as its accent. Glimmer's status is "coming": the page must not
   suggest Glimmer is already working.
3. **Six deliveries at the dock.** A selector for the six entries of `data.cases` (use
   `title`, and colour each by `gate.action`: post = green, block = red, human = amber). For
   the selected case show:
   - `what`, and the camera image with a switch between `images.camera`, `images.masks`
     (SAM 3.1 masks: green sure ≥ 0.88, amber doubtful) and `images.cross` (Spark points sent
     back to SAM: green = both models found the carton, amber = only SAM, red point = only
     Spark); the delivery note image `images.note`;
   - the four readings, each with the avatar of the character who made it: the note
     (Spark: `note.items[0]`, and any `note.embedded_instructions` highlighted in red as a
     hidden instruction), the count (Sam: `sam.sure` sure, `sam.doubtful` doubtful), the
     look (Spark: `spark`), and carton by carton (`cross`: agreed, only SAM, only Spark,
     doubled);
   - the gate (Kapı's avatar): the decision `gate.action` with `gate.reason`, and the rule
     list `data.rules` in order, showing which rules passed, which one decided (`gate.rule`)
     and which were never reached. When the action is "human", show that Şef decides;
   - the agent twice, side by side: "same agent, no gate" (`without_gate`: what it posted,
     or that it asked the supervisor; if it posted while `expected` is not "post", say what
     it should have been) and "Spark agent behind the gate" (`agent.steps` as a timeline:
     tool calls with their arguments and results, `thinking` steps as quiet reasoning
     summaries, `cross` steps as the gate's carton-by-carton check, refused writes clearly
     marked as refused by the gate, a successful post marked as posted; then `agent.answer`
     and `agent.seconds`).
   Remember the selected case in the URL hash; start on the case `talimat` (the injected
   note) when there is no hash.
4. **The receiver's own count.** The clips in `data.voice` with Voice's avatar: an audio
   player (`audio`), the `transcript`, the `quantity` and `supplier`, and whether the
   receiver was sure (`certain`; not sure means the supervisor decides). Say that these are
   synthetic Turkish voice clips.
5. **Footer.** "Built during the Meta Global AI Developer Hackathon, 26 Oct – 4 Nov 2026, by
   Sena Köse.", a link to https://github.com/kosesena/count-before-you-post, the line
   "Characters: Sena's concepts, drawn with Muse Image. Fan-made, not official Meta
   mascots.", and "This page was written by Muse Code."

The avatars are `characters[i].avatar` (small square head crops, show them round).

## Rules

- Every number, name and sentence about results comes from `data.json`. Do not invent or
  hard-code any figure. Do not claim anything the data does not show.
- Escape all text from `data.json` before putting it into HTML.
- Light and dark theme: define colours as CSS custom properties on `:root`, switch them under
  `@media (prefers-color-scheme: dark)`, and add a small theme toggle button. Give `body` an
  explicit background.
- Must work at 375 px wide with no horizontal scroll (long tool arguments and results must
  wrap), and look good at 1280 px. Images have `alt` text. Buttons are real `<button>`s.
- System font stack only (no web fonts needed). No animation that runs on its own.
- Keep it one file under about 60 KB.

Do not touch any other file (in particular not `site/data.json`, `site/img/`,
`experiments/build_site.py`). Do not start a server, do not commit. When done, say what you
built and anything in `data.json` you could not use.
