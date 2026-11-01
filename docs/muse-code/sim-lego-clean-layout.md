# Muse Code task: Brick Dock, a clean three-column layout after Sena's reference

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
(First attempt stalled on the model stream for 8 minutes without an edit and was stopped; this is
the second run.) Sena, 1 Nov, sent a reference of an agent-team product she finds very clean, and asked earlier
that the "Every piece. In its place." receiving card go away: its controls should sit on the
screen as buttons, and the left side should hold only the agents. What matters most to her:
watching the agents talk in every scenario.

---

You are working in the repository `count-before-you-post`, on the LEGO warehouse simulator in
`site/sim-lego/` (`index.html`, `style.css`, `main.js`, `conversation.js`; you built the agent
panel and the live team chat). Rebuild the page's UI as a clean, light, three-column layout,
like this reference (described, not copied):

- **Look**: light and airy. Frosted white panels (white at ~85 % with blur), soft 1px borders
  `#e7eaee`, 16–20 px radius, very soft shadows, dark grey text, one accent blue for primary
  actions, small grey captions in caps with letter spacing. The 3D scene stays in the middle,
  the panels float over its edges; no heavy dark glass any more.
- **Left column (about 260 px)**: the deliveries as a list of "rooms": one card per scenario
  (use the labels of the `#case` options exactly: 01 Matching delivery, 02 Missing carton,
  03 Wrong product, 04 Damaged carton, 05 Injected instructions, 06 Stacked load), each with a small icon, the scenario name and one grey
  line (e.g. "3 agents · BLOCK"); the selected one highlighted; a small red dot on those whose
  recorded decision needs Şef. Above the list, the run language switch TR · EN · DE · ZH as a
  small segmented control (wire it to nothing new yet if the data is not there; leave a clear
  hook). Selecting a card does what `#case` does today.
- **Centre**: the scene, with a title at the top left of the scene area ("Delivery 01 ·
  Matching delivery", small caption "4 agents · recorded run") and a small "● live" + current
  time at the top right. At the bottom centre, one message bar: an agent chip on the left
  (who you are talking to, default Kapı, click to pick another agent) and "Ask anything —
  answered from the recorded evidence", send arrow. It sends to the existing typed-reply logic.
  Small round buttons beside the bar: Prepare dock, Play delivery (primary), Drive forklift; while
  playing they become Pause and a speed pill.
- **In-scene card**: when the recorded decision needs a person (Şef's review, or a handling
  decision at H-01), show a speech-bubble card above that agent in the scene: a black "NEEDS
  YOU" tag, the agent's name, the short reason, and two buttons, "Review first" and "Approve",
  wired to the existing review / approve actions. Nothing else floats in the scene.
- **Right column (about 300 px)**: tabs "Inspector · Team chat · Evidence".
  - Inspector: a small card for the agent speaking now (avatar, name, role, status pill
    READY / WORKING / WAITING); a "NEEDS YOU" card when a decision is pending (same buttons);
    then "WHAT IT IS ACTUALLY DOING": the seven receiving steps as a vertical timeline with
    check marks for done steps, a filled dot and a thin progress bar for the current one, and
    grey "More coming" for the rest, each with the agent's name and one line of what happened
    (from the existing step / status text).
  - Team chat: the live team conversation you built (keep its behaviour, timing and sources).
  - Evidence: the existing recorded evidence rows.
- Remove the old left receiving card (`#panel`), the old "Agents" top button and the top-left
  brand block's heavy style (keep the brand, small and light). Keep the forklift controls, the
  put-away / return / confirm actions (move them into the right column or the in-scene card),
  storage level choice, office doors and other existing functions reachable (a small "⋯" menu is
  fine). On phones: the left and right columns become sheets opened from two small buttons.

Also remove the speech bubble over agents in the scene (`#speech`): Sena wants the conversation
only in the chat. Do not change the 3D scene, the camera follow (`guided && automation` block), the forklift,
routes, collision, recorded data or what any answer says. Keep `node --test
site/sim-lego/*.test.mjs` passing. Do not change `?v=` strings; we bump them.

Do not run commands or write probe scripts: this run cannot approve them. Read the files, edit
them directly, and stop; we play every scenario in the browser ourselves.
