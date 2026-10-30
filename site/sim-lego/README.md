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
node --test site/sim-lego/collision.test.mjs
```

Local review screenshots and the rejected generated loading video are not runtime dependencies and are excluded from this source commit. The live camera tour makes no paid generation calls.

## Known follow-ups

The helmeted character face still uses the original project asset. Imported wave clips are disabled in this scene because of arm deformation; the separate main-site cast media is unchanged. These are not claimed as repaired.
