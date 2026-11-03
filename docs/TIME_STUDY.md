# Controlled screen-review timing

Open `/time-study/`. Six historical synthetic cases are shown twice, with manual and prerecorded-assisted blocks in randomized order and shuffled cases within each block. Policy is shown before starting. Images load and decode before the timer starts. The participant submits post/block/human; correctness feedback is withheld until all 12 trials finish.

The browser records active visible-page milliseconds, wall duration, hidden-tab interruptions, condition order, prior familiarity and correctness against the configured synthetic-case policy. Export is local JSON only; no server submission or persistence. Reloading discards the session. A blocked/failed image load cannot start timing.

The summary compares only paired, correct, uninterrupted trials and reports accuracy for both modes. All raw rows, including incorrect and interrupted trials, remain in the export. Negative time differences are retained. No percentage savings claim is generated. One version 1 participant export has been collected privately; it did not show a review-time saving. No version 2 participant result is recorded yet.

This measures human screen-review time with prerecorded help. It excludes file upload, API/model latency, exception resolution after the decision and physical warehouse work. It is not full workflow latency or field ROI. Repeated cases create learning effects; randomized block order does not remove them for one participant. Version 1 used English model explanations within the Turkish UI, a potential confound; version 2 uses Turkish explanations. A representative multi-participant study with independent cases would be needed for generalizable claims.

Verification: five Node metric tests cover empty/unpaired results, negative effects, wrong answers and interruptions. An automated browser walkthrough reached the 12-trial result screen; those machine-generated times were not saved as participant evidence and must never be presented as human measurements.

## Version 2 presentation revision

The recommendation is now above the images and its explanation is in Turkish. Block (a known document/product mismatch) and human review (damage/visibility uncertainty) are explicitly distinguished. Exports use version 2; do not pool these trials with version 1 as if the interface were unchanged. The first participant's version 1 result showed 3/6 versus 4/6 correct decisions and no review-time saving; it is retained privately, not rewritten by this change.

## Importing participant exports

Run `node evaluation/analyze_time_study.mjs <export-v1.json> <export-v2.json>` and save output under `evaluation/private/`. The importer checks all six case pairs, valid measurements and answers against the current configured case policy, then recomputes accuracy, unsafe accepts and paired timing. Each study is kept separate by UI version; no pooled improvement is calculated. Missing, duplicate or inconsistent trials are rejected. Raw participant exports stay private. Eight metric/import tests pass.

The returning participant has already seen these cases and should mark prior familiarity on the next run. This is a repeat usability check, not a new independent participant. An assistant must not answer the timed trials on the participant’s behalf or describe automated browser timings as human data.
