# Controlled screen-review timing

Open `/time-study/`. Six historical synthetic cases are shown twice, with manual and prerecorded-assisted blocks in randomized order and shuffled cases within each block. Policy is shown before starting. Images load and decode before the timer starts. The participant submits post/block/human; correctness feedback is withheld until all 12 trials finish.

The browser records active visible-page milliseconds, wall duration, hidden-tab interruptions, condition order, prior familiarity and correctness against the configured synthetic-case policy. Export is local JSON only; no server submission or persistence. Reloading discards the session. A blocked/failed image load cannot start timing.

The summary compares only paired, correct, uninterrupted trials and reports accuracy for both modes. All raw rows, including incorrect and interrupted trials, remain in the export. Negative time differences are retained. No percentage savings claim is generated. No human results have been collected yet.

This measures human screen-review time with prerecorded help. It excludes file upload, API/model latency, exception resolution after the decision and physical warehouse work. It is not full workflow latency or field ROI. Repeated cases create learning effects; randomized block order does not remove them for one participant. English model explanations within the Turkish UI are another potential confound. A representative multi-participant study with independent cases would be needed for generalizable claims.

Verification: five Node metric tests cover empty/unpaired results, negative effects, wrong answers and interruptions. An automated browser walkthrough reached the 12-trial result screen; those machine-generated times were not saved as participant evidence and must never be presented as human measurements.

## Version 2 presentation revision

The recommendation is now above the images and its explanation is in Turkish. Block (a known document/product mismatch) and human review (damage/visibility uncertainty) are explicitly distinguished. Exports use version 2; do not pool these trials with version 1 as if the interface were unchanged. The first participant's version 1 result showed 3/6 versus 4/6 correct decisions and no review-time saving; it is retained privately, not rewritten by this change.
