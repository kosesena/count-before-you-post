# Verification and field validation

This document separates implementation from evidence. Historical runs remain unchanged.

## Completed locally

- Product names must match after case/diacritic/spacing normalization. Substrings cannot authorize stock.
- Only explicit carton units are accepted; no carton-to-piece conversion is guessed.
- Invalid/empty quantities are held. Full-check sessions require the trusted order, exact supplier,
  receiver evidence, SAM object evidence, second reader and audit.
- PDF text inspection reaches the write boundary. Reader failure and missing mandatory evidence
  refuse a receipt. New note readings invalidate cached second opinions.
- Local upload UI runs the new-input pipeline with no ERP writer.
- Reviewer page exposes evidence and the actual tool result without driving the forklift.

## Not yet demonstrated

- Fresh live-model success of the hardened revision on a complete real delivery.
- A held-out set of real deliveries. The three folded-carton photos are development hard cases,
  not unseen validation and not examples of successful automatic acceptance.
- Field time saved, reduction in real warehouse errors, or full API cost.
- Concurrent production ERP posting, supplier master-data resolution, multi-line orders, unit
  conversions, and deployment-grade authentication. This remains a single-line prototype.

## Collect 20–30 new cases

Count the physical cartons yourself and record the truth before consulting model outputs.
Include clean deliveries (at least half the set), shortages, different products/pack sizes,
visible damage, partly hidden goods, and harmless notes versus suspicious instructions.
Vary camera angle, lighting, carton material and label layout. A new camera angle of the same
load is not an independent delivery: assign a shared load ID and keep it in one split.
Do not use private customer documents without permission; redact personal contact details.

For each delivery save:

1. Supplier note photo or 1–3 page PDF, with product, quantity and unit readable.
2. Current photo of the full load, including its labels. Do not rearrange after recording truth.
3. Receiver WAV (mono, 16-bit, 16 kHz, <=90 seconds): their own count and unit; uncertainty spoken
   explicitly. Include driver disagreement in some cases. Do not use generated voices as real workers.
4. Trusted purchase-order fields copied independently, not inferred from the supplier note.
5. Human physical count, product match, damage, expected policy action and reason.
6. Stopwatch observations: start checking, checking complete, data entry complete; pauses separately.

Use `evaluation/manifest.example.json` as a schema example; its row is not collected data.
Store private files under ignored `evaluation/inputs/`. Reserve a separate development set.
Freeze the unseen cases BEFORE running:

```sh
.venv/bin/python -m evaluation.run_heldout --freeze evaluation/my-manifest.json evaluation/sealed-01.json
.venv/bin/python -m evaluation.run_heldout --run evaluation/sealed-01.json evaluation/results-01.json
```

The second command sends files to Meta/Baseten and consumes API credits. It performs no ERP writes.
The runner checks every input hash first, includes failures in the report, and refuses to overwrite
an existing trial. If tuning is needed after inspecting results, call that set development and
collect a fresh held-out set; do not keep calling it unseen.

## Report distinct outcomes

- Correct automatic acceptance / eligible clean deliveries.
- Unsafe acceptance / all deliveries (wrong quantity, product or required policy approval).
- Unnecessary review / eligible clean deliveries.
- Physical quantity error separately from policy violation. Correct physical 12 plus an ignored
  escalation requirement is a policy violation, not proof the agent counted 100.
- Technical failures separately, never credited as a correct hold.
- Median/p95 processing latency, active manual time, human review time, and total model billing.
- Total cost remains unknown until ALL providers/calls are accounted for. Agent token cost alone
  is not the workflow cost. API duration is not worker time saved.

`evaluation/report_recorded.py` produces a separate historical synthetic-policy report offline.
New result JSON stores tool-step timings, input hashes and a nullable total cost.

## ERPNext process baseline

Official process: Purchase Order → Purchase Receipt → Purchase Invoice → Payment Entry.
At receipt, the receiver checks quantity/product, accepted/rejected stock, UOM and any required
Quality Inspection. Submission updates stock and order received quantity. Supplier payable is
created by the Purchase Invoice, not by the Purchase Receipt alone.

Sources (checked 1 Nov 2026):
- https://docs.frappe.io/erpnext/purchase-receipt
- https://docs.frappe.io/erpnext/quality-inspection
- https://docs.frappe.io/erpnext/buying

Our contribution is evidence before an agent's receipt write, not replacing these ERP controls.
Creation/modification timestamps can measure document elapsed time, not hands-on count time.
Our local ERPNext is test data: neither its timestamps nor its sample receipts establish field ROI.
A credible future baseline uses the same deliveries, an observer/stopwatch and separately logged
model processing and human-review time. No warehouse benchmark percentage is invented here.

## Hardened live integration check — 1 Nov 2026

