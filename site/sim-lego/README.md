# Count Before You Post — brick warehouse simulator

Independent `/sim-lego/` scene built with OpenAI Codex for the Meta hackathon project. The original Muse Code simulator remains at `/sim/`. Toy-brick styling is a visual direction, not event sponsorship.

## Run

From the repository root:

```sh
python3 -m http.server 8767 --bind 127.0.0.1 --directory site
```

Open http://localhost:8767/sim-lego/ . Deploy the whole `site/` directory: this page depends on `../data.json` and the ten GLB character assets in `../sim/models/`.

## Features

- Procedural warehouse, wall-mounted offices, illuminated nameplates, shelves, meeting table, outdoor truck and loading dock.
- Ten existing project character models, with original names and role descriptions.
- Live 20-second opening camera tour using this scene. Skip with Enter warehouse or Escape; replay from Explore.
- English collapsible receiving controls and navigation drawer.
- WASD / arrow-key forklift driving; E picks up or sets down pallets. Collision checks include the forklift, forks and carried load.
- Recorded delivery decisions from data.json. No model calls or live ERP writes. Playback can be paused or slowed.
- H toggles the interface; R resets the scene.

Three.js 0.170.0 and its loaders are vendored under `vendor/`; see `vendor/LICENSE-three.txt`.

## Checks

```sh
node --input-type=module --check < site/sim-lego/main.js
node --test site/sim-lego/*.test.mjs
```

Local review screenshots and the rejected generated loading video are not runtime dependencies and are excluded from this source commit. The live camera tour makes no paid generation calls.

## Known follow-ups

The helmeted character uses a local refined head/hardhat and restrained Wave clip in `models/sef-refined.glb`. Full wave playback remains disabled in the warehouse; conversation gestures use small shoulder rotations. Other shared character assets and the separate main-site cast media are unchanged.

## Receiving operations and recorded meetings

After physical pickup and placement, the scenario team gathers at five stools. The original Walk clip runs while moving; seated legs and speech gestures are applied separately. A readable transcript and world-anchored speech bubble advance manually by default, with optional paced playback and pause. Per-call count results come from `data.json` agent.steps, not from the final summary count. Internal thinking entries are replaced by labelled concise statuses. Gate decisions, draft summaries, without-gate comparison and `data-en.json` signoff follow-ups retain explicit source labels. No live model or ERP call occurs.

Accepted loads go to A-01-L0 or A-01-L1. Human-review loads go to H-01, blocked loads to R-01. The manual supervisor controls are a separate training choice; they do not rewrite the recorded initial decision. Damaged partial acceptance separates 11 intact cartons and one damaged carton in quarantine. Dispatch adds an in-session history entry and clears the single-load bay for the next exercise; this is not persistent stock accounting.

Automatic and manual forklift movement share collision checking. Pickup requires aligned forks; placement requires whole-load containment, obstacle clearance and the selected shelf height. Q/Z lift/lower in manual mode; travel is disabled with raised forks. The partition has a narrow pedestrian opening that the forklift cannot fit through. Office doors and an illustrative stair route can be previewed. Paths and character staging illustrate the recorded process; they are not reconstructed human motion from the original trial.

Rover's disconnected floor prop is removed only in `models/rover-clean.glb`; original shared `/sim/models/` assets are untouched.
