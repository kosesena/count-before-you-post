# Muse Code task: pallet racks against the walls

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena, 30 Oct: the racks stand in five free rows across the left half of the hall and look
scattered ("raflar ortada çok dağınık duruyor"); they should stand against the walls, the
way a real warehouse keeps its floor clear.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/warehouse.py`, function `p_racks` (the polished pallet racks). Do not
run commands or write probe scripts: this run cannot approve them. Read the file, edit it
directly, and stop; we build and render ourselves.

Today `p_racks` builds five free-standing rows (A–E) at y = 8.5, 6.0, −2.5, −5.0, −7.5 with
bays at x between −12.5 and −6.5: an island of racks in the left half of the hall. Rebuild
it so **every rack stands against a wall** and the middle of the hall is open floor:

1. **Left wall run.** The left wall's inner face is at x ≈ −14.85. Put one continuous run of
   bays along it, backs against the wall: rack depth along x (the bay's 1.0 m depth from
   x = −14.75 to −13.75), bay length along y (2.6 m per bay as now, uprights at the bay
   ends), from y = −10.8 up to y = 8.4 — as many whole bays as fit (7). Same uprights,
   beams, three levels and loaded pallets as now, just rotated 90° so the loads face +x (the
   hall). Keep the row labels (one per bay, `L1`…`L7`) on the beam fronts facing the hall.
2. **Back wall run, left of the dock door.** The back wall's inner face is at y ≈ 9.85 and
   the dock door opening is x in [−1.6, 1.6]. Put a second run along it, backs against the
   wall: depth along y (from y = 9.75 to 8.75), from x = −13.6 to −4.0 (as many whole 2.6 m
   bays as fit, 3), loads facing −y. Labels `B1`…`B3`. Leave x > −3.5 free (the door, its
   bumpers, the signal light and the receiving zone).
3. Keep the yellow floor-guards/footplates if the old rows had them, at the new uprights.
   Every object keeps the `p_rk*` naming so the export and the simulator's colliders pick
   them up.
4. Anything else the polished build places in those two wall strips (x < −13.4 for
   y in [−11, 9]; y > 8.6 for x in [−14, −3.5]) — props, standees, cones, boxes, a
   workbench, a sign — move it out into the open floor just in front of the racks, keeping
   it clear of the meeting area (a 3.5 m circle around (1.0, −7.0)), the receiving zone
   (x in [−2.5, 2.5], y in [3.3, 7.7]), the quarantine bay (x in [5, 9], y in [3.3, 7.7]) and
   the floor stations (around (−4.7, 0.9), (1.4, 1.2), (4.4, 2.0), (−5.9, 0.4),
   (−1.6, −0.9), (−0.6, −0.6), 1.2 m each). Report what you moved.

Change nothing outside `experiments/blender/warehouse.py`.