One new API run combined the existing synthetic matching-delivery images with the existing
synthetic Turkish dialogue `02-tamam.wav`. It took 46.725 seconds. Note, camera and object
cross-check agreed on 12, but voice extraction returned 2 (unit “kolay”). The receiver check
sent the delivery to human review; no ERP write occurred. This demonstrates fail-closed
integration, **not** successful automatic acceptance or real-world accuracy. Second-reader
checks were not reached because the earlier receiver check already held the delivery.
No retry was used to replace this unfavorable result. The complete local trace is at
`.local-verification/synthetic-full-smoke.json` (ignored, not published).

## Follow-up: grounded voice interpretation — 1 Nov 2026

The first smoke test's ASR text was “Saydım, on iki. iki. Tamam.”. The interpretation now
reports all plausible final counts and quotes the complete supporting receiver turn.
Code verifies that the quote belongs to that speaker and requires one supported count
before preserving certainty. Repetition alone is not treated as an explicit correction.
The full workflow report retains this interpretation alongside the original speaker turns.

Three development-only text checks used real Spark calls: the recorded ambiguous text
returned candidates [12, 2] and uncertain; a clean authored statement returned 12 and certain;
an authored explicit recount/correction returned 11 and certain. These are known/authored
transcripts, not fresh ASR, a held-out set, or evidence that transcription accuracy improved.
Candidate extraction and role assignment are still model judgments. The original failed
smoke test remains intact. Results: `evaluation/voice-grounding-development.json`.

## Full integration and supplier follow-up — 1 Nov 2026

A fresh run combined the known matching synthetic images with the existing generated
single-speaker `01-basit.wav` clip. All stages ran, but inspecting its second-reader output
revealed a supplier field containing commentary. Although product/quantity matched, the
old second-reader comparison ignored supplier. That approval is **not** a successful test
of complete supplier agreement.

Full checks now compare the second reader's supplier with the trusted order. Missing,
wrong or commentary-filled suppliers hold the receipt. The note-reading prompt explicitly
requires literal supplier transcription. Replaying the earlier bad supplier through the
corrected gate returns `human / readers_disagree`. A fresh full run on the same development
inputs then completed in 71.161 seconds: both readers returned Doğan Gıda Pazarlama and
12 cartons, the audit agreed, and the dry-run receipt was approved with document=null.
No ERP write occurred. Both runs and the invalidation are retained in
`evaluation/full-integration-development.json`; these known synthetic cases remain
**development integration evidence**, not held-out field accuracy or latency benchmarks.

The revised simulator keeps agents in their offices, with active-office lighting and speech
labels. Only the warehouse receiver and driver perform physical floor work. This supersedes
the earlier floor-group conversation layout requested during development.

## Browser checks of the final receiving UI — 1 Nov 2026

Normal delivery: replayed through the office-based conversation, A-01-L0 staging and final
C-06-L1 rack placement. Empty manual confirmation showed the explicit “grey example is not
an entered address” warning; the simulated scan button completed the location confirmation.
The temporary staging selector was absent at the final scan, and the placed pallet remained
on the rack when the forklift started its return. The top Warehouse 01 badge was absent.
These are simulator behavior checks, not evidence of physical robot operation or ERP writes.

Wrong-product delivery: the recorded BLOCK was retained, the pallet was reloaded onto the
trailer, and Finish exercise completed only after the driver boarded. Missing-carton review
also rejected an acceptance attempt before the required physical/document checks. The
staging selector is now shown only when selecting an accepted load's initial A-01 level.

Offline validation after these changes: 114 Python tests and all five Node test files passed.

Missing-carton delivery: after the physical check, a simulated independently corrected
document and an explicit count of 11, the load moved H-01 → A-01-L0 → C-06-L1. The rack
label showed 11; location confirmation and driver boarding completed. The original BLOCK
remained the recorded gate outcome. Both evidence images loaded successfully in the browser.

Damaged-carton delivery: the recorded ASK ŞEF was retained. After recount, 11 intact cartons
were accepted in the handling simulation and moved via A-01-L0 to C-06-L1; the final scan
reported 11 of 12 and one open on the order. The separate Q-01 object remains in the scene
and the history records the quarantined carton. The driver boarded before completion.

Injected-note delivery: the recorded BLOCK led to H-01, then the explicit Return entire
load choice moved the pallet to R-01. Its simulated scan reported Awaiting carrier
collection, not a completed outbound shipment, and no live inventory update.

Stacked-load delivery: ASK Şef prevented automatic acceptance; the load reached H-01.
Premature acceptance was rejected. The physical recount then completed, and an explicit
12-carton simulated acceptance started the onward handling route. All six scenario decisions
were observed in the browser. The stacked load also reached C-06-L1 with 12 cartons,
passed the simulated scan, and completed driver boarding. All six scenarios reached exercise
completion. Narrow-screen Panel controls were also used during the last two scenarios.

## Pilot preparation — 2 Nov 2026

Blank JSON templates for a field pilot are in evaluation/. No partner, fresh real delivery, field benefit or complete billing result is claimed.
