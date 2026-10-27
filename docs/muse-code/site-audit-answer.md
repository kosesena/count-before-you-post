# Muse Code answer: does the demo page match the repository?

Muse Code's answer to [site-audit.md](site-audit.md), verbatim (26 model calls, read-only; no file was
changed). What was checked and fixed afterwards is in `docs/JOURNAL.md`.

---

Top finding: the page faithfully shows the dock cases, rules, masks, cross-check, both agent runs, voice clips, and cast. The real problems are small: README vs page differ on one agent run, and README/roadmap/test counts are stale.

## 1. Is everything there?

Overview. Detail and line refs follow.

| Claim | Page | Verdict |
|---|---|---|
| Six dock cases | Case explorer | Shown |
| Gate rules | Rule list + decider | Shown |
| SAM masks | Camera switch | Shown |
| Carton cross-check | Readings + timeline | Shown |
| Agent, both modes | Side-by-side runs | Shown |
| ERP receipts | Agent trace only | Partly |
| Voice clips | Audio + transcript | Shown |
| Note reading test | No section | Left out |
| Video/conveyor counts | No section | Left out |
| Cast | Cards + band | Shown |

Six dock cases: shown. `README.md:75-82`, `docs/JOURNAL.md:150-157`, and `experiments/results/gate_warehouse.json` define ok, wrong, eksik, talimat, hasarli, belirsiz. `site/data.json:cases[0-5]` carries all six. `site/index.html:267-271,502-535` renders each with camera, note, readings, gate, and both agent runs.

Gate rules: shown. `cbyp/gate.py:62-63` defines 9 rules. `site/data.json:rules` lists the same 9. `site/index.html:293-306,422-438` labels each rule and marks passed, decided, and not reached per case.

SAM masks: shown. `experiments/draw_masks.py:21,38-43` paints sure green and doubtful amber. `site/data.json:cases[].images.masks` holds each image. `site/index.html:309-313` switches camera, masks, and cross views.

Cross-check: shown. `cbyp/crosscheck.py`, `experiments/results/cross_check.json`, and `site/data.json:cases[].cross` agree on all six counts (verified by re-computation). `site/index.html:411-420,440-447` shows agreed, only-SAM, only-Spark, doubled, plus the gate carton check in the agent timeline.

Agent with and without gate: shown, with one version caveat (see Q2). `site/data.json:cases[].without_gate` and `cases[].agent` come from `experiments/results/agent_warehouse.json` (ungated) and `experiments/results/agent_warehouse_cross.json` (gated). `site/index.html:455-485` renders both.

ERP receipts: partly shown. Three real receipts exist across runs: `MAT-PRE-2026-00001` in `experiments/results/erp_warehouse.json`, `MAT-PRE-2026-00002` in `agent_warehouse.json`, `MAT-PRE-2026-00003` in `agent_warehouse_cross.json`. The page shows only the last, inside the ok agent trace (`site/data.json:cases[ok].agent.posted`). The gate-decision receipt `00001` has no dedicated ERP section. This is fine for a demo. A one-line receipt id per posted case would close it.

Voice clips: shown. `experiments/results/voice_check.json` has 8 rows (4 clips × keywords off/on). `experiments/build_site.py:143-149` keeps only keywords-on rows. `site/data.json:voice[0-3]` has the 4 clips with audio, transcript, quantity, supplier, and certain flag. `site/index.html:273-278,372-383` plays them and marks unsure receivers as supervisor cases. Omitting the keywords-off variants is fine. They differ only in spelling.

Note reading test in several languages: left out. `experiments/results/read_notes.json` has 16 rows, 16/16 quantities right, including German, Chinese, and two injections. The page has no note-reading section. Fine to leave in the repo only. The demo is about the dock. At most link it from the footer.

Video and conveyor counting: left out. `experiments/results/count_video.json`, `experiments/results/count_images.json`, `experiments/count_video.py`, and `experiments/count_images.py` record SAM tracking limits (max 16 objects, line crossing, belt cropping). The page shows none. Fine to leave in the repo only. It is background evidence, not the gate story.

Cast: shown. Eight characters in `experiments/build_site.py:34-58` become eight entries in `site/data.json:characters`. `site/index.html:240-249,359-370` renders the band, cards, speech bubbles, and status pills. Portraits and avatars exist for all eight in `site/img/`.

## 2. Is it consistent?

Overview. Evidence for each follows.

| Check | Result | Weight |
|---|---|---|
| Thresholds 0.88/0.70 | Match | — |
| Rule count 9 | Match | — |
| Per-case numbers | Match | — |
| Gate decisions | Match | — |
| Voice 4 clips | Match | — |
| Model names | Match | — |
| Glimmer/recording status | Match | — |
| belirsiz agent run | Mismatch | Fix |
| Receiver rule in README | Missing | Fix |
| Roadmap cross-check | Stale | Fix |
| Test counts | Stale | Fix |
| 5/6 headline framing | Misleading | Fix |
| Doubtful formula | Latent | Note |

