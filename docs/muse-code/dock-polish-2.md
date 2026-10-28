# Muse Code task: the dock, second round

The prompt below was given verbatim to Muse Code (`muse exec`, model `muse-spark-1.3`).
The first round (`dock-polish.md`) built the polish pass in `experiments/blender/warehouse.py`
and stopped on a network error before rendering; one line was fixed by hand (in `p_clear`,
a removed light was looked at again: `if` → `elif`). These are Sena's and Claude's notes on
the first renders.

---

You are working in the repository `count-before-you-post`, on the polish pass of the dock
scene in `experiments/blender/warehouse.py` (everything under `if POLISH`, the `p_*`
functions). The first round is done and renders; read `docs/muse-code/dock-polish.md` for the
rules, which still hold: polish only with `CBYP_POLISH=1`, the default scene unchanged object
for object, the delivery (pallet, cartons, labels, pallet jack, clipboard and note, gate
barrier and light, decision screen) and `DockCam` untouched, nothing new inside DockCam's view.

Render the current state first to see it:
`CBYP_POLISH=1 blender -b -P experiments/blender/warehouse.py -- experiments/blender/out/polish ok`
(about a minute; renders `depo-ok-genel.png`, `depo-ok-kapi.png`, `depo-ok-irsaliye.png`).

Fix these, in this order:

1. **The characters stand on brown rectangles.** The standee cut-outs have transparent
   backgrounds (`experiments/blender/cutouts/*.png`, RGBA), but in the render the whole
   rectangle shows as a brown board. Make the transparent part invisible so each character
   stands as a silhouette (a thin cardboard edge and a small foot stand are fine). In Blender
   5.2 EEVEE look up how a material becomes transparent by reading the material's properties
   (e.g. the render method / blend settings) instead of guessing names.
2. **The truck's cab is not visible.** From the overview camera you only see the trailer's
   inside through the door. Make the tractor unit readable: either open a wide window or a
   second, raised door next to the dock so the cab shows, or add a camera `disari` outside
   the building that frames the whole truck backed up to the dock (render it too).
3. **The delivery is hidden.** Standees stand in front of the pallet in the `kapi` view and
   the pallet looks small in `genel`. Move every standee so none covers the pallet, the gate,
   the barrier or the clipboard from the `genel` and `kapi` cameras, and frame `genel` so the
   pallet with its 12 cartons is clearly the centre of the shot.
4. **The racks look half empty.** Fill nearly every rack slot with a loaded pallet: stacked
   cartons in varied browns and sizes, several shrink-wrapped, some with labels; add one more
   rack row if there is room. It should look like a busy, organised warehouse.
5. **Hard light circles on the floor.** Replace the bright round pools with soft, even
   high-bay light (bigger or more numerous lights with lower power, softer shadows), keeping
   the warm tone and the daylight through the door.
6. **The forklift** is still the old blocky model: give it a mast with forks, an overhead
   guard, a seat and wheels, in the same yellow.

After each fix, render and look at the images yourself before the next one. At the end:
- confirm the default build is unchanged: `blender -b -P experiments/blender/warehouse.py --
  /tmp/cbyp-check ok` renders without errors;
- list what you changed and anything you could not do.

Touch only `experiments/blender/warehouse.py` (and new files in `experiments/blender/cutouts/`
and `experiments/blender/out/polish/`). No downloads, no network, no new packages, no commits.
