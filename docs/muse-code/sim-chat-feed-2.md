# Muse Code task: make the chat feed feel alive

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, after the first round of the feed (`docs/muse-code/sim-chat-feed.md`) went live: the
chat could be livelier, for example a "typing…" animation while someone writes, a green dot
when they are online; "I trust your imagination". Still only what the recorded runs say, no
sound, and she reads it on her phone.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it, including the agent run feed: `#feed`, `buildFeedRows`, `feedRowEl`,
`feedShowReply`, `feedShowBubble`, the beams). Do not run commands or write probe scripts:
this run cannot approve them. Read the file, edit it directly, and stop; we run the checks
ourselves (`experiments/web/sim_test.mjs` must still print ALL OK).

Make the feed feel like a live chat app while it replays a recorded run. **Do not change what
the rows say**: `buildFeedRows` and `window.__sim.feed()` keep returning exactly the same rows.
Every new element is presentation (motion, state, indicators); none adds a claim or a word
that is not in the data, except the small fixed UI words listed below.

## Pacing: give the chat room to breathe

Today all rows are squeezed into 300–6500 ms. Keep the first row at 300 ms but give every row
a slot of 900 ms (reduced to 650 ms when there are more than 12 rows), so the feed keeps
playing after the result card appears at 6800 ms (the result card and the reading cards keep
their timings exactly). Within a row's slot:

1. **Typing** (0–35%): the row appears as a typing row: the sender's avatar, their name and
   "is typing" in small italic, and three dots bouncing one after another (CSS, staggered
   0.15 s). For a `thinking` row the label is "is thinking" and the dots are dimmer.
2. **Message** (35%): the typing row turns into the message; the text types itself out
   quickly (about 2 ms per character, at most 350 ms for the whole text), with a thin blinking
   caret at the end that disappears when done. The step label (`#3`, `gate`, `draft`) appears
   with it.
3. **Reply** (when the row has one, 60%): under the message a small typing indicator with the
   recipient's avatar (18 px) and bouncing dots for about 200 ms, then the reply fades in.
4. **Ticks**: rows with a recipient show a small tick after the message, "✓" (sent, grey);
   when the reply arrives it becomes "✓✓" in the recipient's colour (seen). Rows with no
   reply keep a single grey "✓". Rows with no recipient have no tick.

The bubble over the speaker's head follows the same steps: first a small bubble with three
bouncing dots (typing), then the message bubble. The beam travels when the message lands.

## Presence

- **Team row**: each avatar gets a 9 px status dot at its bottom right with a 2 px ring in the
  panel colour. Green (`#22c55e`) for characters standing on the floor in this delivery
  (`floorSetFor(caseId)`), amber (`#f59e0b`) for those in this delivery's rows who sit in
  their glass room (Şef in `wrong` and `eksik`), with a tooltip/`title` "on the floor" or
  "in their room". The avatar whose row is typing or speaking gets a soft glowing ring in its
  colour and grows to 1.15×; when no one is speaking all are at rest.
- Under the team row, one quiet status line that changes with the replay: "Spark is
  typing…", "Sam is replying…", "Kapı is deciding…" (gate row), "Wonder is drafting…"
  (draft row), and at the end "Run replayed · <n> steps" with a small check.
- **Header**: while rows are still playing, a small pulsing dot in the decision-neutral cyan
  (`#22d3ee`) with "replaying" next to "Agent run"; when the last row lands it becomes a
  static grey dot and "recorded run". Never the word "live".

## Little moments

- New rows slide up from below with a slight spring (overshoot ~4 px), not just fade.
- The gate row: the decision word lands like a stamp (scale from 1.6 to 1 with a quick
  settle, 250 ms) in its colour, and the row's left edge takes that colour.
- `ask_supervisor` rows get a small "to Şef" envelope icon (inline SVG) before the text.
- `set aside` (instructions to software) and `blocked` replies get a short red flash.
- If the reader has scrolled up while rows keep coming, a pill at the bottom of the list
  "↓ <k> new" appears; tapping it scrolls to the newest row and hides it.

## Phones (max-width 640px)

The strip shows the newest row with its typing state and ticks; the status line and the team
row with dots stay visible (avatars 24 px, dots 8 px). When the strip is collapsed and a new
row lands, the strip gives a brief highlight of the sender's colour on its edge. Tap targets
at least 36 px; text at least 12.5 px. The result sheet at the bottom must not cover the
strip.

## Reduced motion and restart

`prefers-reduced-motion`: no typing phases, no typewriter, no bouncing, no stamp, no spring;
all rows appear at once with their final state (✓✓ where a reply exists), the status line
shows the final text. All timers go through `later(...)`, so a restart or "Try another
delivery" cancels them and `feedClear` resets every new state (pill, status line, header dot).

No sound: no audio of any kind. Change nothing outside `site/sim/index.html`.