Matches (no action): thresholds (`cbyp/gate.py:28-29`, `README.md:45-46`, `site/index.html:311,395-397`), 9 rules in code, data, and page labels, all per-case SAM counts, cross counts, gate actions, reasons, and voice quantities (recomputed from sources, high certainty). Model short names on the page (Muse Spark, SAM 3.1, Muse Voice) match full ids in `cbyp/meta.py:8-9` and `cbyp/voice.py:14`. Glimmer as coming soon matches on page (`site/index.html:314,367-369`), data (`characters[glimmer].status`), and repo roadmap. Recorded runs with no live calls matches (`README.md:9`, `site/index.html:235`).

Real mismatches:

- Belirsiz gated run. README (`README.md:113`) says the gated agent tried to post 12 while cartons were hidden, then was refused. Page data (`site/data.json:cases[belirsiz].agent`: posted [], refused [], supervisor true) says it asked the supervisor without trying. Both match their own sources: README matches `agent_warehouse.json` gated belirsiz (refused [[12,...]]), page matches `agent_warehouse_cross.json` gated belirsiz (refused []). High certainty. The page uses the newer cross-check run. The README describes the older run.
- Receiver rule missing from README table. `cbyp/gate.py:62-63,135-141` and `site/data.json:rules` include `receiver`. `site/index.html:300` labels it. `README.md:53-62` lists 8 situations with no receiver row. The journal gate list (`docs/JOURNAL.md:136-145`) omits it too, though `docs/JOURNAL.md:314-315` describes the rule. High certainty.
- Roadmap says cross-check is future. `README.md:153` says the cross-check is evidence and a picture today and becomes a rule next. But `cbyp/gate.py:93-129`, `cbyp/agent.py:119-129`, and `docs/JOURNAL.md:257-262` already made it a gate rule, and the page shows gate carton checks. High certainty. Roadmap stale.
- Test counts stale. `README.md:27-28` and `docs/JOURNAL.md:186` say 13/13 (9 gate + 4 ERPNext). `docs/JOURNAL.md:262` says 34. Actual files hold 16 in `tests/test_gate.py`, 4 in `tests/test_erpnext.py`, 11 in `tests/test_agent.py`, 8 in `tests/test_crosscheck.py`, total 39. High certainty by direct count. The page claims no test count, so this is repo staleness, not a page bug.
- Journal hand-edit count. `docs/JOURNAL.md:348` says three small edits, then lists four numbered items. High certainty. Trivial.
- 5/6 headline framing. `site/data.json:summary` (`wrong_without_gate` 5) is built in `experiments/build_site.py:154` as expected-non-post count, i.e. the `run_gate.py:47` hypothetical note-posting baseline. The page label (`site/index.html:340`) says when the agent posts what the note says. That matches the README baseline (`README.md:84-85`). But directly below, the per-case ungated Spark traces posted only twice (ok and talimat). Medium certainty. The number is not false, but readers will misread it as describing the shown traces.
- Doubtful formula differs. `experiments/build_site.py:117-118` counts doubtful as conf < SURE. `cbyp/gate.py:68-69` counts MIN_CONF <= conf < SURE. Identical on current data (lowest conf 0.758, verified), different for future confs below 0.7. Medium certainty. Latent only.
- Extra eksik row in source. `experiments/results/agent_warehouse_cross.json` holds 7 rows: two eksik entries, the first with a `note` key. `experiments/build_site.py:101-103` filters it out, so the page correctly shows one eksik. Medium certainty. Provenance quirk, not a page error.

Wording differences that are still true: ERPNext v16 vs v16.37 (`README.md:91`, `docs/JOURNAL.md:189`), Muse Voice vs Muse Voice Transcribe (`site/index.html:245`, `cbyp/voice.py:14`), page omitting the 0.70 lower bound in two legends while code and README state it, mask legend omitting white agreed points while `experiments/cross_check.py:50-54` paints agreed points white and only-Spark points red. None is false.

## Changes, most important first

- Align the README agent table with the page, or label it as the earlier run without cross-check. State which result file each table comes from.
- Add the receiver rule to the README gate table, or note the table is simplified.
- Update the roadmap: cross-check rule and reasoning summaries are done; remaining are Spark Open/Glimmer, unseen scenes, and real photos.
- Clarify the 5/6 stat on the page: hypothetical note-posting baseline, distinct from the ungated Spark traces below it.
- Update test counts in README and journal, or drop exact counts.
- Fix the journal three-vs-four edit wording.
- Unify the doubtful formula between `build_site.py` and `gate.py`.
- Optionally show the ERP receipt id for the gate ok case, not only the agent trace.