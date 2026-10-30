# Muse Code task: tap a row to see who and the raw record; playback controls

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena: "let's do all of them, in order". After Şef's answer and the "Without Kapı" tab
(`docs/muse-code/sim-chat-feed-3.md`) and the meeting table (`sim-meeting-table.md`), the last
two: tapping a row focuses its character in the 3D dock and opens the step exactly as it was
recorded; and playback controls for the feed. Everything stays English (the jury reads
English).

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it, including the agent run feed, the "With Kapı / Without Kapı" tabs, the follow-up
after Şef's answer and the meeting at the table). Do not run commands or write probe scripts:
this run cannot approve them. Read the file, edit it directly, and stop; we run the checks
ourselves (`experiments/web/sim_test.mjs` must still print ALL OK). Do not touch
`site/sim/models/`.

## 3. Tap a row: focus and the raw record

- Every message row (not the divider or the summary rows) is a button for screen readers
  (`role="button"`, `tabindex="0"`, Enter/Space) and shows a pointer cursor.
- **Focus**: tapping a row whose sender is a loaded character glides the camera (about 0.8 s)
  to a three-quarter view of that character from the yard side, head and shoulders in the
  upper middle of the free area (left of the result card on desktop, between the feed strip
  and the result sheet on phones), and lights their station or seat with the existing
  `setStepHighlight([id])` for 3 s. The camera stays on them for 3.5 s, then glides back to
  whatever view the phase has (the deciding view, or the table view while the meeting is on).
  A tap on another row moves the focus there. A small chip "Focused on <Name> · tap to return"
  at the top of the free area returns at once. During driving there is no focus (the feed is
  hidden then anyway). Characters seated in their glass rooms are focused there too.
- **Raw record**: the tapped row also expands (an accordion; tapping again collapses) to show
  the step exactly as recorded, in a mono block with a "Recorded step" label:
  - `tool` steps: `<tool>(<args>)` on the first line and `→ <result>` under it, the strings
    verbatim from the step (`step.args`, `step.result`). If `step.result` ends with "…", add
    a grey note under it: "cut at 160 characters in the site data". `refused: true` steps get
    a red "refused by the gate" tag, `posted: true` steps a green "posted" tag.
  - `thinking` steps: `thinking: "<text>"`.
  - `cross` steps: `gate_cross_check` and the JSON of `step.data`.
  - Kapı's gate row: `decide()` → the JSON of `G.cs.gate` (`action`, `rule`, `reason`,
    `quantity`).
  - Wonder's draft row: the JSON of `G.cs.draft` without `body`, and a "Read the draft"
    link that opens the result card's existing draft `<details>`.
  - Şef's answer row: `signoff` → the JSON of `G.cs.signoff.decision`.
  - Under every raw block, small and grey, its source: "experiments/results/en/
    agent_warehouse_cross.json, via site/data-en.json" for the main and the "Without Kapı"
    rows, "experiments/results/signoff.json (Turkish note)" for the follow-up rows,
    "cbyp/gate.py" for the gate row, "experiments/results/en/wonder_drafts.json" for the draft
    row.
  - Long lines wrap (`overflow-wrap: anywhere`); a "Copy" button copies the block's text.
- Rows keep their typing/message/reply phases; a row that is still typing cannot be opened yet.

## 4. Playback controls

A slim control bar at the bottom of the feed panel (on phones, in the strip under the tabs,
visible also when collapsed), 36 px tall, for the thread on screen:

- **Pause / Play** (an icon button with `aria-label`): pauses the replay where it is (the
  typing dots stop, nothing new lands, bubbles and beams freeze or fade as they are); Play
  resumes from the same point. Implement the replay as a scheduler you can pause (a queue of
  timed events advanced by an elapsed-time clock in the main loop, scaled by the speed),
  instead of fixed `setTimeout`s for the feed; keep `later(...)` for everything else.
  Restart and "Try another delivery" still clear it.
- **Speed**: a toggle cycling 1× → 2× → 0.5× → 1×, shown as text ("1×"). It scales the feed's
  slots, typing, typewriter and reply timings and the meeting's waits for the feed; it does
  not change the 3D walking speed or the reading cards and result timings.
- **Step**: "Next" (an icon button) lands the next row at once with its final state (message,
  reply, ticks), also while paused.
- **Timeline**: a thin progress bar showing how many rows have landed out of all rows of this
  thread (including the follow-up), with a dot per row; tapping a dot jumps there: every row
  up to it lands at once in its final state and the replay continues from there (paused stays
  paused). Rows after it are removed if the reader jumps back.
- When the thread has fully played: Play becomes "Replay" (↺), which clears the thread and
  plays it again from the first row (the 3D bubbles too, the meeting does not walk again).
- `prefers-reduced-motion`: the bar is there, all rows are already landed, Replay re-lands
  them at once.

## Test hook

Keep `window.__sim.feed()`, `feedFollowup()`, `feedNoGate()`, `meeting()` unchanged. Add
`window.__sim.feedPlayer()` returning `{ thread, playing, speed, landed, total }`.

No sound. Change nothing outside `site/sim/index.html`.
