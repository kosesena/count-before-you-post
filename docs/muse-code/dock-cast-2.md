# Muse Code task: the cast at the dock, round 2 (placement, role signs)

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Round 1 is `docs/muse-code/dock-cast.md`; we rendered its stills and Sena looked at them.

---

You are working in the repository `count-before-you-post`, on
`experiments/blender/dock_cast.py` (you wrote it; read it first). We rendered your `stills`;
this is what we saw, and what to change. Change only `dock_cast.py`.

## What we saw

Your log from the render:

    sam: pos=(2.70, 6.80) · voice: (-4.60, 2.10) · wonder: (-8.20, 1.60)
    kapi: (6.30, 3.20) h=1.75 · sef: (8.20, 4.20) h=1.75
    rover: (8.50, 6.20) · glimmer: (7.00, 7.10) · iris: (-6.60, -0.60) · ada: (-9.60, -0.90)
    spark-lego.glb missing, Spark keeps his standee

In the `genel` shot (camera at (10.8, -9.8, 4.8), looking at the pallet at (0, 5.3)):
**Kapı and Şef stand behind the yellow forklift** (it sits around (8, -0.5) to (8, 1.5) in
that view) and are half hidden; **Rover stands behind Şef** and is hardly visible; Glimmer is
small at the back. In `teslimat` the placement reads well. The figures themselves look good.

## Changes

1. **Placement.** Move Kapı, Şef, Rover and Glimmer so that in `genel` none of them is hidden
   behind the forklift, the office, the racks or another figure, and each one's full body is
   visible. Kapı belongs next to the gate barrier and light (his job), Şef close to the
   receiving zone where he would sign off. Keep everything the round-1 rules forbid: no
   figure on the pallet, gate, barrier, light, screen or clipboard, none inside DockCam's view.
   Work it out from the camera positions and object bounding boxes in the scene (you can read
   them in the script); check that each figure's bounding box is not covered by another object
   from the `genel` camera, and log the result per figure.
2. **Role signs.** Next to each figure, a small free-standing sign at about chest height, like a
   name plate on a slim post, facing the same camera as the figure: the name in bold and one
   line for the job, in English:
   Spark · reads the note · Sam · counts the cartons · Voice · hears the receiver ·
   Kapı · the gate · Şef · signs off · Wonder · checks and writes the paperwork ·
   Rover · reads the note again · Glimmer · the other open-weight reader ·
   Iris · drew the cast · Ada · wrote the code.
   Use the same style as the dock's other signs in `warehouse.py` (`text()` and the sign
   materials there): clean, readable at 1920×1080 in `genel` and `teslimat`, not covering the
   figure. Use each character's colour for a thin accent stripe on the sign (Spark #f97316,
   Sam #3b82f6, Voice #1e3a8a, Kapı #a16207, Şef #1d4ed8, Wonder #ca8a04, Rover #0d9488,
   Glimmer #8b5cf6, Iris #db2777, Ada #0f766e). Spark gets his sign even while he is a standee.
3. Keep `stills`, `move` and `all` working as before.

`python3 -m py_compile experiments/blender/dock_cast.py` must pass. In your final answer, list
each figure's new position and why it is not hidden.
