# Muse Code task: Şef answers, and the same agent without the gate

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, after the live-chat round (`docs/muse-code/sim-chat-feed-2.md`): "let's do all of them,
in order". This is the first of the three: Şef's recorded sign-off closes the story where
there is one, and a "Without Kapı" tab shows the same agent's run with no gate. The data was
added to `site/data-*.json` first (`experiments/build_site.py`): per case
`without_gate.steps`/`without_gate.seconds` (from the ungated runs of the same English
deliveries) and `signoff` (recorded once, on the Turkish notes, for `hasarli` and `belirsiz`).

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it, including the agent run feed). Do not run commands or write probe scripts: this run
cannot approve them. Read the file, edit it directly, and stop; we run the checks ourselves
(`experiments/web/sim_test.mjs` must still print ALL OK).

Every word on a row still comes from the data; nothing is invented. The few fixed UI words
are listed below.

## The data (already in `site/data-en.json`, in `G.cs`)

- `G.cs.without_gate.steps` and `G.cs.without_gate.seconds`: the same agent on the same
  delivery, with no gate in front of the ERP. Same step shape as `G.cs.agent.steps`
  (`tool` / `thinking` / `cross`). Its `post_goods_receipt` results look like
  `{"posted": true, "quantity": 12, "document": null}`: no gate, so no refusal.
- `G.cs.signoff` (only `hasarli` and `belirsiz`, otherwise `null`):
  `{ lang: "tr", decision: { approve, quantity, notes }, posted: [[11, "MAT-PRE-2026-00008"]],
  answer, seconds, steps }`. `steps` is what the agent did after Şef answered (same shape).
  This was a separate recorded run on the Turkish version of the delivery note.

## 1. Şef answers (follow-up)

When `G.cs.signoff` exists, after the Wonder row (or the gate row) the "With Kapı" thread
continues:

- A divider row (not a message): a thin line with the centred label "Follow-up · after Şef
  answered" and under it, small and grey, "separate recorded run, on the Turkish note ·
  <seconds> s". No step number.
- **Şef → Spark** (Şef finally speaks, with the typing phase like any message): when
  `decision.approve` is true "Approved: <quantity> cartons" (green, `--dpost`), else
  "Not approved" (red); under it `decision.notes` verbatim.
- Then the follow-up `steps`, built with exactly the same row rules as the main run
  (thinking, cross, `post_goods_receipt` → Kapı replies "posted · <document>" or "blocked").
  Their step labels restart with a small "f" prefix: `f1`, `f2`, ….
  **Everything on screen stays English** (the jury reads English), and this run read the
  Turkish note, so two exceptions: a follow-up `read_delivery_note` row says only "Reads the
  note" (never `G.cs.note`, which is the English note of the main run, and never the Turkish
  items), and a follow-up `look_at_pallet` row leaves out the labels (Turkish product text)
  and shows only cartons seen, damaged, stacked and "not all visible". `decision.notes`, the
  thinking texts and the document numbers are already English.
- The status line ends with "Run replayed · <n> steps · Şef answered ✓".
- In the 3D dock: the Şef row gets the speech bubble over Şef's head and a beam Şef → Spark.

Pacing: the follow-up rows continue after the main rows with the same slot length.

## 2. "With Kapı" / "Without Kapı" tabs

- Under the header, two tabs (a segmented control, 36 px tall, full width of the panel):
  **With Kapı** (default, selected) and **Without Kapı**. Each tab shows its own sub-line:
  with: "recorded run · <agent.seconds> s · <n> steps"; without: "recorded run, no gate ·
  <without_gate.seconds> s · <n> steps".
- The "Without Kapı" thread is built from `G.cs.without_gate.steps` with the same row rules,
  except: there is no Kapı, so a `post_goods_receipt` row is **Spark → ERP** "post <quantity>"
  and its reply is a status line "written to the ERP" when the result has `posted: true`. No
  gate row, no Wonder row, no follow-up. Kapı's avatar is not in its team row.
- At the end of the "Without Kapı" thread, one summary row (no avatar, centred, a coloured
  left edge): when the run posted (`G.cs.without_gate.posted` not empty) and
  `G.cs.expected !== "post"`: red, "A wrong receipt reached the ERP: <quantity> cartons";
  when it posted and `expected === "post"`: green, "Receipt written: <quantity> cartons";
  when it did not post: grey, "Nothing written · the agent asked Şef" if
  `G.cs.without_gate.supervisor` else "Nothing written".
- The "With Kapı" thread plays during the deciding phase as now. The first time the reader
  opens "Without Kapı", that thread replays with the same typing/message/reply phases (the
  same slot length); later visits show it complete. Switching back to "With Kapı" shows it as
  far as it has played and lets it continue. Bubbles and beams in the 3D dock are only for the
  "With Kapı" replay.
- The result card's existing "Without the gate" tile: make it a button that opens the
  "Without Kapı" tab (and, on phones, expands the feed strip).
- On phones the tabs sit in the strip header next to "Show all"; tap targets at least 36 px.

## Test hook

`window.__sim.feed()` keeps returning exactly the main "With Kapı" rows as today (no
follow-up, no divider). Add `window.__sim.feedFollowup()` (the Şef row and the follow-up
rows, `[]` when there is no sign-off) and `window.__sim.feedNoGate()` (the "Without Kapı"
rows, without the summary row), same `{ from, to, text, reply }` shape (`"erp"` as the `to`
id for the ERP).

Keep everything else: timings, reduced motion (everything at once, both threads), restart
and "Try another delivery" clearing all state, no sound. Change nothing outside
`site/sim/index.html`.
