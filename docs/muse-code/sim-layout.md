# Muse Code task: the pallet in view when the gate decides

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Measured with the test hook (camera projection) during `deciding` in the `ok` case, desktop
1600×900: the delivery projects to (755, 471) and the forklift to (778, 497): **the pallet the
whole scene is about is hidden behind the forklift**, and Sam, walking to it, disappears behind
the forklift too. Rover's station also covers Sam's.

---

You are working in the repository `count-before-you-post`, on `site/sim/index.html` (you wrote
it). Do not run commands or write probe scripts: this run cannot approve them. Read the file,
edit it directly, and stop; we measure the result ourselves with the `?test` hook (which now
also exposes `camera` and `delivery`).

1. **The forklift parks after setting the pallet down.** When `deciding` starts, the forklift
   (with nobody driving) reverses about 2.5 m in a straight line, then turns and rolls to a
   parking spot beside the zone on the right (about x = 3.6, y = 0.2 in Blender coordinates,
   heading +x, forks lowered), over about 2.5 s with gentle easing, wheels turning, using the
   existing forklift pose code (`F.x`, `F.y`, `F.h` and the group update), not a teleport;
   colliders don't matter for this scripted move. The walkers start after it has backed off
   enough not to cross it. "Try another delivery" resets it as today.
   Make sure the parked forklift doesn't stand in front of Kapı, Kapı's post or the gate light
   from the deciding camera; pick a spot that keeps them clear (right of the zone, further
   back toward the door if needed).
2. **The walkers' pallet spots**: with the forklift gone, the side of the pallet that faces
   the deciding camera is free. Place a single walker on that side (between the pallet and
   the camera, about 1.3 m from the pallet's centre, slightly to one side so it doesn't cover
   the pallet), facing the pallet; for two walkers (`belirsiz`) one on each front corner.
3. **Rover's station**: move it so it covers no other station from the deciding camera (the
   right side of the arc, beyond Sam's, or the left beyond Wonder's), keeping the arc tidy.

Keep everything else. Change nothing outside `site/sim/index.html`.
