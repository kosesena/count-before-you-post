# Muse Code task: make the receiving dock look like a real, well-kept warehouse

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
Sena's notes on the current scene: the truck is hard to see, the open dock door should read
clearly, the characters are far too small, the hall looks empty, the racks are too few and
too bare, and floor and walls are the same grey.

---

You are working in the repository `count-before-you-post`. The receiving-dock scene is built
from code by `experiments/blender/warehouse.py` (Blender 5.2, EEVEE, run headless as
`blender -b -P experiments/blender/warehouse.py -- <out_dir> <variant>`). Its renders are
the test images of the project: SAM 3.1 and Muse Spark were measured on the ceiling-camera
frames (`DockCam`, saved as `depo-<variant>-kamera.png`), so those must never change.

Make the scene look like a high-quality, busy, real warehouse, **only when the environment
variable `CBYP_POLISH=1` is set**. Without it, the script must build exactly the same scene
as now, object for object, so the measured renders stay reproducible.

## What to improve (in this order)

1. **The truck.** Today it is a plain box trailer behind the door. Build a recognisable
   semi-truck: a coloured tractor cab with windows, headlights and wheels, and the trailer on
   wheels, backed up to the dock, with the trailer's open rear visible through the door and a
   few pallets of cargo inside. It must be clearly visible from the overview camera.
2. **The open dock door.** Make it obvious that the roll-up door is open: the raised door
   with horizontal slats at the top of the opening, a black dock seal (curtains) around the
   opening, a steel dock leveller plate bridging the floor to the trailer, a green/red dock
   light, and daylight outside (a bright sky behind the truck and a sun lamp, so light falls
   in through the door).
3. **The characters.** The cardboard standees (`standee()`, cut-outs in
   `experiments/blender/cutouts/`) are too small. Make them life-size or a bit bigger
   (about 2.0 to 2.4 m tall). Add standees for Spark, Sam, Voice and Wonder next to Kapı and
   Şef: extend `experiments/blender/make_cutouts.py` to cut them out of
   `assets/mascots/hello/<name>.jpg` (plain coloured background, flood from the corners as it
   already does) and write `cutouts/<name>.png`. Place them where the overview camera sees
   them, facing it, each near the thing it does (Spark by the delivery note clipboard, Sam
   under the ceiling camera's line of sight but outside its view, Voice by the receiver,
   Wonder by the workbench/screen, Kapı by the barrier, Şef by the quarantine zone).
4. **A full hall.** More racking: several rows of tall pallet racks (3 to 4 levels, orange
   beams, blue uprights) along the left wall and the back of the hall, almost every slot
   holding a pallet: cardboard cartons in varied browns and sizes, some shrink-wrapped
   (semi-transparent film), some with printed labels. On the floor: wrapped pallets waiting,
   a stack of empty pallets, a hand truck, safety cones, yellow bollards by the door, a fire
   extinguisher on the wall, a small glass-walled office cabin with a desk. Keep walkways
   free and make it look organised, not cluttered.
5. **Floor and walls must differ.** Floor: polished light-grey epoxy/concrete with subtle
   variation (procedural noise, a few tyre marks), yellow walkway lines and hatched zones.
   Walls: insulated panels with vertical seams, a dark coloured lower band (about 1.2 m) and a
   light upper part; steel columns along the walls. Ceiling: visible roof structure with
   high-bay lights.
6. **Quality.** Warm high-bay lighting plus the daylight from the door, soft shadows,
   ambient occlusion / raytracing as Blender 5.2 EEVEE offers it (look the settings up by
   reading `bpy` properties, do not guess enum names), slight bevels on boxes, no flat
   untextured surfaces in the overview shot.

## Must not change (in polish mode too)

- The delivery itself: `pallet`, `load_pallet` cartons and labels, the pallet jack, the
  clipboard and its delivery note texture, the gate barrier and light, the decision screen.
  Their positions, sizes and materials stay as they are.
- `DockCam` (`ceiling_camera`): position, lens, target. Nothing new may appear inside its
  view (roughly x in [-2.5, 2.5], y in [3.5, 7.5] at floor level).
- `VARIANTS`, the truth written to `depo-truth.json`, the `CBYP_LANG` handling.

## How to render and what to hand back

- In polish mode, render only the overview cameras (`genel`, `kapi`, `irsaliye`), not
  `kamera`, and do not write `depo-truth.json`. Use the output folder
  `experiments/blender/out/polish` and the variant `ok`:
  `CBYP_POLISH=1 blender -b -P experiments/blender/warehouse.py -- experiments/blender/out/polish ok`
- You may adjust the overview camera `genel` so the door, truck, pallet and characters fill
  the frame better; keep it a wide shot of the dock.
- Use only procedural materials and Blender primitives: no downloads, no network, no new
  Python packages.
- Touch only `experiments/blender/warehouse.py`, `experiments/blender/make_cutouts.py` and
  the new files in `experiments/blender/cutouts/` and `experiments/blender/out/polish/`.
  Do not commit.
- Check that a run without `CBYP_POLISH` still works:
  `blender -b -P experiments/blender/warehouse.py -- /tmp/cbyp-check ok` must produce the four
  renders without errors.
- At the end, list what you changed, the render time of the polished `ok` scene, and anything
  you could not do.
