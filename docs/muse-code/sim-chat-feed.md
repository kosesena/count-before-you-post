# Muse Code task: a live chat feed of what the agents said to each other

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena: show what the agents say to each other while a delivery is decided, like the "AI virtual
office" pictures (characters at their workstations, a team list and a timestamped activity
feed beside them) and chat-list interfaces. Only what the recorded runs really say; she reads
the simulator on her phone; no sound.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it). Do not run commands or write probe scripts: this run cannot approve them. Read the
file, edit it directly, and stop; we run the checks ourselves (`experiments/web/sim_test.mjs`
must still print ALL OK).

## What the feed shows

While a delivery is decided (`startDeciding`) a feed plays the recorded agent run of that
delivery, step by step, as a chat between the characters. The source is the case in
`site/data-en.json` the page already loads (`G.cs`): `G.cs.agent.steps` in their recorded
order, then the gate's decision `G.cs.gate`, then Wonder's draft `G.cs.draft` when there is
one. **Every word on a row comes from these fields** (verbatim, or numbers read from them);
nothing is paraphrased into new claims, nothing is invented. If the data does not give a
row's content, there is no row. In particular: no row for Rover, Voice, Glimmer, Iris or Ada
(the case data has no output from them), and Şef never speaks (the run only notified Şef).

Spark runs the receiving agent (its character line in `data-en.json`), so the agent's tool
calls are Spark's messages. One row per step:

