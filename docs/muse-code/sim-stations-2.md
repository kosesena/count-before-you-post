# Muse Code task: stations, round 2

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Seen in the deciding view after the stations round: the job signs stand in front of the
characters and cover their bodies, Spark's sign covers the gate's decision screen, and the old
floating name labels still show next to the new signs.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote the stations). Do not run commands or write probe scripts: this run cannot approve them.
Read the file, edit it directly, and stop; we run the checks ourselves.

1. Job signs: put each sign **beside** its character (on the side away from the pallet), not
   between the character and the camera; lower it (top edge at about 1.1 m) and make it a
   little smaller, so from the deciding camera every character's whole body is visible and the
   sign reads as a desk plate.
2. Nothing may cover the gate's decision screen (the canvas display at about x = -3.6, y = 2.6)
   from the deciding camera: move Spark's station (and any other) so the screen is fully
   visible.
3. Floating name labels: hide them for every character that has a station sign (the sign
   replaces it) and for seated characters; keep them only where neither exists.

Keep everything else. Change nothing outside `site/sim/index.html`.
