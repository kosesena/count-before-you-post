# Muse Code task: Brick Dock agent panel (chat), after Sena's reference

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 1 Nov, sent two screenshots of an agent-office product as the look she wants for the
simulator's chat: a dark glass side panel with the team's avatars and recent conversations,
and, on clicking an agent, that agent's chat in the panel while the camera goes to the agent's
desk. Today the Brick Dock has a separate "Recorded conversation" overlay and a small "Meet the
crew" card; neither looks like that.

---

You are working in the repository `count-before-you-post`, on the LEGO warehouse simulator in
`site/sim-lego/` (three.js, plain ES modules, no build step). Read `index.html`, `style.css`,
`conversation.js`, `chat-replies.mjs`, `replay.mjs` and the parts of `main.js` that use them
(`openConversation`, `showRecordedConversation`, `focusCast`, the `#cast-card` / `#cast-select`
crew picker, `castJobs`, `castSlots`).

Build one **agent panel** on the left of the screen that replaces both the "Recorded
conversation" overlay and the "Meet the crew" card:

1. **Team view** (default when opened):
   - A dark, translucent glass panel (about 340 px wide, rounded, soft blur, white text), with
     a search field ("Search agents") at the top that filters by name.
   - A grid of the ten agents (3 per row): round portrait (`site/sim-lego/assets/<id>.png`, the
     ids are spark, sef, sam, voice, kapi, iris, ada, glimmer, wonder, rover), the name under
     it, and a one-line status in small grey text (the agent's job line from `castJobs`; mark
     the agents that take part in the current delivery with a small green dot).
   - Below the grid, **recent conversations**: one row per agent who speaks in the current
     delivery's recorded run (from `replayLines`), with portrait, name, the time stamp shown in
     the recorded run (or its order), and the first line of that agent's last message, cut
     with an ellipsis.
2. **Agent view** (on clicking an agent in the grid or a row):
   - A back arrow, the portrait and name at the top, and the existing quick actions as small
     pill buttons (Evidence, Workflow, Locate).
   - The agent's messages from the recorded run as chat bubbles (agent left, the user right),
     then a message field at the bottom. Typed questions are answered exactly as today, from
     the recorded evidence (`chat-replies.mjs`), with the recorded source one tap away. Keep the
     English/Turkish behaviour.
   - At the same moment the camera goes to that agent at their desk (use `focusCast(id)`).
3. Open/close: a button in the top bar (where "Recorded conversation" is now) toggles the
   panel; Esc closes it. On phones (narrow screens) the panel becomes a bottom sheet that covers
   at most 60 % of the height.

Keep the style of the rest of the UI (fonts, the dark glass of the existing panels); no new
libraries, no external fonts. Do not change what the answers say, the recorded data, the
3D scene, the camera code apart from calling `focusCast`, the forklift, routes or collision.
`node --test site/sim-lego/*.test.mjs` must keep passing (update a test only if it tests the
removed overlay's markup, and say so).

You may edit `index.html`, `style.css`, `conversation.js`, and in `main.js` only the code that
opens the conversation and the crew card (wiring). Do not change any `?v=` strings; we bump
them.

Do not run commands or write probe scripts: this run cannot approve them. Read the files, edit
them directly, and stop; we test it in the browser ourselves.
