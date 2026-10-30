# Muse Code task: when Kapı asks Şef, they meet at the table

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena approved (relayed by the session that runs the dock): when the gate's decision is
"ask Şef" (`human`), the characters concerned gather at the round meeting table in the middle
of the hall, the decision and Şef's answer happen there, then they go back to their stations.
Only in the recorded `human` cases (`hasarli`, `belirsiz`); no gathering anywhere else. The
table itself is built in Blender by the other session and arrives in `dock.glb` separately.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you
wrote it). Do not run commands or write probe scripts: this run cannot approve them. Read the
file, edit it directly, and stop; we run the checks ourselves (`experiments/web/sim_test.mjs`
must still print ALL OK). Do not touch `site/sim/models/` (another session exports the dock).

## Who meets, from the record

Only when `G.cs.gate.action === "human"` (today `hasarli` and `belirsiz`):

- always **Kapı** (who asked) and **Şef** (who decides);
- plus the character(s) whose finding raised the doubt, read from the gate's rule
  (`G.cs.gate.rule`): `damaged` → **Spark** (Spark's look at the pallet saw the damaged
  carton); `disagree` → **Sam** and **Spark** (their counts disagree). Any other `human` rule:
  Kapı and Şef only. Wonder, Rover and anyone else stay where they are.

## The table

Centre at Blender/sim floor coordinates `MEET = { x: -4.0, y: -6.5 }` (the same frame as
`PEOPLE[].b`), radius 1.1 m, top 0.97 m; six stools around it. Standing spots: 1.7 m from the
centre at angles 0°, 60°, 120°, 180°, 240°, 300° (0° = +x), each facing the centre. The
table may not be in `dock.glb` yet: the gathering must work without it (it is just a point on
the floor) and must not look up any object by name.

Spot use, so the deciding camera (from the yard, +y side) sees every face: Şef at 240°, Kapı
at 300° (the far side), Spark at 180°, Sam at 0°. Never use 60° or 120° (they would stand
between the camera and the table).

## The sequence

1. Everything up to Kapı's decision stays as it is (the walk to the pallet, the reading
   cards, the light, the screen). For `human` cases, replace today's reaction (Şef stepping
   away from the pallet, `G._sefStep`, and the `ask` look) by the gathering.
2. 900 ms after Kapı's decision card, the meeting characters walk to their spots with the
   existing walk (`startWalkTo`), a little faster than a stroll (2.0 m/s for this walk only),
   facing the table centre on arrival. Avoid walking through the receiving zone and the
   pallet: if the straight line crosses `ZONE` (with 0.4 m margin), go around via one corner
   waypoint outside it. Everyone else keeps working.
3. The camera: when the walk starts, glide the deciding camera over about 2.5 s to a view of
   the table from the yard side (the table centre slightly below the middle of the screen,
   all meeting spots in view, the result card on the right not covering them on desktop; on
   phones the table in the upper half, above the result sheet). Stay there.
4. At the table: while the feed's follow-up thread plays (`G.cs.signoff`, the Şef row and the
   rows after it), the speech bubbles appear over their heads there as usual. Make the feed's
   follow-up section (the divider and everything after it) wait until all meeting characters
   have arrived (or 9 s have passed), so Şef's answer is given at the table. Characters at the
   table use idle; the one whose row is speaking turns slightly toward the one addressed.
5. After the last follow-up row (or 6 s after arrival when there is no sign-off), wait 2.5 s,
   then everyone walks back to their station (their floor home) at the normal speed and the
   camera glides back to the deciding view.

Restart and "Try another delivery" cancel all of it (timers through `later(...)`, the
camera and walkers reset as today by `sendAllHome`). `prefers-reduced-motion`: no walking or
camera glides: the meeting characters appear at their spots at once, the camera cuts to the
table view, and they appear back home when the feed has finished.

## Test hook

`window.__sim.meeting()` returns `{ ids, spots, arrived }`: the meeting character ids for the
current case (`[]` when there is no meeting), their target spots `{ id: { x, y } }`, and
whether all have arrived.

No sound. Change nothing outside `site/sim/index.html`.