| step | from → to | message | reply on the same row |
|------|-----------|---------|-----------------------|
| `tool` `read_delivery_note` | Spark (no arrow: Spark's own reading) | "Reads the note:" and `G.cs.note.items` as `12 × Sunflower oil 5 L` | if `G.cs.note.embedded_instructions` is not empty: "N instructions to software set aside" in red |
| `tool` `look_at_pallet` | Spark (own look) | "Looks at the pallet:" | from `JSON.parse(step.result)`: labels `product_on_labels`, `cartons_visible` cartons seen, `damaged_cartons` damaged, stacked / not stacked, and "not all visible" when `all_cartons_visible` is false |
| `tool` `count_cartons` | Spark → Sam | `count “<concept>”` (`JSON.parse(step.args).concept`) | Sam: `<sure> sure, <doubtful> doubtful` from `JSON.parse(step.result)` |
| `thinking` | Spark, marked "thinks" (italic, dimmer) | `step.text` verbatim | — |
| `cross` | Sam ↔ Spark | "Carton by carton:" | `<agreed> agreed, <sam_only> only Sam, <spark_only> only Spark` from `step.data` |
| `tool` `post_goods_receipt` | Spark → Kapı | `post <quantity>` (`JSON.parse(step.args).quantity`) | Kapı: when `step.refused` is false and the parsed result has `posted: true`, "posted · <document>"; when `step.refused` is true, "blocked:" and the first sentence of the result's `reason`. The refused result string can be cut off with "…" and fail `JSON.parse`, so read the reason with a regex (`/"reason":\s*"([^"]*?[.!?])/`) and leave the reply as just "blocked" if that finds nothing |
| `tool` `ask_supervisor` | Spark → Şef | the `reason` from `JSON.parse(step.args)`, verbatim (clamped to 3 lines with a "more" toggle) | a small grey status "Şef notified" when `step.result` contains `notified` (not a message from Şef) |
| any other tool | Spark → (nobody) | the tool name in mono | — |
| gate (after the steps) | Kapı → ERP (post), Kapı (block, no arrow), Kapı → Şef (human) | the decision word POST / BLOCK / ASK ŞEF in its colour (`--dpost`, `--dblock`, `--dhuman`) and `firstSentence(G.cs.gate.reason)` | — |
| draft (only when `G.cs.draft`) | Wonder → Şef | "Draft: <draft.title> · to <draft.to>" (use `DOC_LABEL[draft.document]` for the kind) | grey status "waiting for Şef's approval" (the draft's `status` is `draft`) |

A JSON parse that fails must never break the feed: fall back to the tool name for that row.

## The panel

- Desktop: a panel on the **left** (`#feed`), top 10px, left 10px, width min(330px, 30vw),
  max height calc(100dvh - 20px), the same dark frosted glass as the reading cards
  (`rgba(11,18,38,.68)`, blur 16px saturate 1.3, `rgba(255,255,255,.14)` edge, radius 18px).
  Visible in the deciding and done phases (`body.deciding`, `body.done`), hidden otherwise;
  it is cleared when a new delivery starts (where `#reads` is cleared). It must not cover the
  reading cards (right) or the result card (right); the tally chip and other HUD on the left
  move below it or are hidden while it is shown.
- Header: "Agent run" and a sub-line "recorded run · <G.cs.agent.seconds> s · <n> steps".
  Under it a **team row**: the avatars (`AV(id)`, 26px, ring in `charColour(id)`) of the
  characters that appear in this delivery's rows, in order of first appearance; the one
  speaking now gets a soft pulse.
- Each row: a 34px round avatar of the sender with a 2px ring in its colour; a line with the
  sender's name in its colour, "→" and the recipient's name in theirs (or "↔" for the cross
  row, nothing when there is no recipient); on the right of that line the **step number** in
  small mono, `#3` (the runs record the order of the steps, not a clock time per step, so do
  not show times); under it the message (13px, white .92), and the reply indented with the
  recipient's small avatar (18px) when the row has one. Rows slide and fade in; the list
  scrolls to the newest row on its own unless the reader has scrolled up.

## Pacing

Spread the rows evenly over the deciding window: the first at 300 ms after `startDeciding`,
the last no later than 6500 ms (`showResult` runs at 6800 ms; keep every existing timing).
Use the existing `later(...)` so a restart cancels them. In each row's slot the message
appears first and the reply 45% of the slot later. After the result card shows, the whole
feed stays readable and scrollable. `prefers-reduced-motion`: all rows appear at once at
the start of the deciding phase, no bubbles in motion, no beams.

## In the 3D dock

- **Speech bubble**: when a row's message appears, a small bubble rises above the sender's
  head (a DOM element in `#labels`, projected from the character's position each frame as the
  labels are, about 0.35 m above the label height): the message, max 46 characters with "…",
  white text on the same dark glass, a 3px left edge in the character's colour, a small tail.
  It stays 1.6 s or until the next row, then fades. When the reply appears, the reply's bubble
  rises above the recipient's head. Only one bubble per character at a time. No bubble for a
  character who is not loaded or is outside the view; seated characters in their rooms get the
  bubble too (Şef in the `wrong` and `eksik` deliveries sits in their room).
- **Message beam**: when a row has a recipient character and both are loaded, draw a thin line
  between their head positions (`THREE.Line`, `depthTest: false`, additive, the sender's
  colour, opacity fading in and out over about 0.9 s), and a small bright glow (a sprite with
  the existing `radialTex`) travelling from the sender's head to the recipient's head along it
  in about 0.6 s. Reuse one line and one sprite per active beam, at most three at a time;
  remove them after they fade. Nothing for the ERP recipient.
- Don't change the walking, the reading cards, the work poses, the gate light, the barrier or
  the cameras.

## Phones (Sena reads it on her phone)

At `max-width: 640px` the feed is a strip at the top: left 10px, right 10px, top 10px, showing
only the newest row (avatar, names, step, message clamped to 2 lines) with a small button
"All N steps ▾" that expands it to the full list (max height 46dvh, scrollable) and "▴" to
collapse. The reading cards stay at the bottom as now, and the result sheet at the bottom must
not overlap the strip (collapse the strip to one row when the result shows). Text at least
12.5px, tap targets at least 36px. Bubbles over heads on phones: at most 28 characters.

## Test hook

Add `feed` to `window.__sim`: a function that returns the rows built for the current case as
plain objects `{ from, to, text, reply }` (ids for from/to, `null` when there is none), so our
test can check the feed against `data-en.json`.

No sound: do not add or trigger any audio for the feed. Change nothing outside
`site/sim/index.html`.
