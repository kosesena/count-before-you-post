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

## Receiving operations and recorded evidence

The current scene builds on commit 8a17271: its dark panels, portrait transcript, refined Şef asset and original ten-character cast are preserved.

1. Prepare the dock: the receiver checks the paperwork and deck, the driver waits in a marked ground-level refuge, and the restraint/bridge become visible. Handling is locked until preparation completes.
2. Unload to B-01. This is a physical receipt of an **unverified** pallet, not an ERP receipt. Both guided and manual handling require staging before inspection.
3. Move to the yellow inspection bay. The receiver uses a scanner; Spark, Sam and Kapı walk from their offices to workstations. Short, explicitly recorded note/count/visual/gate summaries run there. The full portrait transcript is an optional independent replay and cannot change the handling state or open the barrier.
4. A recorded POST allows put-away. Both BLOCK and HUMAN go to H-01: blocking an ERP write does not authorize returning physical goods.
5. At H-01, Şef and the receiver perform an illustrative check. Damaged/stacked loads need an intact count; shortages and injected documents additionally require explicit simulated document reconciliation. Wrong-product loads cannot be accepted against this order. A return requires a separate supervisor choice. All such choices are training decisions, not new recorded AI results or live ERP writes.
6. Eleven intact cartons can be accepted from a damaged delivery; its damaged carton is separately identified at Q-01 quarantine. R-01 is only for authorized returns awaiting carrier collection. Pallet tags identify the in-session pallet and destination.
7. Confirm the destination address to complete put-away/return staging. Finishing the exercise saves an in-session history entry. After guided put-away, the empty forklift drives back through the aisle to parking, then the driver walks to the cab and climbs in. The pallet and final scene remain visible until the user explicitly starts a new delivery; this does not dispatch a truck or maintain persistent inventory.

Added equipment includes the receiving desk, paper tray, handheld scanner, label printer, a RECOUNT · REPACK sign over H-01 (where the recount happens), a stretch-film bin and a cardboard cage, bridge plate, wheel restraints, driver refuge, first-aid point, fire extinguisher and marked exit. The briefing area has a pedestrian barrier. Office stairs and the balcony entrance are at the near/public end of the office wing; the metal switchback stair has two flights and an intermediate landing on the front pedestrian apron, clear of the lower office frontage and meeting island. The upstairs walking route follows this approach without entering controlled storage. Furniture and floor workers participate in vehicle collision checks. The detailed upper background racks (C, D, E: B-01 is the arrival bay) remain scenic; A-01-L0/L1 is temporary staging; final interactive warehouse storage is C-06-L1. A wrong product is refused at the dock and driven back onto the trailer; the gate decision shows as a card with the three-way match (purchase order, note, pallet).

Manual and guided forklift movement share collision checks. Q/Z lift/lower; E picks/places. Guided transfer only starts from its measured aligned pose; otherwise the selected handling decision remains active and the UI switches to manual handling without snapping the vehicle or driving a blind route. Review routes start at the actual H-01 drop pose, avoiding the former extra approach into the pallet. Pause freezes workers and replay progression. R resets the exercise.

Worker actions and physical checks are illustrative, not reconstructed motion, a new camera measurement, an independent voice result, or a safety training certification. Recorded per-call counts, source labels and historical signoff follow-ups are retained in the optional transcript. The receiver's gestures do not fabricate voice evidence. No live API or ERP calls occur.

Rover's disconnected floor prop is removed only in `models/rover-clean.glb`; original shared `/sim/models/` assets are untouched.

### Agent conversations

The conversation drawer has a searchable agent inbox with last-message previews, followed by individual agent threads with incoming/outgoing bubbles and a full-team view. All recorded speakers and recipients appear in the team, including Şef. Historical records have no message timestamps: displayed 08:00-based times are explicitly labelled demo times. Newly entered messages use Europe/Istanbul time. The composer answers count/product/decision questions from the selected delivery record using local templates; it does not call a live model or alter receiving approvals. Evidence, workflow and scene-location buttons remain functional.

Browser walkthrough on 2026-10-31 completed all six physical exercises through destination confirmation: matching delivery to A-01-L1; missing carton (11) to A-01-L0; wrong product to R-01; damaged delivery (11 accepted, one quarantined) to A-01-L0; injected instructions after clean-document confirmation to A-01-L0; unstacked/recounted load (12) to A-01-L0. A wrong return address was rejected; missing document verification blocked acceptance.

Guided playback pauses at the gate result for a put-away choice and at the destination for an explicit address confirmation. Put-away and closing movement run at no more than normal speed; Pause freezes the movement. The pallet settles onto its destination before the forks detach. There is no timed automatic scene reset.

Accepted pallets now require a second physical transfer from temporary A-01 to C-06-L1 in the rear warehouse rack. That bay is empty and collision geometry retains its posts; confirmation is only offered at the final warehouse address. During inspection, agents stay at their office desks; the active office and its recorded message are highlighted.

### Office-based agents (1 Nov follow-up)
Agents now remain at their own desks, including Şef during exception review. Inspection
frames the office wing; the active speaker gestures, their office lights up and the recorded
message appears above it. The warehouse receiver still walks to inspect/recount the pallet.
No agent deployment route crosses the forklift aisle. Final scans show the actual destination
address; temporary staging controls disappear once the pallet reaches its final location.
Recorded model summaries are explicitly labelled as model text, not proof of an ERP write.
