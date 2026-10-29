# Muse Code task: the 3D cast at the dock, and a camera move for the video

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Muse Code cannot run Blender in its sandbox, so we render its script and send back what we
see. What it produced and what had to be fixed afterwards is recorded in `docs/JOURNAL.md`.

---

You are working in the repository `count-before-you-post`. Read `README.md` ("Meet the cast"),
then `experiments/blender/warehouse.py`, in particular `polish()` and `p_standees()`: the
dressed-up dock (`CBYP_POLISH=1`) has the characters as flat cardboard standees. That scene is
saved after rendering as `experiments/blender/out/polish/depo-ok.blend` (and
`experiments/blender/out/polish/<lang>/depo-ok.blend` for en, de, zh).

The characters now exist as rigged 3D Lego-style figures:
`assets/mascots/3d/lego/<name>-lego.glb` for ada, glimmer, iris, kapi, rover, sam, sef, voice,
wonder (Spark is being made; use `spark-lego.glb` if the file exists, otherwise leave his
standee in place). Each GLB has three actions: `Walk`, `Idle`, `Wave`. Their scale and
origin are whatever the export gave: measure each figure's bounding box after import.

## Goal

Write a new script, `experiments/blender/dock_cast.py`. Do not edit `warehouse.py`, the GLBs or
anything else. Run as:

    blender -b <blend> -P experiments/blender/dock_cast.py -- <out_dir> [stills|move|all]

It opens the saved polish scene and:

1. **Replaces the standees with the 3D figures.** Remove the objects named `p_stand_*` and
   `p_standft_*`, import each GLB, scale it so the figures stand at a consistent height (about
   1.6 m; Kapı and Şef may be a little taller), stand it on the floor (z of its lowest point = 0)
   at the spot its standee had (the `spots` list in `p_standees`), turned towards the camera
   like the standee was. Kapı's standee was `kapi-gec.png`/`kapi-dur.png`; Spark, Sam, Voice,
   Wonder, Kapı, Şef had spots. Place Rover, Glimmer, Iris and Ada too, near the office or the
   racks, where none of the cameras' main subjects (pallet, cartons, gate, barrier, clipboard,
   decision screen) are covered. Actions: Spark `Wave`, Kapı `Wave`, everyone else `Idle`;
   offset each figure's start frame a little so they don't move in sync.
2. **Never changes the delivery.** The pallet, cartons, labels, pallet jack, gate, barrier,
   light, screen, clipboard and the ceiling camera `DockCam` stay exactly as they are, and no
   figure may appear inside DockCam's view.
3. **`stills`**: renders the existing cameras `genel`, `teslimat` and `disari` at 1920×1080 to
   `<out_dir>/cast-<camera>.png`.
4. **`move`**: adds one new camera, `FlyCam`, and renders a 10 second camera move at 24 fps,
   1920×1080, to `<out_dir>/cast-move.mp4` (FFmpeg, H.264). The move, in one continuous,
   smooth path with eased start and end: start outside behind the truck (near the `disari`
   camera), glide along the trailer and in through the open dock door, sweep over the
   characters, and end close on the pallet with the gate's light and the decision screen in
   frame (near the `teslimat` camera). No cuts, no shaking, no spinning. The figures animate
   while the camera moves.

Use the render engine the scene already has. In Blender, look up shader nodes by type, never by
name, and read enum values from the API rather than guessing them (see how `warehouse.py` does
it). Keep the script in the style of `warehouse.py`: small functions, a docstring at the top
saying what it does and how to run it.

## Checks before you finish

- `python3 -m py_compile experiments/blender/dock_cast.py` passes.
- Say in your final answer what each placed figure's position and scale are, which spots you
  chose for Rover, Glimmer, Iris and Ada and why, and anything you could not verify without
  rendering. We will render it and tell you what we see.
