# Muse Code task: Brick Dock, watch the agents talk in every scenario

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 1 Nov: "önemli olan her senaryoda onların konuşmalarını izleyebilmek" (what matters is
being able to watch their conversation in every scenario). After the agent panel round
(`sim-lego-agent-panel.md`) the panel shows one agent's messages at a time and the full team
transcript is gone; during "Play delivery" no agent message is shown at all, only evidence rows.

---

You are working in the repository `count-before-you-post`, on the LEGO warehouse simulator in
`site/sim-lego/` (you built the agent panel in `conversation.js` last round). Read `main.js`
around `runDemo`, `beginInspection`, `updateInspection`, `finish`, `showRecordedConversation`,
`meetingRun` / `#speech`, and `replay.mjs` (`replayLines`, `participants`, `names`).

Make the recorded agent conversation the thing you watch while a delivery plays:

1. **Team conversation view** in the agent panel: a "Team" view (reachable from the team grid,
   e.g. a "Team chat" row at the top of recent conversations, and as the default while a
   delivery plays) that shows the whole recorded run of the current scenario as a group chat:
   each message with the speaker's round avatar (`../img/av-<id>.jpg`), name, time and text,
   the recorded source one tap away, Şef's sign-off at the end when the scenario has one.
   Tapping an avatar opens that agent's own view (as now).
2. **Live during "Play delivery"**: when a delivery is played (`runDemo` sets `guided=true`),
   open the panel in the Team view and reveal the recorded messages one by one in step with the
   scene: start when the inspection begins (`beginInspection`), one message about every 2.4 s at
   speed 1 (scale with `state.speed`, stop while `state.paused`), each preceded by a short
   "typing…" row with the speaker's avatar; keep the newest message in view; mark the speaking
   agent in the team grid; show the same line in the existing speech bubble (`#speech`) over the
   speaker in the scene if that already works for them. The decision (`finish`) must not come
   before the gate's own message has appeared; if the messages need longer than the inspection,
   let the inspection wait for them.
3. **Every scenario**: this must work for all six cases in `#case` (ok, wrong, eksik, talimat,
   hasarli, belirsiz) and in English and Turkish, using only the recorded lines; nothing is
   invented. When a case has no recorded line for an agent, that agent simply does not speak.
4. Do not change the camera follow (`guided && automation` block in `animate`), the forklift,
   the put-away route, routes, collision, or the recorded data. Keep the agent view and typed
   replies as they are.

You may edit `conversation.js`, `style.css`, `index.html`, and in `main.js` only the playback
wiring named above. Do not change `?v=` strings; we bump them. `node --test site/sim-lego/*.test.mjs`
must keep passing.

Do not run commands or write probe scripts: this run cannot approve them. Read the files, edit
them directly, and stop; we play all six scenarios in the browser ourselves.
